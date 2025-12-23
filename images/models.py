from django.db import models
from wagtail.images.models import Image, AbstractImage, AbstractRendition

"""
Enables customization options for image handling.
CustomImage is set as the default image model (WAGTAILIMAGES_IMAGE_MODEL) in base.py
"""


class CustomImage(AbstractImage):
    caption = models.CharField(max_length=255, blank=True)
    admin_form_fields = Image.admin_form_fields + ('caption',)


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage,
        related_name='renditions',
        on_delete=models.CASCADE,
    )

    # Add any additional fields or methods you need for your custom rendition here

    class Meta:
        unique_together = ('image', 'filter_spec', "focal_point_key")

# Create your models here.
