from allauth.socialaccount.models import SocialAccount
from django.core.mail import send_mail
from django.shortcuts import render, redirect

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
        club = Club.objects.filter(pk=id).first()
        club.name = request.POST["name"]
        club.description = request.POST["description"]
        club.logo_link = request.FILES["logo_link"]
        club.save()
        club.type.clear()
        for type in request.POST.getlist("type"):
            club.type.add(Tag.objects.get(pk=type))
        club.save()
        return viewClub(request)

    user_access = ClubMember.objects.filter(user_id=request.user.pk, club_id=id).first()

    # If user isn't a member of the club
    if not user_access or not user_access.position.hasEdit:
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

        memberPosition = ClubPosition.objects.create(club_id=club, position="Member", priority=1, hasEdit=True)

        ClubMember.objects.create(club_id=club, user_id=request.user, position=memberPosition)
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
    clubs_member = ClubMember.objects.filter(user_id=request.user.id)
    clubs = None
    if clubs_member is not None:
        clubs = Club.objects.filter(id__in=[c.club_id.id for c in clubs_member]).values()

    for club in clubs:
        club["tags"] = Club.objects.filter(id=club["id"]).get().type.all()
    context = {'user': request.user, 'clubs': clubs}
    return render(request, 'my_clubs.html', context)


def deleteClub(request):
    pass


def viewEvents(request, club_id):
    club = Club.objects.filter(pk=club_id).first()
    events = Event.objects.filter(club_id=club).values()
    for event in events:
        event["tag"] = Event.objects.filter(id=event["id"]).get().tag.all()

    for i in range(len(events)):
        events[i]["logo"] = str(events[i]["logo"]).split("/")[-1]

    context = {'events': events, "club": club}
    return render(request, 'view_events.html', context)


def deleteEvent(request, club_id, event_id):
    event = Event.objects.filter(id=event_id).delete()
    return redirect("viewEvent", club_id=club_id)


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
        return redirect("viewEvent", club_id=club_id)

    user_access = ClubMember.objects.filter(user_id=request.user.pk, club_id=club_id)

    # If user isn't a member of the club
    if not user_access:
        return customhandler403(request, message="You are not allowed to enter here")

    event_form = EventForm(request.POST, request.FILES)

    context = {'event_form': event_form}
    return render(request, 'create_event.html', context)


def editEvent(request, club_id, event_id):
    if request.method == "POST":
        event = Event.objects.filter(id=event_id).first()
        event.name = request.POST["name"]
        event.datetime = datetime.fromisoformat(request.POST["datetime"])
        event.start = datetime.fromisoformat(request.POST["start"])
        event.end = datetime.fromisoformat(request.POST["end"])
        event.visibility = (True if request.POST["visibility"] == "True" else False)
        event.duration = request.POST["duration"]
        event.description = request.POST["description"]
        event.link = request.POST["link"]
        event.logo = request.FILES["logo"]
        event.tag.clear()
        for tag in request.POST.getlist("tag"):
            event.tag.add(Tag.objects.get(pk=tag))
        event.save()

    user_access = ClubMember.objects.filter(user_id=request.user.pk, club_id=club_id)

    # If user isn't a member of the club
    if not user_access:
        return customhandler403(request, message="You are not allowed to enter here")

    event = Event.objects.filter(id=event_id).values().first()
    event_form = EventForm(event=Event.objects.filter(id=event_id).first())
    print(event)
    event["datetime"] = event["datetime"].strftime("%Y-%m-%dT%H:%M")
    event["start"] = event["start"].strftime("%Y-%m-%dT%H:%M")
    event["end"] = event["end"].strftime("%Y-%m-%dT%H:%M")
    print(event)
    context = {'event_form': event_form, "event": event}
    return render(request, 'edit_event.html', context)


def manageRole(request, id):
    if request.method == "POST":
        role = ClubPosition.objects.filter(position=request.POST["position"]).all()
        if not role:
            new_role = ClubPosition.objects.create(club_id=Club.objects.get(id=id), position=request.POST["position"],
                                                   priority=request.POST["priority"],
                                                   hasEdit=(True if request.POST["hasEdit"] == "True" else False))
    roles = ClubPosition.objects.filter(club_id=str(id)).order_by('priority').all()
    context = {"roles": roles, "club_id": id, "roleForm": RoleForm(request.POST)}

    return render(request, 'manage_roles.html', context)


