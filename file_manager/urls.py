from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Render the UI
    path('api/upload', views.upload_file, name='upload_file'),
    path('api/operation', views.perform_operation, name='perform_operation'),
    path('api/download', views.download_file, name='download_file'),
]
