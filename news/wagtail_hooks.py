# 1. import stuff
# 2. create a snippetviewset
# 3. add some settings for the snippetviewset
# 4. register the class as a snippet
from django.core.cache import cache

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail import hooks

from taggit.models import Tag
from news.models import Author


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


@register_snippet
class AuthorSnippet(SnippetViewSet):
    model = Author
    add_to_admin_menu = False



# https://docs.wagtail.org/en/stable/reference/hooks.html#hooks
@hooks.register("after_publish_page")
def delete_all_cache(request, page):
    """
    Delete all cache when a page is saved.
    """
    cache.clear()
