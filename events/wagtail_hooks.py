from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from events.models import Event


@register_snippet
class EventSnippetViewSet(SnippetViewSet):
    model = Event
    icon = "date"
    add_to_admin_menu = True
    menu_label = "Events"
    menu_order = 250
    list_display = ["title", "event_type", "start_date", "status"]
    list_filter = ["event_type", "status", "program"]
    search_fields = ("title", "subtitle")
    list_per_page = 50
