import time
from decimal import Decimal

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .models import PizzaOrder, PizzaSlices
from .testing_utils import create_event, create_order, create_slices


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless")
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.event = create_event()

    def tearDown(self):
        self.event.delete()

    def test_page_title(self):
        self.selenium.get(f"{self.live_server_url}/events/")
        self.assertIn('pizzapool', self.selenium.title)

    def test_order_creation(self):
        # Event page
        self.selenium.get(f'{self.live_server_url}/events/{self.event.id}/')
        new_order_btn = self.selenium.find_element(By.ID, "create-order-btn")
        new_order_btn.click()

        # New order page
        name = self.selenium.find_element(By.ID, "id_purchaser_name")
        name.send_keys("NAME")
        whatsapp = self.selenium.find_element(By.ID, "id_purchaser_whatsapp")
        whatsapp.send_keys("0871234567")
        revolut = self.selenium.find_element(By.ID, "id_purchaser_revolut")
        revolut.send_keys("REVOLUT")
        pizza_type = self.selenium.find_element(By.ID, "id_pizza_type")
        pizza_type.send_keys("PEPERONI")
        price = self.selenium.find_element(By.ID, "id_price_per_slice")
        price.send_keys("3.14")
        slices = self.selenium.find_element(By.ID, "id_available_slices")
        slices.clear()
        slices.send_keys("7")
        confirm_btn = self.selenium.find_element(By.ID, "confirm-order-btn")
        ActionChains(self.selenium).move_to_element(confirm_btn).perform()
        confirm_btn.click()

        # Check returned to Event page
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/events/{self.event.id}/')

        # Check order is created in database
        order = PizzaOrder.objects.filter(event=self.event)[0]
        self.assertTrue(order.purchaser_name == "NAME")
        self.assertTrue(order.purchaser_whatsapp == "0871234567")
        self.assertTrue(order.purchaser_revolut == "REVOLUT")
        self.assertTrue(order.pizza_type == "PEPERONI")
        self.assertEqual(order.price_per_slice, Decimal('3.14'))
        self.assertEqual(order.available_slices, 7)

    def test_join_order(self):
        # Create order
        order = create_order(event=self.event)

        # Event page
        self.selenium.get(f'{self.live_server_url}/events/{self.event.id}/')
        join_order_btn = self.selenium.find_element(By.ID, "join-order-btn")
        join_order_btn.click()

        # Join order page
        name = self.selenium.find_element(By.ID, "id_buyer_name")
        name.send_keys("NAME")
        whatsapp = self.selenium.find_element(By.ID, "id_buyer_whatsapp")
        whatsapp.send_keys("0871234567")
        slices = self.selenium.find_element(By.ID, "id_number_of_slices")
        slices.clear()
        slices.send_keys("2")
        confirm_btn = self.selenium.find_element(By.ID, "confirm-join-btn")
        ActionChains(self.selenium).move_to_element(confirm_btn).perform()
        confirm_btn.click()

        # Check returned to Event page
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/events/{self.event.id}/')

        # Check order joined in database
        slices = PizzaSlices.objects.filter(pizza_order=order)[0]
        self.assertTrue(slices.buyer_name == "NAME")
        self.assertTrue(slices.buyer_whatsapp == "0871234567")
        self.assertEqual(slices.number_of_slices, 2)

    def test_remove_from_order(self):
        order = create_order(event=self.event)
        slices = create_slices(pizza_order=order)

        # Check slices exist
        self.assertTrue(PizzaSlices.objects.filter(pizza_order=order).count() == 1)

        # Event page
        self.selenium.get(f'{self.live_server_url}/events/{self.event.id}/')
        remove_slices_link = self.selenium.find_elements(By.ID, "remove-slices")[0]
        remove_slices_link.click()

        # Remove slices page
        remove_slices = self.selenium.find_elements(By.ID, "confirm-remove-slices-btn")[0]
        remove_slices.click()

        # Check returned to Event page
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/events/{self.event.id}/')

        # Check slices are deleted from order
        self.assertTrue(PizzaSlices.objects.filter(pizza_order=order).count() == 0)
