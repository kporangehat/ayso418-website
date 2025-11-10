from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from site_settings.models import FAQ


@register_snippet
class FAQSnippetViewSet(SnippetViewSet):
    model = FAQ
    icon = "help"
    add_to_admin_menu = True
    menu_label = "FAQs"
    menu_order = 300
    list_display = ["question", "category", "order"]
    list_filter = ["category"]
    search_fields = ("question", "answer")
    list_per_page = 50
