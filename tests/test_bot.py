import unittest
from src.bot import ShoppingBot

class TestShoppingBot(unittest.TestCase):

    def setUp(self):
        self.bot = ShoppingBot()

    def test_login(self):
        result = self.bot.login('test_user', 'test_password')
        self.assertTrue(result)

    def test_search_item(self):
        result = self.bot.search_item('laptop')
        self.assertIsInstance(result, list)

    def test_add_to_cart(self):
        self.bot.search_item('laptop')
        result = self.bot.add_to_cart('laptop')
        self.assertTrue(result)

    def test_checkout(self):
        self.bot.search_item('laptop')
        self.bot.add_to_cart('laptop')
        result = self.bot.checkout()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()