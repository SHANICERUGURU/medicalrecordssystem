from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
class PatientForm(forms.ModelForm):
    class Meta:
        model=Patient
        fields=['first_name', 'last_name', 'date_of_birth','gender','phone','blood_type','allergies','medical_history','last_appointment','last_doctor','emergency_contact_name','emergency_contact_phone']

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']        