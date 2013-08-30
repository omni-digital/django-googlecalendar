django-googlecalendar
=====================

## FeinCMS regions

Register FeinCMS content regions on the Event model like so:

    Event.register_regions(
        ('main', _('Main region')),
    )
    Event.create_content_type(RichTextContent)
    Event.create_content_type(MediaFileContent, TYPE_CHOICES=(('default', _('Default')),))

