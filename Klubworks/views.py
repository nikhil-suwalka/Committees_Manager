from django.shortcuts import render

from Klubworks.forms import ProfileForm


def profile(request):
    profile_form = ProfileForm(request.POST, request.user)
    context = {'profile_form': profile_form}
    return render(request, 'profile.html', context)


def process_profile(request):
    pass