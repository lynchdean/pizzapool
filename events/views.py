from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView, TemplateView

from .models import OrgUser, Organisation, Event, PizzaOrder, PizzaSlices
from .forms import OrderCreateForm, ServingCreateForm, OrgUpdateForm, EventEditForm, EventCreateForm


class HomePage(TemplateView):
    template_name = "events/homepage.html"


class UserView(generic.DetailView):
    model = OrgUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "events/user.html"


class OrgDetailView(generic.DetailView):
    model = Organisation
    template_name = "events/organisation_detail.html"
    slug_field = "path"
    slug_url_kwarg = "path"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now()
        # Hide private events unless org user is logged in
        filter_kwargs_gte = dict(organisation=self.object, date__gte=today)
        filter_kwargs_lt = dict(organisation=self.object, date__lt=today)
        if user.is_anonymous or self.object != user.organisation:
            filter_kwargs_gte['private'] = False
            filter_kwargs_lt['private'] = False
        context['current_events'] = Event.objects.filter(**filter_kwargs_gte)
        context['past_events'] = Event.objects.filter(**filter_kwargs_lt)
        return context


class OrgUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Organisation
    form_class = OrgUpdateForm
    template_name = "events/organisation_edit.html"
    slug_field = "path"
    slug_url_kwarg = "path"

    def test_func(self):
        org = self.get_object()
        return self.request.user.organisation == org

    def handle_no_permission(self):
        org = self.get_object()
        return redirect("events:org-detail", path=org.path)

    def get_success_url(self):
        return reverse_lazy("events:org-detail", kwargs={"path": self.object.path})


class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = EventCreateForm
    template_name = "events/event_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['org'] = self.request.user.organisation
        return context

    def form_valid(self, form):
        form.instance.organisation = self.request.user.organisation
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("events:org-detail", kwargs={"path": self.request.user.organisation.path})


class EventDetailView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_orders = PizzaOrder.objects.filter(event=self.object)
        context['pizza_orders'] = pizza_orders
        return context


class EventEditView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Event
    form_class = EventEditForm
    template_name = "events/event_edit.html"

    def test_func(self):
        event = self.get_object()
        return self.request.user.organisation == event.organisation

    def handle_no_permission(self):
        event = self.get_object()
        return redirect("events:event-detail", path=event.organisation.path, slug=event.slug)

    def get_success_url(self):
        event = self.get_object()
        return reverse_lazy("events:event-detail", kwargs={"path": event.organisation.path, "slug": event.slug})


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


class OrderCreateView(generic.CreateView):
    model = PizzaOrder
    form_class = OrderCreateForm
    template_name = "events/order_create.html"
    event = None

    def dispatch(self, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=self.kwargs['slug'])
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super(OrderCreateView, self).get_initial()
        initial['event'] = self.event
        return initial

    def form_valid(self, form):
        form.instance.event = self.event
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context

    def get_success_url(self):
        return reverse_lazy("events:event-detail",
                            kwargs={"path": self.event.organisation.path, "slug": self.event.slug})


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


class ServingCreateView(generic.CreateView):
    model = PizzaSlices
    form_class = ServingCreateForm
    template_name = "events/serving_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pizza_order = get_object_or_404(PizzaOrder, pk=self.kwargs.get('pk'))
        context['order'] = pizza_order
        return context

    def form_valid(self, form):
        pizza_order = get_object_or_404(PizzaOrder, pk=self.kwargs.get('pk'))
        form.instance.pizza_order = pizza_order
        return super().form_valid(form)

    def get_success_url(self):
        pizza_order = get_object_or_404(PizzaOrder, pk=self.kwargs.get('pk'))
        return reverse_lazy("events:event-detail", kwargs={
            "path": pizza_order.event.organisation.path,
            "slug": pizza_order.event.slug
        })


class PizzaSlicesDeleteView(DeleteView):
    model = PizzaSlices
    template_name = "events/delete_slices.html"

    def get_success_url(self):
        slices = self.get_object()
        return reverse_lazy("events:event-detail", kwargs={
            "path": slices.pizza_order.event.organisation.path,
            "slug": slices.pizza_order.event.slug
        })
