from django.db import connection
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from marmut_15.utils import login_required
from album.forms import AddAlbumForm, AddSongToAlbumForm
import uuid
from datetime import datetime
from django.utils.decorators import method_decorator

# Create your views here.
@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AlbumView(View):
    def get(self, request: HttpRequest, decoded_token: dict):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/create/'):
            return self.__get_add_album(request, decoded_token)
        elif req_full_path.endswith('/'):
            return self.__get_album_list(request, decoded_token)


    def post(self, request: HttpRequest, decoded_token: dict):
        req_full_path = request.get_full_path()
        
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
            if decoded_token['isArtist']:
                table_name = 'artist'
            elif decoded_token['isSongwriter']:
                table_name = 'songwriter'

            query = f'SELECT album.id, album.judul, label.nama, album.jumlah_lagu, album.total_durasi FROM album \
                    JOIN label ON album.id_label = label.id \
                    JOIN {table_name} ON label.id_pemilik_hak_cipta = {table_name}.id_pemilik_hak_cipta \
                    WHERE {table_name}.email_akun = %s'
            cursor.execute(query, (decoded_token['email'],))

            columns = ['id_album', 'judul_album', 'nama_label', 'jumlah_lagu_album', 'total_durasi_album']
            list_album = [dict(zip(columns, row)) for row in cursor.fetchall()]
            context['list_album'] = list_album

        return render(request, 'albumList.html', context=context)


    def __get_album_list_label(self, request: HttpRequest, decoded_token: dict):
        pass
        

    def __get_add_album(self, request: HttpRequest, decoded_token: dict):
        context = {}

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
                cursor.execute(query, (decoded_token['email'],))

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
                cursor.execute(query, (decoded_token['email'],))

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
        context = {}
        
        with connection.cursor() as cursor:
            data = request.POST.copy()

            if decoded_token['isArtist']:
                query = 'SELECT id, id_pemilik_hak_cipta FROM artist \
                        WHERE email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

                columns = ['id', 'id_pemilik_hak_cipta']
                artist = dict(zip(columns, cursor.fetchone()))

                data['artist'] = artist['id']
                id_pemilik_hak_cipta = artist['id_pemilik_hak_cipta']
            elif decoded_token['isSongwriter']:
                query = 'SELECT id, id_pemilik_hak_cipta FROM songwriter \
                        WHERE email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

                columns = ['id', 'id_pemilik_hak_cipta']
                songwriter = dict(zip(columns, cursor.fetchone()))

                data['songwriter'] = songwriter['id']
                id_pemilik_hak_cipta = songwriter['id_pemilik_hak_cipta']

            form = AddAlbumForm(data)

            if not form.is_valid():
                context['error'] = 'Invalid form input'
                return render(request, 'addAlbum.html', context=context)
            
            cleaned_data = form.cleaned_data

            query = 'UPDATE label SET id_pemilik_hak_cipta = %s WHERE id = %s'
            cursor.execute(query, (id_pemilik_hak_cipta, cleaned_data['label']))

            id_album = uuid.uuid4()
            query = 'INSERT INTO album (id, judul, id_label) \
                    VALUES (%s, %s, %s)'

            try:
                cursor.execute(query, (id_album, cleaned_data['album_title'], cleaned_data['label']))
            except:
                context['error'] = 'Album already exists'
                return render(request, 'addAlbum.html', context=context)

            id_konten = uuid.uuid4()
            now = datetime.now()
            query = 'INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi) \
                    VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (id_konten, cleaned_data['song_title'], now,
                                   now.year, cleaned_data['duration']))
            
            query = 'INSERT INTO song (id_konten, id_artist, id_album) \
                    VALUES (%s, %s, %s)'
            cursor.execute(query, (id_konten, cleaned_data['artist'], id_album))

            query = 'INSERT INTO songwriter_write_song (id_songwriter, id_song) \
                    VALUES (%s, %s)'
            for id_songwriter in cleaned_data['songwriter']:
                cursor.execute(query, (id_songwriter, id_konten))

            query = 'INSERT INTO genre (id_konten, genre) \
                    VALUES (%s, %s)'
            for genre in cleaned_data['genre']:
                cursor.execute(query, (id_konten, genre))

        return redirect(reverse('album:list'))


