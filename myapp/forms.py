from django import forms
from .models import *
class PatientForm(forms.ModelForm):
    class Meta:
        model=Patient
        fields=['first_name', 'last_name', 'date_of_birth','gender','phone','blood_type','allergies','medical_history','last_appointment','last_doctor','emergency_contact_name','emergency_contact_phone']