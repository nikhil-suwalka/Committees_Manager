from django.shortcuts import render

from Klubworks.forms import ProfileForm


def profile(request):
    profile_form = ProfileForm(request.POST, request.user)
    user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
    context = {'profile_form': profile_form, 'user': user_dict}
    return render(request, 'profile.html', context)


def processprofile(request):
    print(request.POST)
