from django import forms
from django.forms import  ModelForm
from django.core.exceptions import ValidationError
from models import Dwelling, Pledge

from postcode_parser import parse_uk_postcode


class DwellingForm(ModelForm):
    """MyHome form"""
    class Meta:
        model = Dwelling
        exclude = ['house_id', 'position']

    def clean_postcode(self):
        """Handles validation of entered postcodes"""
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
    """ModelForm for editing a pledge """
    class Meta:
        model = Pledge
        fields = ['deadline', 'receive_updates']

class PledgeCompleteForm(ModelForm):
    """ModelForm for completing a pledge """
    class Meta:
        model = Pledge
        fields = ['feedback']

class HatFilterForm(forms.Form):
    """Form for filtering HAT results """
    minimum_consumption_reduction = forms.IntegerField(required=False)
    minimum_annual_cost_reduction = forms.IntegerField(required=False)
    maximum_installation_costs = forms.IntegerField(required=False)
    maximum_payback_time = forms.IntegerField(required=False)
    minimum_annual_return_on_investment = forms.IntegerField(required=False)
    green_deal_eligible = forms.BooleanField(required=False)
