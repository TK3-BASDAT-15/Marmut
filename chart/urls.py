from django.urls import path
from . import views

app_name = 'chart'

urlpatterns = [
    path('', views.chart_list, name='chart_list'),
    path('top_20/<str:type_of_top_20>', views.top_20, name='top_20'),
]
