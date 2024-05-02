from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from django.views.generic import DeleteView

from .models import Event, PizzaOrder, PizzaSlices, PizzaOrderForm, PizzaSlicesForm


class IndexView(generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events_list"

    def get_queryset(self):
        return Event.objects.order_by("-date")


class EventView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_orders = PizzaOrder.objects.filter(event=self.object)
        context['pizza_orders'] = pizza_orders
        return context


class PizzaSlicesDeleteView(DeleteView):
    model = PizzaSlices
    template_name = "events/delete_slices.html"

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return "/events"


def create_pizza_order(request, pk):
    if request.method == 'POST':
        form = PizzaOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        event = Event.objects.get(pk=pk)
        form = PizzaOrderForm(initial={'event': event})
    return render(request, 'events/create_pizza_order.html', {'form': form, 'event': event})


def claim_slices(request, pk):
    if request.method == 'POST':
        form = PizzaSlicesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        pizza_order = PizzaOrder.objects.get(pk=pk)
        form = PizzaSlicesForm(initial={'pizza_order': pizza_order})
    return render(request, 'events/claim_slices.html', {'form': form, 'pizza_order': pizza_order})
