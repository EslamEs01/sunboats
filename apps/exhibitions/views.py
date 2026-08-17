from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExhibitionRequestForm
from .models import Exhibition


def exhibition_list(request):
    return render(
        request,
        "pages/exhibitions.html",
        {
            "upcoming": Exhibition.objects.upcoming(),
            "past": Exhibition.objects.past(),
        },
    )


def exhibition_detail(request, slug):
    exhibition = get_object_or_404(
        Exhibition.objects.prefetch_related(
            "program_items",
            "gallery_images",
            "artworks__artist",
        ),
        slug=slug,
    )
    return render(request, "pages/exhibition_detail.html", {"exhibition": exhibition})


def submit_work(request):
    if request.method == "POST":
        form = ExhibitionRequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.status = ExhibitionRequestForm.Meta.model.STATUS_PENDING
            request_obj.save()
            messages.success(
                request,
                "Your work is with us. We review every submission for a future edition.",
            )
            return redirect("submit")
    else:
        form = ExhibitionRequestForm()
    return render(request, "pages/submit.html", {"form": form})
