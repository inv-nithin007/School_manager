from rest_framework import serializers
from .models import Student
from teachers.models import Teacher

class StudentSerializer(serializers.ModelSerializer):
    assigned_teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 
                 'roll_number', 'class_grade', 'date_of_birth', 'admission_date',
                 'status', 'assigned_teacher', 'assigned_teacher_name', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_assigned_teacher_name(self, obj):
        if obj.assigned_teacher:
            return f"{obj.assigned_teacher.first_name} {obj.assigned_teacher.last_name}"
        return None

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                 'roll_number', 'class_grade', 'date_of_birth', 'admission_date',
                 'status', 'assigned_teacher']
        
    def validate_email(self, value):
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value
    
    def validate_roll_number(self, value):
        if Student.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("A student with this roll number already exists.")
        return value