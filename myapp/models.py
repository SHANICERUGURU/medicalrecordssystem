from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

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
    
    # first_name = models.CharField(max_length=100)
    # last_name = models.CharField(max_length=100)
    # username=models.CharField(max_length=100)
    # email = models.EmailField(unique=True)
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
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Auto-populate first_name and last_name from user if not set
        if not self.first_name and self.user.first_name:
            self.first_name = self.user.first_name
        if not self.last_name and self.user.last_name:
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    diagnosis = models.CharField(max_length=200)
    treatment = models.TextField()
    date = models.DateField()
    doctor = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record for {self.patient.first_name} {self.patient.last_name} on {self.date}"   


class Appointment(models.Model):
    appointment_status=[
        ('SCHEDULED','Scheduled'),
        ('COMPLETED','Completed'),
        ('CANCELLED','Cancelled')
    ]
    patient=models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date_time=models.DateTimeField()
    doctor=models.CharField(max_length=100)
    reason=models.TextField()
    status=models.CharField(max_length=20, choices=appointment_status, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)  # Add this
    updated_at = models.DateTimeField(auto_now=True)      # Add this

    def __str__(self):  # Add this method
        return f"Appointment with Dr. {self.doctor} on {self.date_time}"
    


    
