from rest_framework import serializers
from api.models import Usuario, Rol

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']

class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'id_rol', 'rol_nombre', 'estado']
