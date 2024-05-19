import datetime
import uuid
from django.db import connection
from django.shortcuts import redirect, render
from django.urls import reverse
from marmut_15.utils import decode_session_token, extract_session_token
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect



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
            'total_durasi': format_to_hour_minute(row[3]),
            } for row in entries],
        }

    return render(request, 'userPlaylist.html', context)


@csrf_exempt
def add_playlist(request):
    try:
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except:
        return redirect(reverse('main:login'))

    email = decoded_token['email']
    print(email)

    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        id = uuid.uuid4()
        id_playlist = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO playlist (id) VALUES (%s)", [str(id)])
            cursor.execute("INSERT INTO user_playlist (email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, %s, %s)", [email, id_playlist, judul, deskripsi, 0, id, 0])

        return redirect('playlist:user_playlist')

    return render(request, 'addplaylist.html')

@csrf_exempt
def user_playlist_detail(request, id_user_playlist):
    try:
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except:
        return redirect(reverse('main:login'))

    email = decoded_token['email']

    message = None
    with connection.cursor() as cursor:
        # Ambil data playlist
        cursor.execute("SELECT * FROM marmut.user_playlist WHERE id_user_playlist = %s", [id_user_playlist])
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        playlist = dict(zip(columns, row))

        # Ambil nama pembuat playlist
        cursor.execute("SELECT nama FROM akun WHERE email = %s", [playlist['email_pembuat']])
        nama_pembuat = cursor.fetchone()[0]
        playlist['nama_pembuat'] = nama_pembuat
        playlist['id_playlist'] = str(playlist['id_playlist'])
        playlist['total_durasi'] = format_to_hour_minute(int(playlist['total_durasi']))

        # Ambil lagu yang terkait dengan playlist menggunakan query langsung
        cursor.execute("""
            SELECT k.judul, a.nama as artist, k.durasi, ps.id_song as id, a.email
            FROM playlist_song ps
             JOIN song s ON ps.id_song = s.id_konten
             JOIN konten k ON s.id_konten = k.id
             JOIN artist ar ON s.id_artist = ar.id
             JOIN akun a ON ar.email_akun = a.email
            WHERE ps.id_playlist = %s
        """, [playlist['id_playlist']])

        # Ambil hasil query sebagai kamus
        songs_query = cursor.fetchall()
        songs = []
        for song_row in songs_query :
            song_dict = {
                'judul_lagu': song_row[0],
                'artis': song_row[1],
                'durasi': format_to_minute_second(song_row[2]),
                'id': str(song_row[3])
            }
            songs.append(song_dict)

    if request.method == "POST":
        now = datetime.datetime.now()
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO marmut.akun_play_user_playlist (email_pemain,id_user_playlist,email_pembuat,waktu) VALUES
                        (%s,%s,%s,%s);
                """, [email, id_user_playlist, playlist['email_pembuat'] , now])

                for song_item in songs_query:
                    cursor.execute("""
                        INSERT INTO marmut.akun_play_song (email_pemain,id_song,waktu) VALUES
                        (%s,%s,%s);
                    """, [email, song_item[3], now])

                message = "Berhasil shuffle playlist"
            except Exception as e:
                connection.rollback()
                message = str(e)
    if request.session.get('message') is not None:
        message = request.session['message']
        request.session['message'] = None
    return render(request, 'userPlaylistDetail.html', {'playlist': playlist, 'songs': songs, 'message' : message, 'email': email, 'id_user_playlist': id_user_playlist})


@csrf_exempt
def user_playlist_edit(request, id_user_playlist):
    try:
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except:
        return redirect(reverse('main:login'))

    email = decoded_token['email']
    print(email)

    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        try: 
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE marmut.user_playlist SET judul = %s, deskripsi = %s WHERE id_user_playlist = %s",
                    [judul, deskripsi, id_user_playlist]
                )

        except Exception as e:
            connection.rollback()
            print(str(e))

        return redirect('playlist:user_playlist')

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

def user_play_song(request, id_song):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    return render(request,'songDetail.html')

def user_delete_song(request, id_song, id_playlist, id_user_playlist):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)

    with connection.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM playlist_song WHERE id_song = %s AND id_playlist = %s", [id_song, id_playlist])
            request.session['message'] = "Lagu berhasil dihapus"
            return redirect('playlist:user_playlist_detail', id_user_playlist=id_user_playlist ) 
        except Exception as e:
            request.session['message'] = str(e)
            return redirect('playlist:user_playlist_detail', id_user_playlist=id_user_playlist) 

@csrf_exempt
def user_add_song(request, id_playlist, id_user_playlist):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    message = None
    if request.method == "POST":
        id_song = request.POST.get('dropdownLagu') 
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO marmut.playlist_song (id_playlist,id_song) VALUES
                        (%s,%s);
                """, [id_playlist, id_song])
                return redirect('playlist:user_playlist_detail', id_user_playlist= id_user_playlist)
            except Exception as e:
                connection.rollback()
                message = str(e)


    with connection.cursor() as cursor:

        # Ambil lagu yang terkait dengan playlist menggunakan query langsung
        try:
            cursor.execute("""
                SELECT k.judul, a.nama as artist, s.id_konten
                FROM marmut.song s
                FULL OUTER JOIN marmut.konten k ON s.id_konten = k.id
                FULL OUTER JOIN marmut.artist ar ON s.id_artist = ar.id
                FULL OUTER JOIN marmut.akun a ON ar.email_akun = a.email;
            """)
            songs = cursor.fetchall()

            cursor.execute("SELECT judul, id_playlist FROM marmut.user_playlist WHERE id_playlist = %s", [id_playlist])
            playlist = cursor.fetchone()
            context = {
                'songs': songs,
                'playlist': playlist,
                'id_user_playlist': id_user_playlist,
                'message': message
            }


        except Exception as e:
            connection.rollback()
            print(str(e))

    return render(request, 'addSong.html', context)


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
@csrf_exempt
def user_song_detail(request, id, id_playlist):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
    
    email = decoded_token['email']

    if request.method == "POST":
            now = datetime.datetime.now()
            with connection.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO marmut.akun_play_song (email_pemain,id_song,waktu) VALUES
                        (%s,%s,%s);
                    """, [email, id, now])
                    return redirect(reverse('playlist:user_song_detail'))
                except Exception as e:
                    connection.rollback()
                    print(str(e))
    
    with connection.cursor() as cursor:

        # Ambil lagu yang terkait dengan playlist menggunakan query langsung
        try:
            cursor.execute("""
                SELECT email FROM marmut.premium WHERE email = %s;
            """, [email])

            is_premium = True
            if cursor.fetchone() == None:
                is_premium = False

            print(is_premium)

            cursor.execute("""
                SELECT k.judul, a.nama as artist, k.durasi, a.nama, string_agg(g.genre, ', '), s.total_play, s.total_download, k.tanggal_rilis, k.tahun, al.judul, s.id_konten
                FROM marmut.song s
                FULL OUTER JOIN marmut.konten k ON s.id_konten = k.id
                FULL OUTER JOIN marmut.genre g ON s.id_konten = g.id_konten
                FULL OUTER JOIN marmut.artist ar ON s.id_artist = ar.id
                FULL OUTER JOIN marmut.album al on al.id = s.id_album 
                FULL OUTER JOIN marmut.akun a ON ar.email_akun = a.email
                WHERE s.id_konten = %s
                GROUP  BY 1, 2,3,4,6,7,8,9,10,11;
            """, [id])

            song_row = cursor.fetchone()
            print(song_row)
            context = {
                'judul_lagu': str(song_row[0]),
                'artis': str(song_row[1]),
                'durasi': format_to_minute_second(song_row[2]),
                'nama': str(song_row[3]),
                'genre': str(song_row[4]).split(", "),
                'total_play': str(song_row[5]),
                'total_download': str(song_row[6]),
                'tanggal_rilis': str(song_row[7]),
                'tahun': str(song_row[8]),
                'album': str(song_row[9]),
                'id_song': str(song_row[10]),
                'id_playlist' : id_playlist,
                'is_premium' : is_premium
            }

            cursor.execute("""
            SELECT  string_agg(a.nama,', ') as songwriter
            FROM song s 
            FULL OUTER JOIN songwriter_write_song sws ON sws.id_song = s.id_konten
            FULL OUTER JOIN songwriter sw ON sw.id = sws.id_songwriter
            FULL OUTER JOIN akun a ON sw.email_akun = a.email
            WHERE s.id_konten = %s
            """, [id])
            song_writer = cursor.fetchone()
            context['song_writer'] = song_writer[0]
            
        except Exception as e:
            connection.rollback()
            print(str(e))
        
    return render(request, 'songDetail.html', context)


def user_download(request, id_song):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
    email = decoded_token['email']

    context = {
        "message": "Berhasil mengunduh lagu"
    }

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                INSERT INTO marmut.downloaded_song (id_song,email_downloader) VALUES
                    (%s,%s);
            """, [id_song, email])
        except Exception as e:
            connection.rollback()
            context['message'] = str(e)

    return render(request, 'downloadSong.html', context )

