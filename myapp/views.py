from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from .forms import *
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *

def landingPage(request):
    return render (request, 'landing.html')

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

@api_view(['POST','GET'])
def UserPost(request):
    if request.method == 'POST':
        serializers=Userserializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        users=User.objects.all()
        serializers=Userserializer(users, many=True)
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    
    

def login_view(request):
    form= AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html', {'form': form})

@api_view(['GET', 'POST'])
def patient(request):
    if request.method == 'GET':
        patients = Patient.objects.all()
        serializers = PatientSerializer(patients, many=True)
        return Response(serializers.data)

    elif request.method == 'POST':
        serializers = PatientSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    


    
@api_view(['GET', 'PUT', 'DELETE'])
def patient_detail(request, pk):
    try:
        # Get the patient object with proper permission checks
        if request.user.is_doctor():
            # Doctors can access any patient
            patient = Patient.objects.get(pk=pk)
        else:
            # Patients can only access their own profile
            try:
                patient_profile = request.user.patient_profile
                if patient_profile.id != int(pk):
                    return Response(
                        {'error': 'Access denied. You can only access your own profile.'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                patient = Patient.objects.get(pk=pk, user=request.user)
            except AttributeError:
                return Response(
                    {'error': 'Patient profile not found'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
    
    except Patient.DoesNotExist:
        return Response(
            {'error': 'Patient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        return Response(
            {'error': 'Invalid patient ID'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Handle different HTTP methods
    if request.method == 'GET':
        serializers = PatientSerializer(patient)
        return Response(serializers.data)

    elif request.method == 'PUT':
        # For patients, ensure they can only update their own profile
        if not request.user.is_doctor() and patient.user != request.user:
            return Response(
                {'error': 'You can only update your own profile'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializers = PatientSerializer(patient, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Only allow doctors to delete patients
        if not request.user.is_doctor():
            return Response(
                {'error': 'Only doctors can delete patient profiles'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        patient.delete()
        return Response(
            {'message': 'Patient profile deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
@api_view(['GET','POST'])
def doctor_api(request):
    if request.method == 'GET':
        doctors=Doctor.objects.all()
        serializers=DoctorSerializer(doctors, many=True)
        return Response(serializers.data)
    
    elif request.method == 'POST':
        serializers=DoctorSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def doctor_detail_api(request, pk):
    try:
        doctor = Doctor.objects.get(pk=pk)
    except Doctor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = DoctorSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        doctor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
@login_required  
def patient_list(request):
    # Check if user is authenticated and is a doctor
    if not hasattr(request.user, 'is_doctor') or not request.user.is_doctor():
        messages.error(request, '❌ Access denied. Doctor privileges required to view patient lists.')
        return redirect('dashboard')
    
    patients = Patient.objects.all().select_related('user').prefetch_related('medical_records')

    context = {
        'patients': patients,
        'total_patients': patients.count(),
        'patients_with_records': patients.filter(medical_records__isnull=False).distinct().count(),
        'recent_patients': patients.filter(created_at__month=timezone.now().month).count(),
        'appointment_count': Appointment.objects.filter(date_time__gte=timezone.now()).count(),
        'upcoming_appointments': Appointment.objects.filter(date_time__gte=timezone.now()).order_by('date_time')[:10]
    }
    
    return render(request, 'patientlist.html', context)

    
@api_view(['GET', 'POST'])
def appointments(request):
    if request.method == 'GET':
        try:
            # patient = request.user.patient_profile
            appointments = Appointment.objects.all()
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
        


@login_required
def appointment_page(request):
    try:
        patient = request.user.patient_profile
    except AttributeError:
        messages.error(request, "You must complete your patient profile first.")
        return redirect("profile_setup")

    appointments = Appointment.objects.filter(patient=patient)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect("appointments")
    else:
        form = AppointmentForm()

    return render(request, "appointments.html", {
        "appointments": appointments,
        "form": form,
        "patient": patient,
    })
    
@api_view(['GET', 'PUT', 'POST'])
def user_profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializers = Userserializer(user)
        return Response(serializers.data)
    
    elif request.method == 'PUT':
        serializers = Userserializer(user, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
    return Response(serializers.errors, status=400)   
    
         

@login_required
def dashboard(request):
    user = request.user
    
    # Check if profiles exist
    patient = getattr(user, 'patient_profile', None)
    doctor = getattr(user, 'doctor_profile', None)
    
    # Get appointments based on user type
    if patient:
        appointments = Appointment.objects.filter(patient=patient)
    elif doctor:
        appointments = Appointment.objects.filter(doctor=doctor)
    else:
        appointments = Appointment.objects.none()
    
    return render(request, 'dashboard.html', {
        'user': user,
        'patient': patient,
        'doctor': doctor,
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
def doctor_edit_patient(request, pk):
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can edit patient profiles.')
        return redirect('dashboard')
    
    try:
        patient = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient not found.')
        return redirect('patient_list')
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient profile updated successfully.')
            return redirect('patient_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'doctor_edit_patient.html', {'form': form, 'patient': patient})

@login_required
def my_profile_edit(request,pk):
    if not hasattr(request.user, 'is_patient') or not request.user.is_patient():
        messages.error(request, 'Only patients can edit their profile.')
        return redirect('dashboard')
    
    try:
        profile = request.user.patient_profile
    except AttributeError:
        messages.info(request, 'Please complete your profile setup first.')
        return redirect('profile_setup')

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientForm(instance=profile)

    return render(request, 'my_profile_form.html', {'form': form, 'mode': 'edit'})


@login_required
def doctor_profile_setup(request):
    # Check if user already has a doctor profile
    if hasattr(request.user, 'doctor_profile'):
        messages.info(request, 'You already have a doctor profile.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            # Create doctor profile but don't save yet
            doctor = form.save(commit=False)
            doctor.user = request.user  # Associate with current user
            doctor.save()
            messages.success(request, 'Doctor profile created successfully!')
            return redirect('dashboard')
    else:
        form = DoctorForm()
    
    return render(request, 'doctorregistration.html', {
        'form': form,
        'title': 'Doctor Profile Setup'
    })


@login_required
def doctor_profile_edit(request, pk):
    # Verify the user is editing their own profile
    if request.user.id != pk:
        messages.error(request, 'You can only edit your own profile.')
        return redirect('dashboard')
    
    # Check if user has a doctor profile
    if not hasattr(request.user, 'doctor_profile'):
        messages.info(request, 'Please complete your doctor profile setup first.')
        return redirect('doctorprofilesetup')
    
    try:
        profile = request.user.doctor_profile
    except AttributeError:
        messages.info(request, 'Please complete your doctor profile setup first.')
        return redirect('doctorprofilesetup')

    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor profile updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorForm(instance=profile)

    return render(request, 'doctorregistration.html', {'form': form, 'mode': 'edit'})

