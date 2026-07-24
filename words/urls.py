from django.urls import path

from . import views

urlpatterns = [
    path("<slug:slug>/", views.study_set, name="study_set"),
]