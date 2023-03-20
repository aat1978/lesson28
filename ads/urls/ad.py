from django.urls import path
from ads import views

urlpatterns = [
    path('', views.AdView.as_view()),
    path('create/', views.AdCreateView.as_view()),
    path('<int:pk>', views.AdDetailView.as_view()),
    path('<int:pk>/update/', views.AdUpdateView.as_view()),
    path('<int:pk>/delete/', views.AdDeleteView.as_view()),
    path('<int:pk>/upload_image/', views.AdUploadImageView.as_view()),
]
