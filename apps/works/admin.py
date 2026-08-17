from django.contrib import admin

from .models import Artist, Artwork


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country")


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "exhibition", "year", "medium")
    list_filter = ("exhibition", "year")
    search_fields = ("title", "artist__name", "medium")
    prepopulated_fields = {"slug": ("title",)}
