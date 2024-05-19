from django.urls import path

from .views import *

app_name = 'royalti'

urlpatterns = [
    path('', RoyaltiView.as_view(), name='royalti')
]
