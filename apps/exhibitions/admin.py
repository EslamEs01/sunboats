from django.contrib import admin

from .models import Exhibition, ExhibitionImage, ExhibitionProgram, ExhibitionRequest


class ExhibitionProgramInline(admin.TabularInline):
    model = ExhibitionProgram
    extra = 1


class ExhibitionImageInline(admin.TabularInline):
    model = ExhibitionImage
    extra = 1


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "location")
    list_filter = ("status",)
    search_fields = ("title", "location", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ExhibitionProgramInline, ExhibitionImageInline]


@admin.action(description="قبول الطلبات المحددة")
def approve_requests(modeladmin, request, queryset):
    for item in queryset:
        item.approve()


@admin.action(description="رفض الطلبات المحددة")
def reject_requests(modeladmin, request, queryset):
    for item in queryset:
        item.reject()


@admin.register(ExhibitionRequest)
class ExhibitionRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "name", "country", "status", "submitted_at")
    list_filter = ("status", "country")
    search_fields = ("name", "email", "title", "country")
    actions = [approve_requests, reject_requests]
    readonly_fields = ("submitted_at",)
    list_editable = ("status",)
