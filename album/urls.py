from django.urls import path

from .views import *

album_list_view = AlbumListView.as_view()
album_detail_view = AlbumDetailView.as_view()

urlpatterns = [
    path('', album_list_view),
    path('create/', album_list_view),
    path('<uuid:id_album>/songs/', album_detail_view),
    path('<uuid:id_album>/add-song/', album_detail_view),
    path('<uuid:id_album>/delete/', album_detail_view),
]
