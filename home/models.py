from django.db import models
from django.core.exceptions import ValidationError

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel, FieldRowPanel, HelpPanel, MultipleChooserPanel, TitleFieldPanel
from wagtail.fields import RichTextField, BlockField, StreamField
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


class HomePageGalleryImage(Orderable):
    page = ParentalKey(
        'home.HomePage',
        related_name='gallery_images',
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        get_image_model(),
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',  # + means no reverse relation required
    )


class HomePage(Page):
    # default template when not specified
    # template = "home/home_page.html"

    max_count = 1  # only allow one home page.

    CTA = models.ForeignKey(
        'home.CTA',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='homepage_cta',
    )

    body = StreamField(
        [
            ('hero', custom_blocks.HeroBlock()),
            ("six_philosophies", custom_blocks.SixPhilosophiesBlock()),
            ("programs", custom_blocks.ProgramsBlock()),
            ("faq", custom_blocks.FaqListBlock()),
            ("text", custom_blocks.TextBlock()),
            ("carousel", custom_blocks.CarouselBlock()),
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
        },
        blank=True,
        null=True,
    )

    # admin panels for the fields
    content_panels = Page.content_panels + [
        FieldPanel('CTA'),
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


class CTA(
    TranslatableMixin,
    PreviewableMixin,
    LockableMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model
):
    """
    A model to represent a call-to-action.
    """
    title = models.CharField(max_length=255)
    text = RichTextField()
    button_text = models.CharField(max_length=100)
    button_url = models.URLField()
    revisions = GenericRelation('wagtailcore.Revision', related_query_name="cta")


    def __str__(self):
        return self.title

    def get_preview_template(self, request, mode_name):
        templates = {
            "": "includes/cta_preview.html",
        }

        return templates.get(mode_name, "")

    @property
    def preview_modes(self):
        return PreviewableMixin.DEFAULT_PREVIEW_MODES + [
            ("dark_mode", "Dark Mode"),
        ]

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        if mode_name == "dark_mode":
            context["warning"] = "This is a preview in dark mode"

        return context

    # class Meta(TranslatableMixin.Meta):
    #     permissions = [
    #         ("can_edit_author_name", "Can edit author name"),
    #     ]
