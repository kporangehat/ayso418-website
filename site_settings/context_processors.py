from wagtail.models import Page, Locale, Site
from site_settings.models import Banner
from programs.models import Program


def navbar(request):
    """Context processor to add the navbar pages to the context.
    This will show all pages if the user is authenticated, otherwise
    it will show only the public pages.

    This function is called in the settings in the
    TEMPLATES['OPTIONS']['context_processors'] list.
    """
    # Get the current site based on the request
    current_site = Site.find_for_request(request)
    root_page = current_site.root_page
    # this is currently UNUSED but left here for future use
    if request.user.is_authenticated:
        # If the user is authenticated, show all pages
        root_nav = root_page.get_children().live().in_menu().filter(locale=Locale.get_active())
        program_nav = Program.objects.live().in_menu().filter(locale=Locale.get_active())
    else:
        root_nav = root_page.get_children().live().in_menu().public().filter(locale=Locale.get_active())
        program_nav = Program.objects.live().in_menu().public().filter(locale=Locale.get_active())

    return {
        "navbar_pages": root_nav,
        "program_pages": program_nav
    }


def active_banner(request):
    """Context processor to add the active banner to the context.

    Only returns live (published) banners that are marked as active.
    Users can dismiss banners which are tracked in session storage.

    This function is called in the settings in the
    TEMPLATES['OPTIONS']['context_processors'] list.
    """
    try:
        # Get the active banner that is also live (published)
        banner = Banner.objects.filter(
            is_active=True,
            live=True
        ).first()

        return {
            "active_banner": banner
        }
    except Exception:
        # If there's any error (e.g., table doesn't exist yet), return None
        return {
            "active_banner": None
        }
