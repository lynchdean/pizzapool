from django.contrib.auth.decorators import login_required
from django.http import Http404
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
        today = timezone.now()
        context['current_events'] = Event.objects.filter(organisation=self.object, private=False, date__gte=today)
        context['past_events'] = Event.objects.filter(organisation=self.object, private=False, date__lt=today)
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
    slug_field = "sqid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_orders = PizzaOrder.objects.filter(event=self.object)
        context['pizza_orders'] = pizza_orders
        return context


@login_required(login_url='login')
def edit_event(request, path, slug):
    org = request.user.organisation
    event = Event.objects.get(sqid=slug)
    if org is None:
        raise Http404("Your account is not linked to an organisation")
    if org != event.organisation:
        raise Http404("This event is not part of your organisation")

    formset = EventEditForm(instance=event)
    if request.method == "POST":
        formset = EventEditForm(request.POST, request.FILES, instance=event)
        if formset.is_valid():
            formset.save()
            return redirect("events:event", path=path, slug=slug)

    context = {'formset': formset, "event": event}
    return render(request, 'events/event_edit.html', context)


class PizzaSlicesDeleteView(DeleteView):
    model = PizzaSlices
    template_name = "events/delete_slices.html"

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return "/events"


def create_pizza_order(request, path, slug):
    event = Event.objects.get(sqid=slug)
    if request.method == 'POST':
        form = PizzaOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:event", path=path, slug=slug)
    else:
        form = PizzaOrderForm(initial={'event': event})
    return render(request, 'events/create_pizza_order.html', {'form': form, 'event': event})


def claim_slices(request, path, pk):
    pizza_order = PizzaOrder.objects.get(pk=pk)
    if request.method == 'POST':
        form = PizzaSlicesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:event", path=path, slug=pizza_order.event.sqid)
    else:
        form = PizzaSlicesForm(initial={'pizza_order': pizza_order})
    return render(request, 'events/claim_slices.html', {'form': form, 'pizza_order': pizza_order})
