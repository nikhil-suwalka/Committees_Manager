import json

from allauth.socialaccount.models import SocialAccount
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Klubworks.forms import *
from Klubworks.models import User
import csv
import Klubworks.FormType as FormType


def homeView(request):
    context = {"events": getUpcomingVisibleEvents(), "clubs": getAllActiveClubs()}
    return render(request, 'index.html', context)


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
    user = request.user
    if user.user_type == 0:
        clubs_member = ClubMember.objects.filter(user_id=request.user.id)
        clubs = None
        if clubs_member is not None:
            clubs = Club.objects.filter(id__in=[c.club_id.id for c in clubs_member]).values()

        for club in clubs:
            club["tags"] = Club.objects.filter(id=club["id"]).get().type.all()
    else:

        # TODO: add logic so mentor can edit clubs which they are mentor of
        clubs = Club.objects.filter(mentor=user).all()
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
    users = User.objects.all()

    context = {'event_form': event_form, "users": users}
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
        return redirect("viewEvent", club_id=club_id)

    user_access = ClubMember.objects.filter(user_id=request.user.pk, club_id=club_id)

    # If user isn't a member of the club
    if not user_access:
        return customhandler403(request, message="You are not allowed to enter here")

    event = Event.objects.filter(id=event_id).values().first()
    event_form = EventForm(event=Event.objects.filter(id=event_id).first())
    event["datetime"] = event["datetime"].strftime("%Y-%m-%dT%H:%M")
    event["start"] = event["start"].strftime("%Y-%m-%dT%H:%M")
    event["end"] = event["end"].strftime("%Y-%m-%dT%H:%M")
    print(event)
    context = {'event_form': event_form, "event": event}
    return render(request, 'edit_event.html', context)


def manageRole(request, id):
    if request.method == "POST":
        role = ClubPosition.objects.filter(position=request.POST["position"], club_id=Club.objects.get(id=id)).all()
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
    print(member.position)
    context = {"club_id": club_id,
               "memberForm": MemberEditForm(request.POST, club_id=club_id, member_id=member.position.id),
               "member": member}
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
        context["events"] = getAllVisibleEvents(id)
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

    form = Form.objects.filter(event_id=Event.objects.filter(id=event_id).first(),
                               form_type=FormType.REGISTRATION).first()
    if form:
        url1 = request.build_absolute_uri(reverse("fillEventForm", args=(club_id, event_id, form.id)))
        print(url1)
        context["register_form"] = url1
    print(context)
    return render(request, 'view_event.html', context)


def getUpcomingVisibleEvents(club_id: int = None):
    if club_id:
        events = Event.objects.filter(club_id=club_id, visibility=True).filter(Q(end__gte=datetime.now())).order_by(
            "-end").all()
    else:
        events = Event.objects.filter(visibility=True).filter(Q(end__gte=datetime.now())).order_by("-end").all()
    return events[:10]


def getAllActiveClubs():
    events = Event.objects.filter(visibility=True).order_by("-start").all()
    clubs = []
    club_name = {}
    for event in events:
        if not club_name.get(event.club_id.name, False):
            clubs.append(event.club_id)
            club_name[event.club_id.name] = True
    return clubs[:10]


def getAllVisibleEvents(club_id: int):
    events = Event.objects.filter(club_id=club_id).filter(Q(end__gte=datetime.now())).order_by(
        "-end").all()
    return events[:10]


def getOrganizersFromEventID(event_id):
    event = Event.objects.filter(id=event_id).first()
    members = ClubMember.objects.filter(club_id=event.club_id.id).all()
    result = ""
    for member in members:
        result += member.user_id.first_name + " " + member.user_id.last_name + ", "
    return result[:-2]


def search(request):
    events_raw = Event.objects.filter(visibility=True).order_by("-start")
    events = events_raw.values().all()
    for i in range(len(events)):
        events[i]["tags"] = [tag.name for tag in events_raw.filter(id=events[i]["id"]).first().tag.all()]
        events[i]["club_name"] = events_raw.filter(id=events[i]["id"]).first().club_id.name

    data = []
    for event in events:
        print(event)
        e = {
            'name': event["name"],
            'club_id': event["club_id_id"],
            'event_id': event["id"],
            'club_name': event["club_name"],
            'description': event["description"],
            'start_date': event["start"].strftime("%d/%m/%Y, %H:%M"),
            'tags': " ".join(event["tags"]),
            'guests': "TODO",
            'members': getOrganizersFromEventID(event["id"])
        }
        data.append(e)
    print(data)
    context = {"json_data": json.dumps(data)}
    return render(request, 'search.html', context)


def viewRegisteredEvents(request):
    user = request.user
    formSubmitted = FormSubmission.objects.filter(user_id=user, form_id__form_type=FormType.REGISTRATION).all()
    eventIds = [id.form_id.event_id.id for id in formSubmitted]
    events_raw = Event.objects.filter(id__in=eventIds).all()
    events = list(events_raw.values())
    for i in range(len(events)):
        events[i]["club_id"] = events_raw[i].club_id.id
        events[i]["tag"] = Event.objects.filter(id=events[i]["id"]).get().tag.all()

    return render(request, 'view_registered_events.html', {"events": events})


def viewEventForms(request, club_id, event_id):
    club = Club.objects.filter(id=club_id).first()
    event = Event.objects.filter(id=event_id).first()
    forms = list(Form.objects.filter(event_id=event).values())
    types = {0: "Register Form", 1: "Feedback Form", 2: "Custom Form"}
    for i in range(len(forms)):
        forms[i]["form_type"] = types[forms[i]["form_type"]]
        forms[i]["link"] = request.build_absolute_uri(
            reverse("fillEventForm", args=(club_id, event_id, forms[i]["id"])))

    context = {"club": club, "event": event, "forms": forms}
    return render(request, 'view_event_forms.html', context)


