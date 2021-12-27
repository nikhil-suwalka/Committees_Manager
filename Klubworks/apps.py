import datetime
import threading
import time

from django.apps import AppConfig
import os


class KlubworksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Klubworks'

    def ready(self):
        run_once = os.environ.get('CMDLINERUNNER_RUN_ONCE')
        if run_once is not None:
            return
        os.environ['CMDLINERUNNER_RUN_ONCE'] = 'True'

        t1 = threading.Thread(target=self.check_mail_event, args=())
        t1.start()

    def check_mail_event(self):
        from .models import Event, Form, FormSubmission
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string

        while True:

            # Send Feedback form

            event_feedback_form = {}
            feedback_forms = Form.objects.filter(form_type=1, form_start__lte=datetime.datetime.now()).all()
            for feedback_form in feedback_forms:
                event = Event.objects.filter(id=feedback_form.event_id.id,
                                             feedback_form_sent=False).first()
                if event:
                    event_feedback_form[event] = feedback_form

            for event in event_feedback_form:

                form_url = f"http://127.0.0.1:8000/club/{event.club_id.id}/event/{event.id}/form/{event_feedback_form[event].id}"

                print(event)
                register_form = Form.objects.filter(form_type=0, event_id=event).first()
                registrations = FormSubmission.objects.filter(form_id=register_form).all()
                html_message = render_to_string('feedback_mail_template.html',
                                                {'event_name': event.name, "club_name": event.club_id.name,
                                                 "link": form_url})
                for registration in registrations:
                    # TODO: Send mail to this user id with feedback form event_feedback_form[event]
                    print(registration.user_id)

                    message = EmailMessage(subject=f'KlubWorks : {event.name} - Feedback Form', body=html_message,
                                           from_email="", to=[registration.user_id.email])
                    message.content_subtype = 'html'
                    message.send()

                event.feedback_form_sent = True
                event.save()

            # Event start reminder
            events = Event.objects.filter(event_reminder_sent=False,
                                          start__lte=datetime.datetime.now() + datetime.timedelta(hours=1)).all()

            for event in events:
                register_form = Form.objects.filter(form_type=0, event_id=event).first()
                registrations = FormSubmission.objects.filter(form_id=register_form).all()
                html_message = render_to_string('event_reminder_mail_template.html',
                                                {'event_name': event.name, "club_name": event.club_id.name,
                                                 "event_link": event.link})
                for registration in registrations:
                    message = EmailMessage(subject=f'KlubWorks : {event.name} - Reminder', body=html_message,
                                           from_email="", to=[registration.user_id.email])
                    message.content_subtype = 'html'
                    message.send()
                event.event_reminder_sent = True
                event.save()

            time.sleep(600)
