from django.urls import path

from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_to_job, name='apply_to_job'),
    path('apply/success/', views.application_success, name='application_success'),
]
