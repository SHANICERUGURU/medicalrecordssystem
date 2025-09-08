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
            

class DoctorForm(forms.ModelForm):
    class Meta:
        model=Doctor
        fields=['specialty', 'hospital', 'license_number']

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)
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
     
    
        
class AppointmentForm(forms.ModelForm):
    specialty = forms.ChoiceField(
        choices=Doctor.Specialty.choices,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit()'})
    )
    
    class Meta:
        model = Appointment
        fields = ['specialty', 'doctor', 'date', 'time'] 
    
    def __init__(self, *args, **kwargs):
        # Extract specialty from kwargs before calling super()
        specialty = kwargs.pop('specialty', None)
        super().__init__(*args, **kwargs)
        
        # Get specialty from either kwargs, GET data, or POST data
        selected_specialty = specialty
        
        # For GET requests (specialty filter), check initial data
        if not selected_specialty and hasattr(self, 'initial') and self.initial.get('specialty'):
            selected_specialty = self.initial.get('specialty')
        
        # For POST requests, check form data
        if not selected_specialty and hasattr(self, 'data') and self.data.get('specialty'):
            selected_specialty = self.data.get('specialty')
        
        # Filter doctors based on specialty if provided
        if selected_specialty:
            self.fields['doctor'].queryset = Doctor.objects.filter(specialty=selected_specialty)
        else:
            # Show all doctors if no specialty selected, or none if you prefer
            self.fields['doctor'].queryset = Doctor.objects.all()  # or Doctor.objects.none()
        
        # Set empty label for doctor dropdown
        self.fields['doctor'].empty_label = "Select a doctor"
        
        # Add placeholders and improve UX
        self.fields['date'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
        self.fields['time'].widget = forms.TimeInput(attrs={
            'class': 'form-control', 
            'type': 'time'
        })
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name != 'specialty':
                field.widget.attrs['class'] = 'form-control'