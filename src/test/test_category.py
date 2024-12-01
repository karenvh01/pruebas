import pytest
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token
from api.models import db, Category
from api.controllers import Categories


# Configuración del entorno de prueba
@pytest.fixture
def app():
    app = Flask(__name__)
    
    # Configuración de la base de datos y JWT
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'
    
    jwt = JWTManager(app)

    # Inicializar la API y recursos
    api = Api(app)
    api.add_resource(Categories, '/categories', '/categories/<int:category_id>')
    
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
    with app.app_context():
        category = Category(name="Books", description="All about books")
        db.session.add(category)
        db.session.commit()
        return {"category": category}


# Pruebas con autenticación
def test_get_all_categories(client, setup_data):
    """Prueba para obtener todas las categorías."""
    access_token = create_access_token(identity="test_user")
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/categories', headers=headers)
    
    assert response.status_code == 200
    assert "Books" in response.get_data(as_text=True)


def test_get_category_by_id(client, setup_data, app):
    """Prueba para obtener una categoría por ID."""
    with app.app_context():
        category = db.session.merge(setup_data['category'])
        
    access_token = create_access_token(identity="test_user")     
    headers = {'Authorization': f'Bearer {access_token}'}        

    response = client.get(f'/categories/{category.id}', headers=headers)
    
    assert response.status_code == 200
    assert category.name in response.get_data(as_text=True)


def test_get_nonexistent_category(client):
    """Prueba para obtener una categoría inexistente."""
    access_token = create_access_token(identity="test_user")
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get('/categories/999', headers=headers)
    
    assert response.status_code == 404
    assert "Category not found" in response.get_data(as_text=True)


def test_create_duplicate_category(client, setup_data):
    """Prueba para crear una categoría duplicada."""
    access_token = create_access_token(identity="test_user")
    headers = {'Authorization': f'Bearer {access_token}'}

    data = {"name": "Books", "description": "Duplicate category"}
    response = client.post('/categories', json=data, headers=headers)
    
    assert response.status_code == 400
    assert "Category already exists" in response.get_data(as_text=True)


def test_create_category(client):
    """Prueba para crear una categoría nueva."""
    access_token = create_access_token(identity="test_user")     
    headers = {'Authorization': f'Bearer {access_token}'}        

    data = {"name": "Electronics", "description": "Gadgets and devices"}
    response = client.post('/categories', json=data, headers=headers)

    assert response.status_code == 201
    response_json = response.get_json()  # Convierte la respuesta a JSON

    assert "Category created successfully" in response_json.get("message")
    assert response_json.get("id") is not None  # Asegúrate de que el ID de la categoría esté presente

def test_create_category(client):
    """Prueba para crear una categoría nueva."""
    access_token = create_access_token(identity="test_user")     
    headers = {'Authorization': f'Bearer {access_token}'}        

    data = {"name": "Electronics", "description": "Gadgets and devices"}
    response = client.post('/categories', json=data, headers=headers)

    assert response.status_code == 201
    response_json = response.get_json()  # Convierte la respuesta a JSON

    assert "Category created successfully" in response_json.get("message")
    assert response_json.get("id") is not None  # Asegúrate de que el ID de la categoría esté presente

def test_create_category_invalid_data(client):
    """Prueba para crear una categoría con datos inválidos."""
    access_token = create_access_token(identity="test_user")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Caso 1: Nombre vacío
    data = {"name": "", "description": "Valid description"}
    response = client.post('/categories', json=data, headers=headers)
    assert response.status_code == 400
    assert "Name cannot be empty" in response.get_data(as_text=True)
    
    # Caso 2: Descripción vacía
    data = {"name": "Valid Name", "description": ""}
    response = client.post('/categories', json=data, headers=headers)
    assert response.status_code == 400
    assert "Description cannot be empty" in response.get_data(as_text=True)

