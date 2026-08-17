from django.contrib import messages
from django.shortcuts import redirect, render

from apps.exhibitions.models import Exhibition
from apps.works.models import Artwork

from .forms import ContactForm


def home(request):
    featured = Exhibition.objects.featured()
    works = []
    if featured:
        works = list(featured.artworks.select_related("artist")[:6])
    return render(
        request,
        "pages/home.html",
        {
            "featured": featured,
            "featured_works": works,
        },
    )


def about(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you. We received your message.")
            return redirect("about")
    else:
        form = ContactForm()
    return render(request, "pages/about.html", {"form": form})


def gallery(request):
    editions = Exhibition.objects.prefetch_related(
        "artworks__artist",
        "gallery_images",
    ).order_by("-start_date")
    artworks = Artwork.objects.select_related("artist", "exhibition").order_by("-year", "title")
    loose_works = artworks.filter(exhibition__isnull=True)
    return render(
        request,
        "pages/gallery.html",
        {
            "editions": editions,
            "artworks": artworks,
            "loose_works": loose_works,
        },
    )
