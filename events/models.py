from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from modelcluster.models import ClusterableModel

from wagtail.models import Page, DraftStateMixin, RevisionMixin, LockableMixin, PreviewableMixin
from wagtail.search import index
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PublishingPanel
from wagtail.fields import StreamField
from wagtail.contrib.routable_page.models import RoutablePageMixin, path

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


class EventsPage(RoutablePageMixin, Page):
    max_count = 1
    subpage_types = []

    subtitle = models.CharField(max_length=200, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
    ]
    template = "events/events_page.html"

    def _get_events(self, event_type=None):
        events = Event.objects.filter(
            live=True,
            end_date__gte=timezone.now().date(),
        ).select_related('program')
        if event_type:
            events = events.filter(event_type=event_type)
        return events.order_by('start_date')

    def _get_event_types_in_use(self):
        """Get event types that have at least one upcoming published event."""
        type_values = (
            Event.objects.filter(live=True, end_date__gte=timezone.now().date())
            .values_list('event_type', flat=True)
            .distinct()
        )
        type_map = dict(Event.EVENT_TYPE_CHOICES)
        return [(val, type_map[val]) for val in type_values if val in type_map]

    def get_context(self, request):
        context = super().get_context(request)
        context['events'] = self._get_events()
        context['event_types'] = self._get_event_types_in_use()
        context['active_type'] = None
        return context

    @path("type/<str:event_type>/", name="type")
    def events_by_type(self, request, event_type=None):
        type_map = dict(Event.EVENT_TYPE_CHOICES)
        return self.render(
            request,
            context_overrides={
                'events': self._get_events(event_type=event_type),
                'event_types': self._get_event_types_in_use(),
                'active_type': event_type,
                'active_type_label': type_map.get(event_type, event_type),
            },
        )
