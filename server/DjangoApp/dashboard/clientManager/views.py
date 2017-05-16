from .observer import observer, convert_ad_to_json
from .utilities import create_thumbnail, add_message
from .utilities import messages as _messages 
from .models import user, ads, clients, client_health, ad_schedule
from .forms import * 
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.views.generic.edit import FormView, DeleteView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import os 
import shutil
import datetime
import logging


def _login(request):
    if request.method == "GET":
        return render(request, os.path.join("clientManager","login.html"),
                    context={"message": ""})
    elif request.method == "POST":
        name= request.POST["username"]
        pwd = request.POST["password"]
        user = authenticate(username=name, 
                            password=pwd)
        
        if user:
            login(request, user)
            request.session["updates"] = {}
            request.session["start"] = str(datetime.datetime.now())
            add_message("Logged in sucessfully")
            return HttpResponseRedirect(reverse("summary"))
        else: return render(request, os.path.join("clientManager", "login.html"),
                    context={"message": "Invalid Login"})

class signupView(FormView):
    form_class = SignUpForm
    success_url = reverse_lazy("summary")
    template_name = os.path.join("clientManager","signup.html")

    def form_valid(self, form, *args, **kwargs):
        new_user = user.objects.create_user(**form.cleaned_data)
        new_user.save()
        add_message("Created user successfully")
        return super(signupView, self).form_valid(form, *args, **kwargs)
                
        

