from rest_framework import serializers
from ..models import Practica, TipoRecurso, TipoPractica, RecursoPractica, PracticaHerramienta, Prestamo, PrestamoDetalle, DevolucionHerramienta, Herramienta

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

class DevolucionHerramientaSerializer(serializers.ModelSerializer):
    tecnico_receptor_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DevolucionHerramienta
        fields = '__all__'

    def get_tecnico_receptor_nombre(self, obj):
        t = obj.id_tecnico_receptor
        return f"{t.nombre} {t.apellido_paterno} {t.apellido_materno}".strip()

class PrestamoDetalleSerializer(serializers.ModelSerializer):
    herramienta_nombre = serializers.ReadOnlyField(source='id_herramienta.nombre')
    cantidad_devuelta_total = serializers.SerializerMethodField()
    devoluciones = DevolucionHerramientaSerializer(many=True, read_only=True)

    class Meta:
        model = PrestamoDetalle
        fields = '__all__'

    def get_cantidad_devuelta_total(self, obj):
        return sum(d.cantidad_devuelta for d in obj.devoluciones.all())

class PrestamoSerializer(serializers.ModelSerializer):
    id_estudiante = serializers.ReadOnlyField(source='id_inscripcion.id_estudiante.id')
    id_curso = serializers.ReadOnlyField(source='id_inscripcion.id_curso.id')
    estudiante_nombre = serializers.SerializerMethodField()
    estudiante_ci = serializers.ReadOnlyField(source='id_inscripcion.id_estudiante.ci')
    curso_nombre = serializers.ReadOnlyField(source='id_inscripcion.id_curso.nombre')
    practica_titulo = serializers.ReadOnlyField(source='id_practica.titulo')
    tecnico_nombre = serializers.SerializerMethodField()
    
    # Campos para facilitar el uso en el frontend (basados en el primer detalle)
    herramienta_nombre = serializers.SerializerMethodField()
    cantidad_prestada = serializers.SerializerMethodField()
    total_devuelto = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()

    detalles = PrestamoDetalleSerializer(many=True, read_only=True)
    
    # Campos de entrada opcionales para creación simplificada
    id_herramienta = serializers.IntegerField(write_only=True, required=False)
    cantidad_prestada_input = serializers.IntegerField(write_only=True, required=False)
    
    detalles_input = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Prestamo
        fields = [
            'id', 'id_inscripcion', 'id_practica', 'id_tecnico', 'id_estudiante', 'id_curso', 'fecha_prestamo', 
            'observacion', 'activo', 'estudiante_nombre', 'estudiante_ci', 
            'curso_nombre', 'practica_titulo', 'tecnico_nombre', 'herramienta_nombre', 
            'cantidad_prestada', 'total_devuelto', 'estado', 'detalles', 
            'id_herramienta', 'cantidad_prestada_input', 'detalles_input'
        ]

    def get_estudiante_nombre(self, obj):
        e = obj.id_inscripcion.id_estudiante
        return f"{e.nombre} {e.apellido_paterno} {e.apellido_materno}".strip()

    def get_tecnico_nombre(self, obj):
        t = obj.id_tecnico
        return f"{t.nombre} {t.apellido_paterno} {t.apellido_materno}".strip()

    def get_herramienta_nombre(self, obj):
        detalle = obj.detalles.first()
        return detalle.id_herramienta.nombre if detalle else "N/A"

    def get_cantidad_prestada(self, obj):
        detalle = obj.detalles.first()
        return detalle.cantidad_prestada if detalle else 0

    def get_total_devuelto(self, obj):
        detalle = obj.detalles.first()
        if not detalle: return 0
        return sum(d.cantidad_devuelta for d in detalle.devoluciones.all())

    def get_estado(self, obj):
        detalle = obj.detalles.first()
        return detalle.estado if detalle else "N/A"

    def create(self, validated_data):
        from django.db import transaction
        from django.db.models import F
        import logging
        logger = logging.getLogger(__name__)

        detalles_data = validated_data.pop('detalles_input', [])
        id_herramienta = validated_data.pop('id_herramienta', None)
        cantidad_prestada_input = validated_data.pop('cantidad_prestada_input', None)
        
        try:
            with transaction.atomic():
                prestamo = Prestamo.objects.create(**validated_data)
                
                # Normalizar detalles: convertir campos individuales a lista si es necesario
                final_detalles = []
                if detalles_data:
                    final_detalles = detalles_data
                elif id_herramienta and cantidad_prestada_input:
                    final_detalles = [{'id_herramienta': id_herramienta, 'cantidad_prestada': cantidad_prestada_input}]

                if not final_detalles:
                    raise serializers.ValidationError({"error": "Debe incluir al menos una herramienta en el préstamo."})

                # Procesar cada herramienta
                processed_tools = set()
                for detalle in final_detalles:
                    h_id = detalle.get('id_herramienta') or detalle.get('id_herramienta_id')
                    cant = int(detalle.get('cantidad_prestada', 0))
                    
                    if not h_id or cant <= 0:
                        continue
                    
                    if h_id in processed_tools:
                        raise serializers.ValidationError({"error": f"La herramienta con ID {h_id} está duplicada en el pedido."})
                    
                    # Validar stock antes de procesar
                    try:
                        herramienta = Herramienta.objects.select_for_update().get(id=h_id)
                        if herramienta.stock_disponible < cant:
                            raise serializers.ValidationError({
                                "error": f"Stock insuficiente para '{herramienta.nombre}'. Disponible: {herramienta.stock_disponible}, Solicitado: {cant}"
                            })
                        
                        # Crear detalle (el save de PrestamoDetalle restará el stock)
                        PrestamoDetalle.objects.create(
                            id_prestamo=prestamo,
                            id_herramienta=herramienta,
                            cantidad_prestada=cant
                        )
                        processed_tools.add(h_id)
                        
                    except Herramienta.DoesNotExist:
                        raise serializers.ValidationError({"error": f"La herramienta con ID {h_id} no existe."})

                # Verificar si finalmente se crearon detalles
                if not prestamo.detalles.exists():
                    raise serializers.ValidationError({"error": "No se pudieron registrar las herramientas del préstamo."})
                    
            return prestamo
        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Error al crear préstamo: {str(e)}")
            raise serializers.ValidationError({"error": f"Error interno al procesar el préstamo: {str(e)}"})
