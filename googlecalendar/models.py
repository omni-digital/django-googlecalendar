import re
import urllib
from django.db import models
import gdata.calendar.service
import gdata.service
import atom
import datetime
from django.db.models import Manager
from utils import parse_date_w3dtf, format_datetime

VERSION = '0.3'

_services = {}

re_cal_id = re.compile(r".*/(.*)")

class Account(models.Model):
    email = models.CharField(max_length = 100, blank = True)
    password = models.CharField(max_length = 100, blank = True)
    token = models.CharField(max_length = 100, blank = True)

    def __unicode__(self):
        if self.email:
            return u'Account for %s' % self.email
        else:
            return u'Account with token'

    @property
    def service(self):
        if not _services.has_key(self.email):
            _service = gdata.calendar.service.CalendarService()
            _service.source = 'ITSLtd-Django_Google-%s' % VERSION
            if self.token:
                _service.auth_token = self.token
            else:
                _service.email = self.email
                _service.password = self.password
                _service.ProgrammaticLogin()
                _services[self.email] = _service
        return _services[self.email]

    def get_own_calendars(self, commit=True):
        cals = self.service.GetOwnCalendarsFeed()
        result = []
        for cal in cals.entry:
            result.append(Calendar.objects.from_gcal(self, cal, commit=commit))
        return result


class CalendarManager(Manager):
    def from_gcal(self, account, gcal, commit=True):
        uri = gcal.id.text
        try:
            instance = self.get(uri = uri)
        except self.model.DoesNotExist:
            instance = self.model(account=account, uri=uri)

        # copy attributes from gcal
        for prop in ['title', 'where', 'summary', 'color', 'timezone', ]:
            attr = getattr(gcal, prop)
            if hasattr(attr, 'value'):
                setattr(instance, prop, attr.value or '')
            elif hasattr(attr, 'text'):
                setattr(instance, prop, attr.text or '')

        for link in gcal.link:
            if link.rel == 'alternate':
                instance.feed_uri = link.href
                break

        if commit:
            instance.save()

        return instance

class Calendar(models.Model):
    account = models.ForeignKey(Account)
    uri = models.CharField(max_length = 255, unique = True)
    calendar_id = models.CharField(max_length = 255, editable=False, unique = True)
    title = models.CharField(max_length = 100)
    where = models.CharField(max_length = 100, blank = True)
    color = models.CharField(max_length = 10, blank = True)
    timezone = models.CharField(max_length = 100, blank = True)
    summary = models.TextField(blank=True, null=True)
    feed_uri = models.CharField(max_length = 255, blank = True, editable=False)

    objects = CalendarManager()

    def __unicode__(self):
        return self.title


    def save(self):
        gcal = self.gCalendar
        if gcal: 
            # existing calendar update
            new = False
        else:
            new = True
            gcal = gdata.calendar.CalendarListEntry()

        gcal.title = atom.Title(text=self.title)
        gcal.summary = atom.Summary(text=self.summary)
        if self.where:
            gcal.where = gdata.calendar.Where(value_string=self.where)
        elif gcal.where and gcal.where.text:
            self.where = gcal.where.text
        if self.color:
            gcal.color = gdata.calendar.Color(value=self.color)
        elif gcal.color and gcal.color.value:
            self.color = gcal.color.value
        if self.timezone:
            gcal.timezone = gdata.calendar.Timezone(value=self.timezone)
        elif gcal.timezone and gcal.timezone.value:
            self.timezone = gcal.timezone.value

        if new:
            new_gcal = self.account.service.InsertCalendar(new_calendar=gcal)
            # gooogle replaces the title with the (email address) style Calendar Id
            #self.calendar_id = new_gcal.title.text
            new_gcal.title = atom.Title(text=self.title)
            new_gcal = self.account.service.UpdateCalendar(calendar=new_gcal)

            self.uri = new_gcal.id.text
            for link in new_gcal.link:
                if link.rel == 'alternate':
                    self.feed_uri = link.href
                    break

        else:
            new_gcal = self.account.service.UpdateCalendar(calendar=gcal)

        m = re_cal_id.match(self.uri)
        if m:
            self.calendar_id = urllib.unquote(m.group(1))

        # TODO This should be managed by a related ACL model
        # Make the calendar read (share) by default
        self.setAclRole(role='read', scope_type='default')

        super(Calendar, self).save()

    def setAclRole(self, role='read', scope_type='default', scope_value=None):
        gcal = self.gCalendar
        if not gcal:
            return
        aclink = gcal.GetAclLink()

        import gdata

        cRole = gdata.calendar.Role(value='http://schemas.google.com/gCal/2005#%s' % (role))

        try:
            #try to get the entry
            rule = self.account.service.GetCalendarAclEntry('%s/%s' % (aclink.href, scope_type))
        except gdata.service.RequestError, e:
            if e.message['reason'] != 'Not Found':
                raise

            # add the entry
            rule = gdata.calendar.CalendarAclEntry()
            rule.role = cRole

            rule.scope = gdata.calendar.Scope()
            rule.scope.type = scope_type
            if scope_value:
                rule.scope.value = scope_value

            returned_rule = self.account.service.InsertAclEntry(rule, aclink.href)
        else:
            # update the entry
            rule.role = cRole
            returned_rule = self.account.service.UpdateAclEntry(rule.GetEditLink().href, rule)

    @property
    def gCalendar(self):
        if self.uri:
            for c in self.account.service.GetOwnCalendarsFeed().entry:
                if self.uri == c.id.text:
                    return c

        return None

    #def getAclRule(self, role):
    #    gcal = self.gCalendar
    #    if not gcal:
    #        return

    #    role_uri = 'http://schemas.google.com/gCal/2005#%s' % (role)
    #    for r in self.account.service.GetCalendarAclFeed(gcal.GetAclLink().href).entry:
    #        if role_uri == r.role.value:
    #            return r

    #    return None

    def get_events(self, commit=True):
        events = self.account.service.GetCalendarEventFeed(uri = self.feed_uri)
        result = []
        for i, event in enumerate(events.entry):
            result.append(Event.objects.from_gcal(self, event, commit=commit))
        return result


