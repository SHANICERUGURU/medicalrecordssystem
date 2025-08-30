from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializer import *

def RegistrationView(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
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
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def patient(request):
    if request.method == 'GET':
        patients = Patient.objects.all()
        serializer = Patientserializer(patients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        medical_records_data = request.data.pop('medical_records', [])
        serializer = Patientserializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save(user=request.user)
            for record_data in medical_records_data:
                MedicalRecord.objects.create(patient=patient, **record_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@login_required
@permission_classes([IsAuthenticated])
def patient_detail(request, pk):
    if request.user.is_doctor():
        profile = Patient.objects.get(pk=pk)  # doctor can edit any patient
    else:
        profile = request.user.patient_profile  # patient can only edit their own

    if request.method == 'GET':
        serializer = Patientserializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = Patientserializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def medical_records(request):
    try:
        patient = request.user.patient_profile
    except AttributeError:
        return Response({'error': 'Patient profile not found'}, status=403)
    records = MedicalRecord.objects.filter(patient=patient)
    serializer = MedicalRecordserializer(records, many=True)
    return Response(serializer.data)
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
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
        try:
            patient = request.user.patient_profile
            serializer = Appointmentserializer(data=request.data)
            if serializer.is_valid():
                serializer.save(patient=patient)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'error': 'Patient profile not found'}, status=403)
  
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def medical_records_list(request):
    if request.method == 'GET':
        try:
            patient = request.user.patient_profile
            records = MedicalRecord.objects.filter(patient=patient)
            serializer = MedicalRecordserializer(records, many=True)
            return Response(serializer.data)
        except AttributeError:
            return Response({'error': 'Patient profile not found'}, status=403)
    
    elif request.method == 'POST':
        try:
            patient = request.user.patient_profile
            serializer = MedicalRecordserializer(data=request.data)
            if serializer.is_valid():
                serializer.save(patient=patient)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'error': 'Patient profile not found'}, status=403)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def medical_record_detail(request, pk):
    try:
       if request.user.is_doctor():
           record = MedicalRecord.objects.get(pk=pk)
       else:
              patient = request.user.patient_profile
              record = MedicalRecord.objects.get(pk=pk, patient=patient) 
    except MedicalRecord.DoesNotExist:
        return Response({'error': 'Medical record not found'}, status=404)
    
    if request.method == 'GET':
        serializer = MedicalRecordserializer(record)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MedicalRecordserializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        record.delete()
        return Response(status=204)
    
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = Userserializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = Userserializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)   

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

