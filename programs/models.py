from django.db import models
from django.core.exceptions import ValidationError

from wagtail.models import Page, Locale
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model

from blocks import blocks as custom_blocks


class ProgramIndex(Page):
    """
    A page that lists all programs.
    """
    template = 'programs/program_index.html'
    max_count = 1  # only allow one index page.
    parent_page_types = ['home.HomePage']  # restrict parent page to HomePage
    subpage_types = ['programs.Program']  # restrict child pages to Programs

    subtitle = models.CharField(max_length=100, blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    def get_context(self, request):
        """
        Add the list of programs to the context.
        """
        context = super().get_context(request)
        current_locale = Locale.get_active()
        context['program_list'] = Program.objects.live().public().filter(locale=current_locale)
        return context


# Create your models here.
class Program(Page):
    """
    A page that displays specific information about a program.
    """
    template = 'programs/program_detail.html'
    parent_page_types = ['programs.ProgramIndex']   # restrict parent page to NewsIndex
    subpage_types = []  # restrict child pages to none

    # can always override the default template from base.py
    # https://docs.wagtail.org/en/stable/advanced_topics/privacy.html
    # password_required_template = "news/news_item_password_required.html"

    subtitle = models.CharField(max_length=200, blank=True)
    ages = models.CharField(max_length=200, blank=True)
    tryouts = RichTextField(blank=True)
    equipment = RichTextField(blank=True)
    schedule = RichTextField(blank=True)
    location = RichTextField(max_length=200, blank=True)
    registration = RichTextField(blank=True)

    # header image
    image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    logo = models.ForeignKey(
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

    def custom_content(self):
        """
        A custom method to return the body content.
        """
        return "custom content here"

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('image'),
        FieldPanel('logo'),
        FieldPanel('ages'),
        FieldPanel('tryouts'),
        FieldPanel('equipment'),
        FieldPanel('schedule'),
        FieldPanel('location'),
        FieldPanel('registration'),
        FieldPanel('body'),
    ]

    def clean(self):
        super().clean()
        errors = {}
        # can set any field errors and conditions in here
        # if "foo" in self.title.lower():
        #     errors["title"] = "Please don't use the word 'foo' in the title."

        if errors:
            raise ValidationError(errors)
