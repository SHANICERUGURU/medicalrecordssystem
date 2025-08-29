from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
class PatientForm(forms.ModelForm):
    class Meta:
        model=Patient
        fields=['first_name', 'last_name', 'date_of_birth','gender','phone','blood_type','allergies','medical_history','last_appointment','last_doctor','emergency_contact_name','emergency_contact_phone']
         #    adding styling to the form created
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

User = get_user_model()       
class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2'] 

        #    adding styling to the form created
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'