from IPy import IP

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from braces.views import LoginRequiredMixin

from forms import ReadOnlyWidget
from models import Subnet, Address

#
# Helpers and Mixins
#


class GenericSubnetMixin(object):
    model = Subnet
    template_object_name = 'subnet'
    pk_url_kwarg = 'subnet_id'

    def get_queryset(self):
        return Subnet.objects.order_by('is_private', 'network_addr')


def helper_split_subnet(network, len):
    subnet_list = []
    addr_len = (32, 128)[network.version() == 6]
    for s in range(network.int(), network.broadcast().int(), 2**(addr_len-len)):
        subnet_list.append(IP(s).make_net(len))
    return subnet_list


#
# Subnet Views
#

class NetmanIpAddrSubnetHome(LoginRequiredMixin, GenericSubnetMixin, ListView):
    pass


class NetmanIpAddrSubnetView(LoginRequiredMixin, GenericSubnetMixin, DetailView):
    def dispatch(self, request, subnet_id):
        self.subnet = get_object_or_404(Subnet, id=subnet_id)
        return super(NetmanIpAddrSubnetView, self).dispatch(request, subnet_id)

    def get_context_data(self, **kwargs):
        context = super(NetmanIpAddrSubnetView, self).get_context_data(**kwargs)
        context['actions'] = (
            (reverse_lazy('netman_ipaddr_subnet_edit', kwargs={'subnet_id': self.subnet.id}), 'Edit Subnet'),
            (reverse_lazy('netman_ipaddr_subnet_delete', kwargs={'subnet_id': self.subnet.id}), 'Delete Subnet'),
        )
        return context


class NetmanIpAddrSubnetCreate(LoginRequiredMixin, GenericSubnetMixin, SuccessMessageMixin, CreateView):
    success_message = "Subnet %(network_addr)s was created successfully"


class NetmanIpAddrSubnetDelete(LoginRequiredMixin, GenericSubnetMixin, SuccessMessageMixin, DeleteView):
    success_message = "Subnet %(network_addr)s was deleted successfully"
    success_url = reverse_lazy('netman_ipaddr_home')


class NetmanIpAddrSubnetUpdate(LoginRequiredMixin, GenericSubnetMixin, SuccessMessageMixin, UpdateView):
    success_message = "Subnet %(network_addr)s was updated successfully"

    def dispatch(self, request, subnet_id):
        self.subnet = get_object_or_404(Subnet, id=subnet_id)
        return super(NetmanIpAddrSubnetUpdate, self).dispatch(request, subnet_id)

    def get_success_url(self):
        return reverse_lazy('netman_ipaddr_subnet_view', kwargs={'subnet_id': self.subnet.id})


@login_required
def split_subnet(request, subnet_id):
    subnet = get_object_or_404(Subnet, id=subnet_id)
    prefix_len_choices = range(subnet.network_addr.prefixlen() + 1,
                               ((32, 128)[subnet.network_addr.version() == 6]) - 1)

    choices_prefixes = zip(prefix_len_choices, prefix_len_choices)

    class SplitSubnetForm(forms.Form):
        network = forms.CharField(max_length=32, widget=ReadOnlyWidget(subnet.network_addr))
        prefix_len = forms.TypedChoiceField(label='Prefix Length', coerce=int, choices=choices_prefixes)
        super_nets = forms.BooleanField(label='Super Nets', initial=False, required=False)

    if request.method == 'POST':
        form = SplitSubnetForm(request.POST)
        if form.is_valid():
            for sub in helper_split_subnet(subnet.network_addr, form.cleaned_data['prefix_len']):
                Subnet(network_addr=sub, parent=subnet, supernet=form.cleaned_data['super_nets']).save()
            return HttpResponseRedirect('../../')
    else:
        form = SplitSubnetForm()

    context = {'form': form, 'title': 'IP Address Manager :: Split Subnet'}
    return render_to_response('ipaddr/subnet_form.html', context,
                              context_instance=RequestContext(request))


#
# Address Views
#


class NetmanIpAddrAddressUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Address
    template_object_name = 'address'
    pk_url_kwarg = 'addr_id'
    success_url = '../../'
    success_message = "Address %(addr)s was updated successfully"

    def dispatch(self, request, subnet_id, addr_id):
        self.subnet = get_object_or_404(Subnet, id=subnet_id)
        return super(NetmanIpAddrAddressUpdate, self).dispatch(request, subnet_id, addr_id)

    def get_form_class(self):
        class AddressForm(forms.ModelForm):
            addr = forms.CharField(label='Address', max_length=64, widget=ReadOnlyWidget())

            class Meta:
                exclude = ['subnet']
                model = Address
        return AddressForm

    def get_queryset(self):
        return Address.objects.filter(subnet=self.subnet)
