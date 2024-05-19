from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from marmut_15.utils import decode_session_token, extract_session_token
from album.forms import AddAlbumForm
import uuid

# Create your views here.
class AlbumView(View):
    def get(self, request: HttpRequest):
        req_full_path = request.get_full_path()
        
        try:
            session_token = extract_session_token(request)
            decoded_token = decode_session_token(session_token)
        except:
            return redirect(reverse('main:login'))

        if req_full_path.endswith('/create/'):
            return self.__get_add_album(request, decoded_token)
        elif req_full_path.endswith('/'):
            return self.__get_album_list(request, decoded_token)

  
    def post(self, request: HttpRequest):
        req_full_path = request.get_full_path()

        try:
            session_token = extract_session_token(request)
            decoded_token = decode_session_token(session_token)
        except:
            return redirect(reverse('main:login'))

        if req_full_path.endswith('/create/'):
            return self.__post_add_album(request, decoded_token)
        

    def __get_album_list(self, request: HttpRequest, decoded_token: dict):
        is_label = decoded_token['isLabel']

        if is_label:
            return self.__get_album_list_label(request, decoded_token)
        else:
            return self.__get_album_list_user(request, decoded_token)


    def __get_album_list_user(self, request: HttpRequest, decoded_token: dict):
        context = {}

        with connection.cursor() as cursor:
            query = 'SELECT album.judul, label.nama, album.jumlah_lagu, album.total_durasi FROM album \
                    JOIN label ON album.id_label = label.id'
            cursor.execute(query)

            columns = ['judul_album', 'nama_label', 'jumlah_lagu_album', 'total_durasi_album']
            list_album = [dict(zip(columns, row)) for row in cursor.fetchall()]
            context['list_album'] = list_album

        return render(request, 'albumList.html', context=context)


    def __get_album_list_label(self, request: HttpRequest, decoded_token: dict):
        pass
        

    def __get_add_album(self, request: HttpRequest, decoded_token: dict):
        context = {}
        email = decoded_token['email']

        with connection.cursor() as cursor:
            query = 'SELECT id, nama FROM label'
            cursor.execute(query)

            columns = ['id', 'nama']
            labels = [dict(zip(columns, row)) for row in cursor.fetchall()]
            context['labels'] = labels

            if decoded_token['isArtist']:
                query = 'SELECT id, nama FROM artist \
                        JOIN akun ON artist.email_akun = akun.email \
                        WHERE artist.email_akun = %s'
                cursor.execute(query, (email,))

                columns = ['id', 'nama']
                artist = dict(zip(columns, cursor.fetchone()))
                context['artist'] = artist

                query = 'SELECT songwriter.id, akun.nama FROM songwriter \
                        JOIN akun ON songwriter.email_akun = akun.email'
                cursor.execute(query)

                columns = ['id', 'nama']
                songwriters = [dict(zip(columns, row)) for row in cursor.fetchall()]
                context['songwriters'] = songwriters
            elif decoded_token['isSongwriter']:
                query = 'SELECT id, nama FROM artist \
                    JOIN akun ON artist.email_akun = akun.email'
                cursor.execute(query)

                columns = ['id', 'nama']
                artists = [dict(zip(columns, row)) for row in cursor.fetchall()]
                context['artists'] = artists

                query = 'SELECT id, nama FROM songwriter \
                        JOIN akun ON songwriter.email_akun = akun.email \
                        WHERE songwriter.email_akun = %s'
                cursor.execute(query, (email,))

                columns = ['id', 'nama']
                songwriter = dict(zip(columns, cursor.fetchone()))
                context['songwriter'] = songwriter
            else:
                raise 'Invalid user type'

            query = 'SELECT DISTINCT genre FROM genre'
            cursor.execute(query)

            columns = ['genre']
            genres = [dict(zip(columns, row)) for row in cursor.fetchall()]
            context['genres'] = genres

        return render(request, 'addAlbum.html', context=context)
        

    def __post_add_album(self, request: HttpRequest, decoded_token: dict):
        try:
            session_token = extract_session_token(request)
            decoded_token = decode_session_token(session_token)
        except:
            return redirect(reverse('main:login'))
        
        with connection.cursor() as cursor:
            data = request.POST.copy()
            context = {}

            if decoded_token['isArtist']:
                query = 'SELECT id FROM artist \
                        WHERE email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

                try:
                    artist_id = cursor.fetchone()[0]
                except:
                    return redirect(reverse('main:login'))
                
                data['artist'] = artist_id
            elif decoded_token['songwriter']:
                query = 'SELECT id FROM songwriter \
                        WHERE email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

                try:
                    songwriter_id = cursor.fetchone()[0]
                except:
                    return redirect(reverse('main:login'))
                
                data['songwriter'] = songwriter_id

            form = AddAlbumForm(data)

            if not form.is_valid():
                context['error'] = 'Invalid form input'
                return render(request, 'addAlbum.html', context=context)

            query = 'INSERT INTO album (id, judul, id_label) \
                    VALUES (%s, %s, %s)'

            try:
                cursor.execute(query, (uuid.uuid4(), form.cleaned_data['album_title'],
                                       form.cleaned_data['label']))
            except:
                context['error'] = 'Album already exists'
                return render(request, 'addAlbum.html', context=context)
        
        return redirect(reverse('album:album'))


    
