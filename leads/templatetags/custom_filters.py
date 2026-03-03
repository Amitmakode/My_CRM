from django import template

register = template.Library()

@register.filter
def budget_format(value):
    if not value:
        return '—'
    try:
        value = int(float(value))
        if value >= 10000000:
            n = value / 10000000
            return f'₹{int(n)}Cr' if n == int(n) else f'₹{round(n,1)}Cr'
        elif value >= 100000:
            n = value / 100000
            return f'₹{int(n)}L' if n == int(n) else f'₹{round(n,1)}L'
        else:
            return f'₹{value:,}'
    except:
        return '—'