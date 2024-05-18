from django.urls import path

from . import views
app_name = 'podcast'

urlpatterns = [
    path('', views.list_podcasts, name='list_podcasts'),
    path('create_podcast/', views.create_podcast, name='create_podcast'),
    path('<str:podcast_id>/', views.view_episodes, name='view_episodes'),
    path('add_episode/<str:podcast_id>', views.add_episode, name='add_episode'),
    path('play_podcast/<str:podcast_id>/', views.play_podcast, name='play_podcast'),
    path('delete_episode/<str:episode_id>/', views.delete_episode, name='delete_episode'),
    path('delete_podcast/<str:podcast_id>/', views.delete_podcast, name='delete_podcast'),
]