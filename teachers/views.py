from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.http import HttpResponse
from accounts.permissions import IsTeacherOrAdmin, IsAdminOrReadOnly
from accounts.models import UserProfile
from .models import Teacher
from .serializers import TeacherSerializer, TeacherCreateSerializer
import csv

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'subject_specialization']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return TeacherSerializer
    
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
            
            # Create user profile with teacher role
            UserProfile.objects.create(user=user, role='teacher')
            
            teacher = Teacher.objects.create(
                user=user,
                **serializer.validated_data
            )
            
            return Response(
                TeacherSerializer(teacher).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': 'Failed to create teacher'
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
                'error': 'Failed to update teacher'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        try:
            teacher = self.get_object()
            students = teacher.student_set.all()
            from students.serializers import StudentSerializer
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve students'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export all teachers to CSV file
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teachers.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Email', 'Phone Number',
            'Subject Specialization', 'Employee ID', 'Date of Joining',
            'Status', 'Students Count', 'Created At', 'Updated At'
        ])
        
        # Write data
        for teacher in Teacher.objects.all():
            writer.writerow([
                teacher.id,
                teacher.first_name,
                teacher.last_name,
                teacher.email,
                teacher.phone_number,
                teacher.subject_specialization,
                teacher.employee_id,
                teacher.date_of_joining,
                teacher.status,
                teacher.student_set.count(),
                teacher.created_at,
                teacher.updated_at
            ])
        
        return response
