from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


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

# REMOVE these custom login/logout views since you're using Django's auth views
# def login_form(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('dashboard')
#         else:
#             return render(request, 'myapp/login.html', {'error': 'Invalid username or password.'})
#     return render(request, 'myapp/login.html')

# def logout_view(request):
#     logout(request)
#     return redirect('login')