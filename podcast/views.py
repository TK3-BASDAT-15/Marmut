from django.shortcuts import render
from django.http import HttpResponse

def play_podcast(request):
    return render(request, 'playpodcast.html')

def see_chart(request):
    return render(request, 'melihatchart.html')

def chart_detail(request):
    return render(request, 'chartdetail.html')

def list_podcast(request):
    return render(request, 'podcastlist.html')

def create_episde(request):
    return render(request, 'createepisode.html')