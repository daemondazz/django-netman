from decimal import Decimal
from IPy import IP

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields, widgets
from django.forms import ValidationError as FormValidationError
from django.forms.util import flatatt


IP.__long__ = IP.int


def clean_ip(ip):
    'Method for validating IPs on forms'
    try:
        IP(ip)
    except Exception, e:
        raise FormValidationError(e)
    return ip


class IPAddressWidget(widgets.TextInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, IP):
            value = unicode(value)
        return super(IPAddressWidget, self).render(name, value, attrs)


class NewIPAddressField(models.Field):
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'cidr'

    def to_python(self, value):
        if not value or isinstance(value, IP):
            return value
        if isinstance(value, Decimal):
            value = long(value)
        try:
            return IP(value)
        except Exception, e:
            raise ValidationError(e)

    def get_db_prep_lookup(self, lookup_type, value, **kwargs):
        try:
            if lookup_type in ('range', 'in'):
                return [self.get_db_prep_value(v) for v in value]
            return [self.get_db_prep_value(value)]
        except ValidationError:
            return super(NewIPAddressField, self).get_db_prep_lookup(
                lookup_type, value, *kwargs)

    def get_db_prep_value(self, value, **kwargs):
        try:
            return self.to_python(value).strNormal()
        except (AttributeError, TypeError):
            return None

    def formfield(self, **kwargs):
        defaults = {
            'form_class': fields.CharField,
            'widget': IPAddressWidget,
        }
        defaults.update(kwargs)
        return super(NewIPAddressField, self).formfield(**defaults)


class ReadOnlyWidget(forms.Widget):
    def __init__(self, display_value=None, *args, **kwargs):
        super(ReadOnlyWidget, self).__init__(*args, **kwargs)
        self.display_value = display_value

    def render(self, name, value, attrs):
        if hasattr(self, 'initial'):
            value = self.initial
        final_attrs = self.build_attrs(attrs, name=name)
        if 'class' not in final_attrs:
            final_attrs['class'] = 'read-only-field'
        else:
            final_attrs['class'].append(' read-only-field')
        if self.display_value is None:
            self.display_value = value or ''
        return '%s<input type="hidden" %s value="%s" />' % (
            self.display_value, flatatt(final_attrs), self.display_value)

    def _has_changed(self, initial, data):
        return False


class ReadOnlyField(forms.FileField):
    widget = ReadOnlyWidget

    def __init__(self, widget=None, label=None, initial=None, help_text=None):
        forms.Field.__init__(self, label=label, initial=initial,
                             help_text=help_text, widget=widget)

    def clean(self, value, initial):
        self.widget.initial = initial
        return value
