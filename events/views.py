from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView, TemplateView
from django.conf import settings
import stripe

from .models import OrgUser, Organisation, Event, Order, Serving
from .forms import OrderCreateForm, ServingCreateForm, OrgUpdateForm, EventEditForm, EventCreateForm

stripe.api_key = settings.STRIPE_SECRET_KEY


class HomePage(TemplateView):
    template_name = "events/homepage.html"


class UserView(generic.DetailView):
    model = OrgUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "events/user.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # If linked stripe verification = false, recheck account verification
        if not self.object.organisation.stripe_account_verified:
            #  Check if charges and payouts are enabled
            account = stripe.Account.retrieve(self.object.organisation.stripe_account_id)
            if account["charges_enabled"] and account["payouts_enabled"]:
                # Update account if verified
                self.object.organisation.stripe_account_verified = True
                self.object.organisation.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_link'] = self.get_stripe_setup_link()
        return context

    def get_stripe_setup_link(self):
        protocol = 'https' if self.request.is_secure() else 'http'
        host = self.request.get_host()
        base_url = f"{protocol}://{host}"
        link = stripe.AccountLink.create(
            account=self.object.organisation.stripe_account_id,
            refresh_url=f"{base_url}/user/{self.object.username}",
            return_url=f"{base_url}/user/{self.object.username}",
            type="account_onboarding",
            collection_options={"fields": "eventually_due"},
        )
        return link["url"]


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
        orders = Order.objects.filter(event=self.object)
        context['orders'] = orders
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
    model = Order
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
    model = Order
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
    model = Serving
    form_class = ServingCreateForm
    template_name = "events/serving_create.html"
    order = None

    def dispatch(self, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['order'] = self.order
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context

    def form_valid(self, form):
        form.instance.order = self.order
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("events:event-detail", kwargs={
            "path": self.order.event.organisation.path,
            "slug": self.order.event.slug
        })


class ServingDeleteView(DeleteView):
    model = Serving
    template_name = "events/delete_slices.html"

    def get_success_url(self):
        servings = self.get_object()
        return reverse_lazy("events:event-detail", kwargs={
            "path": servings.order.event.organisation.path,
            "slug": servings.order.event.slug
        })
