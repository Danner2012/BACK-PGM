from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
import io
from datetime import datetime
from api.serializers.herramienta_serializer import (
    CategoriaHerramientaSerializer, 
    HerramientaSerializer, 
    HerramientaCreateUpdateSerializer,
    Modelo3DSerializer
)
from api.services.herramienta_service import HerramientaService
from api.models import CategoriaHerramienta, Herramienta, Modelo3D
from api.reports import HerramientaReport

class CategoriaHerramientaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaHerramienta.objects.all()
    serializer_class = CategoriaHerramientaSerializer

class HerramientaViewSet(viewsets.ModelViewSet):
    queryset = Herramienta.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HerramientaCreateUpdateSerializer
        return HerramientaSerializer

    def destroy(self, request, *args, **kwargs):
        """Borrado lógico: desactivar en lugar de eliminar"""
        herramienta = self.get_object()
        herramienta.estado = False
        herramienta.save()
        return Response({'status': 'herramienta desactivada'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request):
        """Generar y descargar el reporte PDF filtrado con datos del usuario"""
        # Intentar obtener datos del usuario autenticado
        user = request.user
        nombre_usuario = "Sistema"
        rol_usuario = "Administrador"

        if user.is_authenticated:
            # Buscar perfil específico (Admin, Técnico, Estudiante)
            if hasattr(user, 'administrador'):
                p = user.administrador
                nombre_usuario = f"{p.nombre} {p.apellido_paterno}"
                rol_usuario = "Administrador"
            elif hasattr(user, 'tecnico'):
                p = user.tecnico
                nombre_usuario = f"{p.nombre} {p.apellido_paterno}"
                rol_usuario = "Técnico"
            else:
                nombre_usuario = user.correo
                rol_usuario = user.id_rol.nombre if user.id_rol else "Usuario"

        filtros = {
            'search': request.query_params.get('search'),
            'categoria': request.query_params.get('categoria'),
            'stock_status': request.query_params.get('stock_status'),
        }
        
        herramientas = HerramientaService.filtrar_herramientas(filtros)
        
        # Generar PDF con datos dinámicos
        pdf = HerramientaReport(usuario_nombre=nombre_usuario, usuario_rol=rol_usuario)
        pdf.add_page()
        pdf.generate_report_content(herramientas)
        
        # Guardar en buffer de memoria
        buffer = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        buffer.write(pdf_content)
        buffer.seek(0)
        
        filename = f'reporte_herramientas_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
        
        return FileResponse(
            buffer, 
            as_attachment=True, 
            filename=filename,
            content_type='application/pdf'
        )

    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        """Endpoint para alternar entre activo/inactivo"""
        herramienta = self.get_object()
        herramienta.estado = not herramienta.estado
        herramienta.save()
        return Response({
            'status': 'success',
            'nuevo_estado': herramienta.estado
        })

    @action(detail=True, methods=['post'], url_path='agregar-modelo')
    def agregar_modelo(self, request, pk=None):
        """Endpoint especial para subir el archivo GLB y su config"""
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'error': 'No se envió ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        modelo = HerramientaService.agregar_modelo_3d(
            herramienta_id=pk,
            archivo=archivo,
            nombre_identificador=request.data.get('nombre_identificador', 'Modelo Principal'),
            escala=request.data.get('escala', 1.0),
            rotacion=request.data.get('rotacion_default', '0 0 0'),
            posicion=request.data.get('posicion_default', '0 0 0')
        )
        return Response(Modelo3DSerializer(modelo).data, status=status.HTTP_201_CREATED)

class Modelo3DViewSet(viewsets.ModelViewSet):
    queryset = Modelo3D.objects.all()
    serializer_class = Modelo3DSerializer
