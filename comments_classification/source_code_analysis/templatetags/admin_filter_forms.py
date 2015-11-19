"""
:Author: Valerio Maggio
:Organization: University of Naples Federico II
:Contact: valerio.maggio@unina.it

"""

from django.template import Library

register = Library()

@register.inclusion_tag('admin/admin_filter_forms.html', takes_context=True)
def admin_filter_forms(context):
    """Custom templatetag to show `AdminFilterForm` instances. All the forms are in the
    context instance. Thus this method needs only to return the context instance in input."""
    return context