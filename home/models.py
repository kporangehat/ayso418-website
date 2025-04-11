from django.db import models
from django.core.exceptions import ValidationError

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
        related_name='+',
    )

    cta_url = models.ForeignKey(
        'wagtailcore.Page',  # can limit this to specific page types
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    cta_external_url = models.URLField(
        blank=True,
        null=True,
    )

    # admin panels for the fields
    content_panels = Page.content_panels + [
        FieldPanel('subtitle', read_only=True),
        FieldPanel('cta_url'),
        FieldPanel('cta_external_url'),
        FieldPanel('body'),
        FieldPanel('image'),  # ImageChooser is a widget for selecting images
        FieldPanel('custom_document'),
    ]

    @property
    def get_cta_url(self):
        """
        Returns the URL for the call to action button.
        If both internal and external URLs are set, it will return the internal URL.
        """
        if self.cta_url:
            return self.cta_url.url
        elif self.cta_external_url:
            return self.cta_external_url
        return None

    def clean(self):
        super().clean()

        errors = {}

        # can set any field errors and conditions in here
        if self.cta_url and self.cta_external_url:
            errors["cta_url"] = "You cannot set both internal and an external URL."
            errors["cta_external_url"] = "You cannot set both internal and an external URL."

        if errors:
            raise ValidationError(errors)
