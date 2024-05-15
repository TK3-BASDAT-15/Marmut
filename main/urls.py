from django.urls import path
from main.views import *

app_name = 'main'

main_view = MainView.as_view()
register_view = RegisterView.as_view()
login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
dashboard_view = DashboardView.as_view()

urlpatterns = [
    path('main/', main_view, name='show_main'),
    path('register/', register_view, name='choose_register'),
    path('register/user/', register_view, name='register_user'),
    path('register/label/', register_view, name='register_label'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', main_view, name='show_dashboard'),
]