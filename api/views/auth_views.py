from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers.auth_serializer import LoginSerializer
from api.services.auth_service import AuthService

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            correo = serializer.validated_data.get('correo')
            clave = serializer.validated_data.get('clave')
            
            user, error = AuthService.authenticate_user(correo, clave)
            
            if user:
                tokens = AuthService.get_tokens_for_user(user)
                return Response(tokens, status=status.HTTP_200_OK)
            else:
                return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
