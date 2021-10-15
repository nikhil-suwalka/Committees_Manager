from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Club(models.Model):
    name = models.CharField(blank=False, null=False, max_length=100)
    type = models.CharField(blank=False, null=False, max_length=100)
    description = models.CharField(blank=False, null=False, max_length=1000)
    logo_link = models.ImageField(upload_to="clubs_images/")


class User(AbstractUser):
    uid = models.CharField(blank=False, null=False, max_length=100)
    college_name = models.CharField(blank=False, null=False, max_length=100)
    address = models.CharField(blank=False, null=False, max_length=100)
    phone_no = models.CharField(blank=False, null=False, max_length=100)





class ClubPosition(models.Model):
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club_member_clubid")
    position = models.CharField(blank=False, null=False, max_length=100)
    priority = models.IntegerField(blank=False, null=False, default=0)


class ClubMember(models.Model):
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club_member_clubid")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_member_userid")
    position = models.ForeignKey(ClubPosition, on_delete=models.CASCADE, related_name="club_member_position")


class UserAccess(models.Model):
    club_id = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="user_access_clubid")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_access_userid")
    access_type = models.IntegerField(blank=False, null=False, default=0)


class Tag(models.Model):
    name = models.CharField(blank=False, null=False, max_length=100)


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
    description = models.CharField(blank=False, null=False, max_length=100)
    link = models.CharField(blank=False, null=True, max_length=100)
    logo = models.ImageField(upload_to="event_images/")
    tag = models.ManyToManyField(Tag, related_name="event_tags")

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

# name = models.CharField(blank=False, null=False, max_length=100)
# information = models.CharField(blank=True, null=False, max_length=1000)
# status = models.IntegerField(blank=False, null=False, default=0)
# submit_date = models.DateTimeField(auto_now=True, null=False, blank=False)
# submit_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user_submit")
# takeaway_user = models.ForeignKey(get_user_model(), null=True, default=None, on_delete=models.CASCADE, related_name="user_takeaway")
# takeaway_date = models.DateTimeField(default=None, null=True, blank=False)
# item_received = models.BooleanField(default=False)