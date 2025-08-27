from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import *
@api_view(['POST', 'GET'])
def RegistrationView(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = RegisterForm()
    return render(request, 'registration.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@api_view(['GET', 'POST'])
def patient(request):
    if request.method == 'GET':
        patients = Patient.objects.all()
        serializer = Patientserializer(patients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = Patientserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def patient_detail(request, pk):
    try:
        patient = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = Patientserializer(patient)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = Patientserializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
    

@api_view(['GET'])
def medical_records(request):
    try:
        patient = request.user.patient_profile
        records = MedicalRecord.objects.filter(patient=patient)
        serializer = MedicalRecordserializer(records, many=True)
        return Response(serializer.data)
    except AttributeError:
        return Response({'error': 'Patient profile not found'}, status=403)
    
@api_view(['GET', 'POST'])
def appointments(request):
    if request.method == 'GET':
        try:
            patient = request.user.patient_profile
            appointments = Appointment.objects.filter(patient=patient)
            serializer = Appointmentserializer(appointments, many=True)
            return Response(serializer.data)
        except AttributeError:
            return Response({'error': 'Patient profile not found'}, status=403)
    
    elif request.method == 'POST':
        # Handle appointment creation
        pass    


@login_required
def dashboard(request):
    user = request.user
    
    # Check if patient profile exists using try/except for better error handling
    try:
        patient = user.patient_profile
        records = MedicalRecord.objects.filter(patient=patient)
        appointments = Appointment.objects.filter(patient=patient)
    except AttributeError:
        # patient_profile doesn't exist
        patient = None
        records = MedicalRecord.objects.none()
        appointments = Appointment.objects.none()
    
    return render(request, 'dashboard.html', {
        'user': user,
        'patient': patient,
        'records': records,
        'appointments': appointments
    })

@login_required
def profile_setup(request):
    # You'll need to implement is_patient() method in your User model
    # or replace this with appropriate logic
    if not hasattr(request.user, 'is_patient') or not request.user.is_patient():
        messages.error(request, 'Only patients can access the profile setup.')
        return redirect('dashboard')
    
    if hasattr(request.user, 'patient_profile'):
        messages.info(request, 'Profile already set up.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        initial = {'first_name': request.user.first_name, 'last_name': request.user.last_name}
        form = PatientForm(initial=initial)

    return render(request, 'my_profile_form.html', {'form': form, 'mode': 'setup'})

@login_required
def my_profile_edit(request,pk):
    if not hasattr(request.user, 'is_patient') or not request.user.is_patient():
        messages.error(request, 'Only patients can access the profile setup.')
        return redirect('dashboard')

    try:
        # Try to get existing profile
        profile = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        # If profile doesn't exist, redirect to setup instead of creating incomplete one
        messages.info(request, 'Please complete your profile setup first.')
        return redirect('profile_setup')

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
        else:
            # Add debug output to see validation errors
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientForm(instance=profile)

    return render(request, 'my_profile_form.html', {'form': form, 'mode': 'edit'})

