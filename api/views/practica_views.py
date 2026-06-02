from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, models
from django.db.models import Q
from django.utils import timezone
from ..models import (
    Practica, TipoRecurso, TipoPractica, RecursoPractica, 
    PracticaHerramienta, Prestamo, PrestamoDetalle, DevolucionHerramienta,
    PracticaEstudiante, EvidenciaPractica, Inscripcion
)
from ..serializers.practica_serializer import (
    PracticaSerializer, TipoRecursoSerializer, TipoPracticaSerializer, RecursoPracticaSerializer,
    PracticaHerramientaSerializer, PrestamoSerializer, PrestamoDetalleSerializer, 
    DevolucionHerramientaSerializer, PracticaEstudianteSerializer, EvidenciaPracticaSerializer
)

class PracticaEstudianteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PracticaEstudianteSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PracticaEstudiante.objects.all().order_by('-fecha_inicio')
        
        if hasattr(user, 'estudiante'):
            queryset = queryset.filter(id_inscripcion__id_estudiante=user.estudiante)
        elif hasattr(user, 'tecnico'):
            queryset = queryset.filter(id_practica__id_curso__cursotecnico__id_tecnico=user.tecnico)
            
        return queryset

    @action(detail=False, methods=['get'])
    def mi_estado_practica(self, request):
        id_practica = request.query_params.get('id_practica')
        if not id_practica or not hasattr(request.user, 'estudiante'):
            return Response({'error': 'Faltan parámetros o permisos'}, status=400)
            
        # Buscar la inscripción activa del estudiante para el curso de esta práctica
        practica = Practica.objects.get(id=id_practica)
        inscripcion = Inscripcion.objects.filter(
            id_estudiante=request.user.estudiante,
            id_curso=practica.id_curso,
            estado='confirmado'
        ).first()

        if not inscripcion:
            return Response({'error': 'No estás inscrito en este curso'}, status=403)

        # Obtener o crear el registro de seguimiento
        pe, created = PracticaEstudiante.objects.get_or_create(
            id_inscripcion=inscripcion,
            id_practica=practica
        )
        
        serializer = self.get_serializer(pe)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def finalizar_entrega(self, request, pk=None):
        pe = self.get_object()
        if pe.estado != 'pendiente':
            return Response({'error': 'Esta práctica ya fue entregada o calificada'}, status=400)
            
        pe.estado = 'entregada'
        pe.fecha_entrega = timezone.now()
        pe.save()
        return Response({'status': 'Práctica entregada correctamente'})

    @action(detail=True, methods=['post'])
    def calificar(self, request, pk=None):
        if not hasattr(request.user, 'tecnico'):
            return Response({'error': 'Solo técnicos pueden calificar'}, status=403)
            
        pe = self.get_object()
        calificacion = request.data.get('calificacion')
        comentario = request.data.get('comentario', '')
        estado = request.data.get('estado') # aprobada/reprobada

        if calificacion is None or not estado:
            return Response({'error': 'Calificación y estado son requeridos'}, status=400)

        try:
            pe.calificacion = float(calificacion)
            pe.comentario_tecnico = comentario
            pe.estado = estado
            pe.save()
            return Response({'status': 'Práctica calificada', 'id': pe.id}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class EvidenciaPracticaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EvidenciaPractica.objects.all()
    serializer_class = EvidenciaPracticaSerializer

    def create(self, request, *args, **kwargs):
        # Validar que la práctica esté pendiente
        pe_id = request.data.get('id_practica_estudiante')
        pe = PracticaEstudiante.objects.get(id=pe_id)
        if pe.estado != 'pendiente':
            return Response({'error': 'No se pueden subir evidencias a una práctica ya entregada'}, status=400)
        return super().create(request, *args, **kwargs)

class TipoRecursoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TipoRecurso.objects.all()
    serializer_class = TipoRecursoSerializer

class TipoPracticaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TipoPractica.objects.all()
    serializer_class = TipoPracticaSerializer

class PracticaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PracticaSerializer

    def get_queryset(self):
        user = self.request.user
        # Si es superusuario o administrador, ve todas
        if user.is_superuser or hasattr(user, 'administrador'):
            return Practica.objects.all().order_by('-id')
        
        # Si es estudiante, ve las de sus cursos inscritos y confirmados
        if hasattr(user, 'estudiante'):
            return Practica.objects.filter(
                id_curso__inscripcion__id_estudiante=user.estudiante,
                id_curso__inscripcion__estado='confirmado',
                estado=True
            ).distinct().order_by('-id')
        
        # Si es técnico, ve las que creó O las de sus cursos asignados
        if hasattr(user, 'tecnico'):
            return Practica.objects.filter(
                Q(id_usuario_creador=user) | 
                Q(id_curso__cursotecnico__id_tecnico=user.tecnico)
            ).distinct().order_by('-id')

        # Por defecto (otros roles si existieran), ve las que creó
        return Practica.objects.filter(id_usuario_creador=user).order_by('-id')


    def perform_create(self, serializer):
        serializer.save(id_usuario_creador=self.request.user)

    @action(detail=False, methods=['get'])
    def mis_practicas(self, request):
        if not hasattr(request.user, 'estudiante'):
            return Response({'error': 'Solo los estudiantes pueden acceder a esta vista'}, status=status.HTTP_403_FORBIDDEN)
        
        estudiante = request.user.estudiante
        practicas = Practica.objects.filter(
            id_curso__inscripcion__id_estudiante=estudiante,
            id_curso__inscripcion__estado='confirmado',
            estado=True
        ).distinct().order_by('id_curso', 'id')
        
        serializer = self.get_serializer(practicas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        practica = self.get_object()
        practica.estado = not practica.estado
        practica.save()
        return Response({'status': 'estado actualizado', 'nuevo_estado': practica.estado})

    @action(detail=True, methods=['get'])
    def recursos(self, request, pk=None):
        practica = self.get_object()
        recursos = RecursoPractica.objects.filter(id_practica=practica, estado=True)
        serializer = RecursoPracticaSerializer(recursos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def herramientas(self, request, pk=None):
        practica = self.get_object()
        herramientas = PracticaHerramienta.objects.filter(id_practica=practica)
        serializer = PracticaHerramientaSerializer(herramientas, many=True)
        return Response(serializer.data)

class RecursoPracticaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecursoPracticaSerializer

    def get_queryset(self):
        return RecursoPractica.objects.filter(estado=True)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = RecursoPractica.objects.get(pk=kwargs.get('pk'))
            # Eliminación física para asegurar que desaparezca de la lista de la práctica
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RecursoPractica.DoesNotExist:
            return Response({'error': 'El recurso no existe'}, status=status.HTTP_404_NOT_FOUND)

class PracticaHerramientaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PracticaHerramienta.objects.all()
    serializer_class = PracticaHerramientaSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PrestamoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Prestamo.objects.filter(activo=True).order_by('-fecha_prestamo')
        
        # Si es estudiante, solo ve sus propios préstamos
        if hasattr(user, 'estudiante'):
            queryset = queryset.filter(id_inscripcion__id_estudiante=user.estudiante)
        
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PrestamoDetalleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PrestamoDetalle.objects.all()
    serializer_class = PrestamoDetalleSerializer

class DevolucionHerramientaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DevolucionHerramienta.objects.all()
    serializer_class = DevolucionHerramientaSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().create(request, *args, **kwargs)

