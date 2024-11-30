from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps

def role_required(*required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in required_roles:
                return {"message": "No tienes permiso para realizar esta acción"}, 403  
            return fn(*args, **kwargs)
        return wrapper
    return decorator


