from django import forms


class ShortClearableFileInput(forms.ClearableFileInput):
    def get_template_substitution_values(self, value):
        original_dict = super().get_template_substitution_values(value)
        original_dict["initial"] = original_dict["initial"].split("/")[-1]
        return original_dict
