from django.contrib import admin
from django import forms
from models import *

class CalendarForm(forms.ModelForm):
    class Meta:
        model = Calendar

    def __init__(self, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)

        self.fields['uri'].required = False
    

class CalendarAdmin(admin.ModelAdmin):
    form = CalendarForm
    list_display = ['title', 'calendar_id', ]

admin.site.register(Account)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event)
