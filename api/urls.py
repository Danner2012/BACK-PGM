from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.auth_views import LoginView
from api.views.user_views import UserProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
]
