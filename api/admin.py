from django.contrib import admin
from .models import Rol, Usuario

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'correo', 'id_rol', 'estado', 'is_staff')
    list_filter = ('id_rol', 'estado')
    search_fields = ('correo',)
