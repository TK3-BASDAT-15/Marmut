from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('song/<uuid:id_song>/royalti/', RoyaltiView.as_view())
]