class EventManager(Manager):
    def from_gcal(self, calendar, data, commit=True):
        uri = data.id.text
        try:
            instance = self.get(uri = uri)
        except self.model.DoesNotExist:
            instance = self.model(calendar = calendar, uri = uri)

        instance.title = data.title.text or ''
        instance.content = data.content.text or ''
        instance.start_time = parse_date_w3dtf(data.when[0].start_time)
        instance.end_time = parse_date_w3dtf(data.when[0].end_time)
        instance.edit_uri = data.GetEditLink().href
        instance.view_uri = data.GetHtmlLink().href

        if commit:
            instance.save()

        return instance

class Event(models.Model):
    objects = EventManager()
    calendar = models.ForeignKey(Calendar)
    uri = models.CharField(max_length = 255, unique = True, editable=False)
    title = models.CharField(max_length = 255)
    edit_uri = models.CharField(max_length = 255, editable=False)
    view_uri = models.CharField(max_length = 255, editable=False)
    content = models.TextField(blank = True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __unicode__(self):
        return u'%s (%s - %s)' % (self.title, self.start_time, self.end_time)

    def save(self):
        if self.uri: 
            # existing event, update
            entry = self.calendar.account.service.GetCalendarEventEntry(uri = self.edit_uri)
            entry.title.text = self.title
            entry.content.text = self.content
            start_time = format_datetime(self.start_time)
            end_time = format_datetime(self.end_time)
            entry.when = []
            entry.when.append(gdata.calendar.When(start_time = start_time, end_time = end_time))
            self.calendar.account.service.UpdateEvent(entry.GetEditLink().href, entry)
        else:
            entry = gdata.calendar.CalendarEventEntry()
            entry.title = atom.Title(text = self.title)
            entry.content = atom.Content(text = self.content)
            if not self.start_time:
                self.start_time = datetime.datetime.utcnow()
            if not self.end_time:
                self.end_time = self.start_time + datetime.timedelta(hours = 1)
            start_time = format_datetime(self.start_time)
            end_time = format_datetime(self.end_time)
            entry.when.append(gdata.calendar.When(start_time = start_time, end_time = end_time))
            new_entry = self.calendar.account.service.InsertEvent(entry, self.calendar.feed_uri)
            self.uri = new_entry.id.text
            self.edit_uri = new_entry.GetEditLink().href
            self.view_uri = new_entry.GetHtmlLink().href

        super(Event, self).save()

    def delete(self):
        if self.uri: 
            # existing event, delete
            self.calendar.account.service.DeleteEvent(self.edit_uri)
        super(Event, self).delete()


