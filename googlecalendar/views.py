from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from models import Event, Calendar

def googlecalendar_list(request, extra_context=None):
    context = RequestContext(request)

    if extra_context is not None:
        contect.update(extra_context)

    context.update({
        'object_list': Calendar.objects.all(),
    })
    
    return render_to_response('googlecalendar/calendar_list.html', context)
    

def googlecalendar(request, calendar, extra_context=None):
    context = RequestContext(request)

    calendar = get_object_or_404(Calendar, slug=calendar)

    if extra_context is not None:
        contect.update(extra_context)

    context.update({
        'object': calendar,
    })
    
    return render_to_response('googlecalendar/calendar_detail.html', context)


def googlecalendar_event(request, calendar, event, extra_context=None):
    context = RequestContext(request)

    event = get_object_or_404(Event, slug=event)

    if extra_context is not None:
        contect.update(extra_context)

    context.update({
        'object': event,
    })
    
    return render_to_response('googlecalendar/event_detail.html', context)

