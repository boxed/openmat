from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def selected(context):
    key = f'{context.get("time")}-{context.get("weekday")}'
    return format_html('class="selected"') if key in context.get('selected') else ''


@register.simple_tag(takes_context=True)
def count(context):
    key = f'{context.get("time")}-{context.get("weekday")}'
    return context.get('counts').get(key, '')
