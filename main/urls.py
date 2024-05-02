from django.urls import path
from main.views import choose_register, register_user, show_main, register #sesuaikan dengan nama fungsi yang dibuat
from main.views import login_user #sesuaikan dengan nama fungsi yang dibuat
from main.views import logout_user

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'), 
    path('login/', login_user, name='login'), 
    path('logout/', logout_user, name='logout'),
    path('register-user/', register_user, name='register_user'),
    path('choose-register/', choose_register, name='choose_register'), 

]