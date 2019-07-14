from django import forms
from django.core.exceptions import ImproperlyConfigured

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout, Div, Field, ButtonHolder, Submit, HTML)

from .fields import MultipleFilesField
from .widgets import ClearableMultipleFilesInput


class UploadForm(forms.Form):
    file_field = MultipleFilesField(widget=ClearableMultipleFilesInput(
        attrs={'multiple': True}), label='Files')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('file_field'),
                ButtonHolder(Submit('submit', 'Upload')),
            )
        )


class ConfirmCancelForm(forms.Form):

    def __init__(self, *args, cancel_url=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not cancel_url:
            raise ImproperlyConfigured(
                'You have to specify the attr "cancel_url" when using the ConfirmCancelForm.')

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Div(
                Submit('submit', 'Submit'),
                HTML('<a href="{}">Cancel</a>'.format(cancel_url))
            )
        )
