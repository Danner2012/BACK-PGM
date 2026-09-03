from rest_framework import serializers
from api.models import (
    AficheComponente, AficheFuncion, AficheCaracteristica,
    AficheMedicionPaso, AficheMedicionRecurso,
    AficheProcedimientoPaso, AficheProcedimientoRecurso,
    Herramienta
)
from api.serializers.herramienta_serializer import HerramientaSerializer

class AficheFuncionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AficheFuncion
        fields = ['id', 'texto', 'activo']

class AficheCaracteristicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AficheCaracteristica
        fields = ['id', 'texto']

class AficheMedicionRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AficheMedicionRecurso
        fields = ['id', 'archivo', 'tipo']

class AficheMedicionPasoSerializer(serializers.ModelSerializer):
    recursos = AficheMedicionRecursoSerializer(many=True, read_only=True)

    class Meta:
        model = AficheMedicionPaso
        fields = ['id', 'orden', 'descripcion', 'recursos']

class AficheProcedimientoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AficheProcedimientoRecurso
        fields = ['id', 'archivo', 'tipo']

class AficheProcedimientoPasoSerializer(serializers.ModelSerializer):
    recursos = AficheProcedimientoRecursoSerializer(many=True, read_only=True)

    class Meta:
        model = AficheProcedimientoPaso
        fields = ['id', 'orden', 'descripcion', 'recursos']

class AficheComponenteSerializer(serializers.ModelSerializer):
    funciones = AficheFuncionSerializer(many=True, read_only=True)
    caracteristicas = AficheCaracteristicaSerializer(many=True, read_only=True)
    pasos_medicion = AficheMedicionPasoSerializer(many=True, read_only=True)
    pasos_procedimiento = AficheProcedimientoPasoSerializer(many=True, read_only=True)
    herramientas = HerramientaSerializer(many=True, read_only=True)

    class Meta:
        model = AficheComponente
        fields = [
            'id', 'clase_ia', 'nombre', 'imagen_referencia', 'imagen_simbolo',
            'descripcion_general', 'funciones', 'caracteristicas',
            'pasos_medicion', 'pasos_procedimiento', 'herramientas',
            'fecha_creacion', 'fecha_actualizacion'
        ]
