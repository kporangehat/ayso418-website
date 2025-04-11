from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


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


class NewsItem(Page):
    """
    A page that displays a specific new article.
    """
    parent_page_types = ['news.NewsIndex']   # restrict parent page to NewsIndex
    subpage_types = []  # restrict child pages to none


    subtitle = models.CharField(max_length=100, blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]
