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
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)

    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO user_playlist (email_pembuat, judul, deskripsi) VALUES (%s, %s, %s)", ['email', judul, deskripsi])


        return redirect('playlist:user_playlist')

    return render(request, 'addplaylist.html')

def user_playlist_detail(request, id_user_playlist):
    try:
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except:
        return redirect(reverse('main:login'))

    email = decoded_token['email']
    print(email)

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_playlist WHERE id_user_playlist = %s", [id_user_playlist])
        row = cursor.fetchone() 
        columns = [col[0] for col in cursor.description] 
        playlist = dict(zip(columns, row)) 

    return render(request, 'userPlaylistDetail.html', {'playlist': playlist})


def user_playlist_edit(request, id_user_playlist):
    if request.method == 'POST':
        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE marmut.user_playlist SET judul = %s, deskripsi = %s WHERE id_user_playlist = %s",
                [judul, deskripsi, id_user_playlist]
            )

        return redirect('hijau:playlist')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM marmut.user_playlist WHERE id_user_playlist = %s", [id_user_playlist])
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]  
        playlist = dict(zip(columns, row)) 

    return render(request, 'updatePlaylist.html', {'playlist': playlist})

def user_playlist_delete(request, id_user_playlist): 
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM user_playlist WHERE id_user_playlist = %s", [id_user_playlist])
    return redirect('playlist:user_playlist') 




def user_playlist_shuffle(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request, 'userPlaylistDetail.html') 

def user_song(request,id_song):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request, 'userPlaylistDetail.html')

def user_play_song(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request,'songDetail.html')

def user_delete_song(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request, 'userPlaylistDetail.html')


def user_add_song(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request, 'addSong.html')


#R Play User Playlist
def play_user_playlist(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request, 'userPlaylistDetail.html')

#R play song
def user_song_detail(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request, 'songDetail.html')

def user_download(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return redirect('songDetail.html')

def add_song_spesific_playlist(request):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return  render(request, 'addSongToPlaylist.html' )

def list_download(request, id_user):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    pass











