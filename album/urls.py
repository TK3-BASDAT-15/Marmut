from django.urls import path

from .views import *

urlpatterns = [
    path('', AlbumView.as_view()),
    path('label/', AlbumView.as_view()),
    path('add-album/', AlbumView.as_view()),
    path('<uuid:id_album>/songs/', AlbumView.as_view()),
    path('<uuid:id_album>/songs/label/', AlbumView.as_view()),
    path('<uuid:id_album>/add-song/', AlbumView.as_view()),
    path('<uuid:id_album>/delete/', AlbumView.as_view()),
]
