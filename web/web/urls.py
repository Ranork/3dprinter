"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from page.views import page, sett, form_ajax, preheat, setbedtemp, setexttemp, manualmove, customcmd, printjob, form_ajax_printjob, settingsAjax
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', page, name='anasayfa'),
    url(r'^yanit/$', form_ajax, name='yanit'),
    url(r'^preheat/$', preheat, name='preheat'),
    url(r'^setbedtemp/$', setbedtemp, name='setbedtemp'),
    url(r'^setexttemp/$', setexttemp, name='setexttemp'),
    url(r'^manualmove/$', manualmove, name='manualmove'),
    url(r'^customcmd/$', customcmd, name='customcmd'),
    url(r'^printjob/$', printjob, name='printjob'),
    url(r'^settings/$', sett, name='ayarlar'),
    url(r'^sAjax/$', settingsAjax, name='ayarlar Ajax'),
    url(r'^printjobajax/$', form_ajax_printjob, name='printjobajax'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)