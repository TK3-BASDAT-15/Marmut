from django import forms
from django.db import connection

class AddAlbumForm(forms.Form):
    album_title = forms.CharField(max_length=100, required=True)
    label = forms.UUIDField(required=True)
    song_title = forms.CharField(max_length=100, required=True)
    artist = forms.UUIDField()
    songwriter = forms.MultipleChoiceField(required=True)
    genre = forms.MultipleChoiceField(required=True)
    duration = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super(AddAlbumForm, self).__init__(*args, **kwargs)
        
        with connection.cursor() as cursor:
            query = 'SELECT DISTINCT genre FROM genre'
            cursor.execute(query)

            genres = [(row[0], row[0]) for row in cursor.fetchall()]
            self.fields['genre'].choices = genres

            query = 'SELECT id FROM songwriter'
            cursor.execute(query)

            songwriters = [(row[0], row[0]) for row in cursor.fetchall()]
            self.fields['songwriter'].choices = songwriters

class AddSongToAlbumForm(forms.Form):
    song_title = forms.CharField(max_length=100, required=True)
    artist = forms.UUIDField()
    songwriter = forms.MultipleChoiceField(required=True)
    genre = forms.MultipleChoiceField(required=True)
    duration = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super(AddSongToAlbumForm, self).__init__(*args, **kwargs)
        
        with connection.cursor() as cursor:
            query = 'SELECT DISTINCT genre FROM genre'
            cursor.execute(query)

            genres = [(row[0], row[0]) for row in cursor.fetchall()]
            self.fields['genre'].choices = genres

            query = 'SELECT id FROM songwriter'
            cursor.execute(query)

            songwriters = [(row[0], row[0]) for row in cursor.fetchall()]
            self.fields['songwriter'].choices = songwriters
