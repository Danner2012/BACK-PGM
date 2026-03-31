from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        try:
            rol_super = Rol.objects.get(id=1)
        except Rol.DoesNotExist:
            rol_super = Rol.objects.create(id=1, nombre='superadministrador')
            
        extra_fields.setdefault('id_rol', rol_super)

        return self.create_user(correo, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(unique=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True)
    estado = models.BooleanField(default=True)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.correo

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

from django.core.exceptions import ValidationError

class Administrador(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='administrador')
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    celular = models.CharField(max_length=20)
    ci = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if self.id_usuario.id_rol_id != 2:
            raise ValidationError("El usuario debe tener el rol 'administrador' (ID 2).")
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'api_administrador'

class Tecnico(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='tecnico')
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    celular = models.CharField(max_length=20)
    ci = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.id_usuario.id_rol_id != 3:
            raise ValidationError("El usuario debe tener el rol 'técnico' (ID 3).")
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'api_tecnico'

class Estudiante(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='estudiante')
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    celular = models.CharField(max_length=20)
    ci = models.CharField(max_length=20, unique=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.id_usuario.id_rol_id != 4:
            raise ValidationError("El usuario debe tener el rol 'estudiante' (ID 4).")
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'api_estudiante'
