from django import forms

FILE_INPUT_CONTRADICTION = object()


class ClearableMultipleFilesInput(forms.ClearableFileInput):
    # Taken from:
    # https://stackoverflow.com/questions/46318587/django-uploading-multiple-files-list-of-files-needed-in-cleaned-datafile#answer-46409022

    def value_from_datadict(self, data, files, name):
        upload = files.getlist(name)  # files.get(name) in Django source

        if not self.is_required and forms.CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):

            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # objects that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False
        return upload
