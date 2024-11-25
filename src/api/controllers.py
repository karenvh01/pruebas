from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with,marshal
from api.models import User, Category, Brand, Product, Order, Cart, OrderProduct, Wishlist, db
import json
import re


user_args = reqparse.RequestParser()
user_args.add_argument("name", type=str, required=True, help="Name is required")
user_args.add_argument("lstF", type=str, required=True, help="Last name (Father's side) is required")
user_args.add_argument("lstM", type=str, required=True, help="Last name (Mother's side) is required")
user_args.add_argument("address", type=str, required=True, help="Address is required")
user_args.add_argument("email", type=str, required=True, help="Email is required")
user_args.add_argument("password", type=str, required=True, help="Password is required")
user_args.add_argument("c_pass", type=str, required=True, help="Confirm password is required")
user_args.add_argument("phone", type=str, required=True, help="Phone is required")
user_args.add_argument("payment", type=str, required=True, help="Payment method is required")
user_args.add_argument("role", type=int, required=False, default=0)
user_args.add_argument("remember_token", type=str, required=False)

# Campos a devolver en la respuesta
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'lstF': fields.String,
    'lstM': fields.String,
    'address': fields.String,
    'email': fields.String,
    'password': fields.String,
    'c_pass': fields.String,
    'phone': fields.String,
    'payment': fields.String,
    'role': fields.Integer,
    'remember_token': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}

