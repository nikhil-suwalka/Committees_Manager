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
        exclude = ["approved"]

    def __init__(self, club=None, **kwargs):
        super(ClubForm, self).__init__(**kwargs)
        self.fields["mentor"].queryset = User.objects.filter(user_type=1)
        self.fields["type"].queryset = Tag.objects.all()

        if club:
            self.fields["type"].initial = club.type.all()
            self.fields["mentor"].initial = club.mentor.all()
            self.fields['mentor'].widget.attrs['disabled'] = 'disabled'

            # self.fields['logo_link'].widget.attrs['disabled'] = 'disabled'
