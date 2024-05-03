from django.utils import timezone

from .models import Event, PizzaOrder, PizzaSlices


def create_event(event_title="Test Event", date=timezone.now(), description="desc", locked=False):
    return Event.objects.create(event_title=event_title, date=date, description=description, locked=locked)


def create_order(event, purchaser_name="Bob", purchaser_whatsapp="0879876543", purchaser_revolut="BobRev",
                 pizza_type="Pep", price_per_slice=4, available_slices=7):
    return PizzaOrder.objects.create(event=event, purchaser_name=purchaser_name, purchaser_whatsapp=purchaser_whatsapp,
                                     purchaser_revolut=purchaser_revolut, pizza_type=pizza_type,
                                     price_per_slice=price_per_slice, available_slices=available_slices)


def create_slices(pizza_order, buyer_name="John", buyer_whatsapp="0871234567", number_of_slices=1):
    return PizzaSlices.objects.create(pizza_order=pizza_order, buyer_name=buyer_name, buyer_whatsapp=buyer_whatsapp,
                                      number_of_slices=number_of_slices)
