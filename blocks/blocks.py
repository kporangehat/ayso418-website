from django.core.exceptions import ValidationError

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock


class TextBlock(blocks.TextBlock):
    """
    A block that displays a text section.
    """
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            help_text="This is from TextBlock. Help text here.",
            min_length=10,
            max_length=500,
        )

    def clean(self, value):
        """
        Custom validation to ensure the text is not empty.
        """
        value = super().clean(value)
        if "fire" in value.lower():
            raise ValidationError("The word 'fire' is not allowed.")

        return value

    class Meta:
        template = "blocks/text_block.html"
        icon = "pilcrow"
        group = "Standalone Blocks"


class RichTextBlock(blocks.RichTextBlock):
    """
    A block that displays a rich text section.
    """
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            help_text="This is from RichTextBlock. Help text here.",
            min_length=10,
        )

    def clean(self, value):
        """
        Custom validation to ensure the text is not empty.
        """
        value = super().clean(value)
        return value

    class Meta:
        template = "blocks/rich_text_block.html"
        icon = "pilcrow"
        group = "Standalone Blocks"


class SixPhilosophiesBlock(blocks.StaticBlock):
    """
    A block that displays a static block showing the six philosophies.
    """
    class Meta:
        template = "blocks/six_philosophies_block.html"
        icon = "info-circle"
        admin_text = "AYSO six philosophies"
        label = "AYSO 6 philosophies"
        group = "Standalone Blocks"


