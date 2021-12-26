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

        t1 = threading.Thread(target=self.check_feedback_form, args=())
        t1.start()

    def check_feedback_form(self):
        from .models import Event, Form, FormSubmission
        from django.core.mail import send_mail, EmailMessage
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        while True:
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
                for registration in registrations:
                    # TODO: Send mail to this user id with feedback form event_feedback_form[event]
                    print(registration.user_id)

                    # message = f"Please fill the feedback form for the event <b>{event.name}</b> by {event.club_id.name}" \
                    #           f"\nClick the below link to open the form" \
                    #           f"\n{form_url}"
                    html_message = render_to_string('mail_template.html',
                                                    {'event_name': event.name, "club_name": event.club_id.name,
                                                     "link": form_url})

                    message = EmailMessage(subject=f'KlubWorks : {event.name} - Feedback Form', body=html_message,
                                           from_email="", to=[registration.user_id.email])
                    message.content_subtype = 'html'  # this is required because there is no plain text email message
                    message.send()

                event.feedback_form_sent = True
                event.save()

            time.sleep(10)
