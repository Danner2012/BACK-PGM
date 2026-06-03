from api.models import CategoriaHerramienta, Herramienta, Modelo3D
from django.shortcuts import get_object_or_404
from django.db import models

class HerramientaService:
    @staticmethod
    def listar_categorias():
        return CategoriaHerramienta.objects.filter(estado=True)

    @staticmethod
    def filtrar_herramientas(filtros):
        queryset = Herramienta.objects.all().select_related('id_categoria').prefetch_related('modelos_3d')
        
        search = filtros.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(nombre__icontains=search) | 
                models.Q(descripcion__icontains=search) |
                models.Q(id_categoria__nombre__icontains=search)
            )
            
        categoria = filtros.get('categoria')
        if categoria and categoria != 'todos':
            queryset = queryset.filter(id_categoria_id=categoria)
            
        stock_status = filtros.get('stock_status')
        if stock_status and stock_status != 'todos':
            if stock_status == 'disponible':
                queryset = queryset.filter(stock_disponible__gt=0)
            elif stock_status == 'agotado':
                queryset = queryset.filter(stock_disponible__lte=0)
            elif stock_status == 'bajo':
                queryset = queryset.filter(stock_disponible__gt=0, stock_disponible__lte=3)
                
        return queryset

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
