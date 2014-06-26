from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from braces.views import LoginRequiredMixin

from models import Rack, RackDevice


#
# Rack Views
#

class GenericRackMixin(object):
    model = Rack
    template_object_name = 'rack'
    pk_url_kwarg = 'rack_id'

    def get_queryset(self):
        return Rack.objects.order_by('name')


class NetmanRackHome(LoginRequiredMixin, GenericRackMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super(NetmanRackHome, self).get_context_data(**kwargs)
        context['actions'] = (
            (reverse_lazy('netman_rack_create'), 'Add Rack'),
        )
        return context


class NetmanRackView(LoginRequiredMixin, GenericRackMixin, DetailView):
    def dispatch(self, request, rack_id):
        self.rack = get_object_or_404(Rack, id=rack_id)
        return super(NetmanRackView, self).dispatch(request, rack_id)

    def get_context_data(self, **kwargs):
        context = super(NetmanRackView, self).get_context_data(**kwargs)
        context['actions'] = (
            (reverse_lazy('netman_rack_add_device', kwargs={'rack_id': self.rack.id}), 'Add Device'),
            (reverse_lazy('netman_rack_delete', kwargs={'rack_id': self.rack.id}), 'Delete Rack'),
            (reverse_lazy('netman_rack_edit', kwargs={'rack_id': self.rack.id}), 'Edit Rack'),
        )
        return context


class NetmanRackCreate(LoginRequiredMixin, GenericRackMixin, SuccessMessageMixin, CreateView):
    success_message = "Rack %(name)s was created successfully"


class NetmanRackDelete(LoginRequiredMixin, GenericRackMixin, DeleteView):
    success_url = reverse_lazy('netman_rack_home')


class NetmanRackUpdate(LoginRequiredMixin, GenericRackMixin, SuccessMessageMixin, UpdateView):
    success_message = "Rack %(name)s was updated successfully"

    def dispatch(self, request, rack_id):
        self.rack = get_object_or_404(Rack, id=rack_id)
        return super(NetmanRackUpdate, self).dispatch(request, rack_id)

    def get_success_url(self):
        return reverse_lazy('netman_rack_view', kwargs={'rack_id': self.rack.id})


#
# Rack Device Views
#


class GenericRackDeviceMixin(object):
    model = RackDevice
    context_object_name = 'device'
    pk_url_kwarg = 'device_id'

    def dispatch(self, request, rack_id, **kwargs):
        self.rack = get_object_or_404(Rack, id=rack_id)
        return super(GenericRackDeviceMixin, self).dispatch(request, rack_id, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GenericRackDeviceMixin, self).get_context_data(**kwargs)
        context['rack'] = self.rack
        return context

    def get_queryset(self):
        return RackDevice.objects.order_by('name')

    def get_success_url(self):
        return reverse_lazy('netman_rack_view', kwargs={'rack_id': self.rack.id})


class NetmanRackCreateDevice(LoginRequiredMixin, GenericRackDeviceMixin, SuccessMessageMixin, CreateView):
    success_message = "Rack Device %(description)s was created successfully"

    def get_form(self, *args, **kwargs):
        form = super(NetmanRackCreateDevice, self).get_form(*args, **kwargs)
        form.fields['rack'].initial = self.rack
        form.fields['rack'].widget = forms.HiddenInput()
        return form


class NetmanRackDeleteDevice(LoginRequiredMixin, GenericRackDeviceMixin, DeleteView):
    pass
