from django.conf.urls import include, patterns, url

from views import NetmanIpAddrSubnetHome, NetmanIpAddrSubnetView
from views import NetmanIpAddrSubnetCreate, NetmanIpAddrSubnetUpdate
from views import split_subnet, NetmanIpAddrSubnetDelete
from views import NetmanIpAddrAddressUpdate


subnet_patterns = patterns('',
    url(r'^$',        NetmanIpAddrSubnetView.as_view(),
        name='netman_ipaddr_subnet_view'),

    url(r'^delete/$', NetmanIpAddrSubnetDelete.as_view(),
        name='netman_ipaddr_subnet_delete'),

    url(r'^edit/$',   NetmanIpAddrSubnetUpdate.as_view(),
        name='netman_ipaddr_subnet_edit'),

    url(r'^split/$',  split_subnet,
        name='netman_ipaddr_subnet_split'),

    url(r'^(?P<addr_id>\d+)/edit/$', NetmanIpAddrAddressUpdate.as_view(), 
        name='netman_ipaddr_addr_edit'),
)

urlpatterns = patterns('',
    url(r'^$', NetmanIpAddrSubnetHome.as_view(), name='netman_ipaddr_home'),

    url(r'^create/$', NetmanIpAddrSubnetCreate.as_view(),
        name='netman_ipaddr_subnet_create'),

    (r'^(?P<subnet_id>\d+)/', include(subnet_patterns)),
)
