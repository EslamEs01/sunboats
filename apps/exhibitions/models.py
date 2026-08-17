from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.imaging import compress_if_new


class ExhibitionQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(status__in=["current", "upcoming"]).order_by("start_date")

    def past(self):
        return self.filter(status="past").order_by("-start_date")

    def featured(self):
        return (
            self.filter(status="current").order_by("start_date").first()
            or self.filter(status="upcoming").order_by("start_date").first()
            or self.order_by("-start_date").first()
        )


class Exhibition(models.Model):
    STATUS_CURRENT = "current"
    STATUS_UPCOMING = "upcoming"
    STATUS_PAST = "past"
    STATUS_CHOICES = (
        (STATUS_CURRENT, "حالي"),
        (STATUS_UPCOMING, "قادم"),
        (STATUS_PAST, "ماضي"),
    )

    title = models.CharField("العنوان", max_length=200)
    slug = models.SlugField("الرابط", unique=True, blank=True)
    description = models.TextField("الوصف")
    image = models.ImageField("الصورة", upload_to="exhibitions/")
    start_date = models.DateField("تاريخ البداية")
    end_date = models.DateField("تاريخ النهاية", null=True, blank=True)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    location = models.CharField("الموقع", max_length=200, blank=True)
    video_url = models.URLField("رابط الفيديو", blank=True)

    objects = ExhibitionQuerySet.as_manager()

    class Meta:
        verbose_name = "معرض"
        verbose_name_plural = "المعارض"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("exhibition-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        compress_if_new(self, "image", max_size=(1800, 1200))
        super().save(*args, **kwargs)


class ExhibitionProgram(models.Model):
    KIND_WORKSHOP = "workshop"
    KIND_VISIT = "visit"
    KIND_TALK = "talk"
    KIND_SHOW = "show"
    KIND_OTHER = "other"
    KIND_CHOICES = (
        (KIND_WORKSHOP, "ورشة"),
        (KIND_VISIT, "زيارة"),
        (KIND_TALK, "حديث"),
        (KIND_SHOW, "عرض"),
        (KIND_OTHER, "أخرى"),
    )

    exhibition = models.ForeignKey(
        Exhibition,
        on_delete=models.CASCADE,
        related_name="program_items",
        verbose_name="المعرض",
    )
    title = models.CharField("العنوان", max_length=200)
    kind = models.CharField("النوع", max_length=20, choices=KIND_CHOICES, default=KIND_OTHER)
    date = models.DateField("التاريخ", null=True, blank=True)
    place = models.CharField("المكان", max_length=200, blank=True)
    short_text = models.TextField("نبذة", blank=True)

    class Meta:
        verbose_name = "فقرة البرنامج"
        verbose_name_plural = "برنامج المعرض"
        ordering = ["date", "pk"]

    def __str__(self):
        return f"{self.exhibition.title} — {self.title}"


class ExhibitionImage(models.Model):
    exhibition = models.ForeignKey(
        Exhibition,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        verbose_name="المعرض",
    )
    image = models.ImageField("الصورة", upload_to="exhibitions/gallery/")
    caption = models.CharField("التعليق", max_length=200, blank=True)

    class Meta:
        verbose_name = "صورة معرض"
        verbose_name_plural = "صور المعارض"

    def __str__(self):
        return self.caption or f"Image for {self.exhibition.title}"

    def save(self, *args, **kwargs):
        compress_if_new(self, "image", max_size=(1600, 1600))
        super().save(*args, **kwargs)


class ExhibitionRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = (
        (STATUS_PENDING, "قيد المراجعة"),
        (STATUS_APPROVED, "مقبول"),
        (STATUS_REJECTED, "مرفوض"),
    )

    name = models.CharField("الاسم", max_length=120)
    email = models.EmailField("البريد الإلكتروني")
    phone = models.CharField("الهاتف", max_length=40)
    country = models.CharField("الدولة", max_length=80)
    title = models.CharField("عنوان العمل", max_length=200)
    medium = models.CharField("الخامة", max_length=120)
    description = models.TextField("الوصف")
    image = models.ImageField("صورة العمل", upload_to="requests/")
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    submitted_at = models.DateTimeField("تاريخ التقديم", auto_now_add=True)

    class Meta:
        verbose_name = "طلب عرض عمل"
        verbose_name_plural = "طلبات العرض"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.title} — {self.name}"

    def save(self, *args, **kwargs):
        compress_if_new(self, "image", max_size=(1400, 1400))
        super().save(*args, **kwargs)

    def approve(self):
        self.status = self.STATUS_APPROVED
        self.save(update_fields=["status"])

    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save(update_fields=["status"])
