from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('update-genres/', views.update_genres, name='update_genres'),
]