from django.urls import path
from apps.learner.views import dashboard
from .views import auth, account

app_name = 'learner'

urlpatterns = [
    # auth urls...
    path('auth/login/', auth.login_view, name='login'),
    path('auth/register/', auth.register_view, name='register'),
    path('auth/logout/', auth.logout_view, name='logout'),

    # account urls...
    path('account/me/', account.account_view, name='account'),
    path('account/settings/', account.settings_view, name='settings'),

    path('', dashboard.learner_dashboard_view, name='dashboard'),
]
