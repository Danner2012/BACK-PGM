from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.serializers.user_serializer import UsuarioSerializer
from django.db import models
from django.db.models import Avg, Count

from rest_framework import viewsets
from rest_framework.decorators import action
from api.models import Tecnico, Usuario, Estudiante, Inscripcion, PracticaEstudiante
from api.serializers.user_serializer import TecnicoCRUDSerializer, EstudianteCRUDSerializer

class StudentDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'estudiante'):
            return Response({"error": "Solo estudiantes pueden acceder a estas estadísticas"}, status=403)
        
        estudiante = request.user.estudiante
        
        # 1. Resumen general
        cursos_activos = Inscripcion.objects.filter(id_estudiante=estudiante, estado='confirmado').count()
        practicas_stats = PracticaEstudiante.objects.filter(id_inscripcion__id_estudiante=estudiante).aggregate(
            pendientes=Count('id', filter=models.Q(estado='pendiente')),
            aprobadas=Count('id', filter=models.Q(estado='aprobada')),
            promedio=Avg('calificacion')
        )
        
        # 2. Datos para gráficas (Promedio por curso)
        rendimiento_cursos = PracticaEstudiante.objects.filter(
            id_inscripcion__id_estudiante=estudiante,
            estado='aprobada'
        ).values('id_inscripcion__id_curso__nombre').annotate(
            promedio=Avg('calificacion')
        ).order_by('id_inscripcion__id_curso__nombre')
        
        labels_rendimiento = [item['id_inscripcion__id_curso__nombre'] for item in rendimiento_cursos]
        data_rendimiento = [float(item['promedio']) if item['promedio'] else 0 for item in rendimiento_cursos]

        # 3. Estado de aprobación (Aprobadas vs Reprobadas vs Pendientes)
        estado_practicas = PracticaEstudiante.objects.filter(
            id_inscripcion__id_estudiante=estudiante
        ).values('estado').annotate(total=Count('id'))
        
        return Response({
            'resumen': {
                'cursos_activos': cursos_activos,
                'practicas_pendientes': practicas_stats['pendientes'] or 0,
                'practicas_aprobadas': practicas_stats['aprobadas'] or 0,
                'promedio_general': round(float(practicas_stats['promedio']), 2) if practicas_stats['promedio'] else 0
            },
            'grafica_rendimiento': {
                'labels': labels_rendimiento,
                'data': data_rendimiento
            },
            'grafica_estados': {
                'labels': [item['estado'].capitalize() for item in estado_practicas],
                'data': [item['total'] for item in estado_practicas]
            }
        })

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TecnicoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Tecnico.objects.select_related('id_usuario').all()
    serializer_class = TecnicoCRUDSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get('password')
        if not password:
            return Response({"error": "La contraseña es requerida para crear un usuario"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data, context={'password': password})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        tecnico = self.get_object()
        usuario = tecnico.id_usuario
        usuario.estado = not usuario.estado
        usuario.save()
        return Response({
            'status': 'success',
            'estado': usuario.estado,
            'mensaje': f"Usuario {'activado' if usuario.estado else 'desactivado'} correctamente"
        })

class EstudianteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Estudiante.objects.select_related('id_usuario').all()
    serializer_class = EstudianteCRUDSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get('password')
        if not password:
            return Response({"error": "La contraseña es requerida para crear un usuario"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data, context={'password': password})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        estudiante = self.get_object()
        usuario = estudiante.id_usuario
        usuario.estado = not usuario.estado
        usuario.save()
        return Response({
            'status': 'success',
            'estado': usuario.estado,
            'mensaje': f"Usuario {'activado' if usuario.estado else 'desactivado'} correctamente"
        })
