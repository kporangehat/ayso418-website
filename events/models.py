from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from modelcluster.models import ClusterableModel

from wagtail.models import DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin
from wagtail.search import index
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PublishingPanel
from wagtail.fields import StreamField

from blocks import blocks as custom_blocks


class Event(
    PreviewableMixin,
    LockableMixin,
    DraftStateMixin,
    RevisionMixin,
    index.Indexed,
    ClusterableModel,
):
    EVENT_TYPE_CHOICES = [
        ("registration", "Registration"),
        ("referee_training", "Referee Training"),
        ("coach_certification", "Coach Certification"),
        ("training_camp", "Training Camp"),
        ("special_event", "Special Event"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("waitlist", "Waitlist"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=255, help_text="The event title")
    subtitle = models.CharField(
        max_length=255, blank=True, help_text="Optional subtitle or tagline"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default="other",
        help_text="Type of event",
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        help_text="Optional: associate this event with a specific program",
    )
    start_date = models.DateField(help_text="Start date of the event")
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Optional end date (leave blank for single-day events)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current status of the event",
    )
    body = StreamField(
        [
            ("text", custom_blocks.RichTextBlock()),
            ("image", custom_blocks.ImageBlock()),
            ("call_to_action_1", custom_blocks.CallToActionBlock()),
        ],
        blank=True,
        null=True,
    )
    link = models.URLField(
        blank=True, help_text="External link (e.g., registration portal URL)"
    )

    revisions = GenericRelation(
        "wagtailcore.Revision", related_query_name="event"
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("subtitle"),
                FieldPanel("event_type"),
                FieldPanel("program"),
            ],
            heading="Event Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("status"),
            ],
            heading="Scheduling",
        ),
        FieldPanel("body"),
        FieldPanel("link"),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("title", boost=10),
        index.SearchField("subtitle"),
        index.FilterField("event_type"),
        index.FilterField("status"),
        index.FilterField("start_date"),
    ]

    def __str__(self):
        return self.title

    def get_preview_template(self, request, mode_name):
        return "includes/event_preview.html"

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["start_date", "title"]
