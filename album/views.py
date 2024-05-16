from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
import json
import uuid

# Create your views here.
class AlbumView(View):
    def __get_album_list(self, request: HttpRequest):
        with connection.cursor() as cursor:
            query = 'SELECT album.id, judul, nama, jumlah_lagu, total_durasi FROM album, label WHERE album.id_label = label.id'
            cursor.execute(query)
            
            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            albums = [dict(zip(columns, row)) for row in entries]

        context = {'albums': albums}

        return render(request, 'albumList.html', context=context)
    
    def __get_add_album(self, request: HttpRequest):
        with connection.cursor() as cursor:
            query = 'SELECT id, nama FROM label'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            labels = [dict(zip(columns, row)) for row in entries]

        context = {'labels': labels}

        return render(request, 'addAlbum.html', context=context)
    
    def __post_add_album(self, request: HttpRequest):
        req_body_dict = json.loads(request.body)

        id_album = uuid.uuid4()
        judul = req_body_dict['judul']
        id_label = req_body_dict['id_label']
        
        with connection.cursor() as cursor:
            query = 'INSERT INTO album (id, judul, id_label) VALUES (%s, %s, %s)'
            cursor.execute(query, [id_album, judul, id_label])

        return HttpResponse(status=201)
    
    def get(self, request: HttpRequest):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/create/'):
            return self.__get_add_album(request)
        elif req_full_path.endswith('/'):
            return self.__get_album_list(request)
        
    def post(self, request: HttpRequest):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/create/'):
            return self.__post_add_album(request)
    
class SingleAlbumView(View):
    def __get_songs(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'SELECT konten.judul, konten.durasi, song.id_konten, song.total_play, song.total_download FROM konten JOIN song ON konten.id = song.id_konten JOIN album ON song.id_album = album.id WHERE album.id = %s'
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
    
    def __get_add_song(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'SELECT judul FROM album WHERE album.id = %s'
            cursor.execute(query, [id_album])

            album_name = cursor.fetchone()[0]

            query = 'SELECT id, nama FROM artist JOIN akun ON artist.email_akun = akun.email'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = ['id', 'nama']
            artists = [dict(zip(columns, row)) for row in entries]

            query = 'SELECT id, nama FROM songwriter JOIN akun ON songwriter.email_akun = akun.email'
            cursor.execute(query)

            entries = cursor.fetchall()
            columns = ['id', 'nama']
            songwriters = [dict(zip(columns, row)) for row in entries]

            query = 'SELECT genre.id_konten, genre.genre FROM genre JOIN song ON genre.id_konten = song.id_konten'
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
    
    def __get_delete_album(self, request: HttpRequest, id_album):
        pass
    
    def __delete_album(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = 'DELETE FROM album WHERE id = %s'
            cursor.execute(query, [id_album])

        return HttpResponse(status=204)

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
