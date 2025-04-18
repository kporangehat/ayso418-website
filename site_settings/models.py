from django.db import models
from django.core.exceptions import ValidationError

from wagtail.contrib.settings.models import register_setting, BaseGenericSetting, BaseSiteSetting
from wagtail.admin.panels import FieldPanel


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