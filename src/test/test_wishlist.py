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