from wagtail.images.formats import Format, register_image_format

# Register a custom image format for 150x150 thumbnails
# this will be an option in the rich text editor image insertion dialog
register_image_format(
    Format(
        name='thumbnail',
        label='150x150 Thumbnail',
        classname='richtext-image thumbnail-150',
        filter_spec='fill-150x150',
    )
)
