from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models import TipoCurso, Dia, Horario, Curso, CursoHorario, Administrador, CursoTecnico, Inscripcion, Pago
from ..serializers.curso_serializer import (
    TipoCursoSerializer, DiaSerializer, HorarioSerializer, 
    CursoSerializer, CursoHorarioSerializer, CursoTecnicoSerializer,
    InscripcionSerializer, PagoSerializer
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
        try:
            administrador = Administrador.objects.get(id_usuario=self.request.user)
            serializer.save(id_administrador=administrador)
        except Administrador.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Su cuenta de usuario no tiene un perfil de Administrador vinculado. No puede crear cursos.")

class CursoHorarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CursoHorario.objects.all()
    serializer_class = CursoHorarioSerializer

    def create(self, request, *args, **kwargs):
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

from rest_framework.decorators import action
from ..models import Estudiante

class InscripcionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer

    @action(detail=False, methods=['get'], url_path='mis-cursos')
    def mis_cursos(self, request):
        try:
            estudiante = Estudiante.objects.get(id_usuario=request.user)
            inscripciones = Inscripcion.objects.filter(id_estudiante=estudiante)
            serializer = self.get_serializer(inscripciones, many=True)
            return Response(serializer.data)
        except Estudiante.DoesNotExist:
            return Response({"error": "No se encontró perfil de estudiante para este usuario."}, status=404)

    def create(self, request, *args, **kwargs):
        id_curso = request.data.get('id_curso')
        id_estudiante = request.data.get('id_estudiante')
        metodo_pago = request.data.get('metodo_pago', 'Fisico')

        if not id_curso or not id_estudiante:
            return Response({"error": "Estudiante y Curso son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        if Inscripcion.objects.filter(id_curso=id_curso, id_estudiante=id_estudiante).exists():
            return Response(
                {"error": "Este estudiante ya está inscrito en este curso."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                curso = Curso.objects.get(id=id_curso)
                inscritos = Inscripcion.objects.filter(id_curso=id_curso, estado='confirmado').count()
                
                if inscritos >= curso.cupo_maximo:
                    return Response(
                        {"error": "No hay cupos disponibles para este curso."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                inscripcion = serializer.save()

                # Determinar estado inicial del pago basado en el estado de la inscripción
                estado_pago = 'pagado' if inscripcion.estado == 'confirmado' else 'pendiente'

                Pago.objects.create(
                    id_inscripcion=inscripcion,
                    monto=curso.precio,
                    metodo=metodo_pago,
                    estado=estado_pago
                )

                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Curso.DoesNotExist:
            return Response({"error": "El curso no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            nuevo_estado = request.data.get('estado', instance.estado)
            
            # Validación: Si ya está cancelado, no se puede mover a ningún otro estado
            if instance.estado == 'cancelado' and nuevo_estado != 'cancelado':
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"error": "Esta inscripción ya fue cancelada y no puede ser reactivada. Debe crear una nueva."})

            # Validación: Si se intenta cancelar, verificamos que no esté pagado
            if nuevo_estado == 'cancelado':
                pago = Pago.objects.filter(id_inscripcion=instance).first()
                if pago and pago.estado == 'pagado':
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({"error": "No se puede cancelar una inscripción que ya ha sido pagada."})

            # Validación: Solo se puede confirmar si estaba pendiente
            if nuevo_estado == 'confirmado' and instance.estado != 'pendiente' and instance.estado != 'confirmado':
                 from rest_framework.exceptions import ValidationError
                 raise ValidationError({"error": "Solo se pueden confirmar inscripciones que estén en estado pendiente."})

            # Si se intenta confirmar (desde pendiente), validamos cupo nuevamente
            if nuevo_estado == 'confirmado' and instance.estado == 'pendiente':
                curso = instance.id_curso
                inscritos_confirmados = Inscripcion.objects.filter(
                    id_curso=curso, 
                    estado='confirmado'
                ).count()
                
                if inscritos_confirmados >= curso.cupo_maximo:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({"error": f"No se puede confirmar. El curso '{curso.nombre}' ya alcanzó su cupo máximo ({curso.cupo_maximo})."})

            # Ejecutar la actualización normal
            response = super().update(request, *args, **kwargs)
            
            # Sincronizar el Pago según el nuevo estado de la Inscripción
            inscripcion = self.get_object()
            if inscripcion.estado == 'confirmado':
                Pago.objects.filter(id_inscripcion=inscripcion).update(estado='pagado')
            elif inscripcion.estado == 'cancelado':
                Pago.objects.filter(id_inscripcion=inscripcion).update(estado='cancelado')
            elif inscripcion.estado == 'pendiente':
                Pago.objects.filter(id_inscripcion=inscripcion).update(estado='pendiente')
                
            return response

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class PagoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            nuevo_estado = request.data.get('estado', instance.estado)
            inscripcion = instance.id_inscripcion

            # Si el pago pasa a 'pagado', confirmamos la inscripción automáticamente
            if nuevo_estado == 'pagado' and instance.estado != 'pagado':
                if inscripcion.estado != 'confirmado':
                    curso = inscripcion.id_curso
                    inscritos = Inscripcion.objects.filter(id_curso=curso, estado='confirmado').count()
                    
                    if inscritos >= curso.cupo_maximo:
                        from rest_framework.exceptions import ValidationError
                        raise ValidationError({"error": f"No se puede registrar el pago. El curso '{curso.nombre}' ya está lleno."})
                    
                    inscripcion.estado = 'confirmado'
                    inscripcion.save()
            
            # Si el pago se cancela, cancelamos la inscripción
            elif nuevo_estado == 'cancelado' and instance.estado != 'cancelado':
                inscripcion.estado = 'cancelado'
                inscripcion.save()

            return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
