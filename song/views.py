from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import uuid
from marmut_15.utils import login_required

# Create your views here.
@method_decorator(login_required, name='get')
class SongView(View):
    def get(self, request: HttpRequest, id_album, id_song):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/delete/'):
            return self.__get_delete_song(request, id_album, id_song)
        elif req_full_path.endswith('/'):
            return self.__get_song(request, id_song)


    def __get_song(self, request: HttpRequest, id_song):
        with connection.cursor() as cursor:
            query = 'SELECT judul, durasi, total_play, total_download FROM konten, song WHERE konten.id = song.id_konten AND song.id_konten = %s'
            cursor.execute(query, [id_song])

            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        retval = [dict(zip(columns, row)) for row in entries]

        return JsonResponse(retval, safe=False)


    def __get_delete_song(self, request: HttpRequest, id_album, id_song):
        with connection.cursor() as cursor:
            query = 'DELETE FROM songwriter_write_song WHERE id_song = %s'
            cursor.execute(query, (id_song,))

            query = 'DELETE FROM song WHERE id_konten = %s'
            cursor.execute(query, (id_song,))

            query = 'DELETE FROM genre WHERE id_konten = %s'
            cursor.execute(query, (id_song,))

            query = 'DELETE FROM konten WHERE id = %s'
            cursor.execute(query, (id_song,))

        return redirect(reverse('album:details', args=(id_album,)))
