from wagtail.models import Page, Locale


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
            "navbar_pages": Page.objects.all().in_menu().filter(locale=Locale.get_active())
        }
    else:
        return {
            "navbar_pages": Page.objects.live().in_menu().public().filter(locale=Locale.get_active())
        }
