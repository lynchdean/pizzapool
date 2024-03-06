from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Event


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events_list"
    
    def get_queryset(self):
        return Event.objects.order_by("-date")
    
    
class EventView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"

