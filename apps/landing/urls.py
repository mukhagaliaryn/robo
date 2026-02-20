from django.urls import path
from .views import main, auth

app_name = 'landing'

urlpatterns = [
    path('', main.landing_view, name='index'),

    # auth urls...
    path('auth/login/', auth.login_view, name='login'),
    path('auth/register/', auth.register_view, name='register'),
    path('auth/logout/', auth.logout_view, name='logout'),

]
