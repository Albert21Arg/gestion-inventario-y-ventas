from django import template

register = template.Library()

@register.filter
def currency(value):
    """
    Formatea un número como moneda con separadores de miles estilo colombiano.
    Ejemplo: 1500000 -> $1.500.000
    """
    try:
        value = float(value)
        return "${:,.0f}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value
