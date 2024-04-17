from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Event, PizzaOrder, PizzaSlices


def create_event(host, event_title="Test Event", date=timezone.now(), description="desc"):
    return Event.objects.create(event_title=event_title, date=date, description=description, host=host)


def create_order(event, purchaser_name="Bob", purchaser_whatsapp="0879876543", purchaser_revolut="BobRev",
                 pizza_type="Pep", price_per_slice=4, available_slices=7):
    return PizzaOrder.objects.create(event=event, purchaser_name=purchaser_name, purchaser_whatsapp=purchaser_whatsapp,
                                     purchaser_revolut=purchaser_revolut, pizza_type=pizza_type,
                                     price_per_slice=price_per_slice, available_slices=available_slices)


def create_slices(pizza_order, buyer_name="John", buyer_whatsapp="0871234567", number_of_slices=1):
    return PizzaSlices.objects.create(pizza_order=pizza_order, buyer_name=buyer_name, buyer_whatsapp=buyer_whatsapp,
                                      number_of_slices=number_of_slices)


class PizzaOrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.event = create_event(host=self.user)
        self.order = create_order(event=self.event)

    def tearDown(self):
        self.user.delete()
        self.event.delete()
        self.order.delete()

    def test_matched_slices_returns_empty_queryset_if_no_matches(self):
        """
        matched_slices() returns empty queryset if there are no slices linked to the order.
        :return:
        """
        self.assertFalse(self.order.matched_slices().exists())

    def test_matched_slices_returns_results(self):
        """
        matched_slices() returns queryset if there are slices linked to the order.
        :return:
        """
        new_slice = create_slices(pizza_order=self.order)
        self.assertTrue(self.order.matched_slices().exists())
