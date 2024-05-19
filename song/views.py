from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import uuid

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class SongView(View):
    def get(self, request: HttpRequest, id_song):
        with connection.cursor() as cursor:
            query = 'SELECT judul, durasi, total_play, total_download FROM konten, song WHERE konten.id = song.id_konten AND song.id_konten = %s'
            cursor.execute(query, [id_song])

            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        retval = [dict(zip(columns, row)) for row in entries]

        return JsonResponse(retval, safe=False)
    
    def post(self, request: HttpRequest):
        req_body_dict = json.loads(request.body)

        id_album = req_body_dict['id_album']
        judul = req_body_dict['judul']
        id_artist = req_body_dict['id_artist']
        id_songwriter = req_body_dict['id_songwriter']
        genres = req_body_dict['genre']
        durasi = req_body_dict['durasi']

        id_konten = uuid.uuid4()

        now = datetime.datetime.now()
        tanggal_rilis = now.strftime('%Y-%m-%d %H:%M:%S')
        tahun = now.strftime('%Y')

        with connection.cursor() as cursor:
            query = 'INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, [id_konten, judul, tanggal_rilis, tahun, durasi])

            query = 'INSERT INTO song (id_konten, id_artist, id_album) VALUES (%s, %s, %s)'
            cursor.execute(query, [id_konten, id_artist, id_album])

            query = 'INSERT INTO songwriter (id_songwriter, id_song) VALUES (%s, %s)'
            cursor.execute(query, [id_songwriter, id_konten])

            genre_entries = ''
            for genre in genres:
                genre_entries += f'(\'{id_konten}\', \'{genre}\'),'
            genre_entries = genre_entries[:-1]
            query = 'INSERT INTO genre (id_song, genre) VALUES (%s)'
            cursor.execute(query, [id_konten, genre_entries])

            query = 'UPDATE album SET jumlah_lagu = jumlah_lagu + 1 WHERE id = %s'
            cursor.execute(query, [id_album])

            query = 'UPDATE album SET total_durasi = total_durasi + %s WHERE id = %s'
            cursor.execute(query, [durasi, id_album])

        return HttpResponse(status=201)
    
    def delete(self, request: HttpRequest, id_song):
        with connection.cursor() as cursor:
            query = 'DELETE FROM lagu WHERE id = %s'
            cursor.execute(query, [id_song])

        return HttpResponse(status=204)
