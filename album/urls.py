from django.urls import path

from .views import *

album_view = AlbumView.as_view()
single_album_view = SingleAlbumView.as_view()

urlpatterns = [
    path('', album_view),
    path('create/', album_view),
    path('<uuid:id_album>/songs/', single_album_view),
    path('<uuid:id_album>/add-song/', single_album_view),
    path('<uuid:id_album>/delete/', single_album_view),
]
