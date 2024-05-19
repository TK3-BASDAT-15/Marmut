from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('akun/<str:email_akun>/royalti/', RoyaltiView.as_view())
]
