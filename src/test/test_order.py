import pytest
from api.models import db, User, Product, Cart, Order
from api.controllers import OrderController
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
    api.add_resource(OrderController, '/orders', '/orders/<int:order_id>')
    
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
    """Crea un usuario, un producto y un carrito en la base de datos."""
    # Crear usuario si no existe
    user = db.session.get(User, 1)

    if not user:
        user = User(
            id=1,  # Asigna un ID fijo para pruebas
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
        db.session.add(user)
        db.session.commit()

    # Verificar que el usuario se ha guardado
    print(f"User in DB: {user.id}, {user.name}")  # Verificación en consola

    # Usar db.session.get para obtener el producto
    product = db.session.get(Product, 1)
    if not product:
        product = Product(
            id=1,  # Asigna un ID fijo para pruebas
            name="Test Product",
            price=100.0,
            description="A sample product for testing.",
            stock=50,
            category_id=1,
            brand_id=1,
            img="http://example.com/product.jpg"
        )
        db.session.add(product)
        db.session.commit()

    # Usar db.session.get para obtener el carrito
    cart_item = db.session.query(Cart).filter_by(user_id=user.id, product_id=product.id).first()
    if not cart_item:
        cart_item = Cart(
            user_id=user.id,
            product_id=product.id,
            quantity=2,
            price=product.price,
            total=product.price * 2
        )
        db.session.add(cart_item)
        db.session.commit()

    return {"user": user, "product": product, "cart_item": cart_item}


def test_create_order(client, setup_data):
    # Verificar si el usuario y carrito existen
    print(f"User ID in setup_data: {setup_data['user'].id}")
    print(f"Cart item ID: {setup_data['cart_item'].id}")
    
    user = setup_data['user']
    cart_item = setup_data['cart_item']

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para crear una orden
    response = client.post('/orders', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 201
    assert "Order created successfully" in response.get_data(as_text=True)
    assert "order_id" in response.get_json()
    assert "total_amount" in response.get_json()


def test_get_orders(client, setup_data):
    user = setup_data['user']

    # Crear un pedido manualmente
    order = Order(
        user_id=user.id,
        total_amount=setup_data['cart_item'].total
    )
    db.session.add(order)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para obtener las órdenes
    response = client.get('/orders', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert "data" in response.get_json()
    assert len(response.get_json()['data']) > 0  # Verificar que al menos una orden esté en la respuesta


def test_delete_order(client, setup_data):
    user = setup_data['user']
    order = Order(
        user_id=user.id,
        total_amount=setup_data['cart_item'].total
    )
    db.session.add(order)
    db.session.commit()

    # Crear un token JWT para el usuario
    access_token = create_access_token(identity=str(user.id))

    # Realizar la solicitud para eliminar la orden
    response = client.delete(f'/orders/{order.id}', headers={'Authorization': f'Bearer {access_token}'})

    # Comprobar la respuesta
    assert response.status_code == 200
    assert "Order deleted successfully" in response.get_data(as_text=True)

def test_create_order_with_empty_cart(client, setup_data):
    user = setup_data['user']
    
    # Eliminar todos los productos del carrito
    Cart.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    # Intentar crear una orden con el carrito vacío
    response = client.post('/orders', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 400
    assert "Your cart is empty" in response.get_data(as_text=True)
def test_delete_nonexistent_order(client, setup_data):
    user = setup_data['user']

    access_token = create_access_token(identity=str(user.id))

    # Intentar eliminar una orden inexistente
    response = client.delete('/orders/999', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 404
    assert "Order not found" in response.get_data(as_text=True)

def test_validate_order_total(client, setup_data):
    user = setup_data['user']
    cart_item = setup_data['cart_item']

    # Cambiar el precio del producto y actualizar el carrito
    cart_item.price = 200.0
    cart_item.total = 200.0 * cart_item.quantity
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    # Crear una orden
    response = client.post('/orders', headers={'Authorization': f'Bearer {access_token}'})
    data = response.get_json()

    assert response.status_code == 201
    assert data["total_amount"] == 200.0 * cart_item.quantity


