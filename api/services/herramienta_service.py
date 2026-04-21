from api.models import CategoriaHerramienta, Herramienta, Modelo3D
from django.shortcuts import get_object_or_404

class HerramientaService:
    @staticmethod
    def listar_categorias():
        return CategoriaHerramienta.objects.filter(estado=True)

    @staticmethod
    def listar_herramientas():
        return Herramienta.objects.all().prefetch_related('modelos_3d')

    @staticmethod
    def obtener_herramienta_por_slug(slug):
        return get_object_or_404(Herramienta, slug=slug)

    @staticmethod
    def crear_herramienta(data):
        # Aquí podrías añadir validaciones extra si fuera necesario
        return Herramienta.objects.create(**data)

    @staticmethod
    def agregar_modelo_3d(herramienta_id, archivo, nombre_identificador, escala=1.0, rotacion="0,0,0", posicion="0,0,0"):
        herramienta = get_object_or_404(Herramienta, id=herramienta_id)
        return Modelo3D.objects.create(
            id_herramienta=herramienta,
            archivo=archivo,
            nombre_identificador=nombre_identificador,
            escala=escala,
            rotacion_default=rotacion,
            posicion_default=posicion
        )
