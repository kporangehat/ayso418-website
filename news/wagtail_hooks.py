# 1. import stuff
# 2. create a snippetviewset
# 3. add some settings for the snippetviewset
# 4. register the class as a snippet
from django.core.cache import cache
from django.contrib.auth.models import Permission
from django.utils.safestring import mark_safe

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail import hooks
from wagtail.admin.ui.components import Component
from wagtail.admin.site_summary import SummaryItem
from wagtail.models import Page

from taggit.models import Tag


@register_snippet
class TagSnippetViewSet(SnippetViewSet):
    model = Tag
    icon = "tag"
    add_to_admin_menu = True
    menu_label = "Tags"
    menu_order = 200
    list_display = ["name", "slug"]
    search_fields = ("name",)
    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]


# https://docs.wagtail.org/en/stable/reference/hooks.html#hooks
@hooks.register("after_publish_page")
def delete_all_cache(request, page):
    """
    Delete all cache when a page is saved.
    """
    cache.clear()


class WelcomePanel(Component):
    order = 10
    template_name = "panels/welcome_panel.html"

    def get_context_data(self, parent_context=None):
        context = super().get_context_data(parent_context)
        context["username"] = parent_context["request"].user.username

        return context

    class Media:
        css = {
            "all": ("css/welcome_panel.css",)
        }
        js = ("js/welcome_panel.js",)


@hooks.register("construct_homepage_panels")
def add_welcome_panel(request, panels):
    """
    Add a welcome panel to the homepage.
    """
    panels.append(WelcomePanel())


class NewSummaryItem(SummaryItem):
    order = 200
    template_name = "panels/new_summary_item.html"

    def get_context_data(self, request):
        context = super().get_context_data(request)
        context["news_item_count"] = 153
        return context


@hooks.register("construct_homepage_summary_items")
def add_new_summary_item(request, items):
    """
    Add a new summary item to the homepage.
    """
    items.append(
        NewSummaryItem(request)
    )
    items.append(
        UnpublishedPages(request)
    )


class UnpublishedPages(SummaryItem):
    order = 400
    template_name = "panels/unpublished_pages.html"

    def get_context_data(self, request):
        context = super().get_context_data(request)
        context["unpublished_pages"] = Page.objects.all().filter(live=False).count()
        return context
