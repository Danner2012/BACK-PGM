from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    clave = serializers.CharField(write_only=True)
