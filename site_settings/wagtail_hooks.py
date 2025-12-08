from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from site_settings.models import FAQ, FAQCategory


@register_snippet
class FAQCategorySnippetViewSet(SnippetViewSet):
    model = FAQCategory
    icon = "tag"
    add_to_admin_menu = True
    menu_label = "FAQ Categories"
    menu_order = 299
    list_display = ["name", "order"]
    search_fields = ("name", "description")
    list_per_page = 50


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
