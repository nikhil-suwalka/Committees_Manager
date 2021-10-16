from django.template.defaulttags import register

...


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_from_model_obj(obj, col):
    return getattr(obj, col)
