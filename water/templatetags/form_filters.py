from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """Returns the form field dynamically by name."""
    return form[field_name]
