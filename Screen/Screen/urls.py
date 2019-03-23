"""Screen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from index.views import index
from motion.views import motion, customcmd
from heat.views import heat, heat_ajax
from settings.views import settingspage, settings_ajax
from preprint.views import preprint, printjob, form_ajax, startPrint, usb, usb_ajax

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='Index'),
    path('motion/', motion, name='Motion'),
    path('heat/', heat, name='Heat'),
    path('settings/', settingspage, name='Settings'),
    path('preprint/', preprint, name='Prepare to Print'),
    path('usb/', usb, name='usb files'),
    path('print/', printjob, name='Printing'),
    path('filecontrol/', form_ajax, name='filecontroller ajax'),
    path('startprint/', startPrint, name='print starter ajax'),
    path('usbcontrol/', usb_ajax, name='usb ajax'),
    path('setsetting/', settings_ajax, name='settings ajax'),
    path('setheat/', heat_ajax, name='heat ajax'),
    path('cmdsend/', customcmd, name='command sender ajax'),

]
