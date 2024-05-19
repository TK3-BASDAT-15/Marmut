from marmut_15.settings import env
from datetime import datetime
import jwt
from jwt.exceptions import InvalidTokenError
from django.http import HttpRequest
from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
import inspect


def decode_session_token(session_token: str):
    try:
        decoded_token: dict = jwt.decode(session_token, env('JWT_KEY'), algorithms=['HS256'])
    except InvalidTokenError as err:
        raise 'Session token is invalid' from err

    if decoded_token['expiresAt'] < datetime.now().timestamp():
        raise 'Session token has expired'
    
    valid_keys = set(('email', 'isArtist', 'isSongwriter',
                     'isPodcaster', 'isLabel', 'expiresAt'))
    token_keys = decoded_token.keys()

    if not valid_keys.issubset(token_keys):
        raise 'Session token is invalid'

    return decoded_token


def extract_session_token(request: HttpRequest):
    if 'session_token' not in request.COOKIES:
        raise 'Session token is missing'

    return request.COOKIES['session_token']


def login_required(func):
    signature = inspect.signature(func)
    params = signature.parameters

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            session_token = extract_session_token(request)
            decoded_token = decode_session_token(session_token)
        except:
            return redirect(reverse('main:login'))
        
        if 'decoded_token' in params:
            kwargs['decoded_token'] = decoded_token

        with connection.cursor() as cursor:
            email = decoded_token['email']
            is_artist = decoded_token['isArtist']
            is_songwriter = decoded_token['isSongwriter']
            is_podcaster = decoded_token['isPodcaster']
            is_label = decoded_token['isLabel']

            if is_artist:
                query = 'SELECT artist.id FROM artist \
                        JOIN akun ON artist.email_akun = akun.email \
                        WHERE artist.email_akun = %s'
            elif is_songwriter:
                query = 'SELECT songwriter.id FROM songwriter \
                        JOIN akun ON songwriter.email_akun = akun.email \
                        WHERE songwriter.email_akun = %s'
            elif is_podcaster:
                query = 'SELECT podcaster.email FROM podcaster \
                        JOIN akun ON podcaster.email = akun.email \
                        WHERE podcaster.email = %s'
            elif is_label:
                query = 'SELECT label.id FROM label \
                        WHERE label.email = %s'
                
            cursor.execute(query, (email,))

            if cursor.fetchone() is None:
                response = redirect(reverse('main:login'))
                response.delete_cookie('session_token')
                return response

        return func(request, *args, **kwargs)
    return wrapper
