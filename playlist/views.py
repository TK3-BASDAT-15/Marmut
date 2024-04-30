from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url= "/login")

# CRUD Kelola Playlist
def user_playlist(request):
    pass

def add_playlist(request):
    pass

def user_playlist_detail(request, id_playlist):
    pass

def user_playlist_edit(request, id_playlist):
    pass

def user_playlist_delete(request, id_playlist):
    pass

def user_playlist_shuffle(request, id_playlist):
    pass

def user_song(request,id_song):
    pass

def user_play_song(request, id_song):
    pass

def user_delete_song(request,id_song):
    pass

def user_add_song(request, id_song):
    pass

#R Play User Playlist
def play_user_playlist(request, id):
    pass

#R play song
def user_song_detail(request, id_song):
    pass

def user_download(request, id_user):
    pass

def add_song_spesific_playlist(request, id):
    pass

def list_download(request, id_user):
    pass











