from wagtail.models import Page


def navbar(request):
    """Context processor to add the navbar pages to the context.
    This will show all pages if the user is authenticated, otherwise
    it will show only the public pages.
    """
    # This function is called in the settings.py file in the TEMPLATES
    # context_processors list.
    if request.user.is_authenticated:
        # If the user is authenticated, show all pages
        return {
            "navbar_pages": Page.objects.all().in_menu(),
        }
    else:
        return {
            "navbar_pages": Page.objects.live().in_menu().public(),
        }
