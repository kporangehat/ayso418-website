from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase

from wagtail.contrib.settings.models import register_setting, BaseGenericSetting, BaseSiteSetting
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin
from wagtail.search import index


@register_setting
class GenericFooterText(BaseGenericSetting):
    """Generic footer text model.

    Base generic setting for EVERY website we have.
    """

    text = models.TextField("Footer Text", blank=True)
    privacy_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )

    panels = [
        FieldPanel("text"),
        FieldPanel("privacy_page"),
    ]

    class Meta:
        verbose_name = "Generic Footer Text"


@register_setting
class SocialMediaLinks(BaseSiteSetting):
    """Social media links model.

    Base site setting for EVERY website we have.
    """

    facebook = models.URLField("Facebook", blank=True)
    twitter = models.URLField("Twitter", blank=True)
    instagram = models.URLField("Instagram", blank=True)

    panels = [
        FieldPanel("facebook"),
        FieldPanel("twitter"),
        FieldPanel("instagram"),
    ]

    def clean(self):
        """
        Clean the URL fields to ensure they are valid URLs.
        and they link to the correct site
        """
        super().clean()
        for field in ["facebook", "twitter", "instagram"]:
            url = getattr(self, field)
            if url and f"{field}.com" not in url:
                raise ValidationError(
                    f"{field.capitalize()} URL must contain '{field}.com'."
                )

    class Meta:
        verbose_name = "Social Media Links"


class FAQCategory(models.Model):
    """
    A model to manage FAQ categories.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Registration', 'Programs', 'General')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of this category"
    )
    order = models.IntegerField(
        default=0,
        help_text="Order of display (lower numbers appear first)"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
        FieldPanel('order'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"
        ordering = ['order', 'name']


class FAQTags(TaggedItemBase):
    """
    A model to manage tags for FAQ items.
    """
    content_object = ParentalKey(
        'site_settings.FAQ',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class FAQ(
    PreviewableMixin,
    LockableMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    ClusterableModel
):
    """
    A snippet model for Frequently Asked Questions.
    """
    question = models.CharField(max_length=255, help_text="The FAQ question")
    answer = RichTextField(help_text="The answer to the question")
    category = models.ForeignKey(
        'site_settings.FAQCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faqs',
        help_text="Optional category for grouping FAQs"
    )
    tags = ClusterTaggableManager(through=FAQTags, blank=True)
    revisions = GenericRelation('wagtailcore.Revision', related_query_name="faq")

    # Order FAQs by category and question
    order = models.IntegerField(
        default=0,
        help_text="Order of display within category (lower numbers appear first)"
    )

    panels = [
        FieldPanel('question'),
        FieldPanel('answer'),
        FieldPanel('category', widget=None),  # Uses autocomplete widget by default
        FieldPanel('tags'),
        FieldPanel('order'),
    ]

    search_fields = [
        index.SearchField('question', boost=10),
        index.SearchField('answer'),
        index.FilterField('category'),
    ]

    def __str__(self):
        return self.question

    def get_preview_template(self, request, mode_name):
        return "includes/faq_preview.html"

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['category', 'order', 'question']