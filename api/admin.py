from django.contrib import admin
from .models import (
    Rol, Usuario, Administrador, Tecnico, Estudiante, 
    TipoCurso, Curso, CursoTecnico, Dia, Horario, 
    CursoHorario, Inscripcion, Pago, Herramienta, CategoriaHerramienta,
    Modelo3D, TipoRecurso, TipoPractica, Practica, RecursoPractica,
    PracticaHerramienta, PrestamoHerramienta, DevolucionHerramienta
)

@admin.register(CategoriaHerramienta)
class CategoriaHerramientaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'estado')

@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'id_categoria', 'stock_total', 'stock_disponible', 'estado')
    list_filter = ('estado', 'id_categoria')
    search_fields = ('nombre',)

@admin.register(Modelo3D)
class Modelo3DAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_herramienta', 'nombre_identificador', 'estado')

@admin.register(TipoRecurso)
class TipoRecursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(TipoPractica)
class TipoPracticaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(Practica)
class PracticaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'id_curso', 'id_tipo_practica', 'estado')
    list_filter = ('id_curso', 'id_tipo_practica', 'estado')

@admin.register(RecursoPractica)
class RecursoPracticaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'id_practica', 'id_tipo_recurso', 'estado')

@admin.register(PracticaHerramienta)
class PracticaHerramientaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_practica', 'id_herramienta', 'cantidad_requerida')

@admin.register(PrestamoHerramienta)
class PrestamoHerramientaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_inscripcion', 'id_practica', 'id_herramienta', 'cantidad_prestada', 'estado', 'fecha_prestamo')
    list_filter = ('estado', 'fecha_prestamo')

@admin.register(DevolucionHerramienta)
class DevolucionHerramientaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_prestamo', 'id_tecnico_receptor', 'cantidad_devuelta', 'fecha_devolucion')

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
    list_display = ('id', 'nombre', 'id_tipo', 'precio', 'cupo_maximo', 'estado', 'fecha_inicio', 'fecha_fin')
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
    list_display = ('id', 'id_curso', 'id_dia', 'id_horario')
    list_filter = ('id_dia', 'id_horario')

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_estudiante', 'id_curso', 'estado', 'fecha_inscripcion')
    list_filter = ('estado',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_inscripcion', 'monto', 'estado', 'metodo', 'fecha_pago')
    list_filter = ('estado', 'metodo')
