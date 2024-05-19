from django.db import connection
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from marmut_15.utils import login_required

# Create your views here.
@method_decorator(login_required, name='get')
class RoyaltiView(View):
    def get(self, request: HttpRequest, decoded_token: dict):
        context = {}

        with connection.cursor() as cursor:
            if decoded_token['isLabel']:
                table_name = 'label'
                column_name = 'email'
            else:
                if decoded_token['isArtist']:
                    table_name = 'artist'
                elif decoded_token['isSongwriter']:
                    table_name = 'songwriter'
                column_name = 'email_akun'

            query = f'SELECT konten.judul, album.judul, song.total_play, song.total_download, royalti.jumlah, pemilik_hak_cipta.rate_royalti, pemilik_hak_cipta.id, konten.id \
                    FROM royalti \
                    JOIN song ON royalti.id_song = song.id_konten \
                    JOIN konten ON song.id_konten = konten.id \
                    JOIN album ON song.id_album = album.id \
                    JOIN {table_name} ON royalti.id_pemilik_hak_cipta = {table_name}.id_pemilik_hak_cipta \
                    JOIN pemilik_hak_cipta ON {table_name}.id_pemilik_hak_cipta = pemilik_hak_cipta.id \
                    WHERE {table_name}.{column_name} = %s'
            cursor.execute(query, (decoded_token['email'],))

            columns = ['judul_konten', 'judul_album', 'total_play_song', 'total_download_song', 'jumlah_royalti', 'rate_royalti_pemilik_hak_cipta', 'id_pemilik_hak_cipta', 'id_konten']
            royalti_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

            for row in royalti_list:
                row['jumlah_royalti'] = row['rate_royalti_pemilik_hak_cipta'] * row['total_play_song']
                query = 'UPDATE royalti SET jumlah = %s WHERE id_pemilik_hak_cipta = %s AND id_song = %s'
                cursor.execute(query, (row['jumlah_royalti'], row['id_pemilik_hak_cipta'], row['id_konten']))

            context['royalti_list'] = royalti_list

        return render(request, 'songRoyalti.html', context=context)
