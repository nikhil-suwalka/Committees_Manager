from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class Tag(models.Model):
    name = models.CharField(blank=False, null=False, max_length=100)

    def __str__(self):
        return str(self.name)


# TODO: add a short bio
# TODO: add user image
class User(AbstractUser):
    uid = models.CharField(blank=False, null=False, max_length=100)
    college_name = models.CharField(blank=False, null=False, max_length=100)
    address = models.CharField(blank=False, null=False, max_length=100)
    phone_no = models.CharField(blank=False, null=False, max_length=100)

    TYPES = ((0, "Student"), (1, "Teacher"))
    user_type = models.IntegerField(default=0, choices=TYPES)

    def __str__(self):
        return str(self.first_name + " " + self.last_name)


class Club(models.Model):
    name = models.CharField(blank=False, null=False, max_length=100)
    type = models.ManyToManyField(Tag, related_name="club_tags")
    description = models.CharField(blank=False, null=False, max_length=1000)
    # TODO: change upload_to directory
    logo_link = models.ImageField(upload_to="static/img/club")
    mentor = models.ManyToManyField(User, related_name="club_mentors")
    approved = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_created_by")

    def __str__(self):
        return str(self.name)


class ClubPosition(models.Model):
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club_position_clubid")
    position = models.CharField(blank=False, null=False, max_length=100)
    priority = models.IntegerField(blank=False, null=False, default=1)
    hasEdit = models.BooleanField(default=False)

    def __str__(self):
        return str(self.position)


class ClubMember(models.Model):
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club_member_clubid")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_member_userid")
    position = models.ForeignKey(ClubPosition, on_delete=models.CASCADE, related_name="club_member_position")

    def __str__(self):
        return str(self.user_id.first_name + " " + self.user_id.last_name + " (" + self.position.position + ")")


class Event(models.Model):
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="event_clubid")
    name = models.CharField(blank=False, null=False, max_length=100)

    # Event date
    datetime = models.DateTimeField(null=False, blank=False)
    visibility = models.BooleanField(default=False)

    # When event listing shows on site
    start = models.DateTimeField(null=False, blank=False)

    # When event listing disappears on the site
    end = models.DateTimeField(null=False, blank=False)

    # Duration of the event
    duration = models.CharField(blank=False, null=False, max_length=100)
    description = models.CharField(blank=False, null=False, max_length=2000)
    link = models.CharField(blank=False, null=True, max_length=100)
    logo = models.ImageField(upload_to="static/img/event")
    tag = models.ManyToManyField(Tag, related_name="event_tags")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_created_by")

    def __str__(self):
        return str(self.name)


class EventAttendance(models.Model):
    event_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="event_attendance_eventid")
    user_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="event_attendance_userid")


class Form(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="form_eventid")
    form_start = models.DateTimeField(null=False, blank=False)
    form_end = models.DateTimeField(null=False, blank=False)
    form_structure = models.CharField(blank=False, null=False, max_length=1000)


class FormSubmission(models.Model):
    form_id = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="form_submission_formid")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="form_submission_userid")
    filled_time = models.DateTimeField(default=datetime.now, blank=True)
    form_data = models.CharField(blank=False, null=False, max_length=1000)
