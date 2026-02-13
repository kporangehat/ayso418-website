from django import template

register = template.Library()


@register.simple_tag
def get_section_nav(page):
    """
    Walk up the page tree to find the section root, category page, and sibling pages.

    Works for any section of the site (Resources, About Us, etc.) — not tied
    to a specific page type.

    Usage:
        {% load section_nav_tags %}
        {% get_section_nav page as section_nav %}
        {{ section_nav.section_index.title }}
        {{ section_nav.category_page.title }}
        {% for p in section_nav.sibling_pages %}...{% endfor %}
    """
    try:
        site_root = page.get_site().root_page
    except Exception:
        return {}

    ancestors = list(page.get_ancestors().specific())

    # Find the section root (direct child of site root among ancestors)
    section_index = None
    for ancestor in ancestors:
        parent = ancestor.get_parent()
        if parent and parent.id == site_root.id:
            section_index = ancestor
            break

    if not section_index:
        return {}

    # Determine the category page (direct child of section_index)
    category_page = None
    if page.get_parent().id == section_index.id:
        # This page IS a category page
        category_page = page
    else:
        # Find the ancestor that's a direct child of section_index
        for ancestor in ancestors:
            parent = ancestor.get_parent()
            if parent and parent.id == section_index.id:
                category_page = ancestor
                break

    sibling_pages = []
    if category_page:
        sibling_pages = category_page.get_children().live().specific().order_by('title')

    return {
        'section_index': section_index,
        'category_page': category_page,
        'sibling_pages': sibling_pages,
        'current_page': page,
    }
