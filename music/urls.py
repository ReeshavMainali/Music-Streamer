from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tracks/', views.track_list, name='track_list'),
    path('tracks/<int:track_id>/', views.track_detail, name='track_detail'),
    path('upload/', views.upload_track, name='upload_track'),
    path('update-listen-status/', views.update_listen_status, name='update_listen_status'),
    # New URL patterns for database file serving
    path('media/db/musicfile/<str:filename>', views.serve_music_file, name='serve_music_file'),
    path('media/db/coverimage/<str:filename>', views.serve_cover_image, name='serve_cover_image'),
]