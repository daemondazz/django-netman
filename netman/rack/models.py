#
# AFOYI Network Manager Models
#
# Models required for the AFOYI network manager system.
#
# Author:    Darryl Ross <darryl@afoyi.com>
# Copyright: (c) 2010 AFOYI
# Version:   $Id$
#


from django.db import models
from django.core.urlresolvers import reverse


class Rack(models.Model):
    name = models.CharField(max_length=64)
    height = models.IntegerField()
    location = models.CharField(max_length=64, blank=True, null=True)
    suite = models.CharField(max_length=64, blank=True, null=True)
    row = models.CharField(max_length=64, blank=True, null=True)

    def populated_slots(self):
        slots = [False] * self.height
        for device in self.rackdevice_set.all():
            device_bottom = device.rack_slot - 1
            device_top = device_bottom + device.height
            for idx in xrange(device_bottom, device_top):
                if not slots[idx]:
                    slots[idx] = {'front': None, 'back': None, 'full': None}
                slots[idx][device.location] = {'populated': True,
                                               'top': (False, True)[idx == device_top - 1],
                                               'device': device}
        return slots

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('netman_rack_view', kwargs={'rack_id': str(self.id)})

    class Meta:
        ordering = ('name',)


class RackDevice(models.Model):
    rack = models.ForeignKey(Rack)
    description = models.CharField(max_length=64)
    height = models.IntegerField()
    rack_slot = models.IntegerField()
    location = models.CharField(max_length=16, choices=(('front', 'Front Only'), ('back', 'Back Only'), ('full', 'Full Depth')))

    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ('rack', 'rack_slot')
