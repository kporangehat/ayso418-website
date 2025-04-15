from django.db import models
from django.core.exceptions import ValidationError

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.blocks import PageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from blocks import blocks as custom_blocks


# Create your models here.
class NewsIndex(Page):
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

    def get_context(self, request):
        """
        Add the list of news articles to the context.
        """
        context = super().get_context(request)
        context['newsitems'] = NewsItem.objects.live().public()
        # context['news_items'] = self.get_children().live().public()
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



class Author(models.Model):
    """
    A model to represent an author.
    """
    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name


class NewsItem(Page):
    """
    A page that displays a specific new article.
    """
    parent_page_types = ['news.NewsIndex']   # restrict parent page to NewsIndex
    subpage_types = []  # restrict child pages to none

    subtitle = models.CharField(max_length=100, blank=True)
    tags = ClusterTaggableManager(through=NewsItemTags, blank=True)

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
        FieldPanel('subtitle'),
        FieldPanel('body'),
        FieldPanel('tags'),
    ]

    def clean(self):
        super().clean()

        errors = {}

        # can set any field errors and conditions in here
        if "news" in self.title.lower():
            errors["title"] = "Please don't use the word 'news' in the title."

        if errors:
            raise ValidationError(errors)
