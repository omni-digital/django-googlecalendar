from django.contrib import admin
from django import forms
from models import *

class CalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'calendar_id', ]

admin.site.register(Account)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event)
