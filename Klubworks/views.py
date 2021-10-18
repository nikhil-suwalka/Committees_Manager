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


def modifyClub(request, id):
    club_obj = Club.objects.get(pk=id)

    print(club_obj.type.all())

    # Two ways to access data from a model object
    # print(club_obj.description)
    # print(getattr(club_obj, "description"))

    club_form = ClubForm(club_obj)

    context = {'club_form': club_form, 'club': club_obj}
    return render(request, 'modify_club.html', context)


def createClub(request):
    if request.method == "POST":

        # updated some entries in profile
        club = Club.objects.create(name=request.POST["name"], description=request.POST["description"],
                                   logo_link=request.POST["logo_link"], )
        for type in request.POST.getlist("type"):
            club.type.add(Tag.objects.get(pk=type))

        for mentor in request.POST["mentor"]:
            club.mentor.add(User.objects.get(pk=mentor))
        #     TODO: send mail to the mentors

        club.save()

    club_form = ClubForm()
    context = {'club_form': club_form}
    return render(request, 'create_club.html', context)
