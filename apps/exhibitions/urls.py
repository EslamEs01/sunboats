from django.urls import path

from . import views

urlpatterns = [
    path("", views.exhibition_list, name="exhibitions"),
    path("<slug:slug>/", views.exhibition_detail, name="exhibition-detail"),
]
