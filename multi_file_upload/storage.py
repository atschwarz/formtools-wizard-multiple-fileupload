from django.core.files.uploadedfile import UploadedFile
from django.utils import six
from django.utils.datastructures import MultiValueDict


from formtools.wizard.storage.exceptions import NoFileStorageConfigured
from formtools.wizard.storage.base import BaseStorage


class MultiFileSessionStorage(BaseStorage):
    """
    Custom session storage to handle multiple files upload.
    """
    storage_name = '{}.{}'.format(__name__, 'MultiFileSessionStorage')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.prefix not in self.request.session:
            self.init_data()

    ################################################################################################
    # Helper
    ################################################################################################

    def _get_data(self):
        self.request.session.modified = True
        return self.request.session[self.prefix]

    def _set_data(self, value):
        self.request.session[self.prefix] = value
        self.request.session.modified = True

    data = property(_get_data, _set_data)

    ################################################################################################
    # formtools.wizard.storage.base.BaseStorage API overrides
    ################################################################################################

    def reset(self):
        # Store unused temporary file names in order to delete them
        # at the end of the response cycle through a callback attached in
        # `update_response`.
        wizard_files = self.data[self.step_files_key]
        for step_files in six.itervalues(wizard_files):
            for file_list in six.itervalues(step_files):
                for step_file in file_list:
                    self._tmp_files.append(step_file['tmp_name'])
        self.init_data()

    def get_step_files(self, step):
        wizard_files = self.data[self.step_files_key].get(step, {})

        if wizard_files and not self.file_storage:
            raise NoFileStorageConfigured(
                "You need to define 'file_storage' in your "
                "wizard view in order to handle file uploads.")

        files = {}
        for field in wizard_files.keys():
            files[field] = {}
            uploaded_file_list = []

            for field_dict in wizard_files.get(field, []):
                field_dict = field_dict.copy()
                tmp_name = field_dict.pop('tmp_name')
                if(step, field, field_dict['name']) not in self._files:
                    self._files[(step, field, field_dict['name'])] = UploadedFile(
                        file=self.file_storage.open(tmp_name), **field_dict)
                uploaded_file_list.append(self._files[(step, field, field_dict['name'])])
            files[field] = uploaded_file_list

        return MultiValueDict(files) or MultiValueDict({})

    def set_step_files(self, step, files):
        if files and not self.file_storage:
            raise NoFileStorageConfigured(
                "You need to define 'file_storage' in your "
                "wizard view in order to handle file uploads.")

        if step not in self.data[self.step_files_key]:
            self.data[self.step_files_key][step] = {}

        for field in files.keys():
            self.data[self.step_files_key][step][field] = []
            for field_file in files.getlist(field):
                tmp_filename = self.file_storage.save(field_file.name, field_file)
                file_dict = {
                    'tmp_name': tmp_filename,
                    'name': field_file.name,
                    'content_type': field_file.content_type,
                    'size': field_file.size,
                    'charset': field_file.charset
                }
                self.data[self.step_files_key][step][field].append(file_dict)
