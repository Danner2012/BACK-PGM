from rest_framework import serializers
from ..models import TipoCurso, Dia, Horario, Curso, CursoHorario, Administrador

class TipoCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCurso
        fields = '__all__'

class DiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dia
        fields = '__all__'

class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = '__all__'

class CursoHorarioSerializer(serializers.ModelSerializer):
    dia_nombre = serializers.ReadOnlyField(source='id_dia.nombre')
    horario_nombre = serializers.ReadOnlyField(source='id_horario.nombre')
    horario_detalle = serializers.SerializerMethodField()

    class Meta:
        model = CursoHorario
        fields = '__all__'

    def get_horario_detalle(self, obj):
        return f"{obj.id_horario.hora_inicio} - {obj.id_horario.hora_fin}"

class CursoSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.ReadOnlyField(source='id_tipo.nombre')
    horarios = CursoHorarioSerializer(many=True, read_only=True, source='cursohorario_set')
    
    class Meta:
        model = Curso
        fields = '__all__'
        extra_kwargs = {
            'id_administrador': {'required': False}
        }

    def create(self, validated_data):
        # El administrador se asignará en la vista basándose en el usuario autenticado
        return super().create(validated_data)
