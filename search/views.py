from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.models import Locale, Page
from wagtail.search.utils import parse_query_string

# To enable logging of search queries for use with the "Promoted search results" module
# <https://docs.wagtail.org/en/stable/reference/contrib/searchpromotions.html>
# uncomment the following line and the lines indicated in the search function
# (after adding wagtail.contrib.search_promotions to INSTALLED_APPS):

from wagtail.contrib.search_promotions.models import Query


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        # parse query
        filters, query_str = parse_query_string(search_query)

        current_locale = Locale.get_active()

        # start with all live pages
        pages = Page.objects.live().filter(locale=current_locale)

        # if adding filter support, do it here
        # # Published filter
        # # An example filter that accepts either `published:yes` or `published:no` and filters the pages accordingly
        # published_filter = filters.get('published')
        # published_filter = published_filter and published_filter.lower()
        # if published_filter in ['yes', 'true']:
        #     pages = pages.filter(live=True)
        # elif published_filter in ['no', 'false']:
        #     pages = pages.filter(live=False)

        search_results = pages.search(query_str, operator="or")
        # To log this query for use with the "Promoted search results" module:
        query = Query.get(search_query)
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
