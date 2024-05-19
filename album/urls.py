from django.urls import path

from .views import *

app_name = 'album'

album_view = AlbumView.as_view()
album_detail_view = AlbumDetailView.as_view()

urlpatterns = [
    path('', album_view, name='list'),
    path('create/', album_view, name='create'),
    path('<uuid:id_album>/songs/', album_detail_view, name='details'),
    path('<uuid:id_album>/add-song/', album_detail_view, name='add_song'),
    path('<uuid:id_album>/delete/', album_detail_view, name='delete'),
]
