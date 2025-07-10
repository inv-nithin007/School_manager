from rest_framework import serializers
from .models import Teacher

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 
                 'subject_specialization', 'employee_id', 'date_of_joining', 
                 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class TeacherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                 'subject_specialization', 'employee_id', 'date_of_joining', 'status']
        
    def validate_email(self, value):
        if Teacher.objects.filter(email=value).exists():
            raise serializers.ValidationError("A teacher with this email already exists.")
        return value
    
    def validate_employee_id(self, value):
        if Teacher.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("A teacher with this employee ID already exists.")
        return value