class CallToActionBlock(blocks.StructBlock):
    """
    A block that displays a call to action section with optional image.
    """
    text = blocks.RichTextBlock(
        features=['bold', 'italic'],
        required=True,
        help_text="The main CTA text content"
    )
    page = blocks.PageChooserBlock(
        required=False,
        help_text="Page for the button to link to"
    )
    button_text = blocks.CharBlock(
        max_length=100,
        required=False,
        help_text="Button text (defaults to page title if empty)"
    )
    target_url = blocks.PageChooserBlock(
        required=False,
        help_text="Optional: Make the entire CTA clickable by selecting a target page"
    )
    image = ImageChooserBlock(
        required=False,
        help_text="Optional image for the CTA"
    )
    image_layout = blocks.ChoiceBlock(
        choices=[
            ('background', 'Background - Image fills entire CTA as background'),
            ('left', 'Left - Image on left, text on right'),
            ('right', 'Right - Image on right, text on left'),
        ],
        default='background',
        required=False,
        help_text="How to display the image"
    )
    image_style = blocks.ChoiceBlock(
        choices=[
            ('fill', 'Fill - Image fills entire section'),
            ('framed', 'Framed - Image with rounded edges and padding'),
        ],
        default='fill',
        required=False,
        help_text="Style for left/right images (not used for background)"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['button_label'] = value.get('button_text') or (value.get('page').title if value.get('page') else 'Learn More')
        context['has_target_url'] = bool(value.get('target_url'))
        context['is_background'] = value.get('image_layout') == 'background'
        context['is_left'] = value.get('image_layout') == 'left'
        context['is_right'] = value.get('image_layout') == 'right'
        context['is_framed'] = value.get('image_style') == 'framed'
        return context

    class Meta:
        template = "blocks/call_to_action_1.html"
        icon = "expand-right"


class CTATextBlock(blocks.StructBlock):
    """
    A block that displays a CTA section.
    """
    headline = blocks.CharBlock(
        max_length=200,
        required=True,
    )
    text = blocks.RichTextBlock(
        features=['bold', 'italic'],
        required=True,
    )
    page = blocks.PageChooserBlock()
    button_text = blocks.CharBlock(
        max_length=100,
        required=False,
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context['button_label'] = value.get('button_text') or value.get('page').title
        return context

    class Meta:
        template = "blocks/cta_text_block.html"
        icon = "expand-right"


class ImageBlock(ImageChooserBlock):
    """
    A block that displays an image.
    """
    def get_api_representation(self, value, context=None):
        return {
            "id": value.id,
            "title": value.title,
            "src": value.file.url,
            "width": value.width,
            "height": value.height,
        }

    def get_context(self, value, parent_context=None):
        from news.models import NewsItem
        context = super().get_context(value, parent_context=parent_context)
        context["news_items"] = NewsItem.objects.all().live().public()
        return context

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"
        group = "Standalone Blocks"


class RecentNewsBlock(blocks.StructBlock):
    """
    A block that displays recent news items with optional tag filtering.
    """
    title = blocks.CharBlock(
        max_length=100,
        required=True,
        help_text="Main heading for this news section"
    )
    subtitle = blocks.TextBlock(
        max_length=200,
        required=False,
        help_text="Optional description text"
    )
    num_items = blocks.IntegerBlock(
        default=3,
        min_value=1,
        max_value=10,
        required=True,
        help_text="Number of recent news items to display"
    )
    filter_by_tag = blocks.CharBlock(
        max_length=50,
        required=False,
        help_text="Optional: filter news items by tag (leave blank to show all)"
    )

    def get_context(self, value, parent_context=None):
        from news.models import NewsItem
        from wagtail.models import Locale

        context = super().get_context(value, parent_context=parent_context)

        # Get the current locale if in a request context
        try:
            current_locale = Locale.get_active()
        except (AttributeError, RuntimeError):
            current_locale = None

        # Start with base queryset
        news_items = NewsItem.objects.live().public()

        # Filter by locale if available
        if current_locale:
            news_items = news_items.filter(locale=current_locale)

        # Exclude current page if specified in parent context
        current_page_id = parent_context.get('current_page_id') if parent_context else None
        if current_page_id:
            news_items = news_items.exclude(id=current_page_id)

        # Filter by tag if specified
        tag = value.get('filter_by_tag', '').strip()
        if tag:
            news_items = news_items.filter(tags__name=tag)

        # Order by most recent and limit to requested number
        num_items = value.get('num_items', 3)
        news_items = news_items.order_by('-first_published_at')[:num_items]

        context['news_items'] = news_items
        context['tag'] = tag

        return context

    class Meta:
        # template = "blocks/recent_news_block.html"
        template = "blocks/recent_news_carousel.html"
        icon = "doc-full-inverse"
        label = "Recent News"
        group = "Standalone Blocks"


class ProgramsBlock(blocks.StructBlock):
    """
    A block that displays all available programs.
    """
    title = blocks.CharBlock(
        max_length=100,
        required=True,
        default="Our Programs",
        help_text="Main heading for this programs section"
    )
    subtitle = blocks.TextBlock(
        max_length=200,
        required=False,
        help_text="Optional description text"
    )

    def get_context(self, value, parent_context=None):
        from programs.models import Program
        from wagtail.models import Locale

        context = super().get_context(value, parent_context=parent_context)

        # Get the current locale if in a request context
        try:
            current_locale = Locale.get_active()
        except (AttributeError, RuntimeError):
            current_locale = None

        # Get all live, published programs
        programs = Program.objects.live().public()

        # Filter by locale if available
        if current_locale:
            programs = programs.filter(locale=current_locale)

        context['programs'] = programs

        return context

    class Meta:
        template = "blocks/programs_block.html"
        icon = "list-ul"
        label = "Programs List"
        group = "Standalone Blocks"


class CustomPageChooserBlock(blocks.PageChooserBlock):
    """
    A block that displays a page chooser.
    """
    def get_api_representation(self, value, context=None):
        return {
            "id": value.id,
            "title": value.title,
            "subtitle": value.specific.subtitle,
            "url": value.url,
        }


class FAQBlock(blocks.StructBlock):
    """
    A block that displays FAQ items with optional tag filtering.

    This works with FAQ snippets defined in site_settings/models.py.
    """
    title = blocks.CharBlock(
        max_length=100,
        required=True,
        default="Frequently Asked Questions",
        help_text="Main heading for this FAQ section"
    )
    subtitle = blocks.TextBlock(
        max_length=200,
        required=False,
        help_text="Optional description text"
    )
    filter_by_tag = blocks.CharBlock(
        max_length=50,
        required=False,
        help_text="Optional: filter FAQs by tag (leave blank to show all)"
    )
    filter_by_category = blocks.CharBlock(
        max_length=100,
        required=False,
        help_text="Optional: filter FAQs by category (leave blank to show all)"
    )
    num_items = blocks.IntegerBlock(
        default=0,
        min_value=0,
        max_value=50,
        required=True,
        help_text="Number of FAQs to display (0 = show all matching items)"
    )
    show_categories = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Display category labels for each FAQ"
    )

    def get_context(self, value, parent_context=None):
        from site_settings.models import FAQ

        context = super().get_context(value, parent_context=parent_context)

        # Start with base queryset - only published FAQs
        faqs = FAQ.objects.filter(live=True).select_related('category')

        # Filter by tag if specified
        tag = value.get('filter_by_tag', '').strip()
        if tag:
            faqs = faqs.filter(tags__name=tag)

        # Filter by category if specified
        category = value.get('filter_by_category', '').strip()
        if category:
            # Filter by category name (case-insensitive)
            faqs = faqs.filter(category__name__iexact=category)

        # Order by category and order field
        faqs = faqs.order_by('category__order', 'category__name', 'order', 'question')

        # Limit to requested number (0 means all)
        num_items = value.get('num_items', 0)
        if num_items > 0:
            faqs = faqs[:num_items]

        context['faqs'] = faqs
        context['tag'] = tag
        context['category'] = category
        context['show_categories'] = value.get('show_categories', True)

        return context

    class Meta:
        template = "blocks/faq_block.html"
        icon = "help"
        label = "FAQ List"
        group = "Standalone Blocks"


class ResourcesNavigationBlock(blocks.StaticBlock):
    """
    A block that displays navigation for the Resources section.
    Shows all categories and pages within the current page's category.
    """

    def get_context(self, value, parent_context=None):
        from flexpage.models import FlexPage, ResourcesIndex

        context = super().get_context(value, parent_context=parent_context)

        # Get the current page from parent context
        current_page = parent_context.get('page') if parent_context else None

        if current_page:
            # Find the ResourcesIndex page (parent of all resource pages)
            resources_index = None
            if isinstance(current_page, ResourcesIndex):
                resources_index = current_page
            else:
                # Get the parent ResourcesIndex
                resources_index = current_page.get_ancestors().type(ResourcesIndex).first()

            if resources_index:
                # Get the parent category page (direct child of ResourcesIndex)
                category_page = None

                # If current page is a direct child of ResourcesIndex, it's a category page
                if current_page.get_parent() == resources_index:
                    category_page = current_page
                else:
                    # Otherwise, find the category page (ancestor that's a direct child of ResourcesIndex)
                    for ancestor in current_page.get_ancestors():
                        if ancestor.get_parent() == resources_index:
                            category_page = ancestor.specific
                            break

                # Get all sibling pages (children of the same category page)
                sibling_pages = []
                if category_page:
                    sibling_pages = category_page.get_children().live().specific().order_by('title')

                context['resources_index'] = resources_index
                context['category_page'] = category_page
                context['sibling_pages'] = sibling_pages
                context['current_page'] = current_page

        return context

    class Meta:
        template = "blocks/resources_navigation_block.html"
        icon = "list-ul"
        label = "Resources Navigation"
        admin_text = "Displays Resources section navigation with categories and pages"
        group = "Standalone Blocks"


class LayoutSectionBlock(blocks.StructBlock):
    """
    A flexible layout block that allows choosing between full-width or content-with-sidebar layouts.
    Supports multiple sections per page with different layouts.
    """
    layout = blocks.ChoiceBlock(
        choices=[
            ('full_width', 'Full Width'),
            ('sidebar', 'Content with Right Sidebar'),
        ],
        default='full_width',
        required=True,
        help_text="Choose the layout for this section"
    )

    content = blocks.StreamBlock(
        [
            ('six', SixPhilosophiesBlock()),
            ('text', TextBlock()),
            ('richtext', RichTextBlock()),
            ('image', ImageBlock()),
            ('call_to_action_1', CallToActionBlock()),
            ('faq', FAQBlock()),
            ('table', TableBlock(
                # template="includes/table.html",
                help_text="Right click on table to access more options",
            )),
            ('recent_news', RecentNewsBlock()),
            ('programs', ProgramsBlock()),
        ],
        required=False,
        help_text="Main content for this section"
    )

    sidebar = blocks.StreamBlock(
        [
            ('text', TextBlock()),
            ('richtext', RichTextBlock()),
            ('image', ImageBlock()),
            ('call_to_action_1', CallToActionBlock()),
            ('recent_news', RecentNewsBlock()),
        ],
        required=False,
        help_text="Sidebar content (only shown when layout is 'Content with Right Sidebar')"
    )

    show_resources_nav = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Show Resources Navigation in the sidebar (only applies when layout is 'Content with Right Sidebar')"
    )

    class Meta:
        template = "blocks/layout_section_block.html"
        icon = "desktop"
        label = "Layout Section"
        group = "Layout"
