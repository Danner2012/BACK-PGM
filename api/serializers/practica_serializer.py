from rest_framework import serializers
from ..models import Practica, TipoRecurso, TipoPractica, RecursoPractica, PracticaHerramienta, PrestamoHerramienta, DevolucionHerramienta, Herramienta

class TipoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRecurso
        fields = '__all__'

class TipoPracticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPractica
        fields = '__all__'

class RecursoPracticaSerializer(serializers.ModelSerializer):
    tipo_recurso_nombre = serializers.ReadOnlyField(source='id_tipo_recurso.nombre')
    
    class Meta:
        model = RecursoPractica
        fields = '__all__'

class PracticaHerramientaSerializer(serializers.ModelSerializer):
    herramienta_nombre = serializers.ReadOnlyField(source='id_herramienta.nombre')
    imagen_previa = serializers.ImageField(source='id_herramienta.imagen_previa', read_only=True)
    modelos_3d = serializers.SerializerMethodField()
    descripcion_herramienta = serializers.ReadOnlyField(source='id_herramienta.descripcion')
    uso_herramienta = serializers.ReadOnlyField(source='id_herramienta.uso')
    seguridad_herramienta = serializers.ReadOnlyField(source='id_herramienta.info_importante')
    
    class Meta:
        model = PracticaHerramienta
        fields = '__all__'

    def get_modelos_3d(self, obj):
        from .herramienta_serializer import Modelo3DSerializer
        return Modelo3DSerializer(obj.id_herramienta.modelos_3d.all(), many=True).data

class PracticaSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.ReadOnlyField(source='id_curso.nombre')
    tipo_practica_nombre = serializers.ReadOnlyField(source='id_tipo_practica.nombre')
    recursos = RecursoPracticaSerializer(many=True, read_only=True)
    herramientas = PracticaHerramientaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Practica
        fields = '__all__'

class PrestamoHerramientaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.SerializerMethodField()
    practica_titulo = serializers.ReadOnlyField(source='id_practica.titulo')
    herramienta_nombre = serializers.ReadOnlyField(source='id_herramienta.nombre')
    tecnico_nombre = serializers.SerializerMethodField()
    devoluciones_detalle = serializers.SerializerMethodField()
    cantidad_devuelta_total = serializers.SerializerMethodField()

    class Meta:
        model = PrestamoHerramienta
        fields = '__all__'

    def get_estudiante_nombre(self, obj):
        e = obj.id_inscripcion.id_estudiante
        return f"{e.nombre} {e.apellido_paterno} {e.apellido_materno}".strip()

    def get_tecnico_nombre(self, obj):
        t = obj.id_tecnico
        return f"{t.nombre} {t.apellido_paterno} {t.apellido_materno}".strip()

    def get_devoluciones_detalle(self, obj):
        return DevolucionHerramientaSerializer(obj.devoluciones.all(), many=True).data

    def get_cantidad_devuelta_total(self, obj):
        return sum(d.cantidad_devuelta for d in obj.devoluciones.all())

class DevolucionHerramientaSerializer(serializers.ModelSerializer):
    tecnico_receptor_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DevolucionHerramienta
        fields = '__all__'

    def get_tecnico_receptor_nombre(self, obj):
        t = obj.id_tecnico_receptor
        return f"{t.nombre} {t.apellido_paterno} {t.apellido_materno}".strip()
