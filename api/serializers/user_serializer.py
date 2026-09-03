from rest_framework import serializers
from api.models import Usuario, Rol, Administrador, Tecnico, Estudiante

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']

class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    perfil_id = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    apellido_paterno = serializers.SerializerMethodField()
    apellido_materno = serializers.SerializerMethodField()
    ci = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'id_rol', 'rol_nombre', 'estado', 'nombre_completo', 'perfil_id', 'nombre', 'apellido_paterno', 'apellido_materno', 'ci']

    def get_perfil_data(self, obj):
        try:
            if obj.id_rol_id == 2: # administrador
                return Administrador.objects.get(id_usuario=obj)
            elif obj.id_rol_id == 3: # técnico
                return Tecnico.objects.get(id_usuario=obj)
            elif obj.id_rol_id == 4: # estudiante
                return Estudiante.objects.get(id_usuario=obj)
        except:
            return None
        return None

    def get_perfil_id(self, obj):
        perfil = self.get_perfil_data(obj)
        return perfil.id if perfil else None

    def get_ci(self, obj):
        perfil = self.get_perfil_data(obj)
        return perfil.ci if perfil and hasattr(perfil, 'ci') else None

    def get_nombre(self, obj):
        perfil = self.get_perfil_data(obj)
        return perfil.nombre if perfil else None

    def get_apellido_paterno(self, obj):
        perfil = self.get_perfil_data(obj)
        return perfil.apellido_paterno if perfil else None

    def get_apellido_materno(self, obj):
        perfil = self.get_perfil_data(obj)
        return perfil.apellido_materno if perfil else None

    def get_nombre_completo(self, obj):
        perfil = self.get_perfil_data(obj)
        if not perfil:
            return obj.correo
        return f"{perfil.nombre} {perfil.apellido_paterno} {perfil.apellido_materno}".strip()
            
class TecnicoCRUDSerializer(serializers.ModelSerializer):
    correo = serializers.EmailField(source='id_usuario.correo')
    estado = serializers.BooleanField(source='id_usuario.estado', read_only=True)
    id_usuario_id = serializers.IntegerField(source='id_usuario.id', read_only=True)

    class Meta:
        model = Tecnico
        fields = [
            'id', 'id_usuario_id', 'correo', 'nombre', 'apellido_paterno', 
            'apellido_materno', 'celular', 'ci', 'especialidad', 'estado'
        ]

    def create(self, validated_data):
        usuario_data = validated_data.pop('id_usuario')
        # Crear el usuario primero
        rol_tecnico = Rol.objects.get(id=3)
        usuario = Usuario.objects.create_user(
            correo=usuario_data['correo'],
            password=self.context.get('password'), # Se pasará desde la vista
            id_rol=rol_tecnico
        )
        # Crear el perfil de técnico
        tecnico = Tecnico.objects.create(id_usuario=usuario, **validated_data)
        return tecnico

    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('id_usuario', None)
        if usuario_data and 'correo' in usuario_data:
            instance.id_usuario.correo = usuario_data['correo']
            instance.id_usuario.save()
        
        # Actualizar campos del técnico
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class EstudianteCRUDSerializer(serializers.ModelSerializer):
    correo = serializers.EmailField(source='id_usuario.correo')
    estado = serializers.BooleanField(source='id_usuario.estado', read_only=True)
    id_usuario_id = serializers.IntegerField(source='id_usuario.id', read_only=True)

    class Meta:
        model = Estudiante
        fields = [
            'id', 'id_usuario_id', 'correo', 'nombre', 'apellido_paterno', 
            'apellido_materno', 'celular', 'ci', 'fecha_registro', 'estado'
        ]
        read_only_fields = ['fecha_registro']

    def create(self, validated_data):
        usuario_data = validated_data.pop('id_usuario')
        # Crear el usuario primero
        rol_estudiante = Rol.objects.get(id=4)
        usuario = Usuario.objects.create_user(
            correo=usuario_data['correo'],
            password=self.context.get('password'), # Se pasará desde la vista
            id_rol=rol_estudiante
        )
        # Crear el perfil de estudiante
        estudiante = Estudiante.objects.create(id_usuario=usuario, **validated_data)
        return estudiante

    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('id_usuario', None)
        if usuario_data and 'correo' in usuario_data:
            instance.id_usuario.correo = usuario_data['correo']
            instance.id_usuario.save()
        
        # Actualizar campos del estudiante
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
