from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('', views.landingPage, name='landing'),
    path('register/', views.RegistrationView, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointment_page,name='appointments'),
    
    # Profile URLs
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/edit/<int:pk>/', views.my_profile_edit, name='my_profile_edit'), 
    
    # Patient management URLs (for doctors)
    path('patients/', views.patient_list, name='patient_list'),  
    path('patients/<int:pk>/edit/', views.doctor_edit_patient, name='doctor_edit_patient'), 
    
    # Medical record HTML view
    path('patients/<int:patient_id>/medical-records/', views.medical_record_view, name='medical_record_view'),  
    
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # API URLs
    path('api/patients/', views.patient, name='patient_api'),
    path('api/patients/<int:pk>/', views.patient_detail, name='patient_detail_api'),
    path('api/user/profile/', views.user_profile, name='user_profile_api'),
    path('api/users/',views.UserPost, name= 'user-post'),
    path('api/medical-records/', views.medical_records_list, name='medical_records_api'),  
    path('api/medical-records/<int:pk>/', views.medical_record_detail, name='medical_record_detail_api'),
    path('api/appointments/', views.appointments, name='appointments_api'),
]