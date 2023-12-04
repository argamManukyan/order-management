from unittest import TestCase

from src.exceptions import ObjectAlreadyExists, StockQuantityIsNotEnough, DiscountError
from src.product import Product, product_instances


class TestProduct(TestCase):
    product_data = {
        "product_name": "Product 1",
        "price": 300,
        "discount": 0,
        "stock_qty": 30,
    }

    def setUp(self):
        product_instances.set_empty_instances()

    def test_create_product_success(self):
        product = Product(**self.product_data)
        assert product.stock_qty == self.product_data["stock_qty"]

    def test_create_product_fail(self):
        Product(**self.product_data)
        try:
            Product(**self.product_data)
        except Exception as e:
            assert isinstance(e, ObjectAlreadyExists)

    def test_wrong_discount(self):
        data = self.product_data
        data["discount"] = -1
        try:
            Product(**data)
        except Exception as e:
            assert isinstance(e, DiscountError)

    def test_calculate_product_final_amount(self):
        data = self.product_data
        data["discount"] = 10
        product = Product(**data)

        assert product.final_price == 270

    def test_updating_product_stock_qty_fail(self):
        product = Product(**self.product_data)
        try:
            product.update_qty(40)
        except Exception as e:
            assert isinstance(e, StockQuantityIsNotEnough)

    def test_update_product_stock_qty_success(self):
        product = Product(**self.product_data)
        product.update_qty(10)

        assert product.stock_qty == 20

    def test_make_sku_dynamically(self):
        product = Product(**self.product_data)
        assert product.sku == "product-1"
