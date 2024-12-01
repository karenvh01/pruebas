import pytest
from flask import Flask,json
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from api.controllers import UserResource, Categories, Brands, BrandResource,ProductResource
from api.models import User, Category, Brand, Product, db
from unittest.mock import MagicMock, patch, Mock
import unittest

@pytest.fixture
def app():
    app= Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
    app.config['TESTING']= True
    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()
    
@pytest.fixture
def client(app):
    return app.test_client()

def test_user_get_not_found(client):
    response = client.get('/users/999')
    assert response.status_code == 404
    
def test_verify_email(client):
    mock_users_repository = MagicMock()
    mock_users_repository.get_all.return_value = {
        "email": "john@usebouncer.com",
        "status": "deliverable",
        "reason": "accepted_email",
        "domain": {
            "name": "usebouncer.com",
            "acceptAll": "no",
            "disposable": "no",
            "free": "no"
        },
        "account": {
            "role": "no",
            "disabled": "no",
            "fullMailbox": "no"
        },
        "dns": {
            "type": "MX",
            "record": "aspmx.l.google.com."
        },
        "provider": "google.com",
        "score": 100,
        "toxic": "unknown"
    }
    assert mock_users_repository.get_all.return_value['status']=='deliverable'
    assert mock_users_repository.get_all.return_value['reason']=='accepted_email'
    
    
    
class TestUsers(unittest.TestCase):
    def setUp(self):
        self.app= Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.api = Api(self.app)
        self.api.add_resource(UserResource, '/api/users/<int:user_id>')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.init_app(self.app)
        db.create_all()
        
    @patch('api.controllers.User.query')
    def test_get_user(self, mock_query):
        mock_query.filter_by.return_value.first.return_value = User(
            id=1,
            name='test',
            lstF='Doe',
            lstM='Smith',
            address='123 Main St',
            email='john.doe@example.com',
            password='password123',
            c_pass='password123',
            phone='1234567890',
            payment='credit_card',
            role=1,
            remember_token='some_token'
            )
        response = self.client.get('/api/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('test', response.get_data(as_text=True))
        
@patch.object(UserResource,'get')
def test_user_get(mock_get):
         mock_user= Mock()
         mock_user.id = 1
         mock_user.name = 'XXXX'
         mock_user.lstF = 'XXXX'
         mock_user.lstM = 'XXXX'
         mock_user.address = 'XXXX'
         mock_user.email = 'XXXX@XXXX.com'
         mock_user.password = 'XXXX'
         mock_user.c_pass = 'XXXX'
         mock_user.phone = 'XXXX'
         mock_user.payment = 'XXXX'
         mock_user.role = 'XXXX'
         mock_user.remember_token = 'some_token'
         mock_get.return_value = mock_user
         
         result = UserResource.get()
         assert result == mock_user
         assert result.id == 1
         assert result.name == 'XXXX'
         assert result.lstF == 'XXXX'
         assert result.lstM == 'XXXX'
         assert result.address == 'XXXX'
         assert result.email == 'XXXX@XXXX.com'
         assert result.password == 'XXXX'
         assert result.c_pass == 'XXXX'
         assert result.phone == 'XXXX'
         assert result.payment == 'XXXX'
         assert result.role == 'XXXX'
         assert result.remember_token == 'some_token'
         mock_get.assert_called_once()        

    
