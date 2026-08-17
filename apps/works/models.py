from django.db import models
from django.utils.text import slugify

from apps.core.imaging import compress_if_new


class Artist(models.Model):
    name = models.CharField("الاسم", max_length=200)
    country = models.CharField("الدولة", max_length=80, blank=True)
    bio = models.TextField("السيرة", blank=True)
    image = models.ImageField("الصورة", upload_to="artists/", blank=True)

    class Meta:
        verbose_name = "فنان"
        verbose_name_plural = "الفنانون"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        compress_if_new(self, "image", max_size=(900, 900))
        super().save(*args, **kwargs)


class Artwork(models.Model):
    title = models.CharField("العنوان", max_length=200)
    slug = models.SlugField("الرابط", unique=True, blank=True)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="artworks",
        verbose_name="الفنان",
    )
    exhibition = models.ForeignKey(
        "exhibitions.Exhibition",
        on_delete=models.SET_NULL,
        related_name="artworks",
        verbose_name="المعرض",
        null=True,
        blank=True,
    )
    image = models.ImageField("الصورة", upload_to="artworks/")
    year = models.CharField("السنة", max_length=20, blank=True)
    medium = models.CharField("الخامة", max_length=120, blank=True)
    description = models.TextField("الوصف", blank=True)

    class Meta:
        verbose_name = "عمل فني"
        verbose_name_plural = "الأعمال الفنية"
        ordering = ["-year", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        compress_if_new(self, "image", max_size=(1600, 1600))
        super().save(*args, **kwargs)
