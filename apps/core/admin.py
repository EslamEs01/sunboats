from django.contrib import admin

from .models import ContactMessage, Settings


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("الهوية", {"fields": ("site_name", "tagline", "description", "logo", "hero_image")}),
        ("التواصل", {"fields": ("email", "phone", "whatsapp", "address")}),
        ("وسائل التواصل", {"fields": ("facebook", "instagram")}),
    )

    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")
