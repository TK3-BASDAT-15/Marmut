from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class AlbumView(View):
    def get(self, request: HttpRequest):
        with connection.cursor() as cursor:
            query = 'SELECT judul, nama, jumlah_lagu, total_durasi FROM album, label WHERE album.id_label = label.id'
            cursor.execute(query)
            entries = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        retval = [dict(zip(columns, row)) for row in entries]

        return JsonResponse(retval, safe=False)

    def post(self, request: HttpRequest):
        req_body_dict = json.loads(request.body)

        id_album = uuid.uuid4()
        judul = req_body_dict['judul']
        id_label = req_body_dict['id_label']
        
        with connection.cursor() as cursor:
            query = f'INSERT INTO album (id, judul, id_label) VALUES (\'{id_album}\', \'{judul}\', \'{id_label}\')'
            cursor.execute(query)

        return HttpResponse(status=201)
    
    def delete(self, request: HttpRequest, id_album):
        with connection.cursor() as cursor:
            query = f'DELETE FROM album WHERE id = \'{id_album}\''
            cursor.execute(query)

        return HttpResponse(status=204)
