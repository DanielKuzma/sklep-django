from django.shortcuts import render
from django.views.generic import ListView, CreateView, View, TemplateView, DetailView

# Create your views here.

class StartingPage(TemplateView):
    template_name = "serwis/start_page.html"

