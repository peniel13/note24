# yourapp/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par clé."""
    return dictionary.get(key)


@register.filter
def sum_by_key(notations, key):
    """Calcule la somme d'une clé spécifique dans une liste d'objets."""
    return sum(getattr(nota, key, 0) for nota in notations if getattr(nota, key, 0) is not None)
