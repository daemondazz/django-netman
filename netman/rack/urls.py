from django.conf.urls import include, patterns, url

from views import NetmanRackHome
from views import NetmanRackView
from views import NetmanRackCreate, NetmanRackDelete, NetmanRackUpdate
from views import NetmanRackCreateDevice, NetmanRackDeleteDevice


rack_patterns = patterns(
    '',

    url(r'^$', NetmanRackView.as_view(),
        name='netman_rack_view'),

    url(r'^edit/$', NetmanRackUpdate.as_view(),
        name='netman_rack_edit'),

    url(r'^delete/$', NetmanRackDelete.as_view(),
        name='netman_rack_delete'),

    url(r'^add-device/$', NetmanRackCreateDevice.as_view(),
        name='netman_rack_add_device'),

    url(r'^delete-(?P<device_id>\d+)/$', NetmanRackDeleteDevice.as_view(),
        name='netman_rack_delete_device'),
)

urlpatterns = patterns(
    '',
    url(r'^$', NetmanRackHome.as_view(), name='netman_rack_home'),
    url(r'^add/$', NetmanRackCreate.as_view(), name='netman_rack_create'),
    (r'^(?P<rack_id>\d+)/', include(rack_patterns)),
)
