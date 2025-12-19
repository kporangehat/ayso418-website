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
    Index page for the Resources section.
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
            ("resources_navigation", custom_blocks.ResourcesNavigationBlock()),
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

    def get_context(self, request):
        context = super().get_context(request)

        # Get direct children (category pages) of ResourcesIndex
        category_pages = self.get_children().live().specific()

        # Build a list of categories with their child pages
        categories_with_children = []
        for category_page in category_pages:
            # Get the children of each category page
            child_pages = category_page.get_children().live().specific()
            categories_with_children.append({
                'category_page': category_page,
                'child_pages': child_pages
            })

        context['categories_with_children'] = categories_with_children
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
            ("layout_section", custom_blocks.LayoutSectionBlock()),
        ],
        block_counts={
            # "layout_section": {"min_num": 1},
        },
        blank=True,
        null=True,
    )

    callouts = StreamField(
        [
            ("call_to_action", custom_blocks.CallToActionBlock()),
            ("recent_news", custom_blocks.RecentNewsBlock()),
            ("programs", custom_blocks.ProgramsBlock()),
            ("faq", custom_blocks.FAQBlock()),
            ("six_philosophies", custom_blocks.SixPhilosophiesBlock()),
        ],
        block_counts={},
        blank=True,
        null=True,
        help_text="Full-width callout blocks that appear below the main page content"
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('category'),
        FieldPanel('image'),
        FieldPanel('body'),
        FieldPanel('callouts'),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Find the ResourcesIndex page (parent of all resource pages)
        resources_index = self.get_ancestors().type(ResourcesIndex).first()

        if resources_index:
            # Get the parent category page (direct child of ResourcesIndex)
            category_page = None

            # Check the depth relative to ResourcesIndex
            # If we're 1 level below ResourcesIndex, we ARE a category page
            # If we're 2+ levels below, we need to find our category page ancestor

            parent_id = self.get_parent().id
            resources_index_id = resources_index.id

            if parent_id == resources_index_id:
                # Current page is a category page (direct child of ResourcesIndex)
                category_page = self
            else:
                # Current page is a content page, find its category page
                # Get all ancestors and find the one that's a direct child of ResourcesIndex
                for ancestor in self.get_ancestors().specific():
                    ancestor_parent = ancestor.get_parent()
                    if ancestor_parent and ancestor_parent.id == resources_index_id:
                        category_page = ancestor
                        break

            # Get all sibling pages (children of the same category page)
            sibling_pages = []
            if category_page:
                sibling_pages = category_page.get_children().live().specific().order_by('title')

            context['resources_index'] = resources_index
            context['category_page'] = category_page
            context['sibling_pages'] = sibling_pages
            context['current_page'] = self

        return context

    def clean(self):
        super().clean()
        errors = {}

        if errors:
            raise ValidationError(errors)