def createEventForm(request, club_id, event_id):
    if request.method == "POST":
        open_date = datetime.fromisoformat(request.POST["open-date"])
        close_date = datetime.fromisoformat(request.POST["close-date"])
        form_name = request.POST["form-name"]
        form_type = int(request.POST["form-type"])
        form_data = request.POST["formdata"]

        Form.objects.create(event_id=Event.objects.filter(id=event_id).first(), form_name=form_name,
                            form_start=open_date,
                            form_end=close_date, form_type=form_type, form_structure=form_data)
        return redirect("viewEventForms", club_id=club_id, event_id=event_id)

    options = ["Register Form", "Feedback Form"]
    available_options = []
    for i in range(2):
        if Form.objects.filter(event_id=Event.objects.filter(id=event_id).first(), form_type=i).all().count() == 0:
            available_options.append((i, options[i]))
    available_options.append((2, "Custom Form"))
    print(available_options)
    return render(request, 'form.html', context={"options": available_options})


def deleteEventForm(request, club_id, event_id, form_id):
    Form.objects.filter(id=form_id).delete()
    return redirect("viewEventForms", club_id=club_id, event_id=event_id)


def fillEventForm(request, club_id, event_id, form_id):
    form = Form.objects.filter(id=form_id).first()
    form_filled = False
    if FormSubmission.objects.filter(form_id=form, user_id=request.user).count() > 0:
        form_filled = True

    if request.method == "POST":
        submitted_form = json.loads(request.POST["formdata"])
        submission_dict = {}

        for data in submitted_form:
            if data["type"] in ["select", "radio-group", "checkbox-group"]:
                selections = []
                for selection in data["userData"]:
                    for value in data["values"]:
                        if value["value"] == selection:
                            selections.append(value["label"])
                            break
                submission_dict[data["label"]] = selections

            else:
                if "userData" in data:
                    submission_dict[data["label"]] = data["userData"]
        print(submission_dict)
        FormSubmission.objects.create(user_id=request.user, form_id=form, form_data=submission_dict)

    return render(request, 'fill_form.html', context={"form": form, "form_filled": form_filled})


def statsEvent(request, club_id, event_id):
    club = Club.objects.filter(id=club_id).first()
    event = Event.objects.filter(id=event_id).first()

    regSub = FormSubmission.objects.filter(form_id__event_id=event, form_id__form_type=FormType.REGISTRATION).all()
    fbSub = FormSubmission.objects.filter(form_id__event_id=event, form_id__form_type=FormType.FEEDBACK).all()
    customSub = FormSubmission.objects.filter(form_id__event_id=event, form_id__form_type=FormType.CUSTOM).all()
    allSub_raw = FormSubmission.objects.filter(form_id__event_id=event).all()
    all_sub = {}
    for sub in allSub_raw:
        all_sub[sub.form_id.id] = all_sub.get(sub.form_id.id, [])
        all_sub[sub.form_id.id].append(sub)
    college_participant_count = FormSubmission.objects.filter(user_id__email__contains="@spit.ac.in").all().count()
    outside_participant_count = regSub.count() - college_participant_count

    all_form_charts = []

    form_struct = Form.objects.filter(event_id=event).all()
    color = "#DC3545CC"
    for i, f in enumerate(form_struct):
        form_charts = []
        struct = json.loads(f.form_structure)
        for j, field in enumerate(struct):
            if field.get("type") in ["select", "radio-group", "checkbox-group", "number"]:
                chart = []
                dict = {}
                for sub in all_sub[f.id]:
                    record = json.loads(str(sub.form_data).replace("'", '"'))[field["label"]]
                    for item in record:
                        dict[item] = dict.get(item, 0) + 1
                for key, value in dict.items():
                    chart.append([key, value, color])
                form_charts.append([field["label"], chart])
        all_form_charts.append(form_charts)
    print(all_form_charts)
    context = {"event": event,
               "club": club,
               "reg_count": regSub.count(),
               "fb_count": fbSub.count(),
               "college_participant_count": college_participant_count,
               "outside_participant_count": outside_participant_count,
               "charts": all_form_charts}
    return render(request, "view_stats_event.html", context=context)


def download_csv(request, club_id, event_id, form_id):
    form = Form.objects.filter(id=form_id).first()

    response = HttpResponse(content_type='text/csv')
    form_name = form.form_name.replace(" ", "_")
    response['Content-Disposition'] = f'attachment; filename="{form_name}.csv"'
    writer = csv.writer(response)

    header_row = ['First Name', 'Last Name', 'Email', 'UID', 'College Name', 'Address', 'Phone number', 'Fill Time']

    form = Form.objects.filter(id=form_id).first()
    all_registrations = FormSubmission.objects.filter(form_id=form).all()

    if all_registrations.count():
        registrations = all_registrations.values_list(
            "user_id__first_name", "user_id__last_name", "user_id__email",
            "user_id__uid", "user_id__college_name", "user_id__address", "user_id__phone_no",
            "filled_time")
        form_datas = all_registrations.values_list("form_data")

        json_form_data = json.loads(form_datas[0][0].replace("'", '"'))
        for data in json_form_data:
            header_row.append(data)

        writer.writerow(header_row)

        for i in range(len(registrations)):
            json_data = json.loads(form_datas[i][0].replace("'", '"'))

            data = tuple((json_data[i] for i in json_data))
            data = tuple((",".join(i) for i in data))
            print(data)
            writer.writerow(registrations[i] + data)

    return response
