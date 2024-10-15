import time
from decimal import Decimal

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .models import Order, Serving
from .testing_utils import create_event, create_order, create_serving, create_organisation


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless")
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.maximize_window()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.org = create_organisation()
        self.event = create_event(organisation=self.org)
        self.org_path = self.event.organisation.path

    def tearDown(self):
        self.event.delete()
        self.org.delete()

    def test_page_title(self):
        self.selenium.get(f"{self.live_server_url}/")
        self.assertIn('pizzapool', self.selenium.title)

    def test_org_page_exists(self):
        self.selenium.get(f"{self.live_server_url}/{self.org_path}/")
        self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/test-org/')

    @override_settings(DEBUG=True)
    def test_order_creation(self):
        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        new_order_btn = self.selenium.find_element(By.ID, "create-order-btn")
        new_order_btn.click()

        # New order page
        name = self.selenium.find_element(By.ID, "id_purchaser_name")
        name.send_keys("NAME")
        whatsapp = self.selenium.find_element(By.ID, "id_purchaser_whatsapp")
        whatsapp.send_keys("0871234567")
        revolut = self.selenium.find_element(By.ID, "id_purchaser_revolut")
        revolut.send_keys("REVOLUT")
        pizza_type = self.selenium.find_element(By.ID, "id_description")
        pizza_type.send_keys("PEPERONI")
        price = self.selenium.find_element(By.ID, "id_price_per_serving")
        price.send_keys("3.14")
        slices = self.selenium.find_element(By.ID, "id_available_servings")
        slices.clear()
        slices.send_keys("7")
        confirm_btn = self.selenium.find_element(By.ID, "confirm-order-btn")
        # ActionChains(self.selenium).move_to_element(confirm_btn).perform()
        confirm_btn.click()
        time.sleep(2)
        # Check returned to Event page
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')

        # Check order is created in database
        order = Order.objects.filter(event=self.event)[0]
        self.assertTrue(order.purchaser_name == "NAME")
        self.assertTrue(order.purchaser_whatsapp == "0871234567")
        self.assertTrue(order.purchaser_revolut == "REVOLUT")
        self.assertTrue(order.description == "PEPERONI")
        self.assertEqual(order.price_per_serving, Decimal('3.14'))
        self.assertEqual(order.available_servings, 7)

    def test_join_order(self):
        # Create order
        order = create_order(event=self.event)

        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        # self.selenium.implicitly_wait(10)
        join_order_btn = self.selenium.find_element(By.ID, "join-order-btn")
        join_order_btn.click()

        # Join order page
        name = self.selenium.find_element(By.ID, "id_buyer_name")
        name.send_keys("NAME")
        whatsapp = self.selenium.find_element(By.ID, "id_buyer_whatsapp")
        whatsapp.send_keys("0871234567")
        servings = self.selenium.find_element(By.ID, "id_number_of_servings")
        servings.clear()
        servings.send_keys("2")
        confirm_btn = self.selenium.find_element(By.ID, "confirm-join-btn")
        ActionChains(self.selenium).move_to_element(confirm_btn).perform()
        confirm_btn.click()

        # Check returned to Event page
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')

        # Check order joined in database
        servings = Serving.objects.filter(order=order)[0]
        self.assertTrue(servings.buyer_name == "NAME")
        self.assertTrue(servings.buyer_whatsapp == "0871234567")
        self.assertEqual(servings.number_of_servings, 2)

    def test_remove_from_order(self):
        order = create_order(event=self.event)
        create_serving(order=order)

        # Check slices exist
        self.assertTrue(Serving.objects.filter(order=order).count() == 1)

        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        remove_slices_link = self.selenium.find_elements(By.ID, "remove-servings")[0]
        remove_slices_link.click()

        # Remove slices page
        remove_slices = self.selenium.find_elements(By.ID, "confirm-remove-slices-btn")[0]
        remove_slices.click()

        # Check returned to Event page
        time.sleep(0.2)
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')

        # Check slices are deleted from order
        self.assertTrue(Serving.objects.filter(order=order).count() == 0)

    def test_cant_join_order_if_full(self):
        order = create_order(event=self.event, available_servings=1)

        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        self.assertTrue(len(self.selenium.find_elements(By.ID, "join-order-btn")) > 0)

        # Add slices to fill order
        create_serving(order=order, number_of_servings=1)
        self.selenium.refresh()

        # Check Order full is now showing and not join order button
        self.assertTrue(len(self.selenium.find_elements(By.ID, "order-full")) > 0)
        self.assertTrue(len(self.selenium.find_elements(By.ID, "join-order-btn")) == 0)

    def test_buttons_disabled_if_locked(self):
        order = create_order(event=self.event)
        create_serving(order=order)
        self.event.locked = True
        self.event.save()

        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        self.assertTrue(len(self.selenium.find_elements(By.ID, "new-orders-locked")) > 0)
        self.assertTrue(len(self.selenium.find_elements(By.ID, "new-servings-locked")) > 0)
        self.assertTrue(len(self.selenium.find_elements(By.ID, "remove-servings")) == 0)
