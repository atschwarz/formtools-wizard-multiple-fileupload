from django import forms

from .widgets import ClearableMultipleFilesInput, FILE_INPUT_CONTRADICTION


class MultipleFilesField(forms.FileField):
    # Taken from:
    # https://stackoverflow.com/questions/46318587/django-uploading-multiple-files-list-of-files-needed-in-cleaned-datafile#answer-46409022

    widget = ClearableMultipleFilesInput

    def clean(self, data, initial=None):
        # If the widget got contradictory inputs, we raise a validation error
        if data is FILE_INPUT_CONTRADICTION:
            raise forms.ValidationError(self.error_message['contradiction'], code='contradiction')
        # False means the field value should be cleared; further validation is
        # not needed.
        if data is False:
            if not self.required:
                return False
            # If the field is required, clearing is not possible (the widg    et
            # shouldn't return False data in that case anyway). False is not
            # in self.empty_value; if a False value makes it this far
            # it should be validated from here on out as None (so it will be
            # caught by the required check).
            data = None
        if not data and initial:
            return initial
        return data