class summaryView(LoginRequiredMixin,TemplateView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = os.path.join("clientManager","summary.html")

    def get_context_data(self, **kwargs):
        context = super(summaryView, self).get_context_data(**kwargs)
        
        errors = [m for m in _messages if "Error" in m]
        
        if "start" not in self.request.session:
            self.request.session["start"] = str(datetime.datetime.now())

        context["ad_number"]= len(ads.objects.all())
        context["client_number"]= len(clients.objects.all())
        context["console_messages"]= _messages
        context["len_errors"]= len(errors)
        context["len_updates"]= len(observer.updated_clients)
        context["session_start"]= self.request.session["start"]
        
        return context
    

class adsView(LoginRequiredMixin,ListView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    model = ads
    template_name = os.path.join("clientManager","adsummary.html")

    def get_context_data(self, **kwargs):
        context = super(adsView, self).get_context_data(**kwargs)
        context['ads'] = ads.objects.all()
        return context

class clientsView(LoginRequiredMixin,ListView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    model = clients
    template_name = os.path.join("clientManager","clientsummary.html")

    def get_context_data(self, *args, **kwargs):
        context = super(clientsView, self).get_context_data(*args, **kwargs)
        context["clients"] = clients.objects.all()
        return context

class clientFormView(LoginRequiredMixin,FormView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = os.path.join("clientManager","newclient.html")
    form_class = ClientForm
    success_url = reverse_lazy("clients")

    def form_invalid(self, form):
        add_message("failed to create client", error=True)
        return super(clientFormView, self).form_invalid(form)
    
    def form_valid(self, form):
        add_message("Client %s added sucessfully" % form.cleaned_data["client_name"])
        form.save()
        #register with observer
        return super(clientFormView, self).form_valid(form)

        
class adFormView(LoginRequiredMixin,FormView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = os.path.join("clientManager","newad.html")
    form_class = AdForm
    success_url = reverse_lazy("schedule")
    
    
    def form_invalid(self, form):
        add_message("failed to create Advertisment", error=True)
        super(adFormView, self).form_invalid(form)
    
    def form_valid(self, form):
        result = super(adFormView, self).form_valid(form)
        form.save()
        add_message("Advertisment %s added sucessfully" % form.cleaned_data["ad_name"])
        
        #register with observer
        return result

class updateAdView(LoginRequiredMixin,UpdateView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    model = ads
    template_name = os.path.join("clientManager","edit_ad.html")
    form_class = EditAdForm
    success_url = reverse_lazy("ads")
    
    def get(self, *args, **kwargs):
        self.request.session["old"] = [c.client_name for c in self.get_object().ad_clients.all()]
        return super(updateAdView, self).get(*args, **kwargs)
    
    def form_valid(self, form):
        if observer.ad_clients_changed(self.get_object().ad_name, self.request.session["old"]):
            add_message("Advertisment %s edited , will update clients of change" % self.object.ad_name)

        return super(updateAdView, self).form_valid(form)

class updateClientView(LoginRequiredMixin,UpdateView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = os.path.join("clientManager","edit_client.html")
    form_class = EditClientForm
    model = clients
    success_url = reverse_lazy("clients")

    def get(self, *args, **kwargs):
        self.request.session["old"] = [ad.ad_name for ad in self.get_object().client_ads.all()]
        return super(updateClientView, self).get(*args, **kwargs)
    
    def form_valid(self, form):
        if observer.client_ads_changed(self.get_object().client_name, self.request.session["old"]):
            add_message("client %s will have some ads modified" % client)
        return super(updateClientView, self).form_valid(form)
            
            
class clientHealthView(LoginRequiredMixin,DetailView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = os.path.join("clientManager","health_stats.html")
    model = client_health
    
    def get_context_data(self, **kwargs):
        context = super(clientHealthView, self).get_context_data(**kwargs)
        data = model_to_dict(self.get_object())
        data.pop("client")
        for l in data:
            data[l] = json.loads(data[l])
        #validation for instance where there is not data
        rows = zip(data["time"],data["cpu_percentages"],data["ram_percentages"],
                    data["disk_space"],data["temperature"],data["latency"],
                    data["connectivity"],data["playing"])

        context["rows"]= rows
        context["name"]= self.object.client
        return context



class deleteAdView( LoginRequiredMixin,DeleteView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    model = ads
    success_url = reverse_lazy("ads")
#delete file and stuff


class deleteClientView(LoginRequiredMixin,DeleteView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    model = clients
    success_url = reverse_lazy("clients")

    def delete(self, *args, **kwargs):
        add_message("Client %s deleted sucessfully" % self.get_object().client_name)
        return super(deleteClientView, self).delete(*args, **kwargs)

@login_required
def add_schedule(request):
    path = os.path.join("clientManager","adschedule.html")
    
    if request.method == "GET":
        context = {"ads": ads.objects.all()}
        return render(request, path, context=context)

    elif request.method == "POST":
        date_format = "%Y-%m-%d"
        
        print "data", request.POST
        #add ad
        data = {"ad": ads.objects.get(ad_name=request.POST["ad"]),
                "start": datetime.datetime.strptime(request.POST["start"], date_format),
                "end": datetime.datetime.strptime(request.POST["end"], date_format),
                "days": json.dumps(request.POST.getlist("days")),
                "interval_one": request.POST["int_1_start"] + \
                "-" + request.POST["int_1_end"],
                "interval_two": request.POST["int_2_start"] + \
                "-" + request.POST["int_2_end"],
                "interval_three": request.POST["int_3_start"] + \
                "-" + request.POST["int_3_end"],
                }

        ad_schedule(**data).save()
        
        return HttpResponseRedirect(reverse("ads"))

def push_updates(request, client_id):
    if client_id in observer.updated_clients:
        data = json.dumps(observer.updated_clients[client_id])
        add_message("Client %s has received updates from this server" % client_id)
        return HttpResponse(data, content_type="application/json")
        
    else:
        add_message("Client, %s requested updates, none were present" \
            % client_id)
        return HttpResponse("No Updates")

@csrf_exempt
def pull_data(request, client_id):
    if request.method == "POST":
        client = clients.objects.get(client_name=client_id)
        
        client_health_data = json.loads(json.loads(request.body))
        
        for data in client_health_data:
            client_health_data[data] = json.dumps(client_health_data[data])
        
        health = client_health(**client_health_data)
        health.client = client 
        health.save()
        
        add_message("client %s pushed new health data to the server" % client_id)
        return HttpResponse("success")

def push_initial(request, client_id):
    try:
        _client = clients.objects.get(client_name = client_id)
    except:
        add_message("The requesting client, %s is not registered \
        with this server and did not get any updates" % client_id)
        return
    
    response = {}
    num_ads = len(_client.client_ads.all())
    if num_ads == 0:
        add_message("The client, %s tried to start at this \
        timestamp but could not find any initial ads to \
        append to its playlist. It will check again after 10 minutes", error=True)
    else:
        add_message("the client, %s will receive %d ads when it starts up " % (client_id ,num_ads))

    for ad in _client.client_ads.all():
        response[ad.ad_name] = convert_ad_to_json(ad.ad_name)

    return HttpResponse(json.dumps(response),
                        content_type="application/json")