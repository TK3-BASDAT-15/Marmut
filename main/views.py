from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import *
from django.views import View
from django.db import connection
from .forms import LoginForm, UserRegisterForm, LabelRegisterForm
import uuid
import jwt
from marmut_15.settings import env
from datetime import datetime, timedelta
from marmut_15.utils import extract_session_token, decode_session_token, login_required
from django.utils.decorators import method_decorator


# Create your views here.
class MainView(View):
    def get(self, request: HttpRequest):
        try:
            session_token = extract_session_token(request)
            decode_session_token(session_token)
            return redirect(reverse('main:show_dashboard'))
        except:
            return render(request, 'main.html')



class RegisterView(View):
    def get(self, request: HttpRequest):
        if 'session_token' in request.COOKIES:
            session_token = request.COOKIES['session_token']
            return self.__get_register_with_auth(request, session_token)

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
        
    def __get_register_with_auth(self, request: HttpRequest, session_token: str):
        req_full_path = request.get_full_path()

        try:
            decode_session_token(session_token)
        except:
            if req_full_path.endswith('/register/'):
                return render(request, 'chooseRegisterRole.html')
            elif req_full_path.endswith('/register/user/'):
                return render(request, 'registerUser.html')
            elif req_full_path.endswith('/register/label/'):
                return render(request, 'registerLabel.html')
            else:
                raise 'An unexpected error occured'
        
        return redirect(reverse('main:show_dashboard'))
        
    def __post_register_user(self, request: HttpRequest):
        form = UserRegisterForm(request.POST)
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
            query = 'SELECT email FROM label WHERE email = %s'
            cursor.execute(query, (cleaned_data['email'],))
            label = cursor.fetchone()

            if label is not None:
                context['error'] = 'User/label already exists'
                return render(request, 'registerUser.html', context=context,
                              status=HttpResponseBadRequest.status_code)

            query = "INSERT INTO akun \
                    (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal) \
                    VALUES \
                    (%s, %s, %s, %s, %s, %s, %s, %s)"
            
            try:
                cursor.execute(query, (cleaned_data['email'], cleaned_data['password'],
                               cleaned_data['name'], gender, cleaned_data['birth_place'],
                               cleaned_data['birth_date'], False, cleaned_data['city']))
            except:
                context['error'] = 'User/label already exists'
                return render(request, 'registerUser.html', context=context,
                              status=HttpResponseBadRequest.status_code)
            
            if cleaned_data['podcaster']:
                query = 'INSERT INTO podcaster (email) VALUES (%s)'
                cursor.execute(query, (cleaned_data['email'],))
            if cleaned_data['artist']:
                id_pemilik_hak_cipta = uuid.uuid4()
                query = 'INSERT INTO pemilik_hak_cipta (id, rate_royalti) \
                        VALUES (%s, %s)'
                cursor.execute(query, (id_pemilik_hak_cipta, 0))
                query = 'INSERT INTO artist (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)'
                cursor.execute(query, (uuid.uuid4(), cleaned_data['email'], id_pemilik_hak_cipta))
            if cleaned_data['songwriter']:
                id_pemilik_hak_cipta = uuid.uuid4()
                query = 'INSERT INTO pemilik_hak_cipta (id, rate_royalti) \
                        VALUES (%s, %s)'
                cursor.execute(query, (id_pemilik_hak_cipta, 0))
                query = 'INSERT INTO songwriter (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)'
                cursor.execute(query, (uuid.uuid4(), cleaned_data['email'], id_pemilik_hak_cipta))

        return redirect(reverse('main:login'))
        
    def __post_register_label(self, request: HttpRequest):
        form = LabelRegisterForm(request.POST)
        context = {}

        if not form.is_valid():
            context['error'] = 'Invalid form input'
            return render(request, 'registerLabel.html', context=context,
                          status=HttpResponseBadRequest.status_code)

        cleaned_data = form.cleaned_data

        with connection.cursor() as cursor:
            query = 'SELECT email FROM akun WHERE email = %s'
            cursor.execute(query, (cleaned_data['email'],))
            akun = cursor.fetchone()

            if akun is not None:
                context['error'] = 'User/label already exists'
                return render(request, 'registerLabel.html', context=context,
                              status=HttpResponseBadRequest.status_code)

            query = 'INSERT INTO label \
                    (id, nama, email, password, kontak) \
                    VALUES \
                    (%s, %s, %s, %s, %s)'

            try:
                cursor.execute(query, (uuid.uuid4(), cleaned_data['name'], cleaned_data['email'],
                               cleaned_data['password'], cleaned_data['contact']))
            except:
                context['error'] = 'User/label already exists'
                return render(request, 'registerLabel.html', context=context,
                              status=HttpResponseBadRequest.status_code)
            
            id_pemilik_hak_cipta = uuid.uuid4()
            query = 'INSERT INTO pemilik_hak_cipta (id, rate_royalti) \
                    VALUES (%s, %s)'
            cursor.execute(query, (id_pemilik_hak_cipta, 0))

            query = 'UPDATE label SET id_pemilik_hak_cipta = %s WHERE email = %s'
            cursor.execute(query, (id_pemilik_hak_cipta, cleaned_data['email']))

        return redirect(reverse('main:login'))


