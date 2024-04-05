from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render

from .models import Event, PizzaOrder, PizzaSlices, PizzaOrderForm


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
        context['slices'] = PizzaSlices.objects.filter(pizza_order__in=pizza_orders)
        return context


def create_pizza_order(request, pk):
    if request.method == 'POST':
        form = PizzaOrderForm(request.POST)
        print(form.fields)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.POST.get('next', '/'))
    else:
        data = {'event': Event.objects.get(pk=pk)}
        form = PizzaOrderForm(data)
    return render(request, 'events/create_pizza_order.html', {'form': form, 'pk': pk})