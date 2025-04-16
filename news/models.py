from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.blocks import PageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.admin.panels import PublishingPanel
from wagtail.models import DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, re_path

from blocks import blocks as custom_blocks


# Create your models here.
class NewsIndex(RoutablePageMixin, Page):
    """
    A page that lists all news articles.
    """
    template = 'news/news_index.html'
    max_count = 1  # only allow one news index page.
    parent_page_types = ['home.HomePage']  # restrict parent page to HomePage
    subpage_types = ['news.NewsItem']  # restrict child pages to NewsItem

    subtitle = models.CharField(max_length=100, blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    # @path("")
    # def default_news_page(self, request):
    #     """
    #     The default route for the news index page.
    #     """
    #     news_headline = "Latest News"

    #     return self.render(
    #         request,
    #         context_overrides={
    #             "news_headline": news_headline,
    #         },
    #     )

    # /news/all
    @path("all/", name="all")
    def all_news_items(self, request):
        """
        A route to display all news articles.
        """
        news_items = NewsItem.objects.live().public()

        return self.render(
            request,
            context_overrides={
                "news_items": news_items,
            },
        )

    # /news/tag/{tag_name}>
    @path("tag/<str:tag>/", name="tag")
    @path("tags/<str:tag>/", name="tags")
    def news_items_by_tag(self, request, tag=None):
        """
        A route to display all news articles.
        """
        news_items = NewsItem.objects.live().public().filter(tags__name=tag)

        return self.render(
            request,
            context_overrides={
                "news_items": news_items,
                "tag": tag,
            },
            template="news/news_tag.html",
        )

    # /news/api/2025
    @re_path(r"^api/(\d+)/$", name="api")
    def api_news_items(self, request, year):
        """
        A route to display all news articles.
        """
        articles = NewsItem.objects.live().public().filter(
            first_published_at__year=year
        )
        return JsonResponse(
            {
                "status": "ok",
                "articles": [
                    {
                        "title": article.title,
                        "url": article.url,  # reminder: url is a method not a property
                        "first_published_at": article.first_published_at.isoformat(),
                    }
                    for article in articles
                ],
            }
        )

    def get_context(self, request):
        """
        Add the list of news articles to the context.
        """
        context = super().get_context(request)
        context['newsitems'] = NewsItem.objects.live().public()
        return context


class NewsItemTags(TaggedItemBase):
    """
    A model to manage tags for news items.
    """
    content_object = ParentalKey(
        'news.NewsItem',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class NewsItem(Page):
    """
    A page that displays a specific new article.
    """
    parent_page_types = ['news.NewsIndex']   # restrict parent page to NewsIndex
    subpage_types = []  # restrict child pages to none

    # can always override the default template from base.py
    # https://docs.wagtail.org/en/stable/advanced_topics/privacy.html
    # password_required_template = "news/news_item_password_required.html"

    subtitle = models.CharField(max_length=100, blank=True)
    tags = ClusterTaggableManager(through=NewsItemTags, blank=True)
    author = models.ForeignKey(
        'news.Author',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    body = StreamField(
        [
            ("info", custom_blocks.InfoBlock()),
            ("faq", custom_blocks.FaqListBlock()),
            ("text", custom_blocks.TextBlock()),
            ("carousel", custom_blocks.CarouselBlock()),
            ("image", custom_blocks.ImageBlock()),
            ("doc", DocumentChooserBlock(
                # can set your own template here if you want
                # template="blocks/document_block.html",
                group="Standalone Blocks"
            )),
            ("page", PageChooserBlock(
                required=False,
                page_type=['news.NewsItem'],
                group="Standalone Blocks"
            )),
            ("author", SnippetChooserBlock('news.Author')),
            ("call_to_action_1", custom_blocks.CallToActionBlock()),
        ],
        block_counts={
            # "text": {"min_num": 1, "max_num": 3},
            # "image": {"min_num": 0, "max_num": 2},
        },
        # use_json_field=True,  # not needed in Wagtail 6+
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('tags'),
        ], heading="News Item information", permission="news.add_author"),
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    def clean(self):
        super().clean()

        errors = {}

        # can set any field errors and conditions in here
        if "news" in self.title.lower():
            errors["title"] = "Please don't use the word 'news' in the title."

        if errors:
            raise ValidationError(errors)


class Author(
    PreviewableMixin,
    LockableMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    models.Model
):
    """
    A model to represent an author.
    """
    name = models.CharField(max_length=100)
    bio = models.TextField()
    revisions = GenericRelation('wagtailcore.Revision', related_query_name="author")

    panels = [
        FieldPanel("name", permission="news.can_edit_author_name"),
        FieldPanel("bio"),
        PublishingPanel(),
    ]

    search_fields = [
        index.FilterField("name"),
        index.SearchField("name", boost=10),
        index.SearchField("bio"),
        index.AutocompleteField("name"),
    ]

    def __str__(self):
        return self.name

    def get_preview_template(self, request, mode_name):
        templates = {
            "": "includes/author.html",
            "dark_mode": "includes/author_dark_mode.html",
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

    class Meta:
        permissions = [
            ("can_edit_author_name", "Can edit author name"),
        ]
