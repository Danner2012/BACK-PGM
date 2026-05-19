from rest_framework import serializers
from api.models import CategoriaHerramienta, Herramienta, Modelo3D, Administrador

class CategoriaHerramientaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaHerramienta
        fields = '__all__'

class Modelo3DSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelo3D
        fields = '__all__'

class HerramientaSerializer(serializers.ModelSerializer):
    # Campos anidados para lectura
    categoria_info = CategoriaHerramientaSerializer(source='id_categoria', read_only=True)
    modelos_3d = Modelo3DSerializer(many=True, read_only=True)
    
    # El slug se autogenera en el modelo, lo ponemos como solo lectura en el serializer
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Herramienta
        fields = [
            'id', 'id_categoria', 'categoria_info', 'id_administrador', 
            'nombre', 'slug', 'descripcion', 'uso', 'info_importante', 
            'imagen_previa', 'stock_total', 'stock_disponible', 'estado', 
            'modelos_3d', 'fecha_creacion', 'fecha_actualizacion'
        ]

class HerramientaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer optimizado para creación y actualización (sin anidamiento pesado)"""
    class Meta:
        model = Herramienta
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }
