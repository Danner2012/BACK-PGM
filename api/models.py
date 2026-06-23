from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.text import slugify

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
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipo_curso'

class Curso(models.Model):
    id_administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE, db_column='id_administrador')
    id_tipo = models.ForeignKey(TipoCurso, on_delete=models.PROTECT, db_column='id_tipo')
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
        return f"{self.nombre} ({self.hora_inicio} - {self.hora_fin})"

    class Meta:
        db_table = 'horario'
        unique_together = ('hora_inicio', 'hora_fin')

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

class Herramienta(models.Model):
    id_administrador = models.ForeignKey(Administrador, on_delete=models.PROTECT, db_column='id_administrador')
    id_categoria = models.ForeignKey(CategoriaHerramienta, on_delete=models.SET_NULL, null=True, db_column='id_categoria')
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    descripcion = models.TextField()
    uso = models.TextField()
    info_importante = models.TextField()
    imagen_previa = models.ImageField(upload_to='herramientas/fotos/', null=True, blank=True)
    stock_total = models.PositiveIntegerField(default=0)
    stock_disponible = models.PositiveIntegerField(default=0)
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
    archivo_esquema = models.ImageField(upload_to='herramientas/esquemas/', null=True, blank=True)
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

class TipoRecurso(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipo_recurso'

class TipoPractica(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'tipo_practica'

class Practica(models.Model):
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, db_column='id_curso')
    id_tipo_practica = models.ForeignKey(TipoPractica, on_delete=models.PROTECT, db_column='id_tipo_practica', null=True)
    id_usuario_creador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, db_column='id_usuario_creador')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id_curso.nombre} - {self.titulo}"

    class Meta:
        db_table = 'practica'

class RecursoPractica(models.Model):
    id_practica = models.ForeignKey(Practica, on_delete=models.CASCADE, db_column='id_practica', related_name='recursos')
    id_tipo_recurso = models.ForeignKey(TipoRecurso, on_delete=models.CASCADE, db_column='id_tipo_recurso')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    archivo_local = models.FileField(upload_to='practicas/recursos/', null=True, blank=True)
    url_externa = models.URLField(null=True, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'recurso_practica'

class PracticaHerramienta(models.Model):
    id_practica = models.ForeignKey(Practica, on_delete=models.CASCADE, db_column='id_practica', related_name='herramientas')
    id_herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, db_column='id_herramienta')
    cantidad_requerida = models.IntegerField()

    class Meta:
        db_table = 'practica_herramienta'
        unique_together = ('id_practica', 'id_herramienta')

class Prestamo(models.Model):
    id_inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, db_column='id_inscripcion')
    id_practica = models.ForeignKey(Practica, on_delete=models.CASCADE, db_column='id_practica')
    id_tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, db_column='id_tecnico')
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'prestamo'

class PrestamoDetalle(models.Model):
    ESTADO_CHOICES = [
        ('prestado', 'Prestado'),
        ('parcial', 'Parcial'),
        ('devuelto', 'Devuelto')
    ]
    id_prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, db_column='id_prestamo', related_name='detalles')
    id_herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, db_column='id_herramienta')
    cantidad_prestada = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='prestado')

    def clean(self):
        if self.pk is None: 
            if self.id_herramienta.stock_disponible < self.cantidad_prestada:
                raise ValidationError(f"No hay suficiente stock para {self.id_herramienta.nombre}. Disponible: {self.id_herramienta.stock_disponible}")

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.id_herramienta.stock_disponible -= self.cantidad_prestada
            self.id_herramienta.save()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'prestamo_detalle'
        unique_together = ('id_prestamo', 'id_herramienta')

class DevolucionHerramienta(models.Model):
    id_prestamo_detalle = models.ForeignKey(PrestamoDetalle, on_delete=models.CASCADE, db_column='id_prestamo_detalle', related_name='devoluciones')
    id_tecnico_receptor = models.ForeignKey(Tecnico, on_delete=models.CASCADE, db_column='id_tecnico_receptor')
    cantidad_devuelta = models.IntegerField()
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(null=True, blank=True)

    def clean(self):
        if not self.id_prestamo_detalle_id:
            return
        total_devuelto = sum(d.cantidad_devuelta for d in self.id_prestamo_detalle.devoluciones.all())
        if self.pk:
            original = DevolucionHerramienta.objects.get(pk=self.pk)
            total_devuelto -= original.cantidad_devuelta
        
        if total_devuelto + self.cantidad_devuelta > self.id_prestamo_detalle.cantidad_prestada:
            raise ValidationError("La cantidad total devuelta no puede superar la cantidad prestada.")

    def save(self, *args, **kwargs):
        if self.pk is None:
            # 1. Actualizar stock físico de la herramienta
            herramienta = self.id_prestamo_detalle.id_herramienta
            herramienta.stock_disponible += self.cantidad_devuelta
            herramienta.save()
            
            # 2. Guardar la devolución
            super().save(*args, **kwargs)
            
            # 3. Recalcular y actualizar estado del detalle del préstamo
            # Sumamos todas las devoluciones confirmadas para este detalle
            total_devuelto = DevolucionHerramienta.objects.filter(
                id_prestamo_detalle=self.id_prestamo_detalle
            ).aggregate(total=models.Sum('cantidad_devuelta'))['total'] or 0
            
            if total_devuelto >= self.id_prestamo_detalle.cantidad_prestada:
                self.id_prestamo_detalle.estado = 'devuelto'
            elif total_devuelto > 0:
                self.id_prestamo_detalle.estado = 'parcial'
            else:
                self.id_prestamo_detalle.estado = 'prestado'
            
            self.id_prestamo_detalle.save()
        else:
            super().save(*args, **kwargs)

    class Meta:
        db_table = 'devolucion_herramienta'

