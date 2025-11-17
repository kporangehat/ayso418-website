from django.db import models
from django.core.exceptions import ValidationError

from wagtail.models import Page, Locale
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model

from blocks import blocks as custom_blocks

# Create your models here.


class ResourcesIndex(Page):
    """
    """
    subtitle = models.CharField(max_length=200, blank=True)
    # header image
    image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    body = StreamField(
        [
            ("six", custom_blocks.SixPhilosophiesBlock()),
            ("text", custom_blocks.TextBlock()),
            ("richtext", custom_blocks.RichTextBlock()),
            ("image", custom_blocks.ImageBlock()),
            ("call_to_action_1", custom_blocks.CallToActionBlock()),
            ("faq", custom_blocks.FaqListBlock()),
        ],
        block_counts={
            # "text": {"min_num": 1},
        },
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('image'),
        FieldPanel('body'),
    ]

    def clean(self):
        super().clean()
        errors = {}

        if errors:
            raise ValidationError(errors)

    # def get_context(self, request):
    #     context = super().get_context(request)

    #     child_pages = self.get_children().live().specific().order_by('category')

    #     context['child_pages'] = child_pages
    #     return context

    def get_context(self, request):
        context = super().get_context(request)

        # Get all live child pages as their specific types, then sort by category
        child_pages = self.get_children().live().specific()
        # Sort in Python if category is on the specific model
        child_pages = sorted(child_pages, key=lambda x: getattr(x, 'category', ''))

        context['child_pages'] = child_pages
        return context

class FlexPage(Page):
    """
    A generic flexible page that can contain various content blocks.
    """
    subtitle = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category of the page for organizational purposes.")

    # header image
    image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    body = StreamField(
        [
            ("six", custom_blocks.SixPhilosophiesBlock()),
            ("text", custom_blocks.TextBlock()),
            ("richtext", custom_blocks.RichTextBlock()),
            ("image", custom_blocks.ImageBlock()),
            ("call_to_action_1", custom_blocks.CallToActionBlock()),
            ("faq", custom_blocks.FaqListBlock()),
        ],
        block_counts={
            # "text": {"min_num": 1},
        },
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('category'),
        FieldPanel('image'),
        FieldPanel('body'),
    ]

    def clean(self):
        super().clean()
        errors = {}

        if errors:
            raise ValidationError(errors)
