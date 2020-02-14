from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='task-home'),
    path('task/<int:task_id>', views.detail, name='task-detail'),
]
