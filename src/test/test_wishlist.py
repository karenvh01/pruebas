import pytest
from api.models import db, User, Product, Wishlist
from api.controllers import WishlistController
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token


@pytest.fixture
def app():
    app = Flask(__name__)
    
    # Configurar base de datos y JWT
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'
    
    jwt = JWTManager(app)

    api = Api(app)
    api.add_resource(WishlistController, '/wishlist', '/wishlist/<int:wishlist_id>')
    
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
    """Crea un usuario y un producto en la base de datos."""
    user = User(
        name="Test User",
        lstF="Doe",
        lstM="Smith",
        address="123 Main St",
        email="test@example.com",
        password="password123",
        c_pass="password123",
        phone="555-1234",
        payment="credit_card",
        role=1,
        remember_token="some_token"
    )
    product = Product(
        name="Test Product",
        price=100.0,
        description="A sample product for testing.",
        stock=50,
        category_id=1,
        brand_id=1,
        img="http://example.com/product.jpg"
    )
    db.session.add(user)
    db.session.add(product)
    db.session.commit()
    return {"user": user, "product": product}


def test_add_product_to_wishlist(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para agregar el producto al wishlist
    response = client.post('/wishlist', json={
        'user_id': user.id,
        'product_id': product.id
    }, headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 201
    assert "Product added to your wishlist" in response.get_data(as_text=True)


def test_get_wishlist(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Agregar un producto al wishlist manualmente
    wishlist_item = Wishlist(user_id=user.id, product_id=product.id)
    db.session.add(wishlist_item)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para obtener el wishlist
    response = client.get('/wishlist', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert product.name in response.get_data(as_text=True)


def test_remove_product_from_wishlist(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Agregar un producto al wishlist manualmente
    wishlist_item = Wishlist(user_id=user.id, product_id=product.id)
    db.session.add(wishlist_item)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para eliminar el producto del wishlist
    response = client.delete(f'/wishlist/{wishlist_item.id}', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert "Product removed from wishlist" in response.get_data(as_text=True)

def test_add_nonexistent_product_to_wishlist(client, setup_data):
    user = setup_data['user']
    access_token = create_access_token(identity=str(user.id))

    response = client.post('/wishlist', json={
        'product_id': 9999  # ID que no existe en la base de datos
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 404
    assert "The product does not exist" in response.get_data(as_text=True)


def test_add_product_already_in_wishlist(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']
    access_token = create_access_token(identity=str(user.id))

    # Agregar el producto manualmente a la wishlist
    wishlist_item = Wishlist(user_id=user.id, product_id=product.id)
    db.session.add(wishlist_item)
    db.session.commit()

    # Intentar agregarlo nuevamente
    response = client.post('/wishlist', json={
        'product_id': product.id
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 400
    assert "The product is already on your wishlist" in response.get_data(as_text=True)


def test_remove_nonexistent_wishlist_item(client, setup_data):
    user = setup_data['user']

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Intentar eliminar un elemento que no existe
    response = client.delete('/wishlist/9999', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 404
    assert "Wishlist item not found" in response.get_data(as_text=True)

def test_wishlist_is_user_specific(client, setup_data):
    user1 = setup_data['user']

    # Crear un segundo usuario
    user2 = User(
        name="Another User",
        lstF="Another",
        lstM="User",
        address="456 Main St",
        email="another@example.com",
        password="password123",
        c_pass="password123",
        phone="555-5678",
        payment="credit_card",
        role=1,
        remember_token="some_other_token"
    )
    db.session.add(user2)
    db.session.commit()

    # Agregar un producto al wishlist del primer usuario
    wishlist_item = Wishlist(user_id=user1.id, product_id=setup_data['product'].id)
    db.session.add(wishlist_item)
    db.session.commit()

    # Crear tokens para ambos usuarios
    token_user1 = create_access_token(identity=str(user1.id))
    token_user2 = create_access_token(identity=str(user2.id))

    # Verificar que el usuario 1 vea su wishlist
    response1 = client.get('/wishlist', headers={'Authorization': f'Bearer {token_user1}'})
    assert response1.status_code == 200
    assert len(response1.get_json()['wishlist']) == 1

    # Verificar que el usuario 2 vea una wishlist vacía
    response2 = client.get('/wishlist', headers={'Authorization': f'Bearer {token_user2}'})
    assert response2.status_code == 200
    assert "Your wishlist is empty" in response2.get_data(as_text=True)


