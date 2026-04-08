from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import TipoCurso, Dia, Horario, Curso, CursoHorario, Administrador, CursoTecnico, Inscripcion
from ..serializers.curso_serializer import (
    TipoCursoSerializer, DiaSerializer, HorarioSerializer, 
    CursoSerializer, CursoHorarioSerializer, CursoTecnicoSerializer,
    InscripcionSerializer
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

class CursoTecnicoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CursoTecnico.objects.all()
    serializer_class = CursoTecnicoSerializer

    def create(self, request, *args, **kwargs):
        id_curso = request.data.get('id_curso')
        id_tecnico = request.data.get('id_tecnico')

        if CursoTecnico.objects.filter(id_curso=id_curso, id_tecnico=id_tecnico).exists():
            return Response(
                {"error": "Este técnico ya está asignado a este curso."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

class InscripcionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer

    def create(self, request, *args, **kwargs):
        id_curso_horario = request.data.get('id_curso_horario')
        id_estudiante = request.data.get('id_estudiante')

        if not id_curso_horario or not id_estudiante:
            return Response({"error": "Estudiante y Horario de curso son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya está inscrito
        if Inscripcion.objects.filter(id_curso_horario=id_curso_horario, id_estudiante=id_estudiante).exists():
            return Response(
                {"error": "Este estudiante ya está inscrito en este horario de curso."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar cupo
        try:
            curso_horario = CursoHorario.objects.get(id=id_curso_horario)
            inscritos = Inscripcion.objects.filter(id_curso_horario=id_curso_horario).count()
            
            if inscritos >= curso_horario.cupo_maximo:
                return Response(
                    {"error": "No hay cupos disponibles para este horario."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except CursoHorario.DoesNotExist:
            return Response({"error": "El horario del curso no existe."}, status=status.HTTP_404_NOT_FOUND)

        return super().create(request, *args, **kwargs)
