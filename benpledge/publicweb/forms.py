from django import forms
from django.forms import  ModelForm
from models import Dwelling, Pledge

from postcode_parser import parse_uk_postcode


class DwellingForm(ModelForm):

    class Meta:
        model = Dwelling
        exclude = ['house_id']

    def is_valid(self):
        valid = super(DwellingForm, self).is_valid()

        if not valid:
            return valid
        try:
            parse_uk_postcode(self.cleaned_data['postcode'])
        except Exception:
            self._errors['postcode_error'] = ['Please enter a valid postcode']
            return False
        return True

class PledgeForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['deadline']