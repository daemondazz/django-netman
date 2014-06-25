from mptt.models import MPTTModel, TreeForeignKey
from django.db import models

from afoyi.modules.dns.models import Domain, Record

from forms import NewIPAddressField


class Subnet(MPTTModel):
    description = models.CharField(max_length=64, blank=True)
    network_addr = NewIPAddressField('Network', db_index=True, unique=True,
                                  blank=True)
    supernet = models.BooleanField('Super Net', default=False)
    mask_len = models.IntegerField(editable=False)
    is_private = models.BooleanField('Is Private Network', default=False,
                                     editable=False)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')

    @property
    def ip_version(self):
        return self.network_addr._ipversion

    @property
    def is_ipv4(self):
        return self.ip_version == 4

    @property
    def is_ipv6(self):
        return self.ip_version == 6

    @property
    def is_empty(self):
        empty = True
        for addr in self.address_set.all():
            if addr.addr in (self.network_addr.net(),
                             self.network_addr.broadcast()):
                continue
            if addr.hostname:
                empty = False
                break
        return empty and not self.supernet

    @property
    def is_split(self):
        return self.supernet and not self.is_leaf_node()

    @property
    def usable_addresses(self):
        return len(self.network_addr) - 2

    @property
    def used_addresses(self):
        return self.address_set.exclude(hostname__isnull=True).count()

    @property
    def used_percentage(self):
        pc = (float(self.used_addresses + 2)) / (self.usable_addresses + 2)
        return '%d' % (pc * 100)

    @property
    def usable_used_percentage(self):
        pc = float(self.used_addresses) / self.usable_addresses
        return '%d' % (pc * 100)

    def __unicode__(self):
        return unicode(self.network_addr.strNormal())

    def save(self, *args, **kwargs):
        self.mask_len = self.network_addr.prefixlen()
        if not self.is_private:
            self.is_private = self.network_addr.iptype() == 'PRIVATE'
        super(Subnet, self).save(*args, **kwargs)
        if not self.supernet and self.address_set.count() == 0:
            if self.is_ipv4:
                for a in self.network_addr:
                    addr = Address(subnet=self, addr=a)
                    if a == self.network_addr.net():
                        addr.description = 'NETWORK ADDRESS'
                    if a == self.network_addr.broadcast():
                        addr.description = 'BROADCAST ADDRESS'
                    addr.save()
            elif self.is_ipv6:
                counter = 0
                for a in self.network_addr:
                    if counter > 0xff:
                        break
                    Address(subnet=self, addr=a).save()
                    counter += 1
        if self.supernet and self.address_set.count() > 0:
            self.address_set.all().delete()

    def get_children_sorted(self):
        return self.get_children().order_by('is_private', 'network_addr')

    class Meta:
        ordering = ['is_private', 'network_addr']

    class MPTTMeta:
        order_insertion_by = ['is_private', 'network_addr']


class Address(models.Model):
    subnet = models.ForeignKey(Subnet)
    addr = NewIPAddressField(db_index=True, unique=True, blank=True)
    hostname = models.CharField(max_length=64, null=True, blank=True)
    description = models.CharField(max_length=64, null=True, blank=True)

    def __unicode__(self):
        return self.addr.strNormal()

    def save(self, *args, **kwargs):
        if self.hostname == '':
            self.hostname = None
        if self.description == '':
            self.description is None
        super(Address, self).save(*args, **kwargs)
        try:
            revname = self.addr.reverseName()[:-1]
            if self.hostname in ('ns1', 'web1', 'shared01'):
                desc = self.description.split('/')[0]
            else:
                desc = self.hostname
            record = Record.objects.get(name=revname)
            if desc is None:
                record.delete()
            else:
                record.content = desc
                record.save()
        except Record.DoesNotExist:
            if desc is None:
                return
            try:
                domain = Domain.objects.extra(where=["'%s' LIKE ('%%%%' || name)" % revname]).order_by('-name').first()
                Record(domain=domain,
                       name=revname,
                       type='PTR',
                       content=desc).save()
            except Domain.DoesNotExist:
                pass

    class Meta:
        ordering = ['addr']
