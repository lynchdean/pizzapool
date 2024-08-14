from django.contrib import admin

from .models import Organisation, Event, PizzaOrder, PizzaSlices

admin.site.register(Organisation, readonly_fields=['path'])
admin.site.register(Event)
admin.site.register(PizzaOrder)
admin.site.register(PizzaSlices)
