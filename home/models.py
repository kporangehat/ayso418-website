from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model
from wagtail.documents import get_document_model


class HomePage(Page):
    # default template when not specified
    # template = "home/home_page.html"

    max_count = 1  # only allow one home page.

    subtitle = models.CharField(max_length=255, blank=True, null=True)
    body = RichTextField(blank=True)

    image = models.ForeignKey(
        get_image_model(),  # will determine this is 'wagtailimages.CustomImage'
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',  # + means no reverse relation required
    )

    custom_document = models.ForeignKey(
        get_document_model(),  # will determine this is soemthing like 'wagtaildocs.CustomDocument'
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',  # + means no reverse relation required
    )

    # admin panels for the fields
    content_panels = Page.content_panels + [
        FieldPanel('subtitle', read_only=True),
        FieldPanel('body'),
        FieldPanel('image'),  # ImageChooser is a widget for selecting images
        FieldPanel('custom_document'),
    ]


