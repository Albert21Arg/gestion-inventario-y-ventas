from django import template
import random

register = template.Library()

@register.filter
def random_msg(lista):
    if lista:  # verificar que la lista no esté vacía
        return random.choice(lista)
    return "Hola"
