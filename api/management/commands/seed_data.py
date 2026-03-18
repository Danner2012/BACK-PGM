from django.core.management.base import BaseCommand
from api.models import Rol, Usuario

class Command(BaseCommand):
    help = 'Seeds the database with roles and initial users'

    def handle(self, *args, **kwargs):
        roles_data = [
            {'id': 1, 'nombre': 'superadministrador'},
            {'id': 2, 'nombre': 'administrador'},
            {'id': 3, 'nombre': 'técnico'},
            {'id': 4, 'nombre': 'estudiante'},
        ]

        for r in roles_data:
            rol, created = Rol.objects.get_or_create(id=r['id'], defaults={'nombre': r['nombre']})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Rol creado: {r["nombre"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Rol ya existe: {r["nombre"]}'))

        users_data = [
            {'correo': 'superadmin@celucentro.com', 'password': 'superpassword123', 'rol_id': 1},
            {'correo': 'admin@celucentro.com', 'password': 'adminpassword123', 'rol_id': 2},
            {'correo': 'tecnico@celucentro.com', 'password': 'tecnicopassword123', 'rol_id': 3},
            {'correo': 'estudiante@celucentro.com', 'password': 'estudiantepassword123', 'rol_id': 4},
        ]

        for u in users_data:
            if not Usuario.objects.filter(correo=u['correo']).exists():
                rol = Rol.objects.get(id=u['rol_id'])
                Usuario.objects.create_user(
                    correo=u['correo'],
                    password=u['password'],
                    id_rol=rol,
                    estado=True
                )
                self.stdout.write(self.style.SUCCESS(f'Usuario creado: {u["correo"]} (Rol: {rol.nombre})'))
            else:
                self.stdout.write(self.style.WARNING(f'Usuario ya existe: {u["correo"]}'))
