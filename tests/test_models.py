# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """Test reading a product"""
        product = ProductFactory()
        app.logger.info("product: {product}")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        fetched = Product.find(product.id)
        self.assertEqual(fetched.name, product.name)
        self.assertEqual(fetched.description, product.description)
        self.assertEqual(fetched.price, product.price)
        self.assertEqual(fetched.available, product.available)
        self.assertEqual(fetched.category, product.category)

    def test_update_a_product(self):
        """Test updating a product"""
        product = ProductFactory()
        app.logger.info("product: {product}")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        text = "test-description"
        product.description = text
        orig_id = product.id
        product.update()
        self.assertEqual(product.id, orig_id)
        self.assertEqual(product.description, text)
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, orig_id)

    def test_update_a_product_without_id(self):
        """Test updating a product without id"""
        product = ProductFactory()
        app.logger.info("product: {product}")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """Test deleting a product"""
        product = ProductFactory()
        app.logger.info("product: {product}")
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """Test listing all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        # create 5 products and save them to db
        total_count = 5
        for _ in range(total_count):
            product = ProductFactory()
            product.create()
        products = Product.all()
        self.assertEqual(len(products), total_count)

    def test_find_product_by_name(self):
        """Test finding a product by name"""
        products = [ProductFactory() for _ in range(5)]
        name = products[0].name
        count = 0
        for product in products:
            product.create()
            if product.name == name:
                count += 1
        # retrieve product from db
        products = Product.find_by_name(name)
        self.assertEqual(products.count(), count)
        for product in products:
            self.assertEqual(product.name, name)

    def test_find_product_by_availability(self):
        """Test finding a product by availability"""
        products = ProductFactory.create_batch(10)
        avai = products[0].available
        count = 0
        for product in products:
            product.create()
            if product.available == avai:
                count += 1
        # retrieve product from db
        products = Product.find_by_availability(avai)
        self.assertEqual(products.count(), count)
        for product in products:
            self.assertEqual(product.available, avai)

    def test_find_product_by_category(self):
        """Test finding a product by category"""
        products = ProductFactory.create_batch(10)
        category = products[0].category
        count = 0
        for product in products:
            product.create()
            if product.category == category:
                count += 1
        # retrieve product from db
        products = Product.find_by_category(category)
        self.assertEqual(products.count(), count)
        for product in products:
            self.assertEqual(product.category, category)

    def test_find_product_by_price(self):
        """Test finding a product by price"""
        products = ProductFactory.create_batch(10)
        price = products[0].price
        count = 0
        for product in products:
            product.create()
            if product.price == price:
                count += 1
        # retrieve product from db
        products = Product.find_by_price(price)
        self.assertEqual(products.count(), count)
        for product in products:
            self.assertEqual(product.price, price)

    def test_find_product_by_price_str(self):
        """Test finding a product by price string"""
        product = ProductFactory()
        product.create()
        product_fetch = Product.find_by_price(str(product.price))
        self.assertEqual(product_fetch.count(), 1)

    def test_ser_des(self):
        """Test serialize and deserialize"""
        product = ProductFactory()
        data = product.serialize()
        self.assertEqual(data['name'], product.name)
        data['name'] = 'testing'
        product.deserialize(data)
        self.assertEqual(product.name, 'testing')

    def test_des_available_type_exception(self):
        """Test deserialize exception: availabe type"""
        product = ProductFactory()
        data = product.serialize()
        data['available'] = 1
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_des_attribute_error_exception(self):
        """Test deserialize exception: attribute error"""
        product = ProductFactory()
        data = product.serialize()
        data['category'] = "abc"
        self.assertRaises(DataValidationError, product.deserialize, data)
        data['category'] = -1
        self.assertRaises(DataValidationError, product.deserialize, data)
