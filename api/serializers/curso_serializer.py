from rest_framework import serializers
from ..models import TipoCurso, Dia, Horario, Curso, CursoHorario, Administrador, CursoTecnico, Tecnico, Inscripcion, Estudiante

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

class TecnicoSimpleSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    class Meta:
        model = Tecnico
        fields = ['id', 'nombre', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'especialidad']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido_paterno} {obj.apellido_materno}".strip()

class CursoTecnicoSerializer(serializers.ModelSerializer):
    tecnico_detalle = TecnicoSimpleSerializer(source='id_tecnico', read_only=True)
    class Meta:
        model = CursoTecnico
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.ReadOnlyField(source='id_tipo.nombre')
    horarios = CursoHorarioSerializer(many=True, read_only=True, source='cursohorario_set')
    tecnicos = CursoTecnicoSerializer(many=True, read_only=True, source='cursotecnico_set')
    
    class Meta:
        model = Curso
        fields = '__all__'
        extra_kwargs = {
            'id_administrador': {'required': False}
        }

    def create(self, validated_data):
        return super().create(validated_data)

class EstudianteSimpleSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    class Meta:
        model = Estudiante
        fields = ['id', 'nombre', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'celular', 'ci']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido_paterno} {obj.apellido_materno}".strip()

class InscripcionSerializer(serializers.ModelSerializer):
    estudiante_detalle = EstudianteSimpleSerializer(source='id_estudiante', read_only=True)
    curso_horario_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = Inscripcion
        fields = '__all__'

    def get_curso_horario_detalle(self, obj):
        ch = obj.id_curso_horario
        return {
            'curso_nombre': ch.id_curso.nombre,
            'dia_nombre': ch.id_dia.nombre,
            'horario_detalle': f"{ch.id_horario.hora_inicio} - {ch.id_horario.hora_fin}",
            'precio': ch.id_curso.precio
        }
