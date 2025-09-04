from django import template
from django.utils.translation import get_language

register = template.Library()

CURRENCY_META = {
    'en': {'symbol': '$', 'code': 'USD', 'thousand': ',', 'decimal': '.'},
    'ru': {'symbol': "сум", 'code': 'UZS', 'thousand': ' ', 'decimal': ','},
    'uz': {'symbol': "so'm", 'code': 'UZS', 'thousand': ' ', 'decimal': ','},
}

def _format_number(value, meta):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        amount = 0.0
    s = f"{amount:0.2f}"
    int_part, frac = s.split('.')
    rev = int_part[::-1]
    grouped = ' '.join([rev[i:i+3] for i in range(0, len(rev), 3)])[::-1]
    if meta['decimal'] != '.':
        frac_sep = meta['decimal']
    else:
        frac_sep = '.'
    return f"{grouped}{frac_sep}{frac}"

@register.filter
def price_local(amount):
    lang = get_language() or 'en'
    meta = CURRENCY_META.get(lang.split('-')[0], CURRENCY_META['en'])
    formatted = _format_number(amount, meta)
    if lang.startswith('en'):
        return f"{meta['symbol']}{formatted}"
    if lang.startswith('ru'):
        return f"{formatted} {meta['symbol']}"
    if lang.startswith('uz'):
        return f"{formatted} {meta['symbol']}"
    return f"{meta['symbol']}{formatted}"
