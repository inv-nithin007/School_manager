import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import UserProfile
from teachers.models import Teacher
from .models import Student


class StudentModelTest(TestCase):
    """Test Student model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='testpass123'
        )
        self.teacher_user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='testpass123'
        )
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
    
    def test_student_creation(self):
        """Test creating a student"""
        student = Student.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='student@example.com',
            phone_number='1234567890',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01'
        )
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(str(student), 'John Doe - S001')
    
    def test_student_with_teacher_assignment(self):
        """Test student with assigned teacher"""
        student = Student.objects.create(
            user=self.user,
            first_name='Jane',
            last_name='Smith',
            email='student@example.com',
            phone_number='1234567890',
            roll_number='S002',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01',
            assigned_teacher=self.teacher
        )
        self.assertEqual(student.assigned_teacher, self.teacher)


class StudentAPITest(APITestCase):
    """Test Student API endpoints"""
    
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
        
        # Create student object
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Student',
            last_name='Test',
            email='student@example.com',
            phone_number='1234567890',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01'
        )
    
    def get_auth_header(self, user):
        """Get authentication header for user"""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_students_as_admin(self):
        """Test listing students as admin"""
        url = reverse('student-list')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_students_as_teacher(self):
        """Test listing students as teacher"""
        url = reverse('student-list')
        response = self.client.get(url, **self.get_auth_header(self.teacher_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_students_as_student(self):
        """Test listing students as student"""
        url = reverse('student-list')
        response = self.client.get(url, **self.get_auth_header(self.student_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_student_as_admin(self):
        """Test creating student as admin"""
        url = reverse('student-list')
        data = {
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'phone_number': '9876543210',
            'roll_number': 'S002',
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'New')
    
    def test_create_student_duplicate_email(self):
        """Test creating student with duplicate email"""
        url = reverse('student-list')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Student',
            'email': 'student@example.com',  # Already exists
            'phone_number': '9876543210',
            'roll_number': 'S003',
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_student_duplicate_roll_number(self):
        """Test creating student with duplicate roll number"""
        url = reverse('student-list')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Student',
            'email': 'duplicate@example.com',
            'phone_number': '9876543210',
            'roll_number': 'S001',  # Already exists
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_student_as_admin(self):
        """Test updating student as admin"""
        url = reverse('student-detail', kwargs={'pk': self.student.pk})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
    
    def test_delete_student_as_admin(self):
        """Test deleting student as admin"""
        url = reverse('student-detail', kwargs={'pk': self.student.pk})
        response = self.client.delete(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_csv_export_as_admin(self):
        """Test CSV export functionality"""
        url = reverse('student-export-csv')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="students.csv"', response['Content-Disposition'])
    
    def test_unauthorized_access(self):
        """Test unauthorized access to student endpoints"""
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_serializer_validation_errors(self):
        """Test serializer validation errors"""
        from students.serializers import StudentCreateSerializer
        
        # Test with missing required fields
        serializer = StudentCreateSerializer(data={})
        self.assertFalse(serializer.is_valid())
        
        # Test with invalid data types
        serializer = StudentCreateSerializer(data={
            'first_name': 123,  # Should be string
            'email': 'invalid-email',  # Invalid email format
            'date_of_birth': 'invalid-date'  # Invalid date format
        })
        self.assertFalse(serializer.is_valid())
    
    def test_create_student_with_invalid_data(self):
        """Test creating student with invalid data"""
        url = reverse('student-list')
        data = {
            'first_name': '',  # Empty first name
            'email': 'invalid-email',  # Invalid email
        }
        response = self.client.post(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_student_with_invalid_data(self):
        """Test updating student with invalid data"""
        url = reverse('student-detail', kwargs={'pk': self.student.pk})
        data = {
            'email': 'invalid-email-format'  # Invalid email
        }
        response = self.client.patch(url, data, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)