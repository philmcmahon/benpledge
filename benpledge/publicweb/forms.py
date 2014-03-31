from django import forms
from django.forms import  ModelForm
from models import Dwelling, Pledge


class DwellingForm(ModelForm):

    class Meta:
        model = Dwelling
        exclude = ['house_id']

class PledgeForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['deadline']