from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','uid','college_name','address','phone_no','user_type']