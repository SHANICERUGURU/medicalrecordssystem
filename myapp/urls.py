from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    # path('', views.home, name='home'),
    path('register/', views.RegistrationView, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/edit/<int:pk>/', views.my_profile_edit, name='my_profile_edit'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/patients/', views.patient , name='patient'),
    path('api/patients/<int:pk>/', views.patient_detail , name='patient_detail'),
    path('api/user/profile/', views.user_profile , name='user_profile'),
    path('api/medical_records/', views.medical_records , name='medical_records'),
    path('api/medical_records/<int:pk>/', views.medical_record_detail , name='medical_record_detail'),
    path('api/appointments/', views.appointments , name='appointments'),
]