import pytest
from unittest.mock import MagicMock, patch
from api.models import Product, Category, Brand, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api.controllers import ProductResource
from flask_restful import Api
import unittest

# TEST DE PRODUCTOS
class TestProduct(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.api = Api(self.app)
        self.api.add_resource(ProductResource, '/products')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.init_app(self.app)
        db.create_all()

        # Crear datos iniciales para pruebas
        with self.app_context:
            self.category = Category(name="Electronics", description="Gadgets and devices")
            self.brand = Brand(username="BrandA", address="123 Brand St", phone="1234567890")
            db.session.add(self.category)
            db.session.add(self.brand)
            db.session.commit()
                        # Asignar category_id y brand_id para pruebas
            
    @patch('api.models.Product.query')
    def test_get(self, product_id):
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return {"message": "Product not found"}, 404
        return {"id": product.id, "name": product.name}, 200
    @patch('api.models.Product.query')
    def test_create_product_success(self, mock_query):
        """Prueba para crear un producto correctamente."""
        mock_query.filter_by.return_value.first.return_value = None

        data = {
            "name": "Smartphone",
            "price": 999.99,
            "description": "High-end smartphone",
            "stock": 50,
            "category_id": self.category.id,
            "brand_id": self.brand.id,
            "img": "http://example.com/smartphone.jpg",
        }

        with self.app_context:
            response = self.client.post('/products', json=data)
            self.assertEqual(response.status_code, 201)
            self.assertIn("Smartphone", response.get_data(as_text=True))
    
    # def test_get_nonexistent_product(self):
    #     response = self.client.get('/products/999')  # Supongamos que el ID 999 no existe
    #     self.assertEqual(response.status_code, 404)  # Verifica el código de estado
    #     self.assertIn("Product not found", response.get_data(as_text=True))  # Verifica el mensaje directamente


    @patch('api.models.Product.query')
    def test_product_already_exists(self, mock_query):
    #"""Probar que el producto no se cree si ya existe."""
    # Simular que el producto ya existe en la base de datos
        mock_query.filter_by.return_value.first.return_value = Product(
        id=1, name="Product 1", price=100.0, description="A great product", stock=10,
        category_id=self.category.id, brand_id=self.brand.id, img="http://example.com/image.jpg"
        )

        data = {
            "name": "Product 1",
            "price": 100.0,
            "description": "A great product",
            "stock": 10,
            "category_id": self.category.id,
            "brand_id": self.brand.id,
            "img": "http://example.com/image.jpg"
        }

        response = self.client.post('/products', json=data)

    # Verifica el código de estado
        self.assertEqual(response.status_code, 400)
        self.assertIn("Product already exists", response.get_data(as_text=True))

    