from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/edit/<int:pk>/', views.my_profile_edit, name='my_profile_edit'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]