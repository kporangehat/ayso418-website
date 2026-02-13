from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path

from taggit.models import Tag

from site_settings.models import FAQ


class FAQPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ['flexpage.ResourcesIndex']
    subpage_types = []

    subtitle = models.CharField(max_length=200, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
    ]

    def _get_all_tags(self):
        """Get all tags that are used by at least one published FAQ."""
        return (
            Tag.objects
            .filter(site_settings_faqtags_items__content_object__live=True)
            .distinct()
            .order_by('name')
        )

    def _get_faqs(self, tag=None):
        """Get published FAQs, optionally filtered by tag."""
        faqs = FAQ.objects.filter(live=True).select_related('category')
        if tag:
            faqs = faqs.filter(tags__name=tag)
        return faqs.order_by('category__order', 'category__name', 'order', 'question')

    def get_context(self, request):
        context = super().get_context(request)
        context['faqs'] = self._get_faqs()
        context['all_tags'] = self._get_all_tags()
        context['active_tag'] = None
        return context

    @path("tag/<str:tag>/", name="tag")
    def faqs_by_tag(self, request, tag=None):
        return self.render(
            request,
            context_overrides={
                'faqs': self._get_faqs(tag=tag),
                'all_tags': self._get_all_tags(),
                'active_tag': tag,
            },
        )
