from django import forms
from .models import *
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
class PatientForm(forms.ModelForm):
    class Meta:
        model=Patient
        fields=['blood_type','allergies','chronic_illness','last_appointment','last_doctor','emergency_contact_name','emergency_contact_phone', 'insurance_type', 'current_medications', 'family_medical_history',]
         #    adding styling to the form created
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

User = get_user_model()       
class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields=['first_name', 'last_name','username','email','phone', 'gender', 'date_of_birth','role' ,'password1','password2'] 

        #    adding styling to the form created
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
     
    
        
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'date', 'doctor', 'notes']
        
    def __init__(self, *args, **kwargs):
        super(MedicalRecordForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'           