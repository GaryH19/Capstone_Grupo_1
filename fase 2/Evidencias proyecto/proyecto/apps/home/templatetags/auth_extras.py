from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Uso en el template: {% if request.user|has_group:"Profesor" %}
    """
    if user.is_superuser:
        return True
    
    # Busca el grupo (insensible a mayúsculas/minúsculas)
    return user.groups.filter(name__iexact=group_name).exists()