from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import *
from django.views import View
from django.db import connection
from .forms import LoginForm, RegisterForm
import uuid
import jwt
from marmut_15.settings import env
from datetime import datetime, timedelta


# Create your views here.
class MainView(View):
    def get(self, request: HttpRequest):
        return render(request, 'main.html')


class RegisterView(View):
    def get(self, request: HttpRequest):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/register/'):
            return render(request, 'chooseRegisterRole.html')
        elif req_full_path.endswith('/register/user/'):
            return render(request, 'registerUser.html')
        elif req_full_path.endswith('/register/label/'):
            return render(request, 'registerLabel.html')

    def post(self, request: HttpRequest):
        req_full_path = request.get_full_path()

        if req_full_path.endswith('/register/user/'):
            return self.__post_register_user(request)
        elif req_full_path.endswith('/register/label/'):
            return self.__post_register_label(request)
        
    def __post_register_user(self, request: HttpRequest):
        form = RegisterForm(request.POST)
        context = {}

        if not form.is_valid():
            context['error'] = 'Invalid form input'
            return render(request, 'registerUser.html', context=context,
                          status=HttpResponseBadRequest.status_code)
        
        cleaned_data = form.cleaned_data
        
        match cleaned_data['gender']:
            case 'male':
                gender = 0
            case 'female':
                gender = 1
            case _:
                context['error'] = 'support for other gender types like attack helicopter \
                                    has not been implemented yet'
                return render(request, 'registerUser.html', context=context,
                              status=HttpResponseBadRequest.status_code)
        
        with connection.cursor() as cursor:
            query = "INSERT INTO akun \
                    (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal) \
                    VALUES \
                    (%s, %s, %s, %s, %s, %s, %s, %s)"
            
            try:
                cursor.execute(query, (cleaned_data['email'], cleaned_data['password'],
                               cleaned_data['name'], gender, cleaned_data['birth_place'],
                               cleaned_data['birth_date'], False, cleaned_data['city']))
            except:
                context['error'] = 'User already exists'
                return render(request, 'registerUser.html', context=context,
                              status=HttpResponseBadRequest.status_code)
            
            if cleaned_data['podcaster']:
                query = 'INSERT INTO podcaster (email) VALUES (%s)'
                cursor.execute(query, (cleaned_data['email'],))
            if cleaned_data['artist']:
                query = 'INSERT INTO artist (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)'
                cursor.execute(query, (uuid.uuid4(), cleaned_data['email'], None))
            if cleaned_data['songwriter']:
                query = 'INSERT INTO songwriter (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)'
                cursor.execute(query, (uuid.uuid4(), cleaned_data['email'], None))
            
        context['success'] = 'User registered successfully'
        return render(request, 'login.html', context=context)
        
    def __post_register_label(self, request: HttpRequest):
        return render(request, 'registerLabel.html')


class LoginView(View):
    def get(self, request: HttpRequest):
        authorization = request.headers.get('Authorization')

        if authorization is not None:
            return self.__get_login_with_auth(authorization)
        else:
            return render(request, 'login.html')

    def post(self, request: HttpRequest):
        form = LoginForm(request.POST)
        context = {}

        if not form.is_valid():
            context['error'] = 'Invalid form input'
            return render(request, 'login.html', context=context,
                          status=HttpResponseBadRequest.status_code)
        
        cleaned_data = form.cleaned_data

        payload = {}

        with connection.cursor() as cursor:
            query = 'SELECT email FROM akun WHERE email = %s AND password = %s'
            cursor.execute(query, (cleaned_data['email'], cleaned_data['password']))
            akun = cursor.fetchone()

            if akun is None:
                context['error'] = 'Invalid email or password'
                return render(request, 'login.html', context=context,
                            status=HttpResponseBadRequest.status_code)
            
            payload['email'] = cleaned_data['email']
            
            query = 'SELECT akun.email FROM akun JOIN artist ON akun.email = artist.email_akun \
                    WHERE akun.email = %s'
            cursor.execute(query, (cleaned_data['email'],))
            artist = cursor.fetchone()

            if artist is not None:
                payload['is_artist'] = True

            query = 'SELECT akun.email FROM akun JOIN podcaster ON akun.email = podcaster.email \
                    WHERE akun.email = %s'
            cursor.execute(query, (cleaned_data['email'],))
            podcaster = cursor.fetchone()

            if podcaster is not None:
                payload['is_podcaster'] = 'PODCASTER'

            query = 'SELECT akun.email FROM akun JOIN songwriter ON akun.email = songwriter.email_akun \
                    WHERE akun.email = %s'
            cursor.execute(query, (cleaned_data['email'],))
            songwriter = cursor.fetchone()

            if songwriter is not None:
                payload['is_songwriter'] = 'SONGWRITER'

        session_id = uuid.uuid4()
        payload['sessionId'] = str(session_id)

        expires_at = datetime.now() + timedelta(hours=1)
        payload['expires_at'] = expires_at.timestamp()

        session_token = jwt.encode(payload, env('JWT_KEY'), algorithm='HS256')

        response = redirect(reverse('main:show_dashboard'))
        response.set_cookie('session_token', session_token)

        return response
    
    def __get_login_with_auth(self, authorization: str):
        context = {}

        if not authorization.startswith('Bearer '):
            context['error'] = 'Invalid authorization header'
            return render(request, 'login.html', context=context,
                          status=HttpResponseBadRequest.status_code)
        
        session_token = authorization[7:]
        decoded_token = jwt.decode(session_token, env('JWT_KEY'), algorithms=['HS256'])

        if decoded_token['expires_at'] < datetime.now().timestamp():
            return render(request, 'login.html')
        
        with connection.cursor() as cursor:
            query = 'SELECT id FROM session WHERE session.id = %s'
            cursor.execute(query, (decoded_token['sessionId'],))
            session_id = cursor.fetchone()

        if session_id is None:
            context['error'] = 'Invalid session'
            return render(request, 'login.html', context=context,
                          status=HttpResponseBadRequest.status_code)
        
        return redirect(reverse('main:show_dashboard'))


class LogoutView(View):
    def get(self):
        response = redirect(reverse('main:login'))
        response.delete_cookie('session_token')
        return response


class DashboardView(View):
    def get(self, request: HttpRequest):
        return render(request, 'dashboard.html')
