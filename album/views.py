from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

# Create your views here.
# @method_decorator(csrf_exempt, name='dispatch')
class AlbumView(View):
    def __get_album_list_page(self, request: HttpRequest):
        with connection.cursor() as cursor:
            query = 'SELECT album.id, judul, nama, jumlah_lagu, total_durasi FROM album, label WHERE album.id_label = label.id'
            cursor.execute(query)
            
            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            albums = [dict(zip(columns, row)) for row in entries]

        context = {'albums': albums}

        return render(request, 'albumList.html', context=context)
    
    def __get_add_song_page(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'SELECT judul FROM album WHERE album.id = %s'
            cursor.execute(query, [id_album])

            album_name = cursor.fetchone()[0]

            query = 'SELECT id, nama FROM artist, akun WHERE artist.email_akun = akun.email'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = ['id', 'nama']
            artists = [dict(zip(columns, row)) for row in entries]

            query = 'SELECT id, nama FROM songwriter, akun WHERE songwriter.email_akun = akun.email'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = ['id', 'nama']
            songwriters = [dict(zip(columns, row)) for row in entries]

            query = 'SELECT genre.id_konten, genre.genre FROM genre, song WHERE genre.id_konten = song.id_konten'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = ['id_konten', 'genre']
            genres = [dict(zip(columns, row)) for row in entries]

        context = {
            'album_name': album_name,
            'artists': artists,
            'songwriters': songwriters,
            'genres': genres
        }

        return render(request, 'addSongToAlbum.html', context=context)
    
    def __get_album_songs_page(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'SELECT konten.judul, konten.durasi, song.id_konten, song.total_play, song.total_download FROM konten, song, album WHERE song.id_album = album.id AND konten.id = song.id_konten AND album.id = %s'
            cursor.execute(query, [id_album])

            entries = cursor.fetchall()
            columns = ['judul_konten', 'durasi_konten', 'id_konten', 'total_play_song', 'total_download_song']
            songs = [dict(zip(columns, row)) for row in entries]

            query = 'SELECT id, judul FROM album WHERE album.id = %s'
            cursor.execute(query, [id_album])

            row = cursor.fetchone()
            columns = ['id', 'judul']
            album = dict(zip(columns, row))

        context = {'songs': songs, 'album': album}

        return render(request, 'albumSongs.html', context=context)
    
    def __get_add_album_page(self, request: HttpRequest):
        with connection.cursor() as cursor:
            query = 'SELECT id, nama FROM label'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            labels = [dict(zip(columns, row)) for row in entries]

        context = {'labels': labels}

        return render(request, 'addAlbum.html', context=context)
    
    def get(self, request: HttpRequest, id_album = None):
        req_full_path = request.get_full_path()

        if id_album is None:
            if req_full_path.endswith('/album/'):
                return self.__get_album_list_page(request)
            elif req_full_path.endswith('/add-album/'):
                return self.__get_add_album_page(request)
        elif req_full_path.endswith('/add-song/'):
            return self.__get_add_song_page(request, id_album)
        elif req_full_path.endswith('/songs/'):
            return self.__get_album_songs_page(request, id_album)

    def post(self, request: HttpRequest):
        req_body_dict = json.loads(request.body)

        id_album = uuid.uuid4()
        judul = req_body_dict['judul']
        id_label = req_body_dict['id_label']
        
        with connection.cursor() as cursor:
            query = 'INSERT INTO album (id, judul, id_label) VALUES (%s, %s, %s)'
            cursor.execute(query, [id_album, judul, id_label])

        return HttpResponse(status=201)
    
    def delete(self, request: HttpRequest, id_album):
        req_full_path = request.get_full_path()

        with connection.cursor() as cursor:
            query = 'DELETE FROM album WHERE id = %s'
            cursor.execute(query, [id_album])

        return HttpResponse(status=204)
