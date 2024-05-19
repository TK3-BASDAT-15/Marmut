from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('<uuid:id_song>/', SongView.as_view())
]
