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

    class Meta:
        template = "blocks/text_block.html"
        icon = "pilcrow"
        group = "Standalone Blocks"


class InfoBlock(blocks.StaticBlock):
    """
    A block that displays a static divider.
    """
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


class FaqListBlock(blocks.ListBlock):
    """
    A block that displays a list of FAQ sections.
    """
    def __init__(self, **kwargs):
        super().__init__(FaqBlock(), **kwargs)

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


class ImageBlock(ImageChooserBlock):
    """
    A block that displays an image.
    """
    def get_context(self, value, parent_context=None):
        from news.models import NewsItem
        context = super().get_context(value, parent_context=parent_context)
        context["news_items"] = NewsItem.objects.all().live().public()
        return context

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"
        group = "Standalone Blocks"
