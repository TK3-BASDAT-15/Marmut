from django.db import connection
from django.shortcuts import render
from .forms import PodcastForm  
from django.shortcuts import redirect  
from .forms import EpisodeForm
import datetime
import uuid

def list_podcasts(request):
    email = request.COOKIES.get("email")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                konten.id,
                konten.judul AS podcast_title,
                COALESCE(SUM(episode.durasi), 0) AS total_durasi,
                COUNT(episode.id_konten_podcast) AS jumlah_episode
            FROM 
                podcast
            JOIN 
                konten ON podcast.id_konten = konten.id
            LEFT JOIN 
                episode ON podcast.id_konten = episode.id_konten_podcast
            WHERE
                podcast.email_podcaster = %s
            GROUP BY 
                konten.id, konten.judul
        """, [email])
        result = cursor.fetchall()
    podcasts = [{'podcast_id':row[0],'judul': row[1], 'jumlah_episode': row[3], 'total_durasi': f"{row[2]} menit"} for row in result]
    return render(request, 'podcastlist.html', {'podcasts': podcasts})




def view_episodes(request, podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT konten.id, konten.judul FROM konten
                JOIN podcast ON konten.id = podcast.id_konten
                WHERE podcast.id_konten = %s """,[podcast_id])
        podcast = cursor.fetchone()
        cursor.execute("""
                        SELECT judul, deskripsi, durasi, tanggal_rilis, episode.id_episode
                        FROM episode 
                        WHERE id_konten_podcast = %s;
                    """, [podcast_id])
        episodes = cursor.fetchall()
    episodes = [{'title': row[0], 'description': row[1], 'duration': f"{row[2]} menit", 'date': row[3].strftime('%Y-%m-%d'), 'episode_id':row[4]} for row in episodes]
    return render(request, 'view_episodes.html', {'podcast': {'id':podcast[0],'judul': podcast[1]}, 'episodes': episodes})

def add_episode(request, podcast_id):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        durasi = request.POST.get('durasi')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO episode (
                    id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, [uuid.uuid4(), podcast_id, judul, deskripsi, durasi, datetime.date.today()])
        return redirect('podcast:view_episodes', podcast_id=podcast_id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT judul FROM konten WHERE id = %s", [podcast_id])
        podcast_title = cursor.fetchone()[0]

    return render(request, 'createepisode.html', {'podcast_title': podcast_title})

def create_podcast(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT genre FROM genre")
        fetched_genres = [genre[0] for genre in cursor.fetchall()]

    if request.method == 'GET' and 'judul' in request.GET:
        judul = request.GET['judul']
        genres = request.GET.getlist('genre')
        id_konten = uuid.uuid4()
        email = request.COOKIES.get("email")
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi) VALUES (%s, %s, %s, %s, %s)
            """, [id_konten, judul, datetime.date.today(), datetime.datetime.now().year, 1])

            cursor.execute("""
                INSERT INTO podcast (id_konten, email_podcaster) VALUES (%s, %s)
            """, [id_konten, email])

            for genre in genres:
                cursor.execute("""
                    INSERT INTO genre (id_konten, genre) VALUES (%s, %s)
                """, [id_konten, genre])
        return redirect('podcast:list_podcasts')

    return render(request, 'create_podcast.html', {'dummy_genres': fetched_genres})

def play_podcast(request, podcast_id):
    podcast_data = {}
    episode_data = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT konten.judul, konten.tanggal_rilis, konten.tahun, 
                AKUN.nama AS podcaster_name, 
                SUM(episode.durasi) AS total_durasi
            FROM podcast
            JOIN podcaster ON podcast.email_podcaster = podcaster.email
            JOIN AKUN ON podcaster.email = AKUN.email
            JOIN konten ON podcast.id_konten = konten.id
            JOIN episode ON podcast.id_konten = episode.id_konten_podcast
            WHERE podcast.id_konten = %s
            GROUP BY konten.judul, konten.tanggal_rilis, konten.tahun, AKUN.nama;
        """, [podcast_id])

        result = cursor.fetchone()
        podcast_data = {}
        if result:
            total_durasi = result[4]
            hours = total_durasi // 60
            minutes = total_durasi % 60
            formatted_duration = f"{hours} jam {minutes} menit" if hours > 0 else f"{minutes} menit"

            podcast_data = {
                'judul': result[0],
                'tanggal_rilis': result[1],
                'tahun': result[2],
                'podcaster': result[3],
                'total_durasi': formatted_duration
            }
        cursor.execute(
            """
            SELECT DISTINCT genre FROM genre WHERE id_konten = %s
            """, [podcast_id]
        )
        result = cursor.fetchall()
        if result:
            podcast_data['genre'] = [e for e in result[0]]
        # Query to get episodes details
        cursor.execute("""
                SELECT judul, deskripsi, durasi, tanggal_rilis
                FROM episode
                WHERE id_konten_podcast = %s
        """, [podcast_id])
        episodes = cursor.fetchall()

        # Format episode duration and store episode data
        for episode in episodes:
            duration_hours = episode[2] // 60
            duration_minutes = episode[2] % 60
            formatted_duration = f"{duration_hours} jam {duration_minutes} menit" if duration_hours else f"{duration_minutes} menit"

            episode_data.append({
                'title': episode[0],
                'description': episode[1],
                'duration': formatted_duration,
                'date': episode[3].strftime('%d/%m/%Y')
            })

    return render(request, 'playpodcast.html', {
        'podcast': podcast_data,
        'episodes': episode_data
    })


def delete_episode(request, episode_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_konten_podcast FROM episode WHERE id_episode = %s", [episode_id])
            podcast_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM episode WHERE id_episode = %s", [episode_id])
            
        return redirect('podcast:view_episodes', podcast_id=podcast_id)
    else:
        return redirect('podcast:list_podcasts') 
    
def delete_podcast(request, podcast_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM podcast WHERE id_konten = %s", [podcast_id])
            cursor.execute("DELETE FROM genre WHERE id_konten = %s", [podcast_id])

        return redirect('podcast:list_podcasts')
    return redirect('podcast:list_podcasts') 