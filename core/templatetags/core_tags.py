from decimal import Decimal
from django import template

register = template.Library()


@register.filter
def moneda(value):
    try:
        n = Decimal(str(value or 0))
    except Exception:
        return value
    s = f'{n:,.0f}'.replace(',', '.')
    return f'${s} COP'
