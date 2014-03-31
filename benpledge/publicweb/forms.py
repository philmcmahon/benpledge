from django import forms
from django.forms import  ModelForm
from models import Dwelling, Pledge

from localflavor.gb.forms import GBPostcodeField


class DwellingForm(ModelForm):

    class Meta:
        model = Dwelling
        exclude = ['house_id']

class PledgeForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['deadline']