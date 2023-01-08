from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    key = str(key)
    return dictionary.get(key)

@register.filter
def to_str(value):
    """converts int to string"""
    return str(value)