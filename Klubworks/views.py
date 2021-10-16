from django.shortcuts import render

from Klubworks.forms import *
from Klubworks.models import User


def profile(request):
    if request.method == "POST":
        # updated some entries in profile
        user = User.objects.get(id=request.user.id)
        user.uid = request.POST["uid"]
        user.college_name = request.POST["college_name"]
        user.address = request.POST["address"]
        user.phone_no = request.POST["phone_no"]
        user.save()
    profile_form = ProfileForm(request.POST, request.user)
    user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
    context = {'profile_form': profile_form, 'user': user_dict}
    return render(request, 'profile.html', context)


def processprofile(request):
    pass


def club(request):
    club_obj = Club.objects.get(pk=1)

    # Two ways to access data from a model object
    # print(club_obj.description)
    # print(getattr(club_obj, "description"))

    club_form = ClubForm(request.POST, club_obj)

    context = {'club_form': club_form, 'club': club_obj}
    return render(request, 'club.html', context)
