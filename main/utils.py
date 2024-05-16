from django.db import connection
from marmut_15.settings import env
from datetime import datetime
import jwt
from jwt.exceptions import InvalidTokenError


def decode_session_token(session_token: str):
    try:
        decoded_token = jwt.decode(session_token, env('JWT_KEY'), algorithms=['HS256'])
    except InvalidTokenError as err:
        raise 'Session token is invalid' from err
    
    if decoded_token['expiresAt'] < datetime.now().timestamp():
        raise 'Session token has expired'

    return decoded_token