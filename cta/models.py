from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from wagtail.models import DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin
from wagtail.fields import RichTextField
from wagtail.images import get_image_model
from wagtail.search import index


class CTA(
    PreviewableMixin,
    LockableMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
    """
    A reusable Call to Action snippet with flexible layout options.

    Supports draft/publish workflow, revisions, and locking.
    """

    LAYOUT_CHOICES = [
        ("text_left", "Text Left, Image Right"),
        ("image_left", "Image Left, Text Right"),
        ("centered", "Text Centered (No Image)"),
    ]

    BACKGROUND_CHOICES = [
        ("", "Default (Inherit)"),
        ("cta-bg-light", "Light Gray"),
        ("cta-bg-primary", "Primary Tint"),
        ("cta-bg-secondary", "Secondary Tint"),
        ("cta-bg-blue", "Blue Gradient"),
        ("cta-bg-green", "Green Gradient"),
        ("cta-bg-purple", "Purple Gradient"),
        ("cta-bg-warm", "Warm Gradient"),
        ("cta-bg-dark", "Dark"),
    ]

    # Admin/internal identifier
    title = models.CharField(
        max_length=255,
        help_text="Internal title for identifying this CTA in the admin",
    )

    # Display content
    heading = models.CharField(
        max_length=255,
        help_text="Heading displayed in the CTA",
    )
    text = RichTextField(
        features=["bold", "italic", "link"],
        help_text="Main body text for the CTA",
    )

    # Optional image
    image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional image (not used for 'Text Centered' layout)",
    )

    # Optional button
    button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Button label (leave blank to use the linked page's title)",
    )
    button_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Internal page for the button to link to",
    )
    button_url = models.URLField(
        blank=True,
        help_text="External URL for the button (used only if no page is selected)",
    )

    # Layout & appearance
    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default="centered",
        help_text="How to arrange the text and optional image",
    )
    background = models.CharField(
        max_length=30,
        choices=BACKGROUND_CHOICES,
        default="",
        blank=True,
        help_text="Background colour or gradient for this CTA",
    )

    revisions = GenericRelation("wagtailcore.Revision", related_query_name="cta")

    search_fields = [
        index.SearchField("title", boost=10),
        index.SearchField("heading", boost=5),
        index.SearchField("text"),
    ]

    def __str__(self):
        return self.title

    def get_button_url(self):
        """Return the resolved button URL, preferring button_page over button_url."""
        if self.button_page:
            return self.button_page.url
        return self.button_url or ""

    def get_button_label(self):
        """Return the button label, falling back to the linked page title."""
        if self.button_text:
            return self.button_text
        if self.button_page:
            return self.button_page.title
        return ""

    def get_preview_template(self, request, mode_name):
        return "includes/cta_snippet_preview.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["cta"] = self
        return context

    class Meta:
        verbose_name = "CTA"
        verbose_name_plural = "CTAs"
        ordering = ["title"]
