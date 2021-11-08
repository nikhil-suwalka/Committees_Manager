from django.template.defaulttags import register

from Klubworks.models import *

...


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_from_model_obj(obj, col):
    return getattr(obj, col)


@register.filter
def get_image_name_from_path(path):
    return str(path).split("/")[-1]


@register.filter
def ellipsis(para):
    if len(str(para)) > 125:
        return para[:125] + "..."
    return para