class AlbumDetailView(View):
    def get(self, request: HttpRequest, id_album):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/songs/'):
            return self.__get_songs(request, id_album)
        elif req_full_path.endswith('/add-song/'):
            return self.__get_add_song(request, id_album)
        elif req_full_path.endswith('/delete/'):
            return self.__get_delete_album(request, id_album)
    

    def delete(self, request: HttpRequest, id_album):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/delete/'):
            return self.__delete_album(request, id_album)
        

    def __get_songs(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'SELECT konten.judul, konten.durasi, song.id_konten, song.total_play, song.total_download \
                    FROM konten \
                    JOIN song ON konten.id = song.id_konten \
                    JOIN album ON song.id_album = album.id \
                    WHERE album.id = %s'
            cursor.execute(query, (id_album,))

            columns = ['judul_konten', 'durasi_konten', 'id_konten', 'total_play_song', 'total_download_song']
            songs = [dict(zip(columns, row)) for row in cursor.fetchall()]

            query = 'SELECT id, judul FROM album WHERE album.id = %s'
            cursor.execute(query, (id_album,))

            columns = ['id', 'judul']
            album = dict(zip(columns, cursor.fetchone()))

        context = {'songs': songs, 'album': album}

        return render(request, 'albumSongs.html', context=context)
    

    def __get_add_song(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'SELECT judul FROM album WHERE album.id = %s'
            cursor.execute(query, (id_album,))

            album_name = cursor.fetchone()[0]

            query = 'SELECT id, nama FROM artist JOIN akun ON artist.email_akun = akun.email'
            cursor.execute(query)

            columns = ['id', 'nama']
            artists = [dict(zip(columns, row)) for row in cursor.fetchall()]

            query = 'SELECT id, nama FROM songwriter JOIN akun ON songwriter.email_akun = akun.email'
            cursor.execute(query)

            columns = ['id', 'nama']
            songwriters = [dict(zip(columns, row)) for row in cursor.fetchall()]

            query = 'SELECT genre.id_konten, genre.genre FROM genre JOIN song ON genre.id_konten = song.id_konten'
            cursor.execute(query)

            columns = ['id_konten', 'genre']
            genres = [dict(zip(columns, row)) for row in cursor.fetchall()]

        context = {
            'album_name': album_name,
            'artists': artists,
            'songwriters': songwriters,
            'genres': genres
        }

        return render(request, 'addSongToAlbum.html', context=context)
    

    def __get_delete_album(self, request: HttpRequest, id_album):
        pass
    

    def __delete_album(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'DELETE FROM album WHERE id = %s'
            cursor.execute(query, (id_album,))

        return HttpResponse(status=204)
