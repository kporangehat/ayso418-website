from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class InfoBlock(blocks.StaticBlock):
    """
    A block that displays a static divider.
    """

    class Meta:
        # template = "blocks/info_block.html"
        # icon = "placeholder"
        admin_text = "This is from InfoBlock"
        label = "General Information"


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
        # template = "blocks/info_block.html"
        # icon = "placeholder"
        min_num = 1
        max_num = 5
        label = "FAQs"


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
        # template = "blocks/text_block.html"
        # icon = "placeholder"
        pass


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
        # template = "blocks/carousel_block.html"
        # icon = "placeholder"
        ...


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

    class Meta:
        # template = "blocks/call_to_action_block.html"
        # icon = "placeholder"
        pass


class ImageBlock(ImageChooserBlock):
    """
    A block that displays an image.
    """

    class Meta:
        # template = "blocks/image_block.html"
        # icon = "placeholder"
        pass
