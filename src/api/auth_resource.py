from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from api.middleware.auth import role_required
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from api.extensions import db
from api.models import User
import re


class AuthResource(Resource):

    def post(self, action):
        data = request.get_json()

        if action == "register":
            # Validar que todos los campos requeridos estén presentes y no vacíos
            required_fields = ["name", "lstF", "lstM", "address", "email", "password", "c_pass", "phone", "payment"]
            missing_fields = [field for field in required_fields if not data.get(field) or data[field].isspace()]
            if missing_fields:
                return {"message": f"Los siguientes campos son requeridos: {', '.join(missing_fields)}"}, 400

            # Validar formato del correo electrónico
            email = data["email"].strip()
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                return {"message": "Formato de correo electrónico inválido"}, 400
            if User.query.filter_by(email=email).first():
                return {"message": "El usuario ya está registrado"}, 400
            
            # Validar que las contraseñas coincidan
            if data["password"] != data["c_pass"]:
                return {"message": "Las contraseñas no coinciden"}, 400

            # Validar longitud de la contraseña
            if len(data["password"]) < 8:
                return {"message": "La contraseña debe tener al menos 8 caracteres"}, 400

            # Validar formato del número de teléfono
            if not re.match(r"^\+?[1-9]\d{1,14}$", data["phone"]):
                return {"message": "Formato de número de teléfono inválido"}, 400

            # Validar el método de pago
            valid_payment_methods = ["credit_card", "paypal", "bank_transfer"]
            if data["payment"] not in valid_payment_methods:
                return {"message": f"Método de pago inválido. Opciones válidas: {', '.join(valid_payment_methods)}"}, 400

            # Validar el rol (opcional)
            if data.get("role") not in [0, 1]:
                return {"message": "Rol inválido"}, 400

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
                identity=usuario.email,
                additional_claims={"id": usuario.id, "role": usuario.role}
            )
            return {"access_token": access_token}, 200

        else:
            return {"message": "Acción no válida. Usa 'register' o 'login'"}, 400

    @jwt_required()
    def get(self):
        claims = get_jwt()
        role = claims.get("role")

        if role == 1:  # Si es administrador
            return {"message": "¡Bienvenido, administrador!"}, 200
        elif role == 0:  # Si es usuario normal
            return {"message": "¡Bienvenido, usuario!"}, 200
        else:
            return {"message": "Rol no reconocido"}, 400
        
