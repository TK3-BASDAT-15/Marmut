from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# Create your views here.

#@login_required(login_url= "/login")

# CRUD Kelola Playlist
def user_playlist(request):
    return render(request, 'userPlaylist.html')

def add_playlist(request):
        return render(request, 'addPlaylist.html')

def user_playlist_detail(request): 
    return render(request, 'userPlaylistDetail.html')

def user_playlist_edit(request): 
    return render(request,'updatePlaylist.html')

def user_playlist_delete(request): 
    return redirect('playlist:user_playlist') 

def user_playlist_shuffle(request):
    return render(request, 'userPlaylistDetail.html') 

def user_song(request,id_song):
    return render(request, 'userPlaylistDetail.html')

def user_play_song(request):
    return render(request,'songDetail.html')

def user_delete_song(request):
    return render(request, 'userPlaylistDetail.html')


def user_add_song(request):
    return render(request, 'addSong.html')


#R Play User Playlist
def play_user_playlist(request):
    return render(request, 'userPlaylistDetail.html')

#R play song
def user_song_detail(request):
    return render(request, 'songDetail.html')

def user_download(request):
    return redirect('songDetail.html')

def add_song_spesific_playlist(request):
    return  render(request, 'addSongToPlaylist.html' )

def list_download(request, id_user):
    pass











