REGISTRATION = 0
FEEDBACK = 1
CUSTOM = 2


def get_form_name(form_type: int):
    return "Registration_form" if form_type == 0 else "Feedback_form" if form_type == 1 else "Custom_form"
