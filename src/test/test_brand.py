import pytest
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token
from api.models import db, Brand
from api.controllers import BrandResource, Brands


@pytest.fixture
def app():
    app = Flask(__name__)
    
    # Configurar base de datos y JWT
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'
    
    jwt = JWTManager(app)

    api = Api(app)
    api.add_resource(Brands, '/api/brands')
    api.add_resource(BrandResource, '/api/brands/<int:brand_id>')
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def setup_data(app):
    """Crea datos iniciales para pruebas."""
    brand = Brand(username="BrandA", address="123 Brand St", phone="1234567890")
    db.session.add(brand)
    db.session.commit()
    return {"brand": brand}


def test_get_brands(client, setup_data):
    """Prueba para obtener todas las marcas."""
    access_token = create_access_token(identity="test_user")
    
    response = client.get('/api/brands', headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    assert "BrandA" in response.get_data(as_text=True)


def test_get_brand_by_id(client, setup_data):
    """Prueba para obtener una marca por ID."""
    brand = setup_data['brand']
    access_token = create_access_token(identity="test_user")
    
    response = client.get(f'/api/brands/{brand.id}', headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    assert brand.username in response.get_data(as_text=True)


def test_create_brand(client):
    """Prueba para crear una marca."""
    access_token = create_access_token(identity="test_user")
    
    data = {
        "username": "BrandB",
        "address": "456 Brand Ave",
        "phone": "0987654321"
    }
    
    response = client.post('/api/brands', json=data, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 201
    assert "BrandB" in response.get_data(as_text=True)


def test_update_brand(client, setup_data):
    """Prueba para actualizar una marca."""
    brand = setup_data['brand']
    access_token = create_access_token(identity="test_user")
    
    data = {
        "username": "UpdatedBrand",
        "address": "Updated Address",
        "phone": "555-0000"
    }
    
    response = client.patch(f'/api/brands/{brand.id}', json=data, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    assert "UpdatedBrand" in response.get_data(as_text=True)


def test_delete_brand(client, setup_data):
    """Prueba para eliminar una marca."""
    brand = setup_data['brand']
    access_token = create_access_token(identity="test_user")
    
    response = client.delete(f'/api/brands/{brand.id}', headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 204
    assert Brand.query.get(brand.id) is None


def test_get_brands_authorized(client):
    # Genera un token JWT de prueba
    access_token = create_access_token(identity="test_user")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Realiza la solicitud GET con el token
    response = client.get('/api/brands', headers=headers)

    assert response.status_code == 200

def test_create_duplicate_brand(client, setup_data):
    access_token = create_access_token(identity="test_user")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    brand = setup_data['brand']
    data = {"username": brand.username, "address": "New Address", "phone": "1234567890"}
    response = client.post('/api/brands', json=data, headers=headers)
    assert response.status_code == 400
    assert "Brand with this username already exists" in response.get_data(as_text=True)


def test_create_brand_with_empty_fields(client):
    access_token = create_access_token(identity="test_user")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    data = {"username": "", "address": "123 Main St", "phone": "555-1234"}
    response = client.post('/api/brands', json=data, headers=headers)
    assert response.status_code == 400
    assert "Username cannot be empty" in response.get_data(as_text=True)
    
    data = {"username": "BrandC", "address": "", "phone": "555-1234"}
    response = client.post('/api/brands', json=data, headers=headers)
    assert response.status_code == 400
    assert "Address cannot be empty" in response.get_data(as_text=True)
    
    data = {"username": "BrandC", "address": "123 Main St", "phone": ""}
    response = client.post('/api/brands', json=data, headers=headers)
    assert response.status_code == 400
    assert "Phone cannot be empty" in response.get_data(as_text=True)

