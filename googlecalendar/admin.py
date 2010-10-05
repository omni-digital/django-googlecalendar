from django.contrib import admin
from django import forms
from models import *
from incunafein.admin import editor

class CalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'calendar_id', ]
    list_filter = ( 'account',)
    search_fields = ('title', 'slug', 'summary',)
    prepopulated_fields = {
        'slug': ('title',),
        }

class EventAdmin(editor.ItemEditor, admin.ModelAdmin):
    date_hierarchy = 'start_time'
    list_display = ('__unicode__', 'calendar', 'start_time', 'end_time',)
    list_filter = ( 'calendar',)
    search_fields = ('title', 'slug', 'summary',)
    prepopulated_fields = {
        'slug': ('title',),
        }

admin.site.register(Account)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)

