from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.serializers.user_serializer import UsuarioSerializer

from rest_framework import viewsets
from rest_framework.decorators import action
from api.models import Tecnico, Usuario
from api.serializers.user_serializer import TecnicoCRUDSerializer

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
