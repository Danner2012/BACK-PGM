from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from ..models import Practica, TipoRecurso, RecursoPractica, PracticaHerramienta, PrestamoHerramienta, DevolucionHerramienta
from ..serializers.practica_serializer import (
    PracticaSerializer, TipoRecursoSerializer, RecursoPracticaSerializer,
    PracticaHerramientaSerializer, PrestamoHerramientaSerializer, DevolucionHerramientaSerializer
)

class TipoRecursoViewSet(viewsets.ModelViewSet):
    queryset = TipoRecurso.objects.all()
    serializer_class = TipoRecursoSerializer

class PracticaViewSet(viewsets.ModelViewSet):
    queryset = Practica.objects.all()
    serializer_class = PracticaSerializer

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
    queryset = RecursoPractica.objects.filter(estado=True)
    serializer_class = RecursoPracticaSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.estado = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PracticaHerramientaViewSet(viewsets.ModelViewSet):
    queryset = PracticaHerramienta.objects.all()
    serializer_class = PracticaHerramientaSerializer

class PrestamoHerramientaViewSet(viewsets.ModelViewSet):
    queryset = PrestamoHerramienta.objects.filter(activo=True)
    serializer_class = PrestamoHerramientaSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DevolucionHerramientaViewSet(viewsets.ModelViewSet):
    queryset = DevolucionHerramienta.objects.all()
    serializer_class = DevolucionHerramientaSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().create(request, *args, **kwargs)
