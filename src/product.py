from dataclasses import dataclass

from .exceptions import StockQuantityIsNotEnough, DiscountError
from .helpers import BaseModel
from src.management import InstanceManagement

product_instances = InstanceManagement([])


@dataclass
class Product(BaseModel):
    product_name: str
    price: float
    discount: float  # by percents
    stock_qty: float
    __sku: str = ''
    __management_instance = product_instances

    @staticmethod
    def validate_discount(discount):
        """Validates product discount"""

        if discount < 0 or discount > 100:
            raise DiscountError

    @property
    def sku(self):
        return self.__sku

    def __post_init__(self):
        self.validate_discount(self.discount)
        self.__slugify_product()
        super().__post_init__()

    def _validate_product(self):
        """Validates is the product sku unique"""

        if (
            len(
                list(
                    filter(
                        lambda x: x.sku == self.sku, product_instances.get_instances()
                    )
                )
            )
            > 0
        ):
            raise ValueError

    @property
    def final_price(self) -> float:
        """Calculates final cost of the product"""

        return self.price - (self.price * self.discount / 100)

    def update_qty(self, sold_qty: float):
        """Updates stock quantity after selling"""
        if sold_qty > self.stock_qty:
            raise StockQuantityIsNotEnough

        self.stock_qty -= sold_qty

    def __slugify_product(self):
        """Generates simple sku for the product"""

        product_name = self.product_name
        product_name.replace(",", "-")
        product_name.replace(".", "-")
        product_name.replace("/", "-")
        product_name.replace("'", "-")
        product_name.replace(":", "-")
        product_name = product_name.split(" ")
        self.__sku = "-".join(product_name).lower()
