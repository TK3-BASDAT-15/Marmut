from django.urls import path, re_path

from .views import *

urlpatterns = [
    re_path(r'^(?P<id_song>.+)?/?$', SongView.as_view())
]
