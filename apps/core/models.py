from django.db import models

from apps.core.imaging import compress_if_new


class Settings(models.Model):
    site_name = models.CharField("اسم الموقع", max_length=200, default="Sun Boats")
    tagline = models.CharField("الشعار", max_length=300, blank=True)
    description = models.TextField("الوصف", blank=True)
    logo = models.ImageField("الشعار البصري", upload_to="site/", blank=True)
    email = models.EmailField("البريد الإلكتروني", blank=True)
    phone = models.CharField("الهاتف", max_length=40, blank=True)
    whatsapp = models.CharField("واتساب", max_length=40, blank=True)
    address = models.CharField("العنوان", max_length=300, blank=True)
    facebook = models.URLField("فيسبوك", blank=True)
    instagram = models.URLField("إنستغرام", blank=True)
    youtube = models.URLField("يوتيوب", blank=True)
    hero_image = models.ImageField("صورة الغلاف", upload_to="site/", blank=True)

    class Meta:
        verbose_name = "الإعدادات"
        verbose_name_plural = "الإعدادات"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        compress_if_new(self, "logo", max_size=(800, 800))
        compress_if_new(self, "hero_image", max_size=(2000, 1400))
        super().save(*args, **kwargs)

    @staticmethod
    def egypt_digits(raw):
        digits = "".join(ch for ch in (raw or "") if ch.isdigit())
        if digits.startswith("00"):
            digits = digits[2:]
        if digits.startswith("0"):
            digits = "20" + digits[1:]
        return digits

    @property
    def phone_digits(self):
        return self.egypt_digits(self.phone)

    @property
    def whatsapp_digits(self):
        return self.egypt_digits(self.whatsapp or self.phone)

    @property
    def tel_href(self):
        digits = self.phone_digits
        return f"tel:+{digits}" if digits else ""

    @property
    def whatsapp_href(self):
        digits = self.whatsapp_digits
        return f"https://wa.me/{digits}" if digits else ""

    @classmethod
    def load(cls):
        obj = cls.objects.order_by("pk").first()
        if obj:
            return obj
        return cls(site_name="Sun Boats", tagline="International exhibitions in Egypt")


class ContactMessage(models.Model):
    name = models.CharField("الاسم", max_length=120)
    email = models.EmailField("البريد الإلكتروني")
    message = models.TextField("الرسالة")
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)

    class Meta:
        verbose_name = "رسالة اتصال"
        verbose_name_plural = "رسائل الاتصال"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
