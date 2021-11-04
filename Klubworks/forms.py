from django import forms

from .models import *


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)
    email = forms.CharField(disabled=True)
    address = forms.CharField(required=False)

    # user_type = forms.IntegerField(disabled=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'uid', 'college_name', 'address', 'phone_no']


class RoleForm(forms.ModelForm):
    TRUE_FALSE_CHOICES = (
        (True, 'Yes'),
        (False, 'No')
    )
    hasEdit = forms.ChoiceField(choices = TRUE_FALSE_CHOICES, label="Has club edit access",
                              initial='', widget=forms.Select(), required=True)

    class Meta:
        model = ClubPosition
        fields = ['position', 'priority','hasEdit']


class ClubForm(forms.ModelForm):
    logo_link = forms.ImageField()

    class Meta:
        model = Club
        fields = "__all__"
        exclude = ["approved", "created_by"]

    def __init__(self, club=None, *args, **kwargs):
        super(ClubForm, self).__init__(*args, **kwargs)
        self.fields["mentor"].queryset = User.objects.filter(user_type=1)
        self.fields["type"].queryset = Tag.objects.all()

        if club:
            # TODO: Sort these lists
            self.fields["type"].initial = club.type.all()
            self.fields["mentor"].initial = club.mentor.all()
            self.fields['mentor'].widget.attrs['disabled'] = 'disabled'

            # self.fields['logo_link'].widget.attrs['disabled'] = 'disabled'


class DateInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class EventForm(forms.ModelForm):
    CHOICES = (
        ("1", True),
        ("2", False),
    )

    visibility = forms.ChoiceField(choices=((True, "Visible"), (False, "Not Visible"),),
                                   required=True,
                                   initial=True,
                                   label='Visibility')

    link = forms.CharField(label="Event link (if available)", required=False)

    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            'start': DateInput(),
            'end': DateInput(),
            'datetime': DateInput(),

        }
        exclude = ["club_id", "created_by"]
