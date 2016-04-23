from django import template


register = template.Library()

def as_percentage_of(part, whole):
    try:
        return "%d%%" % (float(part) / whole * 100)
    except (ValueError, ZeroDivisionError):
        return ""

register.filter('as_percentage_of', as_percentage_of)
