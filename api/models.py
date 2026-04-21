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

class TipoCurso(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipo_curso'

class Curso(models.Model):
    id_administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE, db_column='id_administrador')
    id_tipo = models.ForeignKey(TipoCurso, on_delete=models.CASCADE, db_column='id_tipo')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cupo_maximo = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'curso'

class CursoTecnico(models.Model):
    id_tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, db_column='id_tecnico')
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso')
    estado = models.CharField(max_length=20, default='activo') # activo/inactivo
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curso_tecnico'

class Dia(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'dia'

class Horario(models.Model):
    nombre = models.CharField(max_length=100)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'horario'

class CursoHorario(models.Model):
    id_horario = models.ForeignKey(Horario, on_delete=models.CASCADE, db_column='id_horario')
    id_dia = models.ForeignKey(Dia, on_delete=models.CASCADE, db_column='id_dia')
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso')

    class Meta:
        db_table = 'curso_horario'

class Inscripcion(models.Model):
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso', null=True)
    id_estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, db_column='id_estudiante')
    estado = models.CharField(max_length=20, default='pendiente')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inscripcion'

class Pago(models.Model):
    id_inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, db_column='id_inscripcion')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='pendiente')
    metodo = models.CharField(max_length=20) # Fisico/QR
    fecha_pago = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pago'

class CategoriaHerramienta(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categoria_herramienta'

from django.utils.text import slugify

class Herramienta(models.Model):
    id_administrador = models.ForeignKey(Administrador, on_delete=models.PROTECT, db_column='id_administrador')
    id_categoria = models.ForeignKey(CategoriaHerramienta, on_delete=models.SET_NULL, null=True, db_column='id_categoria')
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    descripcion = models.TextField()
    uso = models.TextField()
    info_importante = models.TextField()
    imagen_previa = models.ImageField(upload_to='herramientas/fotos/', null=True, blank=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'herramienta'

class Modelo3D(models.Model):
    id_herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name='modelos_3d', db_column='id_herramienta')
    archivo = models.FileField(upload_to='herramientas/modelos/')
    nombre_identificador = models.CharField(max_length=100, help_text="Nombre para identificar esta parte o variante")
    descripcion = models.TextField(blank=True, null=True)
    escala = models.FloatField(default=1.0)
    rotacion_default = models.CharField(max_length=50, default='0,0,0')
    posicion_default = models.CharField(max_length=50, default='0,0,0')
    estado = models.BooleanField(default=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id_herramienta.nombre} - {self.nombre_identificador}"

    class Meta:
        db_table = 'modelo_3d'
