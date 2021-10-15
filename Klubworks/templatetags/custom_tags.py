from django.template.defaulttags import register
...
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item2(dictionary, key):
    return dictionary.key