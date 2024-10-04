from decimal import Decimal

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .models import PizzaOrder, PizzaSlices
from .testing_utils import create_event, create_order, create_slices, create_organisation


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless")
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.maximize_window()
        cls.selenium.implicitly_wait(10)

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
        self.assertEqual(url, f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')

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
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        # self.selenium.implicitly_wait(10)
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
        self.assertEqual(url, f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')

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
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        remove_slices_link = self.selenium.find_elements(By.ID, "remove-slices")[0]
        remove_slices_link.click()

        # Remove slices page
        remove_slices = self.selenium.find_elements(By.ID, "confirm-remove-slices-btn")[0]
        remove_slices.click()

        # Check returned to Event page
        self.selenium.implicitly_wait(2)
        url = self.selenium.current_url
        self.assertEqual(url, f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')

        # Check slices are deleted from order
        self.assertTrue(PizzaSlices.objects.filter(pizza_order=order).count() == 0)

    def test_cant_join_order_if_full(self):
        order = create_order(event=self.event, available_slices=1)

        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        self.assertTrue(len(self.selenium.find_elements(By.ID, "join-order-btn")) > 0)

        # Add slices to fill order
        create_slices(pizza_order=order, number_of_slices=1)
        self.selenium.refresh()

        # Check Order full is now showing and not join order button
        self.assertTrue(len(self.selenium.find_elements(By.ID, "order-full")) > 0)
        self.assertTrue(len(self.selenium.find_elements(By.ID, "join-order-btn")) == 0)

    def test_buttons_disabled_if_locked(self):
        order = create_order(event=self.event)
        create_slices(pizza_order=order)
        self.event.locked = True
        self.event.save()

        # Event page
        self.selenium.get(f'{self.live_server_url}/{self.org_path}/{self.event.slug}/')
        self.assertTrue(len(self.selenium.find_elements(By.ID, "new-orders-locked")) > 0)
        self.assertTrue(len(self.selenium.find_elements(By.ID, "new-slices-locked")) > 0)
        self.assertTrue(len(self.selenium.find_elements(By.ID, "remove-slices")) == 0)

    # TODO - replace/fix these tests once new password access limits is decided
    # def test_events_index_is_password_locked(self):
    #     self.selenium.get(f'{self.live_server_url}/{self.org_path}/')
    #     self.assertTrue(len(self.selenium.find_elements(By.ID, "event-login")) > 0)
    #
    # def test_events_index_password_success(self):
    #     self.user = User.objects.create_user(username='events-access', password='12345')
    #     self.selenium.get(f'{self.live_server_url}/orgs/')
    #
    #     # Check redirect is successful to password page
    #     self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/events_access/?next=/orgs/')
    #
    #     # Enter pw and proceed
    #     pw = self.selenium.find_element(By.ID, "id_password")
    #     pw.send_keys("12345")
    #     login_btn = self.selenium.find_element(By.ID, "event-login")
    #     login_btn.click()
    #
    #     # Check redirect to events page on successful password entry
    #     url = self.selenium.current_url
    #     self.assertEqual(url, f'{self.live_server_url}/orgs/')
    #
    # def test_events_index_password_failure(self):
    #     self.user = User.objects.create_user(username='events-access', password='12345')
    #     self.selenium.get(f'{self.live_server_url}/')
    #
    #     # Check redirect is successful to password page
    #     self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/events_access/?next=/')
    #
    #     # Enter wrong pw and proceed
    #     pw = self.selenium.find_element(By.ID, "id_password")
    #     pw.send_keys("abcde")
    #     login_btn = self.selenium.find_element(By.ID, "event-login")
    #     login_btn.click()
    #
    #     # Check for incorrect password warning
    #     warn_text = self.selenium.find_element(By.XPATH, "/html/body/div/div/div/div/form/div[1]/ul/li").text
    #     self.assertEqual(warn_text, "Invalid password")
