from django import template
register = template.Library()

@register.filter
def passwordfield(value):
    print value
    return 'Password' in value

@register.filter
def boolean_to_glyphicon(value):
    if value:
        return "glyphicon glyphicon-ok"
    else:
        return "glyphicon glyphicon-remove"

@register.filter
def round_to_nearest_integer(value):
    return int(round(float(value)))

@register.filter
def round_to_nearest_10(value):
    value = round(float(value))
    return int(value - value % 10)
