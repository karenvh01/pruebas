import pytest
from api.models import db, User, Product, Cart
from api.controllers import CartController
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
    api.add_resource(CartController, '/carts', '/carts/<int:id>')
    
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

def test_add_product_to_cart(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para agregar el producto al carrito
    response = client.post('/carts', json={
        'product_id': product.id,
        'quantity': 1
    }, headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert "Product added to cart" in response.get_data(as_text=True)


def test_get_cart(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Agregar un producto al carrito manualmente
    cart_item = Cart(user_id=user.id, product_id=product.id, quantity=1, price=product.price, total=product.price)
    db.session.add(cart_item)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para obtener el carrito
    response = client.get('/carts', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert product.name in response.get_data(as_text=True)


def test_update_cart_item(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Agregar un producto al carrito manualmente
    cart_item = Cart(user_id=user.id, product_id=product.id, quantity=1, price=product.price, total=product.price)
    db.session.add(cart_item)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para actualizar la cantidad del producto en el carrito
    response = client.put(f'/carts/{cart_item.id}', json={
        'product_id': product.id,
        'quantity': 2
    }, headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert "Cart item quantity updated successfully" in response.get_data(as_text=True)


def test_remove_product_from_cart(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']

    # Agregar un producto al carrito manualmente
    cart_item = Cart(user_id=user.id, product_id=product.id, quantity=1, price=product.price, total=product.price)
    db.session.add(cart_item)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para eliminar el producto del carrito
    response = client.delete(f'/carts/{cart_item.id}', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert "Product removed from cart successfully" in response.get_data(as_text=True)


def test_add_nonexistent_product_to_cart(client, setup_data):
    user = setup_data['user']
    access_token = create_access_token(identity=str(user.id))

    response = client.post('/carts', json={
        'product_id': 9999,  # ID que no existe
        'quantity': 1
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 404
    assert "Product not found" in response.get_data(as_text=True)

def test_update_nonexistent_cart_item(client, setup_data):
    user = setup_data['user']
    access_token = create_access_token(identity=str(user.id))

    response = client.put('/carts/9999', json={
        'product_id': 1,
        'quantity': 2
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 404
    assert "Cart item not found" in response.get_data(as_text=True)

def test_cart_item_total_calculation(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']
    access_token = create_access_token(identity=str(user.id))

    # Agregar producto al carrito
    response = client.post('/carts', json={
        'product_id': product.id,
        'quantity': 3
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200

    # Verificar en la base de datos
    cart_item = Cart.query.filter_by(user_id=user.id, product_id=product.id).first()
    assert cart_item.total == product.price * 3
def test_add_product_to_cart_exceeding_stock(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']
    access_token = create_access_token(identity=str(user.id))

    # Intentar agregar más cantidad que el stock disponible
    response = client.post('/carts', json={
        'product_id': product.id,
        'quantity': product.stock + 1
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 400
    assert f"Quantity exceeds available stock. Only {product.stock} items are available." in response.get_data(as_text=True)

def test_add_product_to_cart_with_negative_values(client, setup_data):
    user = setup_data['user']
    access_token = create_access_token(identity=str(user.id))

    response = client.post('/carts', json={
        'product_id': -1,
        'quantity': -5
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 400
    assert "Product ID must be greater than 0." in response.get_data(as_text=True)

def test_access_cart_with_expired_jwt(client, setup_data):
    user = setup_data['user']
    expired_token = create_access_token(identity=str(user.id), expires_delta=-1)

    response = client.get('/carts', headers={'Authorization': f'Bearer {expired_token}'})
    assert response.status_code == 401
    assert "Token has expired" in response.get_data(as_text=True)

def test_add_product_with_zero_stock(client, setup_data):
    user = setup_data['user']
    product = setup_data['product']
    product.stock = 0
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    response = client.post('/carts', json={
        'product_id': product.id,
        'quantity': 1
    }, headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 400
    assert "Quantity exceeds available stock" in response.get_data(as_text=True)
