from django.urls import path
from . import views

urlpatterns = [
    path('tasks', views.task_list, name='task-list'),
    path('tasks/<int:id>', views.task_detail, name='task-detail'),
    path('insights', views.insights, name='insights'),
]