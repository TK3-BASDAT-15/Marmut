from django.urls import path

from playlist.views import *

app_name = 'playlist'

urlpatterns = [
    path('/', user_playlist, name = 'user_playlist'),
    path('add-playlist/', add_playlist , name = 'add_playlist' ),
    path('detail-playlist/', user_playlist_detail, 'user_playlist_detail'),
    path('edit-playlist/', user_playlist_edit, name = 'user_playlist_edit'),
    path('delete-playlist/', user_playlist_delete, name = 'user_playlist_delete'),
    path('shuffle-playlist/', user_playlist_shuffle, name = 'user_playlist_shuffle'),
    path('song/', user_song, name = 'user_song'),
    path('play-song/', user_play_song, name = 'user_play_song'),
    path('delete-song/', user_delete_song, name = 'user_delete_song'),
    path('add-song/', user_add_song, name = 'user_add_song'),
    path('play-playlist/', play_user_playlist, name = 'play_user_Playlist'),
    path('detail-song/', user_song_detail, name = 'user_song_detail'),
    path('download/', user_download, name = 'user_download'),
    path('to-playlist/', add_song_spesific_playlist, name = 'add_song_spesific_playlist'),
    path('list-download/', list_download, name = list_download)  
]
