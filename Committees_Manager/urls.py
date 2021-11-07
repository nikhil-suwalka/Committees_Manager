"""Committees_Manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from Klubworks.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="index.html")),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', profile, name="profile"),
    path('club/view/', viewClub, name="viewClub"),
    path('club/view/<int:id>', clubDisplay, name="clubDisplay"),
    path('club/modify/<int:id>', modifyClub, name="modifyClub"),
    path('club/create/', createClub, name="createClub"),
    path('club/approve/<int:id>', approveClub, name="approveClub"),
    path('club/<int:club_id>/event/view/', viewEvents, name="viewEvent"),
    path('club/<int:club_id>/event/view/<int:event_id>', eventDisplay, name="eventDisplay"),
    path('club/<int:club_id>/event/delete/<int:event_id>', deleteEvent, name="deleteEvent"),
    path('club/<int:club_id>/event/edit/<int:event_id>', editEvent, name="editEvent"),
    path('club/<int:club_id>/event/create/', createEvent, name="createEvent"),
    path('club/role/<int:id>', manageRole, name="manageRole"),
    path('club/role/<int:club_id>/remove/<int:role_id>', deleteRole, name="deleteRole"),
    path('club/role/<int:club_id>/edit/<int:role_id>', editRole, name="editRole"),
    path('club/member/<int:id>', manageMember, name="manageMember"),
    path('club/member/<int:club_id>/remove/<int:user_id>', deleteMember, name="deleteMember"),
    path('club/member/<int:club_id>/edit/<int:member_id>', editMember, name="editMember"),
]
