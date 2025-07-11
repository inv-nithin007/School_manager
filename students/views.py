from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.http import HttpResponse
from accounts.permissions import IsStudentOrTeacherOrAdmin, IsAdminOrReadOnly
from accounts.models import UserProfile
from .models import Student
from .serializers import StudentSerializer, StudentCreateSerializer
import csv

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsStudentOrTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'class_grade', 'assigned_teacher']
    search_fields = ['first_name', 'last_name', 'email', 'roll_number']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user_data = {
                'username': serializer.validated_data['email'],
                'email': serializer.validated_data['email'],
                'first_name': serializer.validated_data['first_name'],
                'last_name': serializer.validated_data['last_name'],
                'password': 'defaultpassword123'
            }
            
            user = User.objects.create_user(**user_data)
            
            # Create user profile with student role
            UserProfile.objects.create(user=user, role='student')
            
            student = Student.objects.create(
                user=user,
                **serializer.validated_data
            )
            
            return Response(
                StudentSerializer(student).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': 'Failed to create student'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            user_data = {}
            if 'first_name' in serializer.validated_data:
                user_data['first_name'] = serializer.validated_data['first_name']
            if 'last_name' in serializer.validated_data:
                user_data['last_name'] = serializer.validated_data['last_name']
            if 'email' in serializer.validated_data:
                user_data['email'] = serializer.validated_data['email']
                user_data['username'] = serializer.validated_data['email']
            
            if user_data:
                User.objects.filter(id=instance.user.id).update(**user_data)
            
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Failed to update student'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export all students to CSV file
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Email', 'Phone Number',
            'Roll Number', 'Class Grade', 'Date of Birth', 'Admission Date',
            'Status', 'Assigned Teacher', 'Created At', 'Updated At'
        ])
        
        # Write data
        for student in Student.objects.all():
            writer.writerow([
                student.id,
                student.first_name,
                student.last_name,
                student.email,
                student.phone_number,
                student.roll_number,
                student.class_grade,
                student.date_of_birth,
                student.admission_date,
                student.status,
                f"{student.assigned_teacher.first_name} {student.assigned_teacher.last_name}" if student.assigned_teacher else 'None',
                student.created_at,
                student.updated_at
            ])
        
        return response
