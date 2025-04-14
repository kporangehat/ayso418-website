from wagtail.images.formats import Format, register_image_format

register_image_format(
    Format(
        name='thumbnail',
        label='150x150 Thumbnail',
        classname='richtext-image thumbnail-150',
        filter_spec='fill-150x150',
    )
)