@csrf_exempt
def add_song_spesific_playlist(request, id_song):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    message_success = None
    message_failed = None
    if request.method == "POST":
        id_playlist = request.POST.get('dropdownPlaylist') 
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO marmut.playlist_song (id_playlist,id_song) VALUES
                        (%s,%s);
                """, [id_playlist, id_song])
                message_success = "Berhasil menambahkan lagu"
            except Exception as e:
                connection.rollback()
                message_failed = str(e)


    with connection.cursor() as cursor:

        # Ambil lagu yang terkait dengan playlist menggunakan query langsung
        try:
            cursor.execute("""
                SELECT k.judul, a.nama as artist
                FROM marmut.song s
                FULL OUTER JOIN marmut.konten k ON s.id_konten = k.id
                FULL OUTER JOIN marmut.artist ar ON s.id_artist = ar.id
                FULL OUTER JOIN marmut.akun a ON ar.email_akun = a.email
                WHERE s.id_konten = %s;
            """, [id_song])
            song_row = cursor.fetchone()
            print(song_row)

            cursor.execute("SELECT judul, id_playlist FROM marmut.user_playlist WHERE email_pembuat = %s", [email])
            playlist_row = cursor.fetchall()
            context = {
                'judul_lagu': str(song_row[0]),
                'artis': str(song_row[1]),
                'playlist': playlist_row,
                'message_success': message_success,
                'message_failed': message_failed
            }


        except Exception as e:
            connection.rollback()
            print(str(e))

    print(email)
    return  render(request, 'addSongToPlaylist.html', context )

def list_download(request, id_user):
    try :
        session_token = extract_session_token(request)
        decoded_token = decode_session_token(session_token)
    except :
        return redirect(reverse('main:login'))
        
    email = decoded_token['email']
    print(email)
    pass

def format_to_minute_second(seconds):
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)
    return "{} menit {} detik".format(minutes, seconds)

def format_to_hour_minute(seconds):
    hour = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    return "{} jam {} menit".format(hour, minutes)












