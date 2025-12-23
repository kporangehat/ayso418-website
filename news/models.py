from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.admin.panels import PublishingPanel
from wagtail.models import DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, re_path
from wagtail.api import APIField
from wagtail.images import get_image_model
from wagtail.templatetags.wagtailcore_tags import richtext
from wagtail.models import TranslatableMixin, BootstrapTranslatableMixin, Locale
from rest_framework.fields import Field

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

    def get_sitemap_urls(self, request=None):
        """
        We need to manually add sitemap entries for routable pages.
        So here we append the important ones to the sitemap
        https://learnwagtail.com/courses/the-ultimate-wagtail-developers-course/sitemaps/

        Args:
            request (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        # get the existing sitemap
        sitemap = super().get_sitemap_urls(request)
        last_mod = NewsItem.objects.live().public().order_by('-last_published_at').first()
        sitemap.append({
            # even if the path changes it will be auto-updated because we're using the
            # named attribute 'all' to point to that url
            'location': self.get_full_url(request) + self.reverse_subpage('all'),
            'lastmod': last_mod.last_published_at or last_mod.latest_revision_created_at,
        })
        sitemap.append({
            'location': self.get_full_url(request) + self.reverse_subpage('tag', args=['refs']),
        })

        return sitemap

    # /news/tag/{tag_name}>
    @path("tag/<str:tag>/", name="tag")
    @path("tags/<str:tag>/", name="tags")
    def news_items_by_tag(self, request, tag=None):
        """
        A route to display news articles by tag.
        """
        # context = super().get_context(request)
        current_locale = Locale.get_active()
        tagged_news = NewsItem.objects.live().public().filter(locale=current_locale, tags__name=tag).order_by('-first_published_at')

        paginated_items, paginator = self._get_pagination_context(
            request,
            tagged_news,
            limit=2
        )

        return self.render(
            request,
            context_overrides={
                "tag": tag,
                "news_items": paginated_items,
                "paginator": paginator,
            },
            template="news/news_tag.html",
        )

    # /news/api/2025
    @re_path(r"^api/(\d+)/$", name="api")
    def api_news_items(self, request, year):
        """
        A route to display JSON response of news articles for a given year.

        This is not a good practice for building APIs in Wagtail/Django,
        but is included here for demonstration purposes.
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
        Add the list of news articles to the context with pagination.
        """
        current_locale = Locale.get_active()
        all_news = NewsItem.objects.live().public().filter(locale=current_locale).order_by('-first_published_at')

        paginated_items, paginator = self._get_pagination_context(
            request,
            all_news,
            limit=7
        )

        context = super().get_context(request)
        context['news_items'] = paginated_items
        context['paginator'] = paginator

        return context

    def _get_pagination_context(self, request, news_items, limit=20):
        """
        A helper method to get pagination context.
        """
        # Paginate with 20 items per page
        paginator = Paginator(news_items, limit)
        page_number = request.GET.get('page', 1)

        try:
            news_page = paginator.page(page_number)
        except PageNotAnInteger:
            news_page = paginator.page(1)
        except EmptyPage:
            news_page = paginator.page(paginator.num_pages)

        return news_page, paginator


class NewsItemTags(TaggedItemBase):
    """
    A model to manage tags for news items.
    """
    content_object = ParentalKey(
        'news.NewsItem',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


# -------
# Serializers for API fields
# -------

class ImageSerializer(Field):
    def to_representation(self, value):
        return {
            "original": {
                "id": value.id,
                "title": value.title,
                "url": value.file.url,
                "width": value.width,
                "height": value.height,
            },
            "thumbnail": {
                "id": value.get_rendition('max-165x165').id,
                "url": value.get_rendition('max-165x165').url,
                "width": value.get_rendition('max-165x165').width,
                "height": value.get_rendition('max-165x165').height,
            },
            "small": {
                "id": value.get_rendition('max-300x300').id,
                "url": value.get_rendition('max-300x300').url,
                "width": value.get_rendition('max-300x300').width,
                "height": value.get_rendition('max-300x300').height,
            },
            "medium": {
                "id": value.get_rendition('max-700x700').id,
                "url": value.get_rendition('max-700x700').url,
                "width": value.get_rendition('max-700x700').width,
                "height": value.get_rendition('max-700x700').height,
            },
        }


class RichTextSerializer(Field):
    """
    Serializer for RichTextField to convert to HTML for API output.
    """
    def to_representation(self, value):
        return richtext(value)


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
    image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    # TODO: limit to 175 characters so it fits on cards
    intro = RichTextField(blank=True)

    body = StreamField(
        [
            ("text", custom_blocks.RichTextBlock()),
            ("image", custom_blocks.ImageBlock()),
            ("doc", DocumentChooserBlock(
                # can set your own template here if you want
                # template="blocks/document_block.html",
                group="Standalone Blocks"
            )),
            ("page", custom_blocks.CustomPageChooserBlock(
                required=False,
                page_type=['news.NewsItem'],
                group="Standalone Blocks"
            )),
            ("hero", custom_blocks.HeroBlock()),
            ("recent_news", custom_blocks.RecentNewsBlock()),

        ],
        block_counts={
            "hero": {"max_num": 1},
        },
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('image'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    api_fields = [
        APIField("subtitle"),
        APIField("body"),
        APIField("tags"),
        APIField("image", serializer=ImageSerializer()),
        APIField("intro", serializer=RichTextSerializer()),
        APIField("custom_content"),
    ]

    def custom_content(self):
        """
        Custom content that can be serialized in the API.
        """
        return "custom content here"

    def clean(self):
        """
        Custom validation for the NewsItem model.

        Raises:
            ValidationError: If validation fails.
        """
        super().clean()

        errors = {}

        # can set any field errors and conditions in here
        if "news" in self.title.lower():
            errors["title"] = "Please don't use the word 'news' in the title."

        if errors:
            raise ValidationError(errors)

    def get_context(self, request):
        """
        Add recent news block data to the context.
        """
        context = super().get_context(request)

        # Create a RecentNewsBlock instance with desired config
        from blocks.blocks import RecentNewsBlock

        recent_news_block = RecentNewsBlock()

        # Prepare block value (field data)
        block_value = {
            'title': 'Other Recent News',
            'subtitle': '',
            'num_items': 5,
            'filter_by_tag': '',
        }

        # Render the block with current page ID for exclusion
        context['current_page_id'] = self.id
        rendered_block = recent_news_block.render(
            recent_news_block.to_python(block_value),
            context=context
        )

        context['recent_news_html'] = rendered_block
        return context