class UserResource(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        return user, 200

    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        if not args['name'] or args['name'].isspace():
            response = Response(json.dumps({'error': 'name cannot be empty'}),
            status= 400,
            mimetype='application/json')
            return abort(response)
        if not args['lstF'] or args['lstF'].isspace():
            response = Response(json.dumps({'error': 'lstF cannot be empty'}),
            status= 400,
            mimetype='application/json')
            return abort(response)
        if not args['lstM'] or args['lstM'].isspace():
            response = Response(json.dumps({'error': 'lstM cannot be empty'}),
            status= 400,
            mimetype='application/json')
            return abort(response)
        if not args['address'] or args['address'].isspace():
            response = Response(json.dumps({'error': 'Address cannot be empty'}),
            status= 400,
            mimetype='application/json')
            return abort(response)
        if not args['email'] or args['email'].isspace():
            response = Response(json.dumps({'error': 'Email cannot be empty'}),
            status= 400,
            mimetype='application/json')
            return abort(response)
        email= args['email'].strip()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",email):
            response = Response(json.dumps({'error': 'Invalid email format'}),
            status= 400,
            mimetype='application/json')
            return abort(response)
        if len(args['password']) < 8:
            response = Response(json.dumps({'error': 'Password must be at least 8 characters long'}), status=400, mimetype='application/json')
            return abort(response)
        if args['password'] != args['c_pass']:
            response = Response(json.dumps({'error': 'Passwords do not match'}), status=400, mimetype='application/json')
            return abort(response)
        if not re.match(r"^\+?[1-9]\d{1,14}$", args['phone']):
            response = Response(json.dumps({'error': 'Invalid phone number format'}), status=400, mimetype='application/json')
            return abort(response)

        if args['payment'] not in ['credit_card', 'paypal', 'bank_transfer']:
            response = Response(json.dumps({'error': 'Invalid payment method'}), status=400, mimetype='application/json')
            return abort(response)
        
        if args['role'] not in [0, 1]:  # Asegura que el rol es válido
            response = Response(json.dumps({'error': 'Invalid role'}), status=400, mimetype='application/json')
            return abort(response)
 
        # Crear el nuevo usuario
        user = User(
            name=args['name'],
            lstF=args['lstF'],
            lstM=args['lstM'],
            address=args['address'],
            email=email,
            password=args['password'],
            c_pass=args['c_pass'],
            phone=args['phone'],
            payment=args['payment'],
            role=args['role'],
            remember_token=args.get('remember_token')
        )

        db.session.add(user)
        db.session.commit()
        return user, 201

    @marshal_with(user_fields)
    def patch(self, user_id):
        args = user_args.parse_args()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")

        # Actualizar todos los campos
        user.name = args['name']
        user.lstF = args['lstF']
        user.lstM = args['lstM']
        user.address = args['address']
        user.email = args['email']
        user.password = args['password']
        user.c_pass = args['c_pass']
        user.phone = args['phone']
        user.payment = args['payment']
        user.role = args['role']
        user.remember_token = args.get('remember_token')

        db.session.commit()
        return user, 200
    def delete(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()

        return '', 204



product_args = reqparse.RequestParser()
product_args.add_argument("name", type=str, required=True, help="Name is required and should be a valid string")
product_args.add_argument("price", type=float, required=True, help="Price is required and should be numeric")
product_args.add_argument("description", type=str, required=True, help="Description is required")
product_args.add_argument("stock", type=int, required=True, help="Stock is required and should be numeric")
product_args.add_argument("category_id", type=int, required=True, help="Category ID is required")
product_args.add_argument("brand_id", type=int, required=True, help="Brand ID is required")
product_args.add_argument("img", type=str, required=True, help="Image URL is required")

# Campos a devolver en las respuestas
product_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'description': fields.String,
    'stock': fields.Integer,
    # 'category_id': fields.Integer,
    # 'brand_id': fields.Integer,
    'img': fields.String,
    'category_name':fields.String,
    'brand_username':fields.String,
    # 'category_name': fields.String(attribute=lambda x: x.category.name if hasattr(x.category, 'name') else None),
    # 'brand_name': fields.String(attribute=lambda x: x.brand.username if x.brand else None),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}

class ProductResource(Resource):
    def get(self, product_id=None):
        if product_id:
            product = Product.query.filter_by(id=product_id).first()
            if not product:
                # Retorna un mensaje de error directamente
                return {"message": "Product not found"}, 404
            # Completar información adicional
            category = Category.query.get(product.category_id)
            brand = Brand.query.get(product.brand_id)
            product.category_name = category.name if category else None
            product.brand_username = brand.username if brand else None
            # Formatear solo la respuesta válida
            return marshal(product, product_fields), 200
        else:
            products = Product.query.all()
            for product in products:
                category = Category.query.get(product.category_id)
                brand = Brand.query.get(product.brand_id)
                product.category_name = category.name if category else None
                product.brand_username = brand.username if brand else None
            return marshal(products, product_fields), 200
  
    
    def post(self):
        args = product_args.parse_args()
        
        # # Validaciones adicionales si es necesario
        if not args['name'] or args['name'].isspace():
            response = Response(json.dumps({'error': 'Name cannot be empty'}),
                             status=400,
                             mimetype='application/json')
            return abort(response)
            
         # Validación para el precio (debe ser numérico y positivo)
        try:
            price = float(args['price'])
            if price <= 0:
                return abort(400, message="Price must be greater than 0")
        except ValueError:
            return abort(400,message="Price must be a valid number")

        if not args['description'] or args['description'].isspace():
            response = Response(json.dumps({'error': 'description cannot be empty'}),
                             status=400,
                             mimetype='application/json')
            return abort(response)
            
        # Validación para el stock (debe ser un entero no negativo)
        try:
            stock = int(args['stock'])
            if stock < 0:
                return abort(400, message="Stock cannot be negative")
        except ValueError:
            return {"error": "Stock must be a valid integer"}, 400
         # Validación para la URL de la imagen (opcional, pero puede ser verificada si se requiere)
        if args['img'] and not args['img'].startswith(('http://', 'https://')):
            return abort(400, message="Image URL must start with 'http://' or 'https://'")
        
        # if not args['category_id'] and str(args['category_id']).isspace():
        if not args['category_id'] or args['category_id'] == " ":
            # return abort(404,message="category id cannot by empty")
            return {"error": "Category ID cannot be empty"}, 400
        
        if not args['brand_id'] or str(args['brand_id']).isspace():
            return ({"error": "Brand ID cannot be empty or just spaces"}), 400
        # Validaciones para categoría y marca (deben existir en la base de datos)
        category = Category.query.get(args['category_id'])
        if not category:
            return abort(404, message="categroy not found.")

        brand = Brand.query.get(args['brand_id'])
        if not brand:
            return abort(404, message="brand not found.")
        
        existing_product = Product.query.filter_by(name=args['name']).first()
        if existing_product:
            # return abort(400,message="product already exists")
            return {"message": "Product already exists"}, 400

        # Crear el nuevo producto
        new_product = Product(
            name=args['name'],
            price=args['price'],
            description=args['description'],
            stock=args['stock'],
            category_id=args['category_id'],
            brand_id=args['brand_id'],
            img=args['img']
        )
        
        # Guardar el producto en la base de datos
        db.session.add(new_product)
        db.session.commit()
        return marshal(new_product, product_fields), 201


    @marshal_with(product_fields)
    def patch(self, product_id):
        args = product_args.parse_args()
        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Product not found")
        
        # Actualizar campos del producto
        product.name = args['name']
        product.price = args['price']
        product.description = args['description']
        product.stock = args['stock']
        product.category_id = args['category_id']
        product.brand_id = args['brand_id']
        product.img = args['img']
        db.session.commit()
        return product, 200

    def delete(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Product not found")
        db.session.delete(product)
        db.session.commit()
        return '', 204

class WishlistController(Resource):
    # Parser para validar entrada de datos
    wishlist_args = reqparse.RequestParser()
    wishlist_args.add_argument('product_id', type=int, required=True, help="Product ID is required.")

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        args = self.wishlist_args.parse_args()
        product_id = args['product_id']

        # Verificar si ya existe el producto en la lista de deseos
        existing_wishlist = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing_wishlist:
            abort(400, message="The product is already on your wishlist.")

        try:
            # Crear un nuevo registro en la lista de deseos
            new_wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
            db.session.add(new_wishlist_item)
            db.session.commit()
            return {"message": "Product added to your wishlist."}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred: {str(e)}")

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        try:
            # Consultar la lista de deseos del usuario
            wishlist = Wishlist.query.filter_by(user_id=user_id).all()

            if not wishlist:
                return {"message": "Your wishlist is empty."}, 200

            # Construir la respuesta con los detalles de los productos
            wishlist_items = [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product.name,
                    "created_at": item.created_at.isoformat(),
                }
                for item in wishlist
            ]

            return {"wishlist": wishlist_items}, 200
        except Exception as e:
            abort(500, message=f"An error occurred: {str(e)}")

    @jwt_required()
    def delete(self, wishlist_id):
        user_id = get_jwt_identity()

        # Buscar el producto en la lista de deseos
        wishlist_item = Wishlist.query.filter_by(id=wishlist_id, user_id=user_id).first()
        if not wishlist_item:
            abort(404, message="Wishlist item not found.")

        try:
            # Eliminar el producto de la lista de deseos
            db.session.delete(wishlist_item)
            db.session.commit()
            return {"message": "Product removed from wishlist."}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred: {str(e)}")


class CartController(Resource):
    # Parser para validar los datos de entrada
    cart_args = reqparse.RequestParser()
    cart_args.add_argument('product_id', type=int, required=True, help="Product ID is required.")
    cart_args.add_argument('quantity', type=int, required=True, help="Quantity is required.")

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        args = self.cart_args.parse_args()
        product_id = args['product_id']
        quantity = args['quantity']

        # Verificar si el producto existe
        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Product not found")

        # Verificar si el producto ya está en el carrito
        cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

        if cart_item:
            # Si el producto ya está en el carrito, actualizar la cantidad
            cart_item.quantity += quantity
            cart_item.total = cart_item.quantity * cart_item.price
            cart_item.save()
        else:
            # Si no está en el carrito, agregarlo
            price = product.price
            total = price * quantity
            cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity, price=price, total=total)
            db.session.add(cart_item)
            db.session.commit()

        return {"message": "Product added to cart"}, 200

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        
        if not cart_items:
            return {"message": "Your cart is empty"}, 200
        
        formatted_cart_items = [
        {
            'id': item.id,
            'product_name': item.product.name,
            'product_img': item.product.img,
            'quantity': item.quantity,
            'price': float(item.price),  # Convierte a float
            'total': float(item.total)   # Convierte a float
        }
        for item in cart_items
    ]
        return {"data": formatted_cart_items}, 200


    # @jwt_required()
    # def put(self, id):
    #     user_id = get_jwt_identity()
    #     cart_item = Cart.query.filter_by(id=id, user_id=user_id).all()
        
    #     if not cart_item:
    #         abort(404, message="Cart item not found")
            
    #         args = self.cart_args.parse_args()
    #         new_quantity = args['quantity']
            
    #         product = Product.query.get(cart_item.product_id)
            
    #         if new_quantity > product.stock:
    #             abort(400, message="Quantity exceeds available stock")
                
    #             cart_item.quantity = new_quantity
    #             cart_item.total = cart_item.quantity * cart_item.price
    #             db.session.commit()
    #             return {"message": "Cart item quantity updated successfully"}, 200


    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()

        # Buscar el item del carrito
        cart_item = Cart.query.filter_by(id=id, user_id=user_id).first()
        if not cart_item:
            abort(404, message="Cart item not found")

        db.session.delete(cart_item)
        db.session.commit()

        return {"message": "Product removed from cart successfully"}, 200
    

category_args = reqparse.RequestParser()
category_args.add_argument("name", type=str, required=True, help="Name is required and should not exceed 100 characters")
category_args.add_argument("description", type=str, required=True, help="Description is required and should not exceed 255 characters")

category_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String
}   
class Categories(Resource):    
     @marshal_with(category_fields)
     def get(self, category_id=None):
        if category_id:  # Si category_id es proporcionado
            category = Category.query.filter_by(id=category_id).first()  # Busca por ID
            if not category:  # Si no se encuentra la categoría
                abort(404, message="Category not found")
            return category  # Devuelve la categoría específica
        else:  # Si no se proporciona category_id, devuelve todas las categorías
            categories = Category.query.all()
            return categories  # Devuelve todas las categorías
        
     def post(self):
        args = category_args.parse_args()
        if not args['name'] or args['name'].isspace():
         response = Response(json.dumps({'error': 'Name cannot be empty'}),
                             status=400,
                             mimetype='application/json')
         return abort(response)
        if not args['description'] or args['description'].isspace():
         response = Response(json.dumps({'error': 'Description cannot be empty'}),
                             status=400,
                             mimetype='application/json')
         return abort(response)
        data = request.get_json()
        if Category.query.filter_by(name=data['name']).first():
         return {"error": "Category already exists"}, 400
        new_category = Category(name=data['name'], description=data['description'])
        db.session.add(new_category)
        db.session.commit()
        return {"message": "Category created successfully", "id": new_category.id}, 201
     
     def patch(self, category_id):
        args = category_args.parse_args()
        category = Category.query.filter_by(id=category_id).first()

        if not category:
            return {"error": "Category not found"}, 404

        if args['name'] and not args['name'].isspace():
            category.name = args['name']
        if args['description'] and not args['description'].isspace():
            category.description = args['description']

        db.session.commit()
        return {"message": f"Categoría {category_id} actualizada"}
     
     def delete(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return {"error": "Category not found"}, 404
        db.session.delete(category)
        db.session.commit()
        return {"message": "Category deleted successfully"}, 200
     

     

brand_args = reqparse.RequestParser()
brand_args.add_argument("username", type=str, required=True, help="Username is required")
brand_args.add_argument("address", type=str, required=True, help="Address is required")
brand_args.add_argument("phone", type=str, required=True, help="Phone is required")

# Definición de los campos para serializar el modelo
brand_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'address': fields.String,
    'phone': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}

