from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from django.views.generic import DeleteView, ListView

from .models import Organisation, Event, PizzaOrder, PizzaSlices, PizzaOrderForm, PizzaSlicesForm, EventsAccessForm


class OrgIndexView(LoginRequiredMixin, generic.ListView):
    template_name = "events/organisations_list.html"
    context_object_name = "orgs_list"
    login_url = '/events/events_access/'

    def get_queryset(self):
        return Organisation.objects.all()


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = "events/index.html"
    context_object_name = "events_list"
    login_url = '/events/events_access/'

    def get_queryset(self):
        return Event.objects.order_by("-date")


class OrgDetailView(generic.DetailView):
    model = Organisation
    template_name = "events/organisation_detail.html"
    slug_field = "path"
    slug_url_kwarg = "path"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.filter(organisation=self.object)
        context['events'] = events
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


def create_pizza_order(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
        form = PizzaOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        form = PizzaOrderForm(initial={'event': event})
    return render(request, 'events/create_pizza_order.html', {'form': form, 'event': event})


def claim_slices(request, pk):
    pizza_order = PizzaOrder.objects.get(pk=pk)
    if request.method == 'POST':
        form = PizzaSlicesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        form = PizzaSlicesForm(initial={'pizza_order': pizza_order})
    return render(request, 'events/claim_slices.html', {'form': form, 'pizza_order': pizza_order})


class EventsAccessView(LoginView):
    authentication_form = EventsAccessForm
    template_name = 'events/events_access.html'
