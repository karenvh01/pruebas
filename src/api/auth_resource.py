from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask import request
from flask_jwt_extended import create_access_token
from api.extensions import db
from api.models import User

class AuthResource(Resource):
    def post(self, action):
        data = request.get_json()

        if action == "register":
            if User.query.filter_by(email=data["email"]).first():
                return {"message": "El usuario ya está registrado"}, 400

            hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
            nuevo_usuario = User(
                name=data["name"],
                lstF=data["lstF"],
                lstM=data["lstM"],
                address=data["address"],
                email=data["email"],
                password=hashed_password,
                c_pass=data["c_pass"],
                phone=data["phone"],
                payment=data["payment"],
                role=data.get("role", 0)
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return {"message": "Usuario registrado exitosamente"}, 201

        elif action == "login":

            required_fields = ["email", "password"]
            missing_fields = [field for field in required_fields if field not in data or not data[field]]

            if missing_fields:
                return {"message": f"Los siguientes campos son requeridos: {', '.join(missing_fields)}"}, 400
            
            usuario = User.query.filter_by(email=data["email"]).first()
            if not usuario or not check_password_hash(usuario.password, data["password"]):
                return {"message": "Credenciales incorrectas"}, 401

            # Usar email como identity y pasar otros datos en additional_claims
            access_token = create_access_token(
                identity=usuario.email,  # El identity debe ser un string único (como el email)
                additional_claims={"id": usuario.id, "role": usuario.role}  # Otros datos como claims adicionales
            )
            return {"access_token": access_token}, 200

        else:
            return {"message": "Acción no válida. Usa 'register' o 'login'"}, 400