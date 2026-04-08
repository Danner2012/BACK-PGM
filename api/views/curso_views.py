from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import TipoCurso, Dia, Horario, Curso, CursoHorario, Administrador
from ..serializers.curso_serializer import (
    TipoCursoSerializer, DiaSerializer, HorarioSerializer, 
    CursoSerializer, CursoHorarioSerializer
)

class TipoCursoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TipoCurso.objects.all()
    serializer_class = TipoCursoSerializer

class DiaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Dia.objects.all()
    serializer_class = DiaSerializer

class HorarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer

class CursoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    def perform_create(self, serializer):
        # Obtener el administrador asociado al usuario autenticado
        try:
            administrador = Administrador.objects.get(id_usuario=self.request.user)
            serializer.save(id_administrador=administrador)
        except Administrador.DoesNotExist:
            # Si no tiene perfil, intentamos asignar el primer administrador que exista 
            # para que no falle la creación durante el desarrollo.
            primer_admin = Administrador.objects.first()
            if primer_admin:
                serializer.save(id_administrador=primer_admin)
            else:
                # Si no hay NINGÚN administrador en la tabla api_administrador, 
                # entonces sí tenemos un problema de datos.
                from rest_framework.exceptions import ValidationError
                raise ValidationError("No existe ningún perfil de Administrador en la base de datos. Crea uno primero.")

class CursoHorarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CursoHorario.objects.all()
    serializer_class = CursoHorarioSerializer

    def create(self, request, *args, **kwargs):
        # Verificar si ya existe el horario para ese curso en ese día
        id_curso = request.data.get('id_curso')
        id_dia = request.data.get('id_dia')
        id_horario = request.data.get('id_horario')

        if CursoHorario.objects.filter(id_curso=id_curso, id_dia=id_dia, id_horario=id_horario).exists():
            return Response(
                {"error": "Este curso ya tiene asignado este horario en este día."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
