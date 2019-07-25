from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

app_name = 'accounts'

urlpatterns = [
    path('', views.account_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
