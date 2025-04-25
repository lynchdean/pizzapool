from django.core.exceptions import ValidationError
from django.test import TestCase
from django.core import mail

from .testing_utils import create_event, create_order, create_serving, create_organisation


class EmailTests(TestCase):
    # Send message
    def test_send_mail(self):
        from django.core.mail import send_mail
        send_mail(
            'Subject here',
            'Here is the message.',
            'noreply@pizzapool.app',
            ['deanl-dev@outlook.com'],
            fail_silently=False,
        )
        #  Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')


class OrderModelTests(TestCase):
    def setUp(self):
        self.org = create_organisation()
        self.event = create_event(self.org)
        self.order = create_order(event=self.event)

    def tearDown(self):
        self.org.delete()
        self.event.delete()
        self.order.delete()

    def test_matched_servings_returns_empty_queryset_if_no_matches(self):
        """
        matched_servings() returns empty queryset if there are no servings linked to the order.
        :return:
        """
        self.assertFalse(self.order.get_servings().exists())

    def test_matched_servings_returns_results(self):
        """
        matched_servings() returns queryset if there are servings linked to the order.
        :return:
        """
        create_serving(order=self.order)
        self.assertTrue(self.order.get_servings().exists())

    def test_matched_servings_returns_correct_amount(self):
        """
        matched_servings() returns the correct number of Serving objects.
        :return:
        """
        for _ in range(3):
            create_serving(order=self.order)
        self.assertTrue(self.order.get_servings().count() == 3)

    def test_matched_servings_returns_correct_amount_if_slices_deleted(self):
        """
        matched_servings() returns the correct number of Serving objects after some servings have been deleted.
        :return:
        """
        create_serving(order=self.order, number_of_servings=3)
        servings = create_serving(order=self.order, number_of_servings=2)
        self.assertTrue(self.order.get_servings().count() == 2)
        servings.delete()
        self.assertTrue(self.order.get_servings().count() == 1)

    def test_get_total_claimed_returns_zero_if_no_servings(self):
        """
        get_total_claimed() returns 0 if there are no Serving linked to the order.
        :return:
        """
        self.assertTrue(self.order.get_total_claimed() == 0)

    def test_get_total_claimed_returns_correct_total(self):
        """
        get_total_claimed() returns the correct number of total servings
        :return:
        """
        create_serving(order=self.order, number_of_servings=1)
        create_serving(order=self.order, number_of_servings=2)
        self.assertTrue(self.order.get_total_claimed() == 3)

    def test_get_total_claimed_returns_correct_total_if_servings_deleted(self):
        """
        get_total_claimed() returns the correct number of total servings after some servings have been deleted,
        :return:
        """
        create_serving(order=self.order, number_of_servings=1)
        servings = create_serving(order=self.order, number_of_servings=2)
        self.assertTrue(self.order.get_total_claimed() == 3)
        servings.delete()
        self.assertTrue(self.order.get_total_claimed() == 1)

    def test_get_total_claimed_returns_correct_total_if_servings_edited(self):
        """
        get_total_claimed() returns the correct number of total servings after some servings have been edited.
        :return:
        """
        create_serving(order=self.order, number_of_servings=1)
        servings = create_serving(order=self.order, number_of_servings=2)
        self.assertTrue(self.order.get_total_claimed() == 3)
        servings.number_of_servings = 1
        servings.save()
        self.assertTrue(self.order.get_total_claimed() == 2)

    def test_get_total_remaining_returns_correct_total_if_none_claimed(self):
        """
        get_total_remaining() matches available_servings if no servings are linked.
        :return:
        """
        self.assertEqual(self.order.get_total_remaining(), self.order.available_servings)

    def test_get_total_remaining_returns_correct_total(self):
        """
        get_total_remaining() returns correct total if some servings are linked.
        :return:
        """
        create_serving(order=self.order, number_of_servings=3)
        self.assertTrue(self.order.get_total_remaining() == 4)
        create_serving(order=self.order, number_of_servings=4)
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


class ServingModelTests(TestCase):
    def setUp(self):
        self.org = create_organisation()
        self.event = create_event(self.org)
        self.order = create_order(event=self.event)

    def tearDown(self):
        self.org.delete()
        self.event.delete()
        self.order.delete()

    def test_create_servings_fails_if_event_locked(self):
        """
        save() throws Validation error if event is locked.
        :return:
        """
        self.event.locked = True
        with self.assertRaisesRegex(ValidationError, "locked"):
            create_serving(order=self.order)

    def test_create_servings_fails_if_order_is_full(self):
        """
        save() throws Validation error if order is full.
        :return:
        """
        available = self.order.get_total_remaining()
        create_serving(order=self.order, number_of_servings=available)
        with self.assertRaisesRegex(ValidationError, "Insufficient"):
            create_serving(order=self.order, number_of_servings=1)

    def test_create_servings_fails_if_order_doesnt_have_enough_servings(self):
        """
        save() throws Validation error if order doesn't have a sufficient number of servings remaining.
        :return:
        """
        available = self.order.get_total_remaining()
        create_serving(order=self.order, number_of_servings=available - 1)
        with self.assertRaisesRegex(ValidationError, "Insufficient"):
            create_serving(order=self.order, number_of_servings=2)
