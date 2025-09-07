from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import date, time,datetime

class User(AbstractUser):
    class Role(models.TextChoices):  # Changed 'roles' to 'Role' (PascalCase for classes)
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        PATIENT = 'PATIENT', 'Patient'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)  # Fixed reference
   
    def is_patient(self):
        return self.role == self.Role.PATIENT  # Fixed reference
    
    def display_patient_name(self):
        return f"{self.first_name} {self.last_name}".strip()  # Improved with f-string and strip()
    
    def is_doctor(self):
        return self.role == self.Role.DOCTOR  # Fixed reference
    
    def is_admin(self):
        return self.role == self.Role.ADMIN  # Fixed reference
    
    def __str__(self):
        return f"{self.username} ({self.role})"  # Added __str__ method for better representation
    
   
    date_of_birth = models.DateField(null=True)
    
    class Gender(models.TextChoices):  # Using Django choices class pattern
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
    
    gender = models.CharField(max_length=1, choices=Gender.choices, default='F')  # Fixed reference
    phone = models.CharField(max_length=15, default='0000000000')
    

   
class Patient(models.Model):
    # One-to-one relationship with the User model (one profile = one user)
    user = models.OneToOneField(      
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )   
    
    
    blood_type = models.CharField(max_length=3)
    allergies = models.TextField(blank=True)
    chronic_illness = models.TextField(blank=True, null=True)
    last_appointment = models.DateField(null=True, blank=True)
    last_doctor = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    insurance_type = models.CharField(max_length=100, blank=True)
    current_medications = models.TextField(blank=True)  
    family_medical_history = models.TextField(blank=True)
    
    # Add these fields for better data management
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class Doctor(models.Model) :
    user=models.OneToOneField(
       settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    class Specialty(models.TextChoices):
        generaldoctor = 'GENERALDOCTOR','generaldoctor'
        dentist = 'DENTIST', 'dentist'
        oncologist = 'ONCOLOGIST','oncologist'
        orthopaedic = 'ortho', 'orthopaedic'
        optician = 'OPTICIAN', 'optician'
        paediatrician = 'PAEDIATRICIAN', 'paediatrician'
        cardiologist = 'cardio', 'cardiologist'

    specialty= models.CharField(max_length=100, choices=Specialty.choices, default='generaldotor')    
    hospital=models.CharField(max_length=100)
    license_number=models.CharField (max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Appointment(models.Model):
    appointment_status=[
        ('SCHEDULED','Scheduled'),
        ('COMPLETED','Completed'),
        ('CANCELLED','Cancelled')
    ]
    patient=models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date=models.DateField(default='2023-01-01')  
    time= models.TimeField(default='12:00:00') 
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='appointments',null=True,blank=True)
    reason=models.TextField()
    status=models.CharField(max_length=20, choices=appointment_status, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):  
        return f"Appointment with Dr. {self.doctor} on {self.date} at {self.time}"
