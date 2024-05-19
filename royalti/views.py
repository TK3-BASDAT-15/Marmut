from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import uuid

# Create your views here.
# @method_decorator(csrf_exempt, name='dispatch')
class RoyaltiView(View):
    def get(self, request: HttpRequest, email_akun):
        return render(request, 'songRoyalti.html')
