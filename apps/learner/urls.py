from django.urls import path
from apps.learner.views import dashboard
from .views import account

app_name = 'learner'

urlpatterns = [
    # account urls...
    path('account/me/', account.account_view, name='account'),
    path('account/settings/', account.settings_view, name='settings'),

    path('', dashboard.learner_dashboard_view, name='dashboard'),
]
