from django.urls import path

from . import views

urlpatterns = [
    path("playpodcast/", views.play_podcast, name="index"),
    path("see_chart/", views.see_chart, name="index"),
    path("chart_detail/", views.chart_detail, name="index"),
    path("podcast_list/", views.list_podcast, name="index"),
    path("create_episode/", views.create_episde, name="index"),
]