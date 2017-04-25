"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, static
from django.contrib import admin
from clientManager import views
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views._login, name="login"),
    url(r'^signup/?$', views.signupView.as_view(), name="signup"),
    url(r'^summary/?$', views.summaryView.as_view(), name="summary"),
    url(r'^ads/?$', views.adsView.as_view(), name="ads"),
    url(r'^clients/?$', views.clientsView.as_view(), name="clients"),
    url(r'^add_client/?$', views.clientFormView.as_view(), name="new_client"),
    url(r'^add_advertisment/?$', views.adFormView.as_view(), name="new_ad"),
    url(r'^add_schedule_to_ad/?$', views.add_schedule, name="schedule"),
    url(r'^edit_client/(?P<pk>[\w ]+)/?$', views.updateClientView.as_view(), name="edit_client"),
    url(r'^delete_client/(?P<pk>[\w ]+)/?$', views.deleteClientView.as_view(), name="delete_client"),
    url(r'^edit_ad/(?P<pk>[\w ]+)/?$', views.updateAdView.as_view(), name="edit_ad"),
    url(r'^delete_ad/(?P<pk>[\w ]+)/?$', views.deleteAdView.as_view(), name="delete_ad"),
    url(r'^push_updates/(?P<client_id>[\w ]+)/?$', views.push_updates),
    url(r'^pull_data/(?P<client_id>[\w ]+)/?$', views.pull_data),
    url(r'^push_initial/(?P<client_id>[\w ]+)/?$', views.push_initial),
    url(r'^client_health/(?P<pk>[\w ]+)/?$', views.clientHealthView.as_view(), name="client_health"),
] + static.static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
