from django import template
import re
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

@register.filter
def required_for_hat(field_label):
    labels_required_for_hat = (['Dwelling type', 'Property age',
        'Number of bedrooms', 'Heating fuel', 'Heating type', 'Loft insulation',
        'Wall type'])
    if field_label in labels_required_for_hat:
        return field_label + '*'
    else:
        return field_label

@register.filter
def linkify_urls(text):
    return URL_REGEX.sub(r'<a href="\1">\1</a>', text)

# this is at the bottom to stop sublime text syntax highlighting everything
# regex courtesy of stack overflow
URL_REGEX = re.compile(r'''((?:mailto:|ftp://|http://|https://)[^ <>'"{}|\\^`[\]]*)''')
