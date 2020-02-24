from django.urls import path
from . import views
from .views import TaskListView, TaskDetailListView, UserPostListView

urlpatterns = [
    path('', TaskListView.as_view(), name='task-home'),
    path('task/<int:pk>', TaskDetailListView.as_view(), name='task-detail'),
    path('task/<str:username>', UserPostListView.as_view(), name='user-tasks'),
]
