from .models import *
from rest_framework import serializers

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class Patientserializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class MedicalRecordserializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

class Appointmentserializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'      


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user