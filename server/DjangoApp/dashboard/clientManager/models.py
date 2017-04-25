from __future__ import unicode_literals
from utilities import *
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import os
import shutil 
class user(User):
    role = models.CharField(max_length=24, choices= [("admin", "Admin"),
                                                    ("guest", "Guest")])

class client_health(models.Model):
    client = models.OneToOneField("clients", primary_key=True)
    connectivity = models.CharField(max_length= 256, default = None, blank=True, null=True)
    disk_space = models.CharField(max_length= 256, default = None, blank=True, null=True)
    temperature = models.CharField(max_length= 256, default = None, blank=True, null=True)
    latency = models.CharField(max_length= 256, default = None, blank=True, null=True)
    playing = models.CharField(max_length= 256, default = None, blank=True, null=True)
    cpu_percentages = models.CharField(max_length= 256, default = None, blank=True, null=True)
    ram_percentages = models.CharField(max_length= 256, default = None, blank=True, null=True)
    time = models.CharField(max_length=256, default = None, blank=True, null=True)

class ad_schedule(models.Model):
    ad = models.OneToOneField("ads")
    start = models.DateTimeField()
    end = models.DateTimeField()
    days = models.CharField(max_length=64)
    interval_one = models.CharField(max_length=12)
    interval_two = models.CharField(max_length=12)
    interval_three = models.CharField(max_length=12)

    
class clients(models.Model):
    
    def delete(self):
        for ad in self.client_ads.all():
            ad.ad_clients.remove(self)
        super(clients, self).delete()

    def save(self, *args, **kwargs):
        global ads
        old = [ad.ad_name for ad in self.client_ads.all()]
        super(clients, self).save(*args, **kwargs)
        _ads = ads.objects.all()
        for ad in _ads:
            #if self is in the ad's client list, but the ad is not 
            # in self's ad list delete
            if self in ad.ad_clients.all() and \
                            ad not in self.client_ads.all():
                ad.ad_clients.remove(self)
                
            # if ad in self's ad list but self not in the 
            #ad's client list, add self to ad
            elif ad in self.client_ads.all() and \
                            self not in ad.ad_clients.all():
                ad.ad_clients.add(self)
            

        
    
    @property
    def num_ads(self):
        return len(self.client_ads.all())

    def __str__(self):
        return self.client_name

    def __repr__(self):
        return self.__str__()
    client_name = models.CharField(max_length=64, verbose_name="Name", primary_key=True)
    password = models.CharField(max_length= 128)
    ip = models.CharField(max_length= 32, verbose_name="IP Address")
    location = models.CharField(max_length= 64)
    client_ads = models.ManyToManyField("ads", blank= True)
    

class messages(models.Model):
    messages = models.CharField(max_length = 2048)

class ads(models.Model):

    def __str__(self):
        return self.ad_name
    def __repr__(self):
        return self.__str__()

    def delete(self):
        for client in self.ad_clients.all():
            client.client_ads.remove(self)
        super(ads, self).delete()

    def save(self, *args, **kwargs):
        global clients
        
        super(ads, self).save(*args, **kwargs)
        if self.thumbnail == "":
            try:
                self.thumbnail = create_thumbnail(self.source.path)
                self.save()
            except:
                pass
        try:
            dest = os.path.join(settings.MEDIA_ROOT, self.ad_name)
            shutil.copyfile(self.source.path, dest)
        except:
            pass
        _clients = clients.objects.all()
        for client in _clients:
            #if self is in the clients ad list, but the client is not 
            # in self's client list delete
            if self in client.client_ads.all() and \
                            client not in self.ad_clients.all():
                client.client_ads.remove(self)
            # if client in self's client list but self not in the 
            #clients ad list, add self to client
            elif client in self.ad_clients.all() and \
                            self not in client.client_ads.all():
                client.client_ads.add(self)

        
    
    ad_name= models.CharField(max_length= 64, verbose_name="Name", primary_key=True)
    description = models.TextField(max_length= 512)
    customer = models.CharField(max_length= 64)
    duration= models.IntegerField(default=0)
    source = models.FileField(upload_to="LocalAdStorage")
    thumbnail = models.CharField(max_length = 128)
    ad_clients = models.ManyToManyField(clients, blank= True)
    
    @property
    def num_clients(self):
        return len(self.ad_clients.all())