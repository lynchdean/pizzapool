from django.core.exceptions import ValidationError
from django.test import TestCase

from .testing_utils import create_event, create_order, create_slices, create_organisation


class PizzaOrderModelTests(TestCase):
    def setUp(self):
        self.org = create_organisation()
        self.event = create_event(self.org)
        self.order = create_order(event=self.event)

    def tearDown(self):
        self.org.delete()
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
        for _ in range(3):
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

    def test_event_is_locked(self):
        """
        event_is_locked returns True if locked and False if not.
        :return:
        """
        self.event.locked = False
        self.assertFalse(self.order.event_is_locked())
        self.event.locked = True
        self.assertTrue(self.order.event_is_locked())

    def test_order_save_fails_if_event_locked(self):
        """
        save() throws Validation error if event is locked.
        :return:
        """
        self.event.locked = True
        with self.assertRaisesRegex(ValidationError, "locked"):
            self.order.save()


class PizzaSlicesModelTests(TestCase):
    def setUp(self):
        self.org = create_organisation()
        self.event = create_event(self.org)
        self.order = create_order(event=self.event)

    def tearDown(self):
        self.org.delete()
        self.event.delete()
        self.order.delete()

    def test_create_slices_fails_if_event_locked(self):
        """
        save() throws Validation error if event is locked.
        :return:
        """
        self.event.locked = True
        with self.assertRaisesRegex(ValidationError, "locked"):
            create_slices(pizza_order=self.order)

    def test_create_slices_fails_if_order_is_full(self):
        """
        save() throws Validation error if order is full.
        :return:
        """
        available = self.order.get_total_remaining()
        create_slices(pizza_order=self.order, number_of_slices=available)
        with self.assertRaisesRegex(ValidationError, "Insufficient"):
            create_slices(pizza_order=self.order, number_of_slices=1)

    def test_create_slices_fails_if_order_doesnt_have_enough_slices(self):
        """
        save() throws Validation error if order doesn't have a sufficient number of slices remaining.
        :return:
        """
        available = self.order.get_total_remaining()
        create_slices(pizza_order=self.order, number_of_slices=available - 1)
        with self.assertRaisesRegex(ValidationError, "Insufficient"):
            create_slices(pizza_order=self.order, number_of_slices=2)
