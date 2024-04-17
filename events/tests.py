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
        create_slices(pizza_order=self.order)
        self.assertTrue(self.order.matched_slices().exists())

    def test_matched_slices_returns_correct_amount(self):
        """
        matched_slices() returns the correct number of PizzaSlices objects.
        :return:
        """
        for i in range(3):
            create_slices(pizza_order=self.order)
        self.assertTrue(self.order.matched_slices().count() == 3)

    def test_matched_slices_returns_correct_amount_if_slices_deleted(self):
        """
        matched_slices() returns the correct number of PizzaSlices objects after some slices have been deleted.
        :return:
        """
        create_slices(pizza_order=self.order, number_of_slices=3)
        slices = create_slices(pizza_order=self.order, number_of_slices=2)
        self.assertTrue(self.order.matched_slices().count() == 2)
        slices.delete()
        self.assertTrue(self.order.matched_slices().count() == 1)

    def test_get_total_claimed_returns_zero_if_no_slices(self):
        """
        get_total_claimed() returns 0 if there are no PizzaSlices linked to the order.
        :return:
        """
        self.assertTrue(self.order.get_total_claimed() == 0)

    def test_get_total_claimed_returns_correct_total(self):
        """
        get_total_claimed() returns the correct number of total slices
        :return:
        """
        create_slices(pizza_order=self.order, number_of_slices=1)
        create_slices(pizza_order=self.order, number_of_slices=2)
        self.assertTrue(self.order.get_total_claimed() == 3)

    def test_get_total_claimed_returns_correct_total_if_slices_deleted(self):
        """
        get_total_claimed() returns the correct number of total slices after some slices have been deleted,
        :return:
        """
        create_slices(pizza_order=self.order, number_of_slices=1)
        slices = create_slices(pizza_order=self.order, number_of_slices=2)
        self.assertTrue(self.order.get_total_claimed() == 3)
        slices.delete()
        self.assertTrue(self.order.get_total_claimed() == 1)

    def test_get_total_claimed_returns_correct_total_if_slices_edited(self):
        """
        get_total_claimed() returns the correct number of total slices after some slices have been edited.
        :return:
        """
        create_slices(pizza_order=self.order, number_of_slices=1)
        slices = create_slices(pizza_order=self.order, number_of_slices=2)
        self.assertTrue(self.order.get_total_claimed() == 3)
        slices.number_of_slices = 1
        slices.save()
        self.assertTrue(self.order.get_total_claimed() == 2)

    def test_get_total_remaining_returns_correct_total_if_none_claimed(self):
        """
        get_total_remaining() matches available_slices if no slices are linked.
        :return:
        """
        self.assertEqual(self.order.get_total_remaining(), self.order.available_slices)

    def test_get_total_remaining_returns_correct_total(self):
        """
        get_total_remaining() returns correct total if some slices are linked.
        :return:
        """
        create_slices(pizza_order=self.order, number_of_slices=3)
        self.assertTrue(self.order.get_total_remaining() == 4)
        create_slices(pizza_order=self.order, number_of_slices=4)
        self.assertTrue(self.order.get_total_remaining() == 0)
