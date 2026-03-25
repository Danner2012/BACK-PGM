from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Usuario

class AuthService:
    @staticmethod
    def authenticate_user(correo, clave):
        user = authenticate(username=correo, password=clave)
        
        if user is None:
            return None, "Credenciales inválidas"
        
        if not user.estado:
            return None, "Usuario inactivo"
        
        return user, None

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'rol': user.id_rol.nombre if user.id_rol else None,
            'email': user.correo
        }
