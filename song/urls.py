from django.urls import path, re_path

from .views import *

app_name = 'song'

song_view = SongView.as_view()

urlpatterns = [
        path('album/<uuid:id_album>/songs/<uuid:id_song>/', song_view),
        path('album/<uuid:id_album>/songs/<uuid:id_song>/delete/', song_view),
]
