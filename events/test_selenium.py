import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options

from .testing_utils import create_event, create_order, create_slices


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = create_event()
        cls.order = create_order(event=cls.event)

        options = Options()
        options.add_argument("--headless")
        cls.selenium = WebDriver(options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        cls.event.delete()
        cls.order.delete()
        super().tearDownClass()

    def test_page_title(self):
        self.selenium.get(f"{self.live_server_url}/events/")
        self.assertIn('pizzapool', self.selenium.title)

    # def test_order_creation(self):
    #     self.browser.get(f'http://127.0.0.1:8000/events/{self.event.id}/')
    #     time.sleep(10)
