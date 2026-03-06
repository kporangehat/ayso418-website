from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, PublishingPanel

from cta.models import CTA


@register_snippet
class CTASnippetViewSet(SnippetViewSet):
    model = CTA
    icon = "expand-right"
    add_to_admin_menu = True
    menu_label = "CTAs"
    menu_order = 295
    list_display = ["title", "heading", "layout", "background"]
    list_filter = ["layout", "background"]
    search_fields = ("title", "heading", "text")
    list_per_page = 50

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
            ],
            heading="Internal",
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading"),
                FieldPanel("text"),
            ],
            heading="Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("layout"),
                FieldPanel("background"),
            ],
            heading="Layout & Appearance",
        ),
        MultiFieldPanel(
            [
                FieldPanel("button_text"),
                FieldPanel("button_page"),
                FieldPanel("button_url"),
            ],
            heading="Button (optional)",
        ),
        PublishingPanel(),
    ]
