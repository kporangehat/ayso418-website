from django.db import models

from wagtail.documents.models import Document, AbstractDocument


# Create your models here.
class CustomDocument(AbstractDocument):
    """
    Custom document model that extends Wagtail's AbstractDocument.
    You can add additional fields or methods here if needed.
    """

    # Add any custom fields or methods here
    # For example, you can add a description field:
    description = models.CharField(blank=True, max_length=255)

    admin_form_fields = Document.admin_form_fields + ('description',)