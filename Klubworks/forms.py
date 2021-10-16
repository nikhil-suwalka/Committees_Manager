from django import forms
from .models import *


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)
    email = forms.CharField(disabled=True)
    address = forms.CharField(required=False)
    user_type = forms.IntegerField(disabled=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'uid', 'college_name', 'address', 'phone_no', 'user_type']


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = "__all__"
