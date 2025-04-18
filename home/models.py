from django.db import models
from django.core.exceptions import ValidationError

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel, FieldRowPanel, HelpPanel, MultipleChooserPanel, TitleFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model
from wagtail.documents import get_document_model

from modelcluster.fields import ParentalKey


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

    subtitle = models.CharField(max_length=255, blank=True, null=True)
    body = RichTextField(blank=True)

    image = models.ForeignKey(
        get_image_model(),  # will determine this is 'wagtailimages.CustomImage'
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',  # + means no reverse relation required
    )

    custom_document = models.ForeignKey(
        get_document_model(),  # will determine this is soemthing like 'wagtaildocs.CustomDocument'
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    cta_url = models.ForeignKey(
        'wagtailcore.Page',  # can limit this to specific page types
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    cta_external_url = models.URLField(
        blank=True,
        null=True,
    )

    # admin panels for the fields
    content_panels = Page.content_panels + [
        FieldPanel(
            "subtitle",
            help_text="Subtitle for the home page",
        ),

        PageChooserPanel(
            'cta_url',
            page_type=['news.NewsItem'],  # can limit this to specific page types
            help_text="Select a news itemm for the call to action button",
            heading="Call to Action - News Item",
        ),

        # CAN'T HAVE BOTH InlinePanel and MultipleChooserPanel named gallery_images
        # so we comment one out before deploying
        # InlinePanel(
        #     'gallery_images',
        #     label="Gallery Images",
        #     min_num=2,
        #     max_num=5,
        # ),

        MultipleChooserPanel(
            'gallery_images',
            label="Gallery Images",
            min_num=2,
            max_num=5,
            chooser_field_name='image',
            icon="image",
        ),

        # MultiFieldPanel(
        #     [
        #         HelpPanel(
        #             content="<strong>Help Panel</strong><p>Help text goes here",
        #             heading="Note:"
        #         ),
        #         FieldRowPanel(
        #             [
        #                 PageChooserPanel(
        #                     'cta_url',
        #                     page_type=['news.NewsItem'],  # can limit this to specific page types
        #                     help_text="Select a news item for the call to action button",
        #                     heading="News Item Selection",
        #                     classname="col6",
        #                 ),
        #                 FieldPanel(
        #                     'cta_external_url',
        #                     help_text="Enter an external URL for the call to action button",
        #                     heading="External URL",
        #                     classname="col6",
        #                 ),
        #             ],
        #             help_text="Select a news item or enter an external URL",
        #             heading="Call to Action URLs",
        #         ),
        #     ],
        #     heading="MultiField Panel",
        #     help_text="Random help text",
        #     classname="collapsed",
        # ),

        FieldPanel('body'),
    ]

    @property
    def get_cta_url(self):
        """
        Returns the URL for the call to action button.
        If both internal and external URLs are set, it will return the internal URL.
        """
        if self.cta_url:
            return self.cta_url.url
        elif self.cta_external_url:
            return self.cta_external_url
        return None

    def clean(self):
        super().clean()

        errors = {}

        # can set any field errors and conditions in here
        if self.cta_url and self.cta_external_url:
            errors["cta_url"] = "You cannot set both internal and an external URL."
            errors["cta_external_url"] = "You cannot set both internal and an external URL."

        if errors:
            raise ValidationError(errors)
