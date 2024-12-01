import pytest
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token
from api.models import db, Product, Category, Brand
from api.controllers import ProductResource
import json


@pytest.fixture
def app():
    app = Flask(__name__)
    
    # Configurar base de datos y JWT
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'
    
    jwt = JWTManager(app)

    api = Api(app)
    api.add_resource(ProductResource, '/products', '/products/<int:product_id>')
    
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
    category = Category(name="Electronics", description="Gadgets and devices")
    brand = Brand(username="BrandA", address="123 Brand St", phone="1234567890")
    db.session.add(category)
    db.session.add(brand)
    db.session.commit()
    return {"category": category, "brand": brand}


def test_get_product(client, setup_data):
    """Prueba para obtener un producto."""
    category = setup_data['category']
    brand = setup_data['brand']
    
    # Crear un producto en la base de datos
    product = Product(
        name="Laptop",
        price=1200.99,
        description="A high-performance laptop",
        stock=5,
        category_id=category.id,
        brand_id=brand.id,
        img="http://example.com/laptop.jpg"
    )
    db.session.add(product)
    db.session.commit()

    # Crear un token JWT
    access_token = create_access_token(identity="test_user")
    
    # Realizar la solicitud GET
    response = client.get(f'/products/{product.id}', headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    assert product.name in response.get_data(as_text=True)


def test_create_product_success(client, setup_data):
    """Prueba para crear un producto correctamente."""
    category = setup_data['category']
    brand = setup_data['brand']
    
    # Crear un token JWT
    access_token = create_access_token(identity="test_user")
    
    data = {
        "name": "Smartphone",
        "price": 999.99,
        "description": "High-end smartphone",
        "stock": 50,
        "category_id": category.id,
        "brand_id": brand.id,
        "img": "http://example.com/smartphone.jpg",
    }

    response = client.post('/products', json=data, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 201
    assert "Smartphone" in response.get_data(as_text=True)


def test_delete_product_success(client, setup_data):
    """Prueba para eliminar un producto exitosamente."""
    category = setup_data['category']
    brand = setup_data['brand']
    
    # Crear un producto en la base de datos
    product = Product(
        name="Camera",
        price=499.99,
        description="High-resolution camera",
        stock=10,
        category_id=category.id,
        brand_id=brand.id,
        img="http://example.com/camera.jpg"
    )
    db.session.add(product)
    db.session.commit()

    # Crear un token JWT
    access_token = create_access_token(identity="test_user")

    # Realizar la solicitud DELETE
    response = client.delete(f'/products/{product.id}', headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 204
    
    # Verificar que ya no existe en la base de datos
    deleted_product = Product.query.get(product.id)
    assert deleted_product is None


def test_product_already_exists(client, setup_data):
    """Prueba para validar que no se cree un producto duplicado."""
    category = setup_data['category']
    brand = setup_data['brand']
    
    # Crear un producto en la base de datos
    product = Product(
        name="Smartwatch",
        price=150.0,
        description="A wearable device",
        stock=20,
        category_id=category.id,
        brand_id=brand.id,
        img="http://example.com/smartwatch.jpg"
    )
    db.session.add(product)
    db.session.commit()

    # Crear un token JWT
    access_token = create_access_token(identity="test_user")

    # Intentar crear el mismo producto nuevamente
    data = {
        "name": "Smartwatch",
        "price": 150.0,
        "description": "A wearable device",
        "stock": 20,
        "category_id": category.id,
        "brand_id": brand.id,
        "img": "http://example.com/smartwatch.jpg",
    }

    response = client.post('/products', json=data, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 400
    assert "Product already exists" in response.get_data(as_text=True)


def test_get_products_by_category(client, setup_data):
    category = setup_data['category']
    brand = setup_data['brand']

    # Crear productos
    product1 = Product(name="Laptop", price=1200.99, description="A high-performance laptop",
                       stock=5, category_id=category.id, brand_id=brand.id, img="http://example.com/laptop.jpg")
    product2 = Product(name="Phone", price=799.99, description="A high-end smartphone",
                       stock=10, category_id=category.id, brand_id=brand.id, img="http://example.com/phone.jpg")
    db.session.add_all([product1, product2])
    db.session.commit()

    # Crear token JWT
    access_token = create_access_token(identity="test_user")

    # Realizar la solicitud con filtro
    response = client.get(f'/products?category_id={category.id}', headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2  # Debería devolver ambos productos de la categoría

def test_create_product_invalid_data(client, setup_data):
    category = setup_data['category']
    brand = setup_data['brand']

    access_token = create_access_token(identity="test_user")

    # Producto con precio inválido
    data = {
        "name": "Smartphone",
        "price": -100,  # Precio inválido
        "description": "A high-end smartphone",
        "stock": 10,
        "category_id": category.id,
        "brand_id": brand.id,
        "img": "http://example.com/smartphone.jpg",
    }
    response = client.post('/products', json=data, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 400
    assert "Price must be greater than 0" in response.get_data(as_text=True)

