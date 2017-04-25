

from .models import clients, ads, ad_schedule
from django.core import serializers
import pickle
import json
import atexit
import os


# Observer that stores a list of all the addedd ads, deleted ads
# if a client requests an update, the observer must check if any changes are
# present for that client and return a string (HTTP formatted) that 
# represents the instructions that must be executed for the client 
# if an ad is added to a client return an http request object give the 
# client a json string that includes all the data for the ad as well 
# as a link for downloading the ad if the ad is being deleted from the
# client provide a http response that provides the 
# client {"added": [], "deleted": []}

class Observer():
    def __init__(self):
        '''Try and load a pickled observer otherwise create
        a new one'''
        
        self.updated_clients = {}
  
    def client_ads_changed(self, client, old):
        """Returns true or false depending on whether the ads associated
        with the given client have changed with the most recent update.
        If any changes are detected the observer dictionary is updated 
        with the relevent creation and deletion instructions"""
        new = set([ad.ad_name for ad in \
            clients.objects.get(client_name=client).client_ads.all()])
        old = set(old)
        
        new_changes = new.difference(old)
        for ad in new_changes:
            self.add_ad_to_client(ad, client)

        old_changes = old.difference(new)
        for ad in old_changes:
            self.remove_ad_from_client(ad, client)            
  
        if len(old_changes) == 0 and len(new_changes) == 0:
            return False
        else: return True

    def ad_clients_changed(self, ad, old):
        """Returns true or false depending on whether the ad's associated
        clients are updated since the last edit by comparing the most recent 
        value with one stored in the observer. It will also update the observer
        dictionary with the appropriate instructions depending on the results of
        the check"""
        old = set(old)
        new =set([c.client_name for c in \
                    ads.objects.get(ad_name=ad).ad_clients.all()])
        
        new_changes = new.difference(old)
        for client in new_changes:
            self.add_ad_to_client(ad, client)
                        
        old_changes = old.difference(new)
        for client in old_changes:
            self.remove_ad_from_client(ad, client)

        if len(old_changes) == 0 and len(new_changes) == 0:
            return False
        else: return True
        

    def delete_ad(self, ad):
        '''Takes a string for an ad name, query's all clients to identify
        those that contain it and flaggs it for deletion in each'''
        _clients = clients.objects.all()
        for client in _clients:
            if ad in [ad.ad_name for ad in client.client_ads.all()]:
                self.remove_ad_from_client(ad.ad_name,
                                    client.client_name)

    def add_ad_to_client(self, ad, client):
        """appends an ad to a client and removes any DELETE instructions
        from the dict"""
        self.updated_clients[client] = self.updated_clients.get(client, {"CREATE": {}, "DELETE": []})
        self.updated_clients[client]["CREATE"][ad] = convert_ad_to_json(ad)
        if ad in self.updated_clients[client]["DELETE"]: 
            self.updated_clients[client]["DELETE"].remove(ad)
        
    def remove_ad_from_client(self, ad, client):
        """Takes a string that represents an ad and a client and 
        gives the instruction to delete the ad from the client """
        self.updated_clients[client] = self.updated_clients.get(client, {"CREATE": {},"DELETE": []})

        self.updated_clients[client]["DELETE"].append(ad)
        if ad in self.updated_clients[client]["CREATE"]:  
            self.updated_clients[client]["CREATE"].pop(ad)
        
    def update_client(self, client):
        """The application checks if the client has any updates
        returns a no operation signal if not. Returns a json string for"""
        instructions = self.updated_clients.get(client, None)
        if instructions:
            response = json.dumps(instructions)
            self.updated_clients.pop(client)
            return response 
        else:
            return -1

            
observer = Observer()

def convert_ad_to_json(ad):

    _ad = ads.objects.get(ad_name = ad)
    try:
        schedule = ad_schedule.objects.get(ad_id=ad)
    except:
        duration = {}
    else:
        duration = {"start": schedule.start.strftime("%Y-%m-%d") ,
                        "end": schedule.end.strftime("%Y-%m-%d"),
                        "days": schedule.days,
                        "interval_one": schedule.interval_one,
                        "interval_two": schedule.interval_two,
                        "interval_three": schedule.interval_three}
                        
    filename = os.path.split(_ad.source.name)[1]
    js =  {"name": _ad.ad_name,
            "filename": filename,
            "duration": duration,
            "link": _ad.source.url}
    return json.dumps(js)