class PracticaEstudiante(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregada', 'Entregada'),
        ('aprobada', 'Aprobada'),
        ('reprobada', 'Reprobada')
    ]
    id_inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, db_column='id_inscripcion')
    id_practica = models.ForeignKey(Practica, on_delete=models.CASCADE, db_column='id_practica')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comentario_tecnico = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'practica_estudiante'
        unique_together = ('id_inscripcion', 'id_practica')

    def __str__(self):
        return f"{self.id_inscripcion.id_estudiante.nombre} - {self.id_practica.titulo}"

class EvidenciaPractica(models.Model):
    id_practica_estudiante = models.ForeignKey(PracticaEstudiante, on_delete=models.CASCADE, db_column='id_practica_estudiante', related_name='evidencias')
    archivo = models.FileField(upload_to='practicas/evidencias/')
    descripcion = models.TextField(null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidencia_practica'

    def __str__(self):
        return f"Evidencia de {self.id_practica_estudiante}"


# =====================================================================
#                        MÓDULO DE RECONOCIMIENTO IA
# =====================================================================

class AficheComponente(models.Model):
    clase_ia = models.CharField(max_length=50, unique=True, help_text="Ej: CAPACITOR, FPC, BOBINA")
    nombre = models.CharField(max_length=150)
    imagen_referencia = models.ImageField(upload_to='ia/afiches/referencias/', null=True, blank=True)
    imagen_simbolo = models.ImageField(upload_to='ia/afiches/simbolos/', null=True, blank=True)
    descripcion_general = models.TextField()
    herramientas = models.ManyToManyField(Herramienta, related_name='afiches_componentes', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Afiche - {self.nombre} ({self.clase_ia})"

    class Meta:
        db_table = 'afiche_componente'


class AficheFuncion(models.Model):
    id_afiche = models.ForeignKey(AficheComponente, on_delete=models.CASCADE, related_name='funciones')
    texto = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id_afiche.nombre} - Función: {self.texto}"

    class Meta:
        db_table = 'afiche_funcion'


class AficheCaracteristica(models.Model):
    id_afiche = models.ForeignKey(AficheComponente, on_delete=models.CASCADE, related_name='caracteristicas')
    texto = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id_afiche.nombre} - Característica: {self.texto}"

    class Meta:
        db_table = 'afiche_caracteristica'


class AficheMedicionPaso(models.Model):
    id_afiche = models.ForeignKey(AficheComponente, on_delete=models.CASCADE, related_name='pasos_medicion')
    orden = models.PositiveIntegerField()
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.id_afiche.nombre} - Medición Paso {self.orden}"

    class Meta:
        db_table = 'afiche_medicion_paso'
        ordering = ['orden']


class AficheMedicionRecurso(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video')
    ]
    id_paso = models.ForeignKey(AficheMedicionPaso, on_delete=models.CASCADE, related_name='recursos')
    archivo = models.FileField(upload_to='ia/mediciones/recursos/')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='imagen')

    def __str__(self):
        return f"Recurso {self.tipo} - Paso Medición {self.id_paso.id}"

    class Meta:
        db_table = 'afiche_medicion_recurso'


class AficheProcedimientoPaso(models.Model):
    id_afiche = models.ForeignKey(AficheComponente, on_delete=models.CASCADE, related_name='pasos_procedimiento')
    orden = models.PositiveIntegerField()
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.id_afiche.nombre} - Procedimiento Paso {self.orden}"

    class Meta:
        db_table = 'afiche_procedimiento_paso'
        ordering = ['orden']


class AficheProcedimientoRecurso(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video')
    ]
    id_paso = models.ForeignKey(AficheProcedimientoPaso, on_delete=models.CASCADE, related_name='recursos')
    archivo = models.FileField(upload_to='ia/procedimientos/recursos/')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='imagen')

    def __str__(self):
        return f"Recurso {self.tipo} - Paso Procedimiento {self.id_paso.id}"

    class Meta:
        db_table = 'afiche_procedimiento_recurso'

