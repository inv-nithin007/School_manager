import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import UserProfile
from students.models import Student
from .models import Teacher


class TeacherModelTest(TestCase):
    """Test Teacher model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='testpass123'
        )
    
    def test_teacher_creation(self):
        """Test creating a teacher"""
        teacher = Teacher.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='teacher@example.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='T001',
            date_of_joining='2024-01-01'
        )
        self.assertEqual(teacher.user, self.user)
        self.assertEqual(teacher.first_name, 'John')
        self.assertEqual(teacher.subject_specialization, 'Math')
        self.assertEqual(str(teacher), 'John Doe - T001')
    
    def test_teacher_student_relationship(self):
        """Test teacher-student relationship"""
        teacher = Teacher.objects.create(
            user=self.user,
            first_name='Jane',
            last_name='Smith',
            email='teacher@example.com',
            phone_number='1234567890',
            subject_specialization='Science',
            employee_id='T002',
            date_of_joining='2024-01-01'
        )
        
        # Create student user
        student_user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123'
        )
        
        # Create student assigned to teacher
        student = Student.objects.create(
            user=student_user,
            first_name='Student',
            last_name='Test',
            email='student@example.com',
            phone_number='1234567890',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01',
            assigned_teacher=teacher
        )
        
        self.assertEqual(teacher.student_set.count(), 1)
        self.assertEqual(teacher.student_set.first(), student)


class TeacherAPITest(APITestCase):
    """Test Teacher API endpoints"""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        UserProfile.objects.create(user=self.admin_user, role='admin')
        
        # Create teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='teacherpass123'
        )
        UserProfile.objects.create(user=self.teacher_user, role='teacher')
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='studentpass123'
        )
        UserProfile.objects.create(user=self.student_user, role='student')
        
        # Create teacher object
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='Teacher',
            last_name='Test',
            email='teacher@example.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='T001',
            date_of_joining='2024-01-01'
        )
    
    def get_auth_header(self, user):
        """Get authentication header for user"""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_teachers_as_admin(self):
        """Test listing teachers as admin"""
        url = reverse('teacher-list')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_teachers_as_teacher(self):
        """Test listing teachers as teacher (read-only)"""
        url = reverse('teacher-list')
        response = self.client.get(url, **self.get_auth_header(self.teacher_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_teachers_as_student(self):
        """Test listing teachers as student (read-only)"""
        url = reverse('teacher-list')
        response = self.client.get(url, **self.get_auth_header(self.student_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_teacher_as_admin(self):
        """Test creating teacher as admin"""
        url = reverse('teacher-list')
        data = {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@example.com',
            'phone_number': '9876543210',
            'subject_specialization': 'Physics',
            'employee_id': 'T002',
            'date_of_joining': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'New')
    
    def test_create_teacher_as_teacher_forbidden(self):
        """Test creating teacher as teacher (should be forbidden)"""
        url = reverse('teacher-list')
        data = {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@example.com',
            'phone_number': '9876543210',
            'subject_specialization': 'Physics',
            'employee_id': 'T003',
            'date_of_joining': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.teacher_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_teacher_duplicate_email(self):
        """Test creating teacher with duplicate email"""
        url = reverse('teacher-list')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Teacher',
            'email': 'teacher@example.com',  # Already exists
            'phone_number': '9876543210',
            'subject_specialization': 'Physics',
            'employee_id': 'T004',
            'date_of_joining': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_teacher_duplicate_employee_id(self):
        """Test creating teacher with duplicate employee ID"""
        url = reverse('teacher-list')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Teacher',
            'email': 'duplicate@example.com',
            'phone_number': '9876543210',
            'subject_specialization': 'Physics',
            'employee_id': 'T001',  # Already exists
            'date_of_joining': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_teacher_as_admin(self):
        """Test updating teacher as admin"""
        url = reverse('teacher-detail', kwargs={'pk': self.teacher.pk})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
    
    def test_update_teacher_as_teacher_forbidden(self):
        """Test updating teacher as teacher (should be forbidden)"""
        url = reverse('teacher-detail', kwargs={'pk': self.teacher.pk})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, **self.get_auth_header(self.teacher_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_teacher_as_admin(self):
        """Test deleting teacher as admin"""
        url = reverse('teacher-detail', kwargs={'pk': self.teacher.pk})
        response = self.client.delete(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_delete_teacher_as_teacher_forbidden(self):
        """Test deleting teacher as teacher (should be forbidden)"""
        url = reverse('teacher-detail', kwargs={'pk': self.teacher.pk})
        response = self.client.delete(url, **self.get_auth_header(self.teacher_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_teacher_students_endpoint(self):
        """Test teacher's students endpoint"""
        # Create student assigned to teacher
        student_user = User.objects.create_user(
            username='student2@example.com',
            email='student2@example.com',
            password='testpass123'
        )
        
        Student.objects.create(
            user=student_user,
            first_name='Student',
            last_name='Test',
            email='student2@example.com',
            phone_number='1234567890',
            roll_number='S002',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01',
            assigned_teacher=self.teacher
        )
        
        url = reverse('teacher-students', kwargs={'pk': self.teacher.pk})
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_csv_export_as_admin(self):
        """Test CSV export functionality"""
        url = reverse('teacher-export-csv')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="teachers.csv"', response['Content-Disposition'])
    
    def test_unauthorized_access(self):
        """Test unauthorized access to teacher endpoints"""
        url = reverse('teacher-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_serializer_validation_errors(self):
        """Test serializer validation errors"""
        from teachers.serializers import TeacherCreateSerializer
        
        # Test with missing required fields
        serializer = TeacherCreateSerializer(data={})
        self.assertFalse(serializer.is_valid())
        
        # Test with invalid data types
        serializer = TeacherCreateSerializer(data={
            'first_name': 123,  # Should be string
            'email': 'invalid-email',  # Invalid email format
            'date_of_joining': 'invalid-date'  # Invalid date format
        })
        self.assertFalse(serializer.is_valid())
    
    def test_create_teacher_with_invalid_data(self):
        """Test creating teacher with invalid data"""
        url = reverse('teacher-list')
        data = {
            'first_name': '',  # Empty first name
            'email': 'invalid-email',  # Invalid email
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_teacher_with_invalid_data(self):
        """Test updating teacher with invalid data"""
        url = reverse('teacher-detail', kwargs={'pk': self.teacher.pk})
        data = {
            'email': 'invalid-email-format'  # Invalid email
        }
        response = self.client.patch(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)