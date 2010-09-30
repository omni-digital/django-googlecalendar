import urllib
from django import template 
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from googlecalendar.utils import request_single_token
from googlecalendar.models import Calendar

register = template.Library()

class GoogleCalendarAuthNode(template.Node):
	def __init__(self, uri):
		self.uri = uri
	def render(self, context):
		uri = template.resolve_variable(self.uri, context)
		return request_single_token(uri)

@register.tag
def google_calendar_auth(parser, token):
	bits = token.contents.split()
	len_bits = len(bits)
	if len_bits != 2:
		raise template.TemplateSyntaxError('%s tag requires URI as an argument' % bits[0])
	return GoogleCalendarAuthNode(bits[1])


class CalendarNode(template.Node):
    """
        Render a google calendar (iframe) embed.

        Usage:
            {% calendar calendar width="580" height="350" %}
    """

    COLOURS = ['#D96666', '#E67399', '#8C66D9', '#668CB3', '#668CD9', '#59BFB3', '#65AD89', '#4CB052', '#8CBF40', '#E0C240',
               '#E6804D', '#BE9494', '#A992A9', '#8997A5', '#94A2BE', '#85AAA5', '#A7A77D', '#C4A883', '#C7561E', '#B5515D',
               '#C244AB', '#603F99', '#536CA6', '#3640AD', '#3C995B', '#5CA632', '#7EC225', '#A7B828', '#CF9911', '#D47F1E',
               '#B56414', '#914D14', '#AB2671', '#9643A5', '#4585A3', '#737373', '#41A587', '#D1BC36', '#AD2D2D', ]

    @staticmethod
    def coulours(start = 0):
        """
        Returns a stream of colours, if the end of the list is reached then it starts back at the beginning.
        """
        while True:
            try:
                yield CalendarNode.COLOURS[start]
            except IndexError:
                start = 0
                yield CalendarNode.COLOURS[start]
            start += 1

    def __init__(self, *args, **kwargs):
        self.calendars = args
        self.attrs = kwargs

    def render(self, context):

        final_attrs = dict(style=" border-width:0 ", 
                           width="800", 
                           height="600", 
                           frameborder="0", 
                           scrolling="no")

        src_attrs = dict(showTitle="0", 
                         showCalendars="1", 
                         showTz="0", 
                         wkst="1", 
                         bgcolor="#FFFFFF", 
                         ctz="Europe/London"
                        )

        #calendars = [calendar.resolve(context) for calendar in self.calendars]
        calendars = []
        for calendar in self.calendars:
            calendar = calendar.resolve(context)
            if not isinstance(calendar, Calendar):
                try:
                    calendar = Calendar.objects.get(calendar_id=calendar)
                except Calendar.DoesNotExist:
                    continue

            calendars.append(calendar)


        if not calendars:
            return ''

        attrs = {}
        for key in self.attrs:
            value = self.attrs[key].resolve(context) or self.attrs[key]
            if key in src_attrs:
                src_attrs[key] = value
            else:
                attrs[key] = value

        if attrs:
            final_attrs.update(attrs)

        coulours = self.coulours()
        src = "https://www.google.com/calendar/embed?%s" % ( '&'.join(["%s=%s" % (k, urllib.quote(v)) for k, v in src_attrs.items()]) )
        for calendar in calendars:
            src += "&src=%s&color=%s" % tuple(map(urllib.quote, (calendar.calendar_id, calendar.color or coulours.next())))

        final_attrs['src'] = src

        return mark_safe(u'<iframe%s ></iframe>' % flatatt(final_attrs))

@register.tag()
def embedcalendar(parser, token):
    bits = token.split_contents() 

    if len(bits) < 2:
        raise template.TemplateSyntaxError("'%s tag requires at least 1 arguments." % bits[0])

    calendars = [parser.compile_filter(bits[1])]
    dict = {}
    try:
        for bit in bits[2:]:
            try:
                bit.index('=')
            except ValueError:
                calendars.append(parser.compile_filter(bit))
            else:
                pair = bit.split('=')
                dict[str(pair[0])] = parser.compile_filter(pair[1])
    except TypeError:
        raise template.TemplateSyntaxError('Bad arguments for tag "%s"' % bits[0])

    return CalendarNode(*calendars, **dict)

