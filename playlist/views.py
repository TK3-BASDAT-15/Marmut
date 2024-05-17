from django.db import connection
from django.shortcuts import redirect, render
from django.urls import reverse
from marmut_15.utils import decode_session_token, extract_session_token
from django.http import HttpRequest


# CRUD Kelola Playlist
#@login_required(login_url= "/login")
def user_playlist(request: HttpRequest):
    try:
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except:
        return redirect(reverse('main:login'))

    email = decoded_token['email']
    print(email)

    with connection.cursor() as cursor:
        query = f"select id_user_playlist, jumlah_lagu, judul, total_durasi FROM user_playlist WHERE email_pembuat = '{email}';"
        cursor.execute(query)
        
        entries = cursor.fetchall()
        print(entries)

        context = {
        'data_playlist': [{
            'id_user_playlist': row[0],
            'jumlah_lagu': row[1],
            'judul': row[2],
            'total_durasi': row[3],
            } for row in entries],
        }

    return render(request, 'userPlaylist.html', context)

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











