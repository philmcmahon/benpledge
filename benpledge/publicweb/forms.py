from django import forms
from django.forms import  ModelForm
from django.core.exceptions import ValidationError
from models import Dwelling, Pledge

from postcode_parser import parse_uk_postcode


class DwellingForm(ModelForm):

    class Meta:
        model = Dwelling
        exclude = ['house_id']

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





# replaced by clean_postcode
    # def is_valid(self):
    #     valid = super(DwellingForm, self).is_valid()

    #     if not valid:
    #         return valid
    #     try:
    #         parse_uk_postcode(self.cleaned_data['postcode'])
    #     except ValueError:
    #         if len(self.cleaned_data['postcode']) == 0:
    #             self.null_postcode = True
    #             return True
    #         else:
    #             self.null_postcode = False
    #             self._errors['postcode'].append(_(u'Please enter a valid postcode.'))
    #             return False
    #     return True