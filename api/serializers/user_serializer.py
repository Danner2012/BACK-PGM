from rest_framework import serializers
from api.models import Usuario, Rol, Administrador, Tecnico, Estudiante

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']

class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'id_rol', 'rol_nombre', 'estado', 'nombre_completo']

    def get_nombre_completo(self, obj):
        try:
            if obj.id_rol_id == 2: # administrador
                perfil = Administrador.objects.get(id_usuario=obj)
            elif obj.id_rol_id == 3: # técnico
                perfil = Tecnico.objects.get(id_usuario=obj)
            elif obj.id_rol_id == 4: # estudiante
                perfil = Estudiante.objects.get(id_usuario=obj)
            else:
                return obj.correo # Para superadministrador u otros roles sin perfil detallado
            
            return f"{perfil.nombre} {perfil.apellido_paterno} {perfil.apellido_materno}".strip()
        except (Administrador.DoesNotExist, Tecnico.DoesNotExist, Estudiante.DoesNotExist):
            return obj.correo # Fallback si no tiene perfil creado
