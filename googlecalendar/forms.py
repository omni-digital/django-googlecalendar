from django import forms
from googlecalendar.models import Event, Calendar
from django.utils.translation import ugettext_lazy as _
#from django.forms.extras.widgets import SplitDateTimeWidget


class AddEventForm(forms.ModelForm):
    """ Add event form for calendar_list page """
    calendar = forms.ModelChoiceField(queryset=Calendar.active)
    start_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(), label=_('Start date and time'))
    end_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(), label=_('End date and time'))



    def clean_end_time(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        if end_time < start_time:
            raise forms.ValidationError("End date can not be earlier than start date.")

        return end_time


    class Meta:
        model = Event
        fields = ('calendar', 'title', 'summary', 'start_time', 'end_time')



class AddEventCalendarForm(AddEventForm):
    """ Add event form for calendar page. Calendar is preset. """

    def __init__(self, *args, **kwargs):
        self.calendar = kwargs.pop('calendar')
        super(AddEventCalendarForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].widget=forms.HiddenInput()
        self.fields['calendar'].initial=self.calendar
