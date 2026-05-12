from django.urls import path
from .views import StartingPage

urlpatterns = [
    path("", StartingPage.as_view(), name = "starting_page"),
]
