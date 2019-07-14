from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse_lazy
from django.core.exceptions import SuspiciousMultipartForm

import os
from formtools.wizard.views import SessionWizardView

from .storage import MultiFileSessionStorage
from .forms import UploadForm, ConfirmCancelForm


class FileUpload(SessionWizardView):
    storage_name = MultiFileSessionStorage.storage_name
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'upload'))

    form_list = [
        ('upload', UploadForm),
        ('confirm', ConfirmCancelForm),
    ]

    templates = {
        'upload': 'upload.html',
        'confirm': 'confirm.html',
        'done': 'summary.html'
    }

    form_kwargs = {
        'confirm': {'cancel_url': reverse_lazy('file-upload')}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_done = False

    def get_template_names(self):
        if self.is_done:
            return [self.templates['done']]
        else:
            return [self.templates[self.steps.current]]

    def get_form_kwargs(self, step=None):
        if not step:
            return {}
        if not hasattr(self, 'form_kwargs'):
            return {}
        return self.form_kwargs.get(step, {})

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        step_context_handler_name = 'get_{}_context_data'.format(self.steps.current.lower())
        if hasattr(self, step_context_handler_name):
            context.update(getattr(self, step_context_handler_name)(form=form, **kwargs))

        return context

    def get_confirm_context_data(self, form, **kwargs):
        cleaned_data = self.get_cleaned_data_for_step('upload')
        if cleaned_data:
            return {'files': [file.name for file in cleaned_data.get('file_field', [])]}
        else:
            return {}

    def done(self, form_list, **kwargs):
        self.is_done = True
        form_dict = kwargs.get('form_dict', {})
        upload_form = form_dict.get('upload', None)
        if not upload_form:
            raise SuspiciousMultipartForm('Could not find the formular for the upload step.')

        cleaned_data = upload_form.cleaned_data
        files = []
        if cleaned_data:
            files = [file.name for file in cleaned_data.get('file_field', [])]

        return self.render(self.templates['done'], files=files)
