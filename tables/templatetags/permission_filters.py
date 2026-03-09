from django import template
from tables.utils import user_in_group

register = template.Library()


@register.filter(name='in_group')
def in_group(user, group_name):
    return user_in_group(user, group_name)
