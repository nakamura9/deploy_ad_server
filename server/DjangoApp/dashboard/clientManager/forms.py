from django import forms
from .models import *
import os


class NiceModalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['placeholder'] =field.label
                field.label = ""
            else:
                field.widget.attrs["class"] = "form-control"


class SignUpForm(NiceModalForm):
    class Meta:
        model = user
        fields = ["first_name", "last_name","email", "password", "username", "role"]
        
class EditClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields["client_ads"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["client_ads"].queryset = ads.objects.all()
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
    class Meta:
        model = clients
        fields = ["client_name", "password", "ip", "location", "client_ads"]

class EditAdForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields["ad_clients"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["ad_clients"].queryset = clients.objects.all()
        self.fields["description"].widget.attrs["rows"] = 5
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
    
    class Meta:
        model = ads
        fields = ["ad_name", "description", "customer", "duration", "source", "ad_clients"]

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields["client_ads"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["client_ads"].queryset = ads.objects.all()
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['placeholder'] =field.label
                field.label = ""
            else:
                field.widget.attrs["class"] = "form-control"
        
    class Meta:
        model = clients
        fields = ["client_name", "password", "ip", "location", "client_ads"]

class AdForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields["ad_clients"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["ad_clients"].queryset = clients.objects.all()
        self.fields["description"].widget.attrs["rows"] = 5
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['placeholder'] =field.label
                field.label = ""
            else:
                field.widget.attrs["class"] = "form-control"    
    class Meta:
        model= ads
        fields = ["ad_name", "description", "customer", "duration", "source", "ad_clients"]


