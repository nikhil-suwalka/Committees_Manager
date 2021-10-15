from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Club)
admin.site.register(User)
admin.site.register(ClubPosition)
admin.site.register(ClubMember)
admin.site.register(UserAccess)
admin.site.register(Tag)
admin.site.register(Event)
admin.site.register(EventAttendance)
admin.site.register(Form)
admin.site.register(FormSubmission)