def deleteRole(request, club_id, role_id):
    club_position = ClubPosition.objects.filter(pk=role_id).get()
    club_members_count = ClubMember.objects.filter(position=club_position).count()
    if club_members_count > 0:
        roles = ClubPosition.objects.filter(club_id=str(club_id)).order_by('priority').all()
        context = {"roles": roles, "club_id": club_id, "roleForm": RoleForm(request.POST), "message": "Cannot delete a "
                                                                                                      "position which has "
                                                                                                      "members assigned "
                                                                                                      "to. Please reassign "
                                                                                                      "the members to a "
                                                                                                      "new position first."}

        return render(request, 'manage_roles.html', context)

    ClubPosition.objects.filter(id=role_id).delete()

    return redirect("manageRole", id=club_id)


def editRole(request, club_id, role_id):
    role = ClubPosition.objects.filter(id=role_id).first()
    if request.method == "POST":
        role.position = request.POST["position"]
        role.priority = request.POST["priority"]
        role.hasEdit = (True if request.POST["hasEdit"] == "True" else False)
        role.save()

        return redirect("manageRole", id=club_id)

    context = {"club_id": id, "roleForm": RoleForm(request.POST), "role": role}
    return render(request, 'edit_role.html', context)


def manageMember(request, id):
    if request.method == "POST":
        user = User.objects.get(id=request.POST["id_members"])

        if not ClubMember.objects.filter(user_id=user):
            position = ClubPosition.objects.get(id=request.POST["position"])
            club = Club.objects.get(id=id)
            ClubMember.objects.create(club_id=club, user_id=user, position=position)

    members = ClubMember.objects.filter(club_id=id).all()
    all_users = User.objects.filter(user_type=0, is_superuser=False).all()
    all_users = [{"id": user.id, "name": user.first_name + " " + user.last_name, "email": user.email} for user in
                 all_users]
    context = {"members": members, "club_id": id, "memberForm": MemberForm(request.POST, club_id=id),
               "users": all_users}
    return render(request, 'manage_members.html', context)


def deleteMember(request, club_id, user_id):
    ClubMember.objects.filter(user_id=User.objects.get(id=user_id)).delete()
    return redirect("manageMember", id=club_id)


def editMember(request, club_id, member_id):
    member = ClubMember.objects.filter(id=member_id).first()
    if request.method == "POST":
        member.position = ClubPosition.objects.get(id=int(request.POST["position"]))
        member.save()
        return redirect("manageMember", id=club_id)

    context = {"club_id": club_id, "memberForm": MemberEditForm(request.POST, club_id=club_id), "member": member}
    return render(request, 'edit_member.html', context)


def clubDisplay(request, id):
    club = Club.objects.filter(id=id).first()
    context = {}
    if club and club.approved:
        members = ClubMember.objects.filter(club_id=club).order_by("position__priority").all()
        context["members"] = [
            {"member_id": member.id, "name": member.user_id.first_name + " " + member.user_id.last_name,
             "email": member.user_id.email, "position": member.position.position,
             "photo": SocialAccount.objects.get(user_id=member.user_id.id).extra_data["picture"]

             } for member in
            members]
        context["club"] = club
        context["tags"] = club.type.all()
        context["mentors"] = club.mentor.values()
        for i in range(len(context["mentors"])):
            mentor_id = context["mentors"][i]["id"]
            context["mentors"][i]["photo"] = \
                SocialAccount.objects.get(user_id=club.mentor.get(id=mentor_id)).extra_data["picture"]
        context["logo"] = str(club.logo_link).split("/")[-1]

        # TODO: send events

        return render(request, 'view_club.html', context)
    else:
        return customhandler403(request, message="Club doesn't exist or isn't approved yet")


def eventDisplay(request, club_id, event_id):
    club = Club.objects.filter(id=club_id).first()
    event = Event.objects.filter(pk=event_id).values().first()
    event_tags = Event.objects.filter(pk=event_id).first().tag.values().all()
    members = ClubMember.objects.filter(club_id=club).order_by("position__priority").all()
    event["logo"] = str(event["logo"]).split("/")[-1]
    context = {"members": [
        {"member_id": member.id, "name": member.user_id.first_name + " " + member.user_id.last_name,
         "email": member.user_id.email, "position": member.position.position,
         "photo": SocialAccount.objects.get(user_id=member.user_id.id).extra_data["picture"]
         } for member in
        members], "club": club, "tags": event_tags, "mentors": club.mentor.values(), "event": event}
    print(context)
    return render(request, 'view_event.html', context)
