from django.contrib import admin
from .models import (
    Rol, Usuario, Administrador, Tecnico, Estudiante, 
    TipoCurso, Curso, CursoTecnico, Dia, Horario, 
    CursoHorario, Inscripcion, Pago
)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'correo', 'id_rol', 'estado', 'is_staff')
    list_filter = ('id_rol', 'estado')
    search_fields = ('correo',)

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido_paterno', 'ci', 'celular')
    search_fields = ('nombre', 'apellido_paterno', 'ci')

@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido_paterno', 'ci', 'especialidad', 'celular')
    search_fields = ('nombre', 'apellido_paterno', 'ci', 'especialidad')

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido_paterno', 'ci', 'fecha_registro', 'celular')
    search_fields = ('nombre', 'apellido_paterno', 'ci')

@admin.register(TipoCurso)
class TipoCursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'id_tipo', 'precio', 'estado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'id_tipo')
    search_fields = ('nombre',)

@admin.register(CursoTecnico)
class CursoTecnicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_tecnico', 'id_curso', 'estado', 'fecha_asignacion')
    list_filter = ('estado',)

@admin.register(Dia)
class DiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'hora_inicio', 'hora_fin')

@admin.register(CursoHorario)
class CursoHorarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_curso', 'id_dia', 'id_horario', 'cupo_maximo')
    list_filter = ('id_dia', 'id_horario')

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_estudiante', 'id_curso_horario', 'estado', 'fecha_inscripcion')
    list_filter = ('estado',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_inscripcion', 'monto', 'estado', 'metodo', 'fecha_pago')
    list_filter = ('estado', 'metodo')
