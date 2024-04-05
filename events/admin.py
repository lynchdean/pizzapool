from django.contrib import admin

from .models import Event, PizzaOrder, PizzaSlices

admin.site.register(Event)
admin.site.register(PizzaOrder)
admin.site.register(PizzaSlices)