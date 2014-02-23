from django import template
register = template.Library()

@register.filter
def passwordfield(value):
    print value
    return 'Password' in value