@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class AlbumDetailView(View):
    def get(self, request: HttpRequest, id_album: str, decoded_token: dict):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/songs/'):
            return self.__get_songs(request, id_album)
        elif req_full_path.endswith('/add-song/'):
            return self.__get_add_song(request, id_album, decoded_token)
        elif req_full_path.endswith('/delete/'):
            return self.__get_delete_album(request, id_album)
        

    def post(self, request: HttpRequest, id_album: str, decoded_token: dict):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/add-song/'):
            return self.__post_add_song(request, id_album, decoded_token)
        

    def __get_songs(self, request: HttpRequest, id_album: str):
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


    def __get_add_song(self, request: HttpRequest, id_album: str, decoded_token: dict):
        context = {}

        with connection.cursor() as cursor:
            query = 'SELECT judul FROM album WHERE album.id = %s'
            cursor.execute(query, (id_album,))

            columns = ['judul']
            album = dict(zip(columns, cursor.fetchone()))
            context['album'] = album

            if decoded_token['isArtist']:
                query = 'SELECT id, nama FROM artist \
                        JOIN akun ON artist.email_akun = akun.email \
                        WHERE artist.email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

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
                cursor.execute(query, (decoded_token['email'],))

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

        return render(request, 'addSongToAlbum.html', context=context)
    

    def __get_delete_album(self, request: HttpRequest, id_album: str):
        with connection.cursor() as cursor:
            query = 'DELETE FROM album WHERE id = %s'
            cursor.execute(query, (id_album,))

            query = 'DELETE FROM song WHERE id_album = %s'
            cursor.execute(query, (id_album,))

        return redirect(reverse('album:list'))
    

    def __post_add_song(self, request: HttpRequest, id_album: str, decoded_token: dict):
        context = {}

        with connection.cursor() as cursor:
            data = request.POST.copy()

            if decoded_token['isArtist']:
                query = 'SELECT id, id_pemilik_hak_cipta FROM artist \
                        WHERE email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

                columns = ['id', 'id_pemilik_hak_cipta']
                artist = dict(zip(columns, cursor.fetchone()))

                data['artist'] = artist['id']
                id_pemilik_hak_cipta = artist['id_pemilik_hak_cipta']
            elif decoded_token['isSongwriter']:
                query = 'SELECT id, id_pemilik_hak_cipta FROM songwriter \
                        WHERE email_akun = %s'
                cursor.execute(query, (decoded_token['email'],))

                columns = ['id', 'id_pemilik_hak_cipta']
                songwriter = dict(zip(columns, cursor.fetchone()))

                data['songwriter'] = songwriter['id']
                id_pemilik_hak_cipta = songwriter['id_pemilik_hak_cipta']

            form = AddSongToAlbumForm(data)

            if not form.is_valid():
                context['error'] = 'Invalid form input'
                return render(request, 'addSongToAlbum.html', context=context)
            
            cleaned_data = form.cleaned_data

            id_konten = uuid.uuid4()
            now = datetime.now()
            query = 'INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi) \
                    VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (id_konten, cleaned_data['song_title'], now,
                                   now.year, cleaned_data['duration']))
            
            query = 'INSERT INTO song (id_konten, id_artist, id_album) \
                    VALUES (%s, %s, %s)'
            cursor.execute(query, (id_konten, cleaned_data['artist'], id_album))

            query = 'INSERT INTO songwriter_write_song (id_songwriter, id_song) \
                    VALUES (%s, %s)'
            for id_songwriter in cleaned_data['songwriter']:
                cursor.execute(query, (id_songwriter, id_konten))

            query = 'INSERT INTO genre (id_konten, genre) \
                    VALUES (%s, %s)'
            for genre in cleaned_data['genre']:
                cursor.execute(query, (id_konten, genre))

        return redirect(reverse('album:songs', args=(id_album,)))
