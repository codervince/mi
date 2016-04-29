from django import forms
from .models import RPRunner

class RPRunnerSearchForm(forms.Form):
    horsename = forms.CharField(max_length=100)

