from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import *
from django.core import serializers
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.db import connection
from .forms import RegisterForm
import uuid


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
            context['form'] = form
            return render(request, 'registerUser.html', context=context,
                          status=HttpResponseBadRequest.status_code)
        
        cleaned_data = form.cleaned_data
        
        match cleaned_data['gender']:
            case 'male':
                gender = 0
            case 'female':
                gender = 1
            case _:
                context['error'] = 'no. just no.'
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
                context['error'] = 'Failed to register user'
                return render(request, 'registerUser.html', context=context,
                              status=HttpResponseBadRequest.status_code)
            
            if cleaned_data['podcaster']:
                query = 'INSERT INTO podcaster (email) VALUES (%s)'
                cursor.execute(query, cleaned_data['email'])
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
        req_full_path = request.get_full_path()

        return render(request, 'login.html')

    def post(self, request: HttpRequest):
        req_full_path = request.get_full_path()


class LogoutView(View):
    def get(self, request: HttpRequest):
        response = redirect(reverse('main:login'))
        response.delete_cookie('last_login')
        return response


class DashboardView(View):
    def get(self, request: HttpRequest):
        return render(request, 'dashboard.html')
