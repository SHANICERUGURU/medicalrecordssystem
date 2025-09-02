from .models import *
from rest_framework import serializers


class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

class MedicalRecordserializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    medical_records = MedicalRecordserializer(many=True, required=False)

    class Meta:
        model = Patient
        fields = '__all__'

    def create(self, validated_data):
        medical_records_data = validated_data.pop('medical_records', [])
        patient = Patient.objects.create(**validated_data)

        for record_data in medical_records_data:
            MedicalRecord.objects.create(patient=patient, **record_data)

        return patient

    def update(self, instance, validated_data):
        medical_records_data = validated_data.pop('medical_records', None)

        # update patient fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if medical_records_data is not None:
            self._update_medical_records(instance, medical_records_data)

        return instance

    def _update_medical_records(self, instance, medical_records_data):
        current_records = instance.medical_records.all()
        current_ids = set(current_records.values_list('id', flat=True))
        incoming_ids = set()

        for record_data in medical_records_data:
            record_id = record_data.get('id', None)
            if record_id:
                incoming_ids.add(record_id)
                # update existing
                record = MedicalRecord.objects.get(id=record_id, patient=instance)
                for attr, value in record_data.items():
                    if attr != 'id':  # don’t override id
                        setattr(record, attr, value)
                record.save()
            else:
                # create new
                record = MedicalRecord.objects.create(patient=instance, **record_data)
                incoming_ids.add(record.id)

        # delete records missing in payload
        records_to_delete = current_ids - incoming_ids
        MedicalRecord.objects.filter(id__in=records_to_delete, patient=instance).delete()

        return instance


class Appointmentserializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'      


