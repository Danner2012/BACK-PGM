from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth_views import LoginView
from api.views.user_views import UserProfileView, TecnicoViewSet, EstudianteViewSet
from api.views.curso_views import (
    TipoCursoViewSet, DiaViewSet, HorarioViewSet, 
    CursoViewSet, CursoHorarioViewSet, CursoTecnicoViewSet,
    InscripcionViewSet
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

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
