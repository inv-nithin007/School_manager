import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import UserProfile
from students.models import Student
from teachers.models import Teacher


class CombinedExportCSVTest(APITestCase):
    """Test combined CSV export functionality"""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        UserProfile.objects.create(user=self.admin_user, role='admin')
        
        # Create teacher
        self.teacher_user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='teacherpass123'
        )
        UserProfile.objects.create(user=self.teacher_user, role='teacher')
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Teacher',
            email='teacher@example.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='T001',
            date_of_joining='2024-01-01'
        )
        
        # Create student
        self.student_user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='studentpass123'
        )
        UserProfile.objects.create(user=self.student_user, role='student')
        
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Jane',
            last_name='Student',
            email='student@example.com',
            phone_number='9876543210',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01',
            assigned_teacher=self.teacher
        )
    
    def get_auth_header(self, user):
        """Get authentication header for user"""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_export_all_data_csv(self):
        """Test exporting all data to CSV"""
        url = reverse('export-all-csv')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="school_data_', response['Content-Disposition'])
        
        # Check content contains both student and teacher data
        content = response.content.decode('utf-8')
        self.assertIn('Student', content)
        self.assertIn('Teacher', content)
        self.assertIn('Jane', content)
        self.assertIn('John', content)
    
    def test_export_students_detailed_csv(self):
        """Test exporting detailed student data"""
        url = reverse('export-students-detailed-csv')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="students_detailed_', response['Content-Disposition'])
        
        # Check content contains student details
        content = response.content.decode('utf-8')
        self.assertIn('Jane', content)
        self.assertIn('S001', content)
        self.assertIn('John Teacher', content)  # Assigned teacher name
    
    def test_export_teachers_detailed_csv(self):
        """Test exporting detailed teacher data"""
        url = reverse('export-teachers-detailed-csv')
        response = self.client.get(url, **self.get_auth_header(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="teachers_detailed_', response['Content-Disposition'])
        
        # Check content contains teacher details
        content = response.content.decode('utf-8')
        self.assertIn('John', content)
        self.assertIn('T001', content)
        self.assertIn('Jane Student', content)  # Assigned student name
    
    def test_export_unauthorized(self):
        """Test unauthorized access to export endpoints"""
        urls = [
            reverse('export-all-csv'),
            reverse('export-students-detailed-csv'),
            reverse('export-teachers-detailed-csv')
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_export_as_student(self):
        """Test student can access export endpoints"""
        url = reverse('export-all-csv')
        response = self.client.get(url, **self.get_auth_header(self.student_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_export_as_teacher(self):
        """Test teacher can access export endpoints"""
        url = reverse('export-students-detailed-csv')
        response = self.client.get(url, **self.get_auth_header(self.teacher_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MigrationFunctionalityTest(TestCase):
    """Test migration functionality"""
    
    def test_migration_file_exists(self):
        """Test that migration file exists"""
        import os
        migration_file = '/home/nithinkrishna/school_manager/students/migrations/0002_auto_20250711_0919.py'
        self.assertTrue(os.path.exists(migration_file))
    
    def test_migration_functions_exist(self):
        """Test that migration functions exist"""
        import sys
        import os
        
        # Add the migration directory to the path
        migration_dir = '/home/nithinkrishna/school_manager/students/migrations'
        sys.path.insert(0, migration_dir)
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "migration_module", 
                "/home/nithinkrishna/school_manager/students/migrations/0002_auto_20250711_0919.py"
            )
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            # Check if functions exist
            self.assertTrue(hasattr(migration_module, 'truncate_students_and_teachers'))
            self.assertTrue(hasattr(migration_module, 'reverse_truncate'))
            self.assertTrue(hasattr(migration_module, 'Migration'))
            
        finally:
            sys.path.remove(migration_dir)


class PermissionTest(APITestCase):
    """Test permission classes"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        self.teacher_user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='teacherpass123'
        )
        self.student_user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='studentpass123'
        )
        
        UserProfile.objects.create(user=self.admin_user, role='admin')
        UserProfile.objects.create(user=self.teacher_user, role='teacher')
        UserProfile.objects.create(user=self.student_user, role='student')
    
    def get_auth_header(self, user):
        """Get authentication header for user"""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_admin_permissions(self):
        """Test admin can access all endpoints"""
        from accounts.permissions import IsAdminOrReadOnly
        
        permission = IsAdminOrReadOnly()
        
        # Mock request objects
        class MockRequest:
            def __init__(self, user, method='GET'):
                self.user = user
                self.method = method
        
        # Test admin access
        request = MockRequest(self.admin_user, 'POST')
        self.assertTrue(permission.has_permission(request, None))
        
        # Test teacher read access
        request = MockRequest(self.teacher_user, 'GET')
        self.assertTrue(permission.has_permission(request, None))
        
        # Test teacher write access (should be denied)
        request = MockRequest(self.teacher_user, 'POST')
        self.assertFalse(permission.has_permission(request, None))
    
    def test_student_teacher_admin_permissions(self):
        """Test IsStudentOrTeacherOrAdmin permission"""
        from accounts.permissions import IsStudentOrTeacherOrAdmin
        
        permission = IsStudentOrTeacherOrAdmin()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Test all roles have access
        for user in [self.admin_user, self.teacher_user, self.student_user]:
            request = MockRequest(user)
            self.assertTrue(permission.has_permission(request, None))
    
    def test_teacher_or_admin_permissions(self):
        """Test IsTeacherOrAdmin permission"""
        from accounts.permissions import IsTeacherOrAdmin
        
        permission = IsTeacherOrAdmin()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Test admin access
        request = MockRequest(self.admin_user)
        self.assertTrue(permission.has_permission(request, None))
        
        # Test teacher access
        request = MockRequest(self.teacher_user)
        self.assertTrue(permission.has_permission(request, None))
        
        # Test student access (should be denied)
        request = MockRequest(self.student_user)
        self.assertFalse(permission.has_permission(request, None))


class SerializerTest(TestCase):
    """Test serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='teacherpass123'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='Test',
            last_name='Teacher',
            email='teacher@example.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='T001',
            date_of_joining='2024-01-01'
        )
    
    def test_student_serializer(self):
        """Test student serializer"""
        from students.serializers import StudentSerializer
        
        student = Student.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Student',
            email='test@example.com',
            phone_number='1234567890',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01',
            assigned_teacher=self.teacher
        )
        
        serializer = StudentSerializer(student)
        data = serializer.data
        
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['assigned_teacher_name'], 'Test Teacher')
    
    def test_teacher_serializer(self):
        """Test teacher serializer"""
        from teachers.serializers import TeacherSerializer
        
        serializer = TeacherSerializer(self.teacher)
        data = serializer.data
        
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['employee_id'], 'T001')
    
    def test_student_create_serializer_validation(self):
        """Test student create serializer validation"""
        from students.serializers import StudentCreateSerializer
        
        # Create a student first
        Student.objects.create(
            user=self.user,
            first_name='Existing',
            last_name='Student',
            email='existing@example.com',
            phone_number='1234567890',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01'
        )
        
        # Test duplicate email validation
        serializer = StudentCreateSerializer(data={
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'existing@example.com',  # Duplicate email
            'phone_number': '9876543210',
            'roll_number': 'S002',
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        
        # Test duplicate roll number validation
        serializer = StudentCreateSerializer(data={
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'new@example.com',
            'phone_number': '9876543210',
            'roll_number': 'S001',  # Duplicate roll number
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('roll_number', serializer.errors)
    
    def test_teacher_create_serializer_validation(self):
        """Test teacher create serializer validation"""
        from teachers.serializers import TeacherCreateSerializer
        
        # Test duplicate email validation
        serializer = TeacherCreateSerializer(data={
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'teacher@example.com',  # Duplicate email
            'phone_number': '9876543210',
            'subject_specialization': 'Physics',
            'employee_id': 'T002',
            'date_of_joining': '2024-01-01'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        
        # Test duplicate employee ID validation
        serializer = TeacherCreateSerializer(data={
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@example.com',
            'phone_number': '9876543210',
            'subject_specialization': 'Physics',
            'employee_id': 'T001',  # Duplicate employee ID
            'date_of_joining': '2024-01-01'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('employee_id', serializer.errors)