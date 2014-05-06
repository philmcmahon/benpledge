from django import forms
from django.forms import  ModelForm
from django.core.exceptions import ValidationError
from models import Dwelling, Pledge

from postcode_parser import parse_uk_postcode


class DwellingForm(ModelForm):

    class Meta:
        model = Dwelling
        exclude = ['house_id', 'position']

    def clean_postcode(self):
        postcode = self.cleaned_data['postcode']
        try:
            outward, inward = parse_uk_postcode(postcode)
            return outward + inward
        except ValueError:
            if len(postcode) == 0:
                return None
            else:
                raise ValidationError('Please enter a valid postcode.')


class PledgeForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['deadline', 'receive_updates']

class PledgeCompleteForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['feedback']

