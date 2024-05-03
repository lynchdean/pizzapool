import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument('--headless=new')
        self.browser = webdriver.Chrome(options=options)
        self.addCleanup(self.browser.quit)

    def test_page_title(self):
        self.browser.get('http://127.0.0.1:8000/events')
        self.assertIn('pizzapool', self.browser.title)