class Brands(Resource):
    @marshal_with(brand_fields)
    def post(self):
        # Obtener los argumentos de la solicitud
        args = brand_args.parse_args()

        # Validaciones básicas
        if not args['username'] or args['username'].isspace():
            response = Response(json.dumps({'error': 'Username cannot be empty'}),
                                status=400, mimetype='application/json')
            return response
        
        if not args['address'] or args['address'].isspace():
            response = Response(json.dumps({'error': 'Address cannot be empty'}),
                                status=400, mimetype='application/json')
            return response
        
        if not args['phone'] or args['phone'].isspace():
            response = Response(json.dumps({'error': 'Phone cannot be empty'}),
                                status=400, mimetype='application/json')
            return response

        # Crear la nueva marca y guardarla en la base de datos
        brand = Brand(username=args['username'], address=args['address'], phone=args['phone'])
        db.session.add(brand)
        db.session.commit()

        # Retornar el objeto brand recién creado
        return brand, 201

    @marshal_with(brand_fields)
    def get(self):
        # Obtener todas las marcas
        brands = Brand.query.all()
        return brands

class BrandResource(Resource):
    @marshal_with(brand_fields)
    def get(self, brand_id):
        # Obtener una marca específica por ID
        brand = Brand.query.filter_by(id=brand_id).first()
        if not brand:
            abort(404, message="Brand not found")
        return brand

    @marshal_with(brand_fields)
    def patch(self, brand_id):
        # Obtener los argumentos de la solicitud
        args = brand_args.parse_args()

        # Buscar la marca por ID
        brand = Brand.query.filter_by(id=brand_id).first()
        if not brand:
            abort(404, message="Brand not found")

        # Actualizar los campos
        brand.username = args['username']
        brand.address = args['address']
        brand.phone = args['phone']
        db.session.commit()

        return brand

    def delete(self, brand_id):
        # Buscar la marca por ID
        brand = Brand.query.filter_by(id=brand_id).first()
        if not brand:
            abort(404, message="Brand not found")

        # Eliminar la marca
        db.session.delete(brand)
        db.session.commit()
        return '', 204  # Respuesta vacía para indicar que se eliminó correctamente