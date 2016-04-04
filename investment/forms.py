from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

# class InvestorCreateForm(forms.ModelForm):
#     model = Investor
#     fields = ('language', )

class UserAuthForm(AuthenticationForm):
    remember_me = forms.BooleanField(label='Remember me', required=False, widget=forms.CheckboxInput())
