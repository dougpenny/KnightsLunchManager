from django import template
register = template.Library()

@register.filter
def forKey(value, arg):
    if value:
        return value.get(arg)
    else:
        return ""