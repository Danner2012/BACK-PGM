from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth_views import LoginView
from api.views.user_views import UserProfileView, TecnicoViewSet, EstudianteViewSet
from api.views.curso_views import (
    TipoCursoViewSet, DiaViewSet, HorarioViewSet, 
    CursoViewSet, CursoHorarioViewSet, CursoTecnicoViewSet,
    InscripcionViewSet, PagoViewSet
)
from api.views.herramienta_views import (
    CategoriaHerramientaViewSet,
    HerramientaViewSet,
    Modelo3DViewSet
)
from api.views.practica_views import (
    TipoRecursoViewSet, TipoPracticaViewSet, PracticaViewSet, RecursoPracticaViewSet,
    PracticaHerramientaViewSet, PrestamoViewSet, PrestamoDetalleViewSet, DevolucionHerramientaViewSet
)

router = DefaultRouter()
router.register(r'tecnicos', TecnicoViewSet, basename='tecnico')
router.register(r'estudiantes', EstudianteViewSet, basename='estudiante')
router.register(r'tipos-curso', TipoCursoViewSet, basename='tipo-curso')
router.register(r'dias', DiaViewSet, basename='dia')
router.register(r'horarios', HorarioViewSet, basename='horario')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'curso-horarios', CursoHorarioViewSet, basename='curso-horario')
router.register(r'curso-tecnicos', CursoTecnicoViewSet, basename='curso-tecnico')
router.register(r'inscripciones', InscripcionViewSet, basename='inscripcion')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'categorias-herramientas', CategoriaHerramientaViewSet, basename='categoria-herramienta')
router.register(r'herramientas', HerramientaViewSet, basename='herramienta')
router.register(r'modelos-3d', Modelo3DViewSet, basename='modelo-3d')
router.register(r'tipos-recurso', TipoRecursoViewSet, basename='tipo-recurso')
router.register(r'tipos-practica', TipoPracticaViewSet, basename='tipo-practica')
router.register(r'practicas', PracticaViewSet, basename='practica')
router.register(r'recursos-practica', RecursoPracticaViewSet, basename='recurso-practica')
router.register(r'practica-herramientas', PracticaHerramientaViewSet, basename='practica-herramienta')
router.register(r'prestamos', PrestamoViewSet, basename='prestamo')
router.register(r'detalles-prestamos', PrestamoDetalleViewSet, basename='prestamo-detalle')
router.register(r'devoluciones-herramientas', DevolucionHerramientaViewSet, basename='devolucion-herramienta')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
