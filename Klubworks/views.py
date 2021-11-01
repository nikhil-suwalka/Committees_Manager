from django.core.mail import send_mail
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
    context = {'profile_form': profile_form, 'user_dict': user_dict, 'user': request.user}
    return render(request, 'profile.html', context)


def customhandler403(request, message, template_name='403.html'):
    response = render(request, template_name, context={"message": message})
    response.status_code = 403
    return response


def modifyClub(request, id):
    if request.method == "POST":
        club = Club.objects.filter(pk=id)
        club.update(name=request.POST["name"], description=request.POST["description"],
                    logo_link=request.POST["logo_link"])

        club = club.get()
        club.type.clear()
        for type in request.POST.getlist("type"):
            club.type.add(Tag.objects.get(pk=type))
        club.save()
        return viewClub(request)

    user_access = UserAccess.objects.filter(user_id=request.user.pk, club_id=id)

    # If user isn't a member of the club
    if not user_access:
        return customhandler403(request, message="You are not allowed to enter here")
        # return HttpResponseForbidden("You're not allowed to modify this club")
    club_obj = Club.objects.get(pk=id)
    club_form = ClubForm(club=club_obj)

    context = {'club_form': club_form, 'club': club_obj}
    return render(request, 'modify_club.html', context)


def approveClub(request, id):
    user = User.objects.get(id=request.user.id)
    if user.is_authenticated and user.user_type == 1:
        club = Club.objects.get(id=id)
        club.approved = True
        club.save()
        return render(request, 'message.html', {'user': user, 'message': "Club request has been approved"})
    else:
        return render(request, 'message.html', {'user': user, 'message': "You are not authorized to access this page!"})


def createClub(request):
    if request.method == "POST":
        # updated some entries in profile
        club = Club.objects.create(name=request.POST["name"], description=request.POST["description"],
                                   logo_link=request.FILES["logo_link"], created_by=request.user)
        for type in request.POST.getlist("type"):
            club.type.add(Tag.objects.get(pk=type))

        clubAccess = UserAccess.objects.create(club_id=club, user_id=request.user)

        for mentor in request.POST["mentor"]:
            club.mentor.add(User.objects.get(pk=mentor))

        # If the user is a faculty member
        if request.user.user_type == 1:
            club.approved = True
            club.save()
            return render(request, 'message.html', {'user': request.user, 'message': "Club has been created!"})

        message = request.user.first_name \
                  + " " + request.user.last_name \
                  + "(" + request.user.email \
                  + ") has requested to create a new Club" \
                  + "\n Club Name: " + request.POST["name"] \
                  + "\n Club description: " + request.POST["description"] \
                  + "\n Click the below link to approve the request" \
                  + "\n" + request.build_absolute_uri('/') + "club/approve/" + str(club.id)

        mentors_list = User.objects.filter(id__in=request.POST["mentor"]).all()
        send_mail(
            'KlubWorks : New Club Approval Request',
            message,
            request.user.email,
            [m.email for m in mentors_list],
            fail_silently=False,
        )
        # print('KlubWorks : New Club Approval Request',
        #     message,
        #     request.user.email,
        #     [m.email for m in mentors_list],
        #     )
        club.save()
        return render(request, 'message.html', {'user': request.user, 'message': "Club request sent to mentors!"})
    club_form = ClubForm(request.POST, request.FILES)
    context = {'club_form': club_form}
    return render(request, 'create_club.html', context)


def viewClub(request):
    clubs_ids = UserAccess.objects.filter(user_id=request.user.id)
    clubs = None
    if clubs_ids is not None:
        clubs = Club.objects.filter(id__in=[c.club_id.id for c in clubs_ids]).values()
    context = {'user': request.user, 'clubs': clubs}
    return render(request, 'my_clubs.html', context)


def deleteClub(request):
    pass


def createEvent(request, club_id):
    # print(getUserClubs(request))
    if request.method == "POST":
        club = Club.objects.get(pk=club_id)
        event = Event.objects.create(name=request.POST["name"], club_id=club, datetime=request.POST["datetime"],
                                     visibility=request.POST["visibility"], start=request.POST["start"],
                                     end=request.POST["end"], duration=request.POST["duration"],
                                     description=request.POST["description"], link=request.POST["link"],
                                     logo=request.FILES["logo"], created_by=request.user)
        for tag in request.POST.getlist("tag"):
            event.tag.add(Tag.objects.get(pk=tag))
        event.save()

    user_access = UserAccess.objects.filter(user_id=request.user.pk, club_id=club_id)

    # If user isn't a member of the club
    if not user_access:
        return customhandler403(request, message="You are not allowed to enter here")

    event_form = EventForm(request.POST, request.FILES)

    context = {'event_form': event_form}
    return render(request, 'create_event.html', context)
