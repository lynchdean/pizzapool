from django.db.models import Sum
from django.utils import timezone
from django.views import generic
from django.shortcuts import render, redirect
from django.views.generic import DeleteView, ListView, TemplateView

from .models import Organisation, Event, PizzaOrder, PizzaSlices, PizzaOrderForm, PizzaSlicesForm


class HomePage(TemplateView):
    template_name = "events/homepage.html"


class OrgIndexView(generic.ListView):
    template_name = "events/organisations_list.html"
    context_object_name = "orgs_list"

    def get_queryset(self):
        return Organisation.objects.all()


class OrgDetailView(generic.DetailView):
    model = Organisation
    template_name = "events/organisation_detail.html"
    slug_field = "path"
    slug_url_kwarg = "path"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        context['current_events'] = Event.objects.filter(organisation=self.object, private=False, date__gte=today)
        context['past_events'] = Event.objects.filter(organisation=self.object, private=False, date__lt=today)
        return context


class EventView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_orders = PizzaOrder.objects.filter(event=self.object)
        context['pizza_orders'] = pizza_orders
        return context


class PizzaOrderStatsView(ListView):
    model = PizzaOrder
    template_name = "events/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_orders"] = PizzaOrder.objects.count()
        context["total_slices"] = PizzaSlices.objects.aggregate(Sum('number_of_slices'))['number_of_slices__sum']
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


def create_pizza_order(request, path, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
        form = PizzaOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:event", path=path, pk=pk)
    else:
        form = PizzaOrderForm(initial={'event': event})
    return render(request, 'events/create_pizza_order.html', {'form': form, 'event': event})


def claim_slices(request, path, pk):
    pizza_order = PizzaOrder.objects.get(pk=pk)
    if request.method == 'POST':
        form = PizzaSlicesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:event", path=path, pk=pizza_order.event.id)
    else:
        form = PizzaSlicesForm(initial={'pizza_order': pizza_order})
    return render(request, 'events/claim_slices.html', {'form': form, 'pizza_order': pizza_order})
