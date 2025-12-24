from django.db import models
from django.core.exceptions import ValidationError

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model
from wagtail.documents import get_document_model
from wagtail.models import Locale
# snippet-related imports
from wagtail.models import DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin, TranslatableMixin
from wagtail.search import index
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.admin.panels import PublishingPanel

from news.models import NewsItem

from modelcluster.fields import ParentalKey
from blocks import blocks as custom_blocks



class HomePage(Page):
    # default template when not specified
    # template = "home/home_page.html"

    max_count = 1  # only allow one home page.

    hero = models.ForeignKey(
        'home.Hero',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='homepage_hero',
    )

    body = StreamField(
        [
            ('hero', custom_blocks.HeroBlock()),
            ("six_philosophies", custom_blocks.SixPhilosophiesBlock()),
            ("programs", custom_blocks.ProgramsBlock()),
            ("text", custom_blocks.TextBlock()),
            ("rich_text", custom_blocks.RichTextBlock()),
            ("image", custom_blocks.ImageBlock()),
            ("page", custom_blocks.CustomPageChooserBlock(
                required=False,
                page_type=['news.NewsItem'],
                group="Standalone Blocks"
            )),
            ("recent_news", custom_blocks.RecentNewsBlock()),
        ],
        block_counts={
            "hero": {"max_num": 1},
            "six_philosophies": {"max_num": 1},
            "programs": {"max_num": 1},
            "recent_news": {"max_num": 1},
        },
        blank=True,
        null=True,
    )

    # admin panels for the fields
    content_panels = Page.content_panels + [
        FieldPanel('hero'),
        FieldPanel('body'),
    ]

    def get_context(self, request):
        """
        Add the list of 6 latest news articles to the context.
        """
        context = super().get_context(request)
        current_locale = Locale.get_active()
        context['news_articles'] = NewsItem.objects.live().public().filter(locale=current_locale).order_by("-first_published_at")[:6]
        return context


class Hero(
    TranslatableMixin,
    PreviewableMixin,
    LockableMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model
):
    """
    A model to represent a hero section with optional image and flexible layouts.

    This is a snippet model that can be reused across different pages.
    """
    title = models.CharField(max_length=255, help_text="The hero title")
    text = RichTextField(help_text="The main hero text content")
    button_text = models.CharField(
        max_length=100,
        help_text="Button text",
        null=True,
        blank=True
    )
    button_url = models.URLField(
        null=True,
        blank=True,
        help_text="Button URL"
    )
    # New fields for enhanced functionality
    target_url = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Optional: Make the entire hero clickable by selecting a target page"
    )
    image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Optional image for the hero"
    )
    image_layout = models.CharField(
        max_length=20,
        choices=[
            ('background', 'Background - Image fills entire hero as background'),
            ('left', 'Left - Image on left, text on right'),
            ('right', 'Right - Image on right, text on left'),
        ],
        default='background',
        help_text="How to display the image"
    )
    image_style = models.CharField(
        max_length=20,
        choices=[
            ('fill', 'Fill - Image fills entire section'),
            ('framed', 'Framed - Image with rounded edges and padding'),
        ],
        default='fill',
        help_text="Style for left/right images (not used for background)"
    )

    revisions = GenericRelation('wagtailcore.Revision', related_query_name="hero")

    def __str__(self):
        return self.title

    def get_preview_template(self, request, mode_name):
        templates = {
            "": "includes/hero_preview.html",
        }

        return templates.get(mode_name, "")


    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)

        # Add layout context flags
        context['has_target_url'] = bool(self.target_url)
        context['is_background'] = self.image_layout == 'background'
        context['is_left'] = self.image_layout == 'left'
        context['is_right'] = self.image_layout == 'right'
        context['is_framed'] = self.image_style == 'framed'

        return context
