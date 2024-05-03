import time
from decimal import Decimal

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options

from .models import PizzaOrder
from .testing_utils import create_event, create_order, create_slices


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless")
        cls.selenium = WebDriver(options=options)
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
        self.selenium.get(f'{self.live_server_url}/events/{self.event.id}/')
        # Event page
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
        confirm_btn.click()

        # Check order is created in database
        order = PizzaOrder.objects.filter(event=self.event)[0]
        self.assertTrue(order.purchaser_name == "NAME")
        self.assertTrue(order.purchaser_whatsapp == "0871234567")
        self.assertTrue(order.purchaser_revolut == "REVOLUT")
        self.assertTrue(order.pizza_type == "PEPERONI")
        self.assertEqual(order.price_per_slice, Decimal('3.14'))
        self.assertEqual(order.available_slices, 7)
