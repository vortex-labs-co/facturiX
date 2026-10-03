import json
import urllib.request
from decimal import Decimal

_cache = {}


def tasa_a_cop(moneda):
    """Tasa de conversión desde `moneda` a COP usando API pública gratuita."""
    if moneda == 'COP':
        return Decimal('1')
    if moneda in _cache:
        return _cache[moneda]
    try:
        url = f'https://open.er-api.com/v6/latest/{moneda}'
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        tasa = Decimal(str(data['rates']['COP']))
        _cache[moneda] = tasa
        return tasa
    except Exception:
        # Tasas aproximadas de respaldo en caso de no tener internet
        respaldo = {'USD': Decimal('4200'), 'EUR': Decimal('4550'), 'GBP': Decimal('5300'), 'MXN': Decimal('230')}
        return respaldo.get(moneda, Decimal('1'))