class LoginView(View):
    def get(self, request: HttpRequest):
        if 'session_token' not in request.COOKIES:
            return render(request, 'login.html')
        else:
            session_token = request.COOKIES['session_token']
            return self.__get_login_with_auth(request, session_token)

    def post(self, request: HttpRequest):
        form = LoginForm(request.POST)
        context = {}

        if not form.is_valid():
            context['error'] = 'Invalid form input'
            return render(request, 'login.html', context=context,
                          status=HttpResponseBadRequest.status_code)
        
        cleaned_data = form.cleaned_data

        payload = {
            'email': None,
            'isLabel': False,
            'isArtist': False,
            'isPodcaster': False,
            'isSongwriter': False
        }

        with connection.cursor() as cursor:
            query = 'SELECT email FROM label WHERE email = %s AND password = %s'
            cursor.execute(query, (cleaned_data['email'], cleaned_data['password']))
            label = cursor.fetchone()

            if label is not None:
                payload['isLabel'] = True
            else:
                query = 'SELECT email FROM akun WHERE email = %s AND password = %s'
                cursor.execute(query, (cleaned_data['email'], cleaned_data['password']))
                akun = cursor.fetchone()

                if akun is None:
                    context['error'] = 'Invalid email or password'
                    return render(request, 'login.html', context=context,
                                status=HttpResponseBadRequest.status_code)
                
                query = 'SELECT akun.email FROM akun JOIN artist ON akun.email = artist.email_akun \
                        WHERE akun.email = %s'
                cursor.execute(query, (cleaned_data['email'],))
                artist = cursor.fetchone()

                payload['isArtist'] = artist is not None

                query = 'SELECT akun.email FROM akun JOIN podcaster ON akun.email = podcaster.email \
                        WHERE akun.email = %s'
                cursor.execute(query, (cleaned_data['email'],))
                podcaster = cursor.fetchone()

                payload['isPodcaster'] = podcaster is not None

                query = 'SELECT akun.email FROM akun JOIN songwriter ON akun.email = songwriter.email_akun \
                        WHERE akun.email = %s'
                cursor.execute(query, (cleaned_data['email'],))
                songwriter = cursor.fetchone()

                payload['isSongwriter'] = songwriter is not None

                session_id = str(uuid.uuid4())
                payload['sessionId'] = session_id

        payload['email'] = cleaned_data['email']

        expires_at = datetime.now() + timedelta(hours=1)
        payload['expiresAt'] = expires_at.timestamp()

        session_token = jwt.encode(payload, env('JWT_KEY'), algorithm='HS256')

        response = redirect(reverse('main:show_dashboard'))
        response.set_cookie('session_token', session_token)

        return response
    
    def __get_login_with_auth(self, request: HttpRequest, session_token: str):
        try:
            decode_session_token(session_token)
        except:
            return render(request, 'login.html')
        
        return redirect(reverse('main:show_dashboard'))


class LogoutView(View):
    def get(self, request: HttpRequest):
        response = redirect(reverse('main:login'))
        response.delete_cookie('session_token')
        return response


@method_decorator(login_required, name='get')
class DashboardView(View):
    def get(self, request: HttpRequest, decoded_token: dict):
        context = {}

        with connection.cursor() as cursor:
            if decoded_token['isArtist'] or decoded_token['isSongwriter']:
                query = 'SELECT nama, kota_asal, gender, tempat_lahir, tanggal_lahir FROM akun \
                        WHERE email = %s'
                cursor.execute(query, (decoded_token['email'],))

                columns = ['nama', 'kota_asal', 'gender', 'tempat_lahir', 'tanggal_lahir']
                akun = dict(zip(columns, cursor.fetchone()))

                akun['email'] = decoded_token['email']

                if decoded_token['isArtist']:
                    akun['role'] = 'Artist'
                elif decoded_token['isSongwriter']:
                    akun['role'] = 'Songwriter'
                else:
                    akun['role'] = 'User'

                context['nama'] = akun['nama']
                context['akun'] = akun
            elif decoded_token['isLabel']:
                query = 'SELECT nama, kontak FROM label WHERE email = %s'
                cursor.execute(query, (decoded_token['email'],))

                columns = ['nama', 'email', 'kontak']
                label = dict(zip(columns, cursor.fetchone()))

                label['email'] = decoded_token['email']

                context['nama'] = label['nama']
                context['label'] = label

        return render(request, 'dashboard.html', context=context)
