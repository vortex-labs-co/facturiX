from decimal import Decimal
from django import template

register = template.Library()

SIMBOLOS = {'COP': '$', 'USD': 'US$', 'EUR': '€', 'MXN': '$', 'GBP': '£'}


@register.filter
def moneda(value, codigo='COP'):
    try:
        n = Decimal(str(value or 0))
    except Exception:
        return value
    if codigo == 'EUR':
        s = f'{n:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        s = f'{n:,.0f}'.replace(',', '.')
    return f'{SIMBOLOS.get(codigo, "$")} {s} {codigo}'
