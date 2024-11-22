import pytest
from flask import Flask
from flask_restful import Api
from api.models import db, Brand
from api.controllers import Brands, BrandResource
from unittest.mock import MagicMock, patch
import unittest


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestBrands(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.api = Api(self.app)
        self.api.add_resource(Brands, '/api/brands/')
        self.api.add_resource(BrandResource, '/api/brands/<int:brand_id>')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.init_app(self.app)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('api.controllers.Brand.query')
    def test_get_brands(self, mock_query):
        mock_query.all.return_value = [
            Brand(id=1, username='Brand1', address='123 Street', phone='555-5555'),
            Brand(id=2, username='Brand2', address='456 Avenue', phone='555-1234')
        ]
        response = self.client.get('/api/brands/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Brand1', response.get_data(as_text=True))
        self.assertIn('Brand2', response.get_data(as_text=True))

    @patch('api.controllers.Brand.query')
    def test_get_brand_by_id(self, mock_query):
        # Simular la consulta para devolver una marca específica
        mock_query.filter_by.return_value.first.return_value = Brand(
            id=1, username='Brand1', address='123 Street', phone='555-5555')
        response = self.client.get('/api/brands/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Brand1', response.get_data(as_text=True))

    @patch('api.controllers.Brand.query')
    def test_get_brand_not_found(self, mock_query):
        # Simular que no se encuentra la marca
        mock_query.filter_by.return_value.first.return_value = None
        response = self.client.get('/api/brands/9999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Brand not found', response.get_data(as_text=True))

    @patch('api.controllers.db.session')
    def test_create_brand(self, mock_session):
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()

        response = self.client.post('/api/brands/', json={
            'username': 'NewBrand',
            'address': '789 Road',
            'phone': '555-6789'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('NewBrand', response.get_data(as_text=True))

    @patch('api.controllers.db.session')
    @patch('api.controllers.Brand.query')
    def test_update_brand(self, mock_query, mock_session):
        mock_query.filter_by.return_value.first.return_value = Brand(
            id=1, username='Brand1', address='123 Street', phone='555-5555')
        mock_session.commit = MagicMock()

        response = self.client.patch('/api/brands/1', json={
            'username': 'UpdatedBrand',
            'address': 'Updated Address',
            'phone': '555-0000'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('UpdatedBrand', response.get_data(as_text=True))

    @patch('api.controllers.db.session')
    @patch('api.controllers.Brand.query')
    def test_delete_brand(self, mock_query, mock_session):
        mock_query.filter_by.return_value.first.return_value = Brand(
            id=1, username='Brand1', address='123 Street', phone='555-5555')
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()

        response = self.client.delete('/api/brands/1')
        self.assertEqual(response.status_code, 204)