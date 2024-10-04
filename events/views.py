from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.shortcuts import render, redirect
from django.views.generic import DeleteView, TemplateView

from .models import OrgUser, Organisation, Event, PizzaOrder, PizzaSlices
from .forms import PizzaOrderForm, PizzaSlicesForm, OrgEditForm, EventEditForm


class UserView(generic.DetailView):
    model = OrgUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "events/user.html"


class HomePage(TemplateView):
    template_name = "events/homepage.html"


class OrgDetailView(generic.DetailView):
    model = Organisation
    template_name = "events/organisation_detail.html"
    slug_field = "path"
    slug_url_kwarg = "path"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now()
        filter_kwargs_gte = dict(organisation=self.object, date__gte=today)
        filter_kwargs_lt = dict(organisation=self.object, date__lt=today)
        if user.is_anonymous or self.object != user.organisation:
            filter_kwargs_gte['private'] = False
            filter_kwargs_lt['private'] = False

        context['current_events'] = Event.objects.filter(**filter_kwargs_gte)
        context['past_events'] = Event.objects.filter(**filter_kwargs_lt)
        return context


@login_required(login_url='login')
def edit_organisation(request, path):
    org = request.user.organisation
    if org is None:
        raise Http404("Your account is not linked to an organisation")
    formset = OrgEditForm(instance=org)
    if request.method == 'POST':
        formset = OrgEditForm(request.POST, request.FILES, instance=org)
        if formset.is_valid():
            formset.save()
            return redirect("events:org-detail", path=path)

    context = {'formset': formset, "org": org}
    return render(request, 'events/organisation_edit.html', context)


class EventView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_orders = PizzaOrder.objects.filter(event=self.object)
        context['pizza_orders'] = pizza_orders
        return context


@login_required(login_url='login')
def edit_event(request, path, slug):
    org = request.user.organisation
    event = Event.objects.get(slug=slug)
    if org is None:
        raise Http404("Your account is not linked to an organisation")
    if org != event.organisation:
        raise Http404("This event is not part of your organisation")

    formset = EventEditForm(instance=event)
    if request.method == "POST":
        formset = EventEditForm(request.POST, request.FILES, instance=event)
        if formset.is_valid():
            formset.save()
            return redirect("events:event-detail", path=path, slug=slug)

    context = {'formset': formset, "event": event}
    return render(request, 'events/event_edit.html', context)


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = "events/event_delete.html"

    def test_func(self):
        event = self.get_object()
        return self.request.user.organisation == event.organisation

    def handle_no_permission(self):
        event = self.get_object()
        return redirect("events:event-detail", path=event.organisation.path, slug=event.slug)

    def get_success_url(self):
        event = self.get_object()
        return reverse_lazy("events:org-detail", kwargs={"path": event.organisation.path})


def create_pizza_order(request, path, slug):
    event = Event.objects.get(slug=slug)
    if request.method == 'POST':
        form = PizzaOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:event-detail", path=path, slug=slug)
    else:
        form = PizzaOrderForm(initial={'event': event})
    return render(request, 'events/create_pizza_order.html', {'form': form, 'event': event})


class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PizzaOrder
    template_name = "events/order_delete.html"

    def test_func(self):
        order = self.get_object()
        return self.request.user.organisation == order.event.organisation

    def handle_no_permission(self):
        order = self.get_object()
        return redirect("events:event-detail", path=order.event.organisation.path, slug=order.event.slug)

    def get_success_url(self):
        order = self.get_object()
        return reverse_lazy("events:event-detail",
                            kwargs={"path": order.event.organisation.path, "slug": order.event.slug})


def claim_slices(request, path, pk):
    pizza_order = PizzaOrder.objects.get(pk=pk)
    if request.method == 'POST':
        form = PizzaSlicesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:event-detail", path=path, slug=pizza_order.event.slug)
    else:
        form = PizzaSlicesForm(initial={'pizza_order': pizza_order})
    return render(request, 'events/claim_slices.html', {'form': form, 'pizza_order': pizza_order})


class PizzaSlicesDeleteView(DeleteView):
    model = PizzaSlices
    template_name = "events/delete_slices.html"

    def get_success_url(self):
        slices = self.get_object()
        return reverse_lazy("events:event-detail", kwargs={
            "path": slices.pizza_order.event.organisation.path,
            "slug": slices.pizza_order.event.slug
        })
