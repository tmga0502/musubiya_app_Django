from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, DetailView

app_name = 'c_data'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    path('user/<int:pk>/profile', views.profile, name='profile'),
    path('user/<int:pk>/list', views.list, name='list'),
    path('user/<int:pk>/new', views.new_data, name='new_data'),
    path('user/<int:pk>/detail/<int:CustomerData_id>',
         views.detail, name='detail'),
    path('user/<int:pk>/conditions/<int:CustomerData_id>',
         views.conditions, name='conditions'),
    path('user/<int:pk>/prospect', views.prospect, name='prospect'),
    path('user/<int:pk>/progress', views.progress, name='progress'),
    path('user/<int:pk>/budget_control',
         views.budget_control, name='budget_control'),
    path('user/<int:pk>/data', views.data, name='data'),
]
