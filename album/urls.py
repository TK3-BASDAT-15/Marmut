from django.urls import path

from .views import *

single_album_view = SingleAlbumView.as_view()

urlpatterns = [
    path('', AlbumView.as_view()),
    path('<uuid:id_album>/songs/', single_album_view),
    path('<uuid:id_album>/add-song/', single_album_view),
    path('<uuid:id_album>/delete/', single_album_view),
]
