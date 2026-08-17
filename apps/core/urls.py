from django.urls import path

from apps.exhibitions.views import submit_work

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("gallery/", views.gallery, name="gallery"),
    path("submit/", submit_work, name="submit"),
]
