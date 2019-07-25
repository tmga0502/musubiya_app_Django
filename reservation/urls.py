from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required

app_name = 'reservation'

urlpatterns = [
    path('/month', login_required(views.Index.as_view()), name='index'),
    path('/month/<int:year>/<int:month>/<int:day>/',
         login_required(views.Index.as_view()), name='index'),
    path('/month/create', login_required(views.MonthCalendar.as_view()), name='create'),
    path('/month/create/<int:year>/<int:month>/<int:day>/',
         login_required(views.MonthCalendar.as_view()), name='create'),
    path('/month/update/<int:pk>',
         login_required(views.ScheduleUpdateView.as_view()), name='update'),
    path('/month/delete/<int:pk>',
         login_required(views.ScheduleDeleteView.as_view()), name='delete'),
]
