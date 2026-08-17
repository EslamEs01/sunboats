from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def compress_image(image_field, max_size=(1800, 1800), quality=85):
    """Return a JPEG ContentFile from an uploaded image. Huge files are thumbnailed."""
    if not image_field:
        return image_field

    image_field.open()
    image_field.seek(0)
    img = Image.open(image_field)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)
    name = Path(getattr(image_field, "name", "image.jpg")).stem + ".jpg"
    return ContentFile(buffer.read(), name=name)


def compress_if_new(instance, field_name, max_size=(1800, 1800)):
    field = getattr(instance, field_name)
    if not field:
        return
    if instance.pk:
        old = instance.__class__.objects.filter(pk=instance.pk).first()
        if old and getattr(old, field_name) == field:
            return
    setattr(instance, field_name, compress_image(field, max_size=max_size))
