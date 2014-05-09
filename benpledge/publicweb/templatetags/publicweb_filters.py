# -*- coding: utf-8 -*-
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

# from http://stackoverflow.com/questions/19268727/django-how-to-get-the-name-of-the-template-being-rendered
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
def update_field_label(field_label):
    labels_required_for_hat = (['Dwelling type', 'Property age',
        'Number of bedrooms', 'Heating fuel', 'Heating type', 'Loft insulation',
        'Wall type'])
    currency_labels = (['Approximate spent on electricity per month',
        'Aprroximate spent on gas per month',  'Minimum consumption reduction',
        'Minimum annual cost reduction', 'Maximum installation costs'])

    if field_label in labels_required_for_hat:
        return field_label + '*'
    elif field_label in currency_labels:
        return field_label + u' (£)'
    elif field_label == 'Maximum payback time':
        return field_label + ' (years)'
    elif field_label == 'Minimum annual return on investment':
        return field_label + ' (%)'
    else:
        return field_label

@register.filter
def get_field_prefix(field_label):
    if (field_label == "" or 
        field_label == ""):
        return u'£'
    else:
        return ""


@register.filter
def linkify_urls(text):
    return URL_REGEX.sub(r'<a href="\1">\1</a>', text)

@register.filter
def name_from_identifier(value):
    """Replaces underscores with whitespace, capitalises"""
    value = value.replace('_', ' ').title()
    return value

@register.filter
def number_to_position(value):
    if value <= 0:
        return str(value)
    elif value > 9 and value < 21:
        return str(value) + 'th'
    elif value % 10 == 1:
        return str(value) + 'st'
    elif value % 10 == 2:
        return str(value) + 'nd'
    elif value % 10 == 3:
        return str(value) + 'rd'
    else:
        return str(value) + 'th'

# this is at the bottom to stop sublime text syntax highlighting everything
# regex courtesy of stack overflow
URL_REGEX = re.compile(r'''((?:mailto:|http://|https://)[^ <>'"{}|\\^`[\]]*)''')
