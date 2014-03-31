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

# courtesy of http://stackoverflow.com/questions/19268727/django-how-to-get-the-name-of-the-template-being-rendered
@register.simple_tag
def active_page(request, view_name):
    from django.core.urlresolvers import resolve, Resolver404
    if not request:
        return ""
    try:
        return "active" if resolve(request.path_info).url_name == view_name else ""
    except Resolver404:
        return ""