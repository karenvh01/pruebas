from flask import Flask
from api.extensions import db
from flask_jwt_extended import JWTManager
from api.auth_resource import AuthResource
from api.middleware.auth import role_required
from api.controllers import UserResource, BrandResource, Categories, ProductResource, WishlistController, CartController, Brands,OrderController, UserListResource
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = "tu_clave_secreta_super_segura"  # Cambia esto por una clave segura
jwt = JWTManager(app)

db.init_app(app)
api = Api(app)

with app.app_context():
    db.create_all()
    
api.add_resource(UserResource, "/api/users/","/api/users/<int:user_id>")
api.add_resource(UserListResource, '/users')
api.add_resource(Brands, "/api/brands/")
api.add_resource(BrandResource, "/api/brands/<int:brand_id>")
api.add_resource(Categories, "/api/categories/", "/api/categories/<int:category_id>")
api.add_resource(ProductResource, "/api/products/", "/api/products/<int:product_id>")
api.add_resource(AuthResource, "/auth/<string:action>", "/auth/role") 
api.add_resource(WishlistController, '/wishlist', '/wishlist/<int:wishlist_id>')
api.add_resource(CartController, '/carts', '/carts/<int:id>')
api.add_resource(OrderController, '/orders','/orders/<int:order_id>')



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)