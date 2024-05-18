from django.urls import path

from .views import *

app_name = 'album'

album_view = AlbumView.as_view()
album_detail_view = AlbumDetailView.as_view()

urlpatterns = [
    path('', album_view, name='album'),
    path('create/', album_view, name='album_create'),
    path('<uuid:id_album>/songs/', album_detail_view, name='album_detail'),
    path('<uuid:id_album>/add-song/', album_detail_view, name='album_add-song'),
    path('<uuid:id_album>/delete/', album_detail_view, name='album_delete'),
]
