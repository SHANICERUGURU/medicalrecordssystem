from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  

urlpatterns = [
    path('', views.landingPage, name='landing'),
    path('register/', views.RegistrationView, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointment_page,name='appointments'),
    path('patientlist/', views.patient_list, name='patient-list'),
    path('patient/<int:pk>/', views.patient_detail_view, name='patient_detail'),
    
    # Profile URLs
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/edit/<int:pk>/', views.my_profile_edit, name='my_profile_edit'), 
    path('doctor/setup/', views.doctor_profile_setup,name='doctorprofilesetup'),
    path('doctor/edit/<int:pk>/', views.doctor_profile_edit, name='doctoreditprofile'),
    
    # Patient management URLs (for doctors)
    path('patients/', views.patient_list, name='patient_list'),  
    path('patients/<int:pk>/edit/', views.doctor_edit_patient, name='doctor_edit_patient'), 
    
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    
    # API URLs
    path('api/patients/', views.patient, name='patient_api'),
    path('api/patients/<int:pk>/', views.patient_detail, name='patient_detail_api'),
    path('api/doctors/', views.doctor_api, name='doctor_api'),
    path('api/doctors/<int:pk>/', views.doctor_detail_api, name= 'doctor_detail'),
    path('api/user/profile/', views.user_profile, name='user_profile_api'),
    path('api/users/',views.UserPost, name= 'user-post'),
    path('api/appointments/', views.appointments, name='appointments_api'),

    
]