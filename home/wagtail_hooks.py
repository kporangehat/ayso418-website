from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, PublishingPanel

from home.models import CTA


class CTASnippetViewSet(SnippetViewSet):
    model = CTA
    icon = "placeholder"
    add_to_admin_menu = True
    menu_label = "Call to Actions"
    menu_order = 300
    list_display = ["title", "button_text", "button_url"]
    search_fields = ("title", "text", "button_text", "button_url")
    template = "home/cta2.html"

    panels = [
        FieldPanel("title"),
        FieldPanel("text"),
        FieldPanel("button_text"),
        FieldPanel("button_url"),
        FieldPanel("target_url"),
        FieldPanel("image"),
        FieldPanel("image_layout"),
        FieldPanel("image_style"),
        PublishingPanel(),
    ]

register_snippet(CTASnippetViewSet)
