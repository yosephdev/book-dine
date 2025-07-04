from django import template

register = template.Library()

@register.inclusion_tag('partials/navigation.html', takes_context=True)
def main_navigation(context):
    return {
        'user': context['user'],
        'request': context['request'],
    }
