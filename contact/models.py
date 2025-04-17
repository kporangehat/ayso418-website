from django.db import models

from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel, InlinePanel
from modelcluster.fields import ParentalKey


# TODO: should use django-recaptcha or similar for spam prevention

class FormField(AbstractFormField):
    """
    A form field for the contact form.
    """
    page = ParentalKey(
        "ContactPage",
        related_name="form_fields",
        on_delete=models.CASCADE,
        verbose_name="Contact Page",
    )


class ContactPage(AbstractEmailForm):
    """
    A contact page that allows users to send messages.
    """
    template = "contact/contact_page.html"

    body = RichTextField(blank=True, help_text="Introductory text for the contact page.")
    thank_you_text = RichTextField(blank=True, help_text="Text to display after form submission.")

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("body"),
        InlinePanel("form_fields", label="Custom Form Fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("to_address"),
                FieldPanel("from_address"),
            ]),
            FieldPanel("subject"),
        ]),
    ]
