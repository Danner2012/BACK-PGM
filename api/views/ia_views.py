import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from api.models import (
    AficheComponente, AficheFuncion, AficheCaracteristica,
    AficheMedicionPaso, AficheMedicionRecurso,
    AficheProcedimientoPaso, AficheProcedimientoRecurso,
    Herramienta
)
from api.serializers.ia_serializer import AficheComponenteSerializer

class AficheComponenteViewSet(viewsets.ModelViewSet):
    queryset = AficheComponente.objects.all().order_by('nombre')
    serializer_class = AficheComponenteSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['get'], url_path='clase/(?P<clase_ia>[a-zA-Z0-9_\\-]+)')
    def buscar_por_clase(self, request, clase_ia=None):
        """Buscar afiche de componente por la clase que detecta la IA (insensible a mayúsculas)"""
        try:
            afiche = AficheComponente.objects.get(clase_ia__iexact=clase_ia)
            serializer = self.get_serializer(afiche)
            return Response(serializer.data)
        except AficheComponente.DoesNotExist:
            return Response(
                {'detail': f'Afiche no encontrado para la clase {clase_ia}'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear un afiche con sus datos estructurados y archivos multimedia anidados"""
        data = request.data
        
        # 1. Crear el objeto base del Afiche
        afiche = AficheComponente.objects.create(
            clase_ia=data.get('clase_ia', '').upper(),
            nombre=data.get('nombre', ''),
            descripcion_general=data.get('descripcion_general', ''),
            imagen_referencia=request.FILES.get('imagen_referencia'),
            imagen_simbolo=request.FILES.get('imagen_simbolo')
        )

        # 2. Asignar Herramientas (ManyToMany)
        herramientas_str = data.get('herramientas', '[]')
        try:
            herramientas_ids = json.loads(herramientas_str)
            if herramientas_ids:
                herramientas = Herramienta.objects.filter(id__in=herramientas_ids)
                afiche.herramientas.set(herramientas)
        except Exception as e:
            print("Error parsing herramientas:", e)

        # 3. Guardar Funciones (Checks)
        funciones_str = data.get('funciones', '[]')
        try:
            funciones_data = json.loads(funciones_str)
            for f in funciones_data:
                if f.get('texto'):
                    AficheFuncion.objects.create(
                        id_afiche=afiche,
                        texto=f.get('texto'),
                        activo=f.get('activo', True)
                    )
        except Exception as e:
            print("Error parsing funciones:", e)

        # 4. Guardar Características (Viñetas)
        caracteristicas_str = data.get('caracteristicas', '[]')
        try:
            caracteristicas_data = json.loads(caracteristicas_str)
            for c in caracteristicas_data:
                if c.get('texto'):
                    AficheCaracteristica.objects.create(
                        id_afiche=afiche,
                        texto=c.get('texto')
                    )
        except Exception as e:
            print("Error parsing caracteristicas:", e)

        # 5. Guardar Pasos de Medición y sus Archivos
        pasos_medicion_str = data.get('pasos_medicion', '[]')
        try:
            pasos_medicion_data = json.loads(pasos_medicion_str)
            for idx, p in enumerate(pasos_medicion_data):
                paso_obj = AficheMedicionPaso.objects.create(
                    id_afiche=afiche,
                    orden=p.get('orden', idx + 1),
                    descripcion=p.get('descripcion', '')
                )
                
                # Buscar archivos asociados a este paso (ej. medicion_archivos_paso_0)
                file_key = f'medicion_archivos_paso_{idx}'
                archivos_subidos = request.FILES.getlist(file_key)
                for f in archivos_subidos:
                    tipo_rec = 'video' if f.content_type.startswith('video/') else 'imagen'
                    AficheMedicionRecurso.objects.create(
                        id_paso=paso_obj,
                        archivo=f,
                        tipo=tipo_rec
                    )
        except Exception as e:
            print("Error parsing pasos de medición:", e)

        # 6. Guardar Pasos de Procedimiento y sus Archivos
        pasos_procedimiento_str = data.get('pasos_procedimiento', '[]')
        try:
            pasos_procedimiento_data = json.loads(pasos_procedimiento_str)
            for idx, p in enumerate(pasos_procedimiento_data):
                paso_obj = AficheProcedimientoPaso.objects.create(
                    id_afiche=afiche,
                    orden=p.get('orden', idx + 1),
                    descripcion=p.get('descripcion', '')
                )
                
                # Buscar archivos asociados a este paso (ej. procedimiento_archivos_paso_0)
                file_key = f'procedimiento_archivos_paso_{idx}'
                archivos_subidos = request.FILES.getlist(file_key)
                for f in archivos_subidos:
                    tipo_rec = 'video' if f.content_type.startswith('video/') else 'imagen'
                    AficheProcedimientoRecurso.objects.create(
                        id_paso=paso_obj,
                        archivo=f,
                        tipo=tipo_rec
                    )
        except Exception as e:
            print("Error parsing pasos de procedimiento:", e)

        serializer = self.get_serializer(afiche)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Actualizar afiche limpiando relaciones de lista y guardando nuevos valores"""
        afiche = self.get_object()
        data = request.data

        # 1. Actualizar datos base del Afiche
        afiche.clase_ia = data.get('clase_ia', afiche.clase_ia).upper()
        afiche.nombre = data.get('nombre', afiche.nombre)
        afiche.descripcion_general = data.get('descripcion_general', afiche.descripcion_general)
        
        if 'imagen_referencia' in request.FILES:
            afiche.imagen_referencia = request.FILES['imagen_referencia']
        if 'imagen_simbolo' in request.FILES:
            afiche.imagen_simbolo = request.FILES['imagen_simbolo']
        afiche.save()

        # 2. Actualizar Herramientas (ManyToMany)
        if 'herramientas' in data:
            try:
                herramientas_ids = json.loads(data.get('herramientas', '[]'))
                herramientas = Herramienta.objects.filter(id__in=herramientas_ids)
                afiche.herramientas.set(herramientas)
            except Exception as e:
                print("Error actualizando herramientas:", e)

        # 3. Actualizar Funciones (Limpiar y volver a crear)
        if 'funciones' in data:
            try:
                afiche.funciones.all().delete()
                funciones_data = json.loads(data.get('funciones', '[]'))
                for f in funciones_data:
                    if f.get('texto'):
                        AficheFuncion.objects.create(
                            id_afiche=afiche,
                            texto=f.get('texto'),
                            activo=f.get('activo', True)
                        )
            except Exception as e:
                print("Error actualizando funciones:", e)

        # 4. Actualizar Características (Limpiar y volver a crear)
        if 'caracteristicas' in data:
            try:
                afiche.caracteristicas.all().delete()
                caracteristicas_data = json.loads(data.get('caracteristicas', '[]'))
                for c in caracteristicas_data:
                    if c.get('texto'):
                        AficheCaracteristica.objects.create(
                            id_afiche=afiche,
                            texto=c.get('texto')
                        )
            except Exception as e:
                print("Error actualizando características:", e)

        # 5. Actualizar Pasos de Medición y sus Archivos (Limpiar y volver a crear)
        if 'pasos_medicion' in data:
            try:
                # OJO: Para no perder archivos multimedia existentes al reescribir,
                # podemos recopilar los recursos de los pasos que continúan.
                # Para simplificar y evitar fugas, guardaremos de manera limpia:
                pasos_medicion_data = json.loads(data.get('pasos_medicion', '[]'))
                
                # Guardamos los recursos multimedia existentes temporalmente si su ID está mapeado
                recursos_a_mantener = []
                for p in pasos_medicion_data:
                    recursos_existentes = p.get('recursos_existentes', [])
                    for rec in recursos_existentes:
                        recursos_a_mantener.append(rec.get('id'))

                # Borrar pasos antiguos (también borra en cascada los recursos no listados)
                pasos_antiguos = afiche.pasos_medicion.all()
                for pa in pasos_antiguos:
                    # Borrar recursos que no se mantendrán
                    pa.recursos.exclude(id__in=recursos_a_mantener).delete()
                pasos_antiguos.delete()

                # Volver a crear los pasos
                for idx, p in enumerate(pasos_medicion_data):
                    paso_obj = AficheMedicionPaso.objects.create(
                        id_afiche=afiche,
                        orden=p.get('orden', idx + 1),
                        descripcion=p.get('descripcion', '')
                    )

                    # Si tenía recursos existentes que mantener, los reasignamos al nuevo paso
                    recursos_existentes_data = p.get('recursos_existentes', [])
                    for rec_data in recursos_existentes_data:
                        rec_id = rec_data.get('id')
                        try:
                            # Reasociar el recurso al nuevo paso
                            recurso_db = AficheMedicionRecurso.objects.get(id=rec_id)
                            recurso_db.id_paso = paso_obj
                            recurso_db.save()
                        except AficheMedicionRecurso.DoesNotExist:
                            pass

                    # Agregar nuevos archivos subidos para este paso
                    file_key = f'medicion_archivos_paso_{idx}'
                    archivos_subidos = request.FILES.getlist(file_key)
                    for f in archivos_subidos:
                        tipo_rec = 'video' if f.content_type.startswith('video/') else 'imagen'
                        AficheMedicionRecurso.objects.create(
                            id_paso=paso_obj,
                            archivo=f,
                            tipo=tipo_rec
                        )
            except Exception as e:
                print("Error actualizando pasos de medición:", e)

        # 6. Actualizar Pasos de Procedimiento y sus Archivos (Limpiar y volver a crear)
        if 'pasos_procedimiento' in data:
            try:
                pasos_procedimiento_data = json.loads(data.get('pasos_procedimiento', '[]'))
                
                # Guardamos recursos existentes a mantener
                recursos_a_mantener = []
                for p in pasos_procedimiento_data:
                    recursos_existentes = p.get('recursos_existentes', [])
                    for rec in recursos_existentes:
                        recursos_a_mantener.append(rec.get('id'))

                # Borrar pasos antiguos
                pasos_antiguos = afiche.pasos_procedimiento.all()
                for pa in pasos_antiguos:
                    pa.recursos.exclude(id__in=recursos_a_mantener).delete()
                pasos_antiguos.delete()

                # Volver a crear los pasos
                for idx, p in enumerate(pasos_procedimiento_data):
                    paso_obj = AficheProcedimientoPaso.objects.create(
                        id_afiche=afiche,
                        orden=p.get('orden', idx + 1),
                        descripcion=p.get('descripcion', '')
                    )

                    # Reasociar recursos existentes
                    recursos_existentes_data = p.get('recursos_existentes', [])
                    for rec_data in recursos_existentes_data:
                        rec_id = rec_data.get('id')
                        try:
                            recurso_db = AficheProcedimientoRecurso.objects.get(id=rec_id)
                            recurso_db.id_paso = paso_obj
                            recurso_db.save()
                        except AficheProcedimientoRecurso.DoesNotExist:
                            pass

                    # Agregar nuevos archivos subidos para este paso
                    file_key = f'procedimiento_archivos_paso_{idx}'
                    archivos_subidos = request.FILES.getlist(file_key)
                    for f in archivos_subidos:
                        tipo_rec = 'video' if f.content_type.startswith('video/') else 'imagen'
                        AficheProcedimientoRecurso.objects.create(
                            id_paso=paso_obj,
                            archivo=f,
                            tipo=tipo_rec
                        )
            except Exception as e:
                print("Error actualizando pasos de procedimiento:", e)

        serializer = self.get_serializer(afiche)
        return Response(serializer.data, status=status.HTTP_200_OK)
