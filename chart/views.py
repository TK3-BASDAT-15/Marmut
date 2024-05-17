from django.db import connection
from django.shortcuts import render

def chart_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT tipe FROM chart")
        charts = cursor.fetchall()
    chart_list = [{'tipe': row[0]} for row in charts]
    return render(request, 'chart_list.html', {'charts': chart_list})

def top_20(request, type_of_top_20):
    with connection.cursor() as cursor:
        print(type_of_top_20)
        if type_of_top_20 == "Daily Top 20":
            cursor.execute("""
                SELECT 
                    konten.id,
                    konten.judul AS "Judul Lagu",
                    akun.nama AS "Oleh",
                    konten.tanggal_rilis AS "Tanggal Rilis",
                    COUNT(*) AS "Total Plays"
                FROM akun_play_song
                JOIN song ON akun_play_song.id_song = song.id_konten
                JOIN konten ON song.id_konten = konten.id
                JOIN artist ON song.id_artist = artist.id
                JOIN akun ON artist.email_akun = akun.email
                WHERE akun_play_song.waktu::date = CURRENT_DATE
                GROUP BY konten.id, konten.judul, akun.nama, konten.tanggal_rilis
                ORDER BY "Total Plays" DESC
                LIMIT 20;
            """)
        elif type_of_top_20 == "Weekly Top 20":
            cursor.execute("""
                SELECT 
                    konten.id,
                    konten.judul AS "Judul Lagu",
                    akun.nama AS "Oleh",
                    konten.tanggal_rilis AS "Tanggal Rilis",
                    COUNT(*) AS "Total Plays"
                FROM akun_play_song
                JOIN song ON akun_play_song.id_song = song.id_konten
                JOIN konten ON song.id_konten = konten.id
                JOIN artist ON song.id_artist = artist.id
                JOIN akun ON artist.email_akun = akun.email
                WHERE akun_play_song.waktu >= date_trunc('week', CURRENT_DATE)
                GROUP BY konten.id, konten.judul, akun.nama, konten.tanggal_rilis
                ORDER BY "Total Plays" DESC
                LIMIT 20;
            """)
        elif type_of_top_20 == "Monthly Top 20":
            cursor.execute("""
                SELECT 
                    konten.id,
                    konten.judul AS "Judul Lagu",
                    akun.nama AS "Oleh",
                    konten.tanggal_rilis AS "Tanggal Rilis",
                    COUNT(*) AS "Total Plays"
                FROM akun_play_song
                JOIN song ON akun_play_song.id_song = song.id_konten
                JOIN konten ON song.id_konten = konten.id
                JOIN artist ON song.id_artist = artist.id
                JOIN akun ON artist.email_akun = akun.email
                WHERE akun_play_song.waktu >= date_trunc('month', CURRENT_DATE)
                GROUP BY konten.id, konten.judul, akun.nama, konten.tanggal_rilis
                ORDER BY "Total Plays" DESC
                LIMIT 20;
            """)
        elif type_of_top_20 == "Yearly Top 20":
            cursor.execute("""
                SELECT 
                    konten.id,
                    konten.judul AS "Judul Lagu",
                    akun.nama AS "Oleh",
                    konten.tanggal_rilis AS "Tanggal Rilis",
                    COUNT(*) AS "Total Plays"
                FROM akun_play_song
                JOIN song ON akun_play_song.id_song = song.id_konten
                JOIN konten ON song.id_konten = konten.id
                JOIN artist ON song.id_artist = artist.id
                JOIN akun ON artist.email_akun = akun.email
                WHERE akun_play_song.waktu >= date_trunc('year', CURRENT_DATE)
                GROUP BY konten.id, konten.judul, akun.nama, konten.tanggal_rilis
                ORDER BY "Total Plays" DESC
                LIMIT 20;
            """)
            # print(cursor.fetchall())
        else:
            return render(request, '404.html')
        top_songs = cursor.fetchall()
        print(top_songs)
        songs_list = [{'id_lagu': row[0], 'title': row[1], 'artist': row[2], 'release_date': row[3].strftime('%d/%m/%Y'), 'total_plays': row[4]} for row in top_songs]
        return render(request, 'top_20.html', {'title': f'{type_of_top_20}', 'top_songs': songs_list})
        