from django.core.exceptions import ValidationError

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


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
    A block that displays a static divider.
    """
    class Meta:
        template = "blocks/six_philosophies_block.html"
        icon = "info-circle"
        admin_text = "AYSO six philosophies"
        label = "AYSO 6 philosophies"
        group = "Standalone Blocks"


class InfoBlock(blocks.StaticBlock):
    class Meta:
        template = "blocks/info_block.html"
        icon = "info-circle"
        admin_text = "This is from InfoBlock"
        label = "General Information"
        group = "Standalone Blocks"


class FaqBlock(blocks.StructBlock):
    """
    A block that displays a FAQ section.
    """
    question = blocks.CharBlock()
    answer = blocks.RichTextBlock(
        features=['bold', 'italic']
    )

    def clean(self, value):
        """
        Custom validation to ensure the question is not empty.
        """
        cleaned_data = super().clean(value)
        if "fire" in str(cleaned_data['answer']).lower():
            raise blocks.StructBlockValidationError(
                block_errors={
                    "answer": ValidationError("The word 'fire' is not allowed in the FAQ.")
                }
            )
        return cleaned_data


class FaqListBlock(blocks.ListBlock):
    """
    A block that displays a list of FAQ sections.
    """
    def __init__(self, **kwargs):
        super().__init__(FaqBlock(), **kwargs)

    def clean(self, value):
        """
        Custom validation to ensure the list of FAQs is not empty.
        """
        cleaned_data = super().clean(value)
        errors = {}

        for index, obj in enumerate(cleaned_data):
            if "fire" in str(obj["answer"]).lower():
                errors[index] = ValidationError("The word 'fire' is not allowed in the FAQ.")

        if errors:
            raise blocks.ListBlockValidationError(block_errors=errors)
        return cleaned_data

    class Meta:
        template = "blocks/faq_list_block.html"
        icon = "help"
        min_num = 1
        max_num = 5
        label = "FAQs"
        group = "Iterables"


class CarouselBlock(blocks.StreamBlock):
    """
    A block that displays a carousel of images.
    """
    image = ImageChooserBlock()
    quotation = blocks.StructBlock(
        [
            ("text", blocks.TextBlock()),
            ("author", blocks.TextBlock()),
        ]
    )

    def clean(self, value):
        """
        Custom validation to ensure the carousel has at least one image.
        """
        value = super().clean(value)
        images = [item for item in value if item.block_type == "image"]
        quotations = [item for item in value if item.block_type == "quotation"]

        if not images or not quotations:
            raise ValidationError("At least one image and one quotation are required.")

        if len(images) != len(quotations):
            raise ValidationError("The number of images and quotations must match.")

        return value

    class Meta:
        template = "blocks/carousel_block.html"
        icon = "rotate"
        group = "Iterables"


class CallToActionBlock(blocks.StructBlock):
    """
    A block that displays a call to action section.
    """
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
        template = "blocks/call_to_action_1.html"
        icon = "expand-right"


class HeroBlock(blocks.StructBlock):
    """
    A block that displays a hero section.
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
        template = "blocks/hero_text.html"
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
        template = "blocks/recent_news_block.html"
        icon = "doc-full-inverse"
        label = "Recent News"
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
