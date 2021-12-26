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
        while True:
            event_feedback_form = {}
            feedback_forms = Form.objects.filter(form_type=1).all()
            for feedback_form in feedback_forms:
                event = Event.objects.filter(id=feedback_form.event_id.id,
                                                         feedback_form_sent=False, end__lte=datetime.datetime.now()).first()
                if event:
                    event_feedback_form[event] = feedback_form

            for event in event_feedback_form:

                print(event)
                register_form = Form.objects.filter(form_type=0, event_id=event).first()
                registrations = FormSubmission.objects.filter(form_id=register_form).all()
                for registration in registrations:
                    # TODO: Send mail to this user id with feedback form event_feedback_form[event]
                    print(registration.user_id)

            time.sleep(600)
