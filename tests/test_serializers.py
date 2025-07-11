"""
Comprehensive serializer tests for School Management System
"""
import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from students.models import Student
from teachers.models import Teacher
from students.serializers import StudentSerializer, StudentCreateSerializer
from teachers.serializers import TeacherSerializer, TeacherCreateSerializer


class StudentSerializerTest(TestCase):
    """Test Student serializers"""
    
    def setUp(self):
        # Create users
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123'
        )
        
        # Create teacher
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Teacher',
            email='teacher@test.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='T001',
            date_of_joining='2024-01-01'
        )
        
        # Create student
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Jane',
            last_name='Student',
            email='student@test.com',
            phone_number='9876543210',
            roll_number='S001',
            class_grade='10',
            date_of_birth='2005-01-01',
            admission_date='2024-01-01',
            assigned_teacher=self.teacher
        )
    
    def test_student_serializer_fields(self):
        """Test StudentSerializer includes all required fields"""
        serializer = StudentSerializer(self.student)
        data = serializer.data
        
        expected_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'roll_number', 'class_grade', 'date_of_birth', 'admission_date',
            'status', 'assigned_teacher', 'assigned_teacher_name',
            'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_student_serializer_assigned_teacher_name(self):
        """Test assigned_teacher_name method in StudentSerializer"""
        serializer = StudentSerializer(self.student)
        data = serializer.data
        
        self.assertEqual(data['assigned_teacher_name'], 'John Teacher')
    
    def test_student_serializer_no_assigned_teacher(self):
        """Test assigned_teacher_name when no teacher assigned"""
        self.student.assigned_teacher = None
        self.student.save()
        
        serializer = StudentSerializer(self.student)
        data = serializer.data
        
        self.assertIsNone(data['assigned_teacher_name'])
    
    def test_student_serializer_read_only_fields(self):
        """Test read-only fields in StudentSerializer"""
        serializer = StudentSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        
        expected_read_only = ['id', 'created_at', 'updated_at']
        for field in expected_read_only:
            self.assertIn(field, read_only_fields)
    
    def test_student_create_serializer_fields(self):
        """Test StudentCreateSerializer includes correct fields"""
        serializer = StudentCreateSerializer()
        fields = serializer.Meta.fields
        
        expected_fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'roll_number', 'class_grade', 'date_of_birth', 'admission_date',
            'status', 'assigned_teacher'
        ]
        
        for field in expected_fields:
            self.assertIn(field, fields)
    
    def test_student_create_serializer_valid_data(self):
        """Test StudentCreateSerializer with valid data"""
        valid_data = {
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'new@test.com',
            'phone_number': '5555555555',
            'roll_number': 'S002',
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01',
            'status': 'active',
            'assigned_teacher': self.teacher.id
        }
        
        serializer = StudentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['first_name'], 'New')
    
    def test_student_create_serializer_email_validation(self):
        """Test email validation in StudentCreateSerializer"""
        # Test duplicate email
        invalid_data = {
            'first_name': 'Duplicate',
            'last_name': 'Student',
            'email': 'student@test.com',  # Already exists
            'phone_number': '5555555555',
            'roll_number': 'S003',
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        }
        
        serializer = StudentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['email'][0]))
    
    def test_student_create_serializer_roll_number_validation(self):
        """Test roll number validation in StudentCreateSerializer"""
        # Test duplicate roll number
        invalid_data = {
            'first_name': 'Duplicate',
            'last_name': 'Student',
            'email': 'duplicate@test.com',
            'phone_number': '5555555555',
            'roll_number': 'S001',  # Already exists
            'class_grade': '9',
            'date_of_birth': '2006-01-01',
            'admission_date': '2024-01-01'
        }
        
        serializer = StudentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('roll_number', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['roll_number'][0]))
    
    def test_student_create_serializer_invalid_data_types(self):
        """Test StudentCreateSerializer with invalid data types"""
        invalid_data = {
            'first_name': 123,  # Should be string
            'email': 'invalid-email',  # Invalid email format
            'roll_number': '',  # Empty string
            'date_of_birth': 'invalid-date',  # Invalid date format
            'admission_date': '2024-99-99'  # Invalid date
        }
        
        serializer = StudentCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('date_of_birth', serializer.errors)


class TeacherSerializerTest(TestCase):
    """Test Teacher serializers"""
    
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Teacher',
            email='teacher@test.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='T001',
            date_of_joining='2024-01-01'
        )
    
    def test_teacher_serializer_fields(self):
        """Test TeacherSerializer includes all required fields"""
        serializer = TeacherSerializer(self.teacher)
        data = serializer.data
        
        expected_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'subject_specialization', 'employee_id', 'date_of_joining',
            'status', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_teacher_serializer_data_accuracy(self):
        """Test TeacherSerializer data accuracy"""
        serializer = TeacherSerializer(self.teacher)
        data = serializer.data
        
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Teacher')
        self.assertEqual(data['email'], 'teacher@test.com')
        self.assertEqual(data['employee_id'], 'T001')
        self.assertEqual(data['subject_specialization'], 'Math')
    
    def test_teacher_serializer_read_only_fields(self):
        """Test read-only fields in TeacherSerializer"""
        serializer = TeacherSerializer()
        read_only_fields = serializer.Meta.read_only_fields
        
        expected_read_only = ['id', 'created_at', 'updated_at']
        for field in expected_read_only:
            self.assertIn(field, read_only_fields)
    
    def test_teacher_create_serializer_fields(self):
        """Test TeacherCreateSerializer includes correct fields"""
        serializer = TeacherCreateSerializer()
        fields = serializer.Meta.fields
        
        expected_fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'subject_specialization', 'employee_id', 'date_of_joining', 'status'
        ]
        
        for field in expected_fields:
            self.assertIn(field, fields)
    
    def test_teacher_create_serializer_valid_data(self):
        """Test TeacherCreateSerializer with valid data"""
        valid_data = {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'new@test.com',
            'phone_number': '5555555555',
            'subject_specialization': 'Science',
            'employee_id': 'T002',
            'date_of_joining': '2024-01-01',
            'status': 'active'
        }
        
        serializer = TeacherCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['first_name'], 'New')
    
    def test_teacher_create_serializer_email_validation(self):
        """Test email validation in TeacherCreateSerializer"""
        # Test duplicate email
        invalid_data = {
            'first_name': 'Duplicate',
            'last_name': 'Teacher',
            'email': 'teacher@test.com',  # Already exists
            'phone_number': '5555555555',
            'subject_specialization': 'Science',
            'employee_id': 'T003',
            'date_of_joining': '2024-01-01'
        }
        
        serializer = TeacherCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['email'][0]))
    
    def test_teacher_create_serializer_employee_id_validation(self):
        """Test employee ID validation in TeacherCreateSerializer"""
        # Test duplicate employee ID
        invalid_data = {
            'first_name': 'Duplicate',
            'last_name': 'Teacher',
            'email': 'duplicate@test.com',
            'phone_number': '5555555555',
            'subject_specialization': 'Science',
            'employee_id': 'T001',  # Already exists
            'date_of_joining': '2024-01-01'
        }
        
        serializer = TeacherCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('employee_id', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['employee_id'][0]))
    
    def test_teacher_create_serializer_invalid_data_types(self):
        """Test TeacherCreateSerializer with invalid data types"""
        invalid_data = {
            'first_name': 123,  # Should be string
            'email': 'invalid-email',  # Invalid email format
            'employee_id': '',  # Empty string
            'date_of_joining': 'invalid-date',  # Invalid date format
            'subject_specialization': None  # None value
        }
        
        serializer = TeacherCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('date_of_joining', serializer.errors)
    
    def test_teacher_create_serializer_missing_required_fields(self):
        """Test TeacherCreateSerializer with missing required fields"""
        incomplete_data = {
            'first_name': 'John'
            # Missing other required fields
        }
        
        serializer = TeacherCreateSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        
        # Check that required fields are in errors
        required_fields = ['last_name', 'email', 'employee_id', 'subject_specialization']
        for field in required_fields:
            self.assertIn(field, serializer.errors)


class SerializerIntegrationTest(TestCase):
    """Test serializer integration with models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='integration@test.com',
            email='integration@test.com',
            password='testpass123'
        )
    
    def test_student_serializer_model_integration(self):
        """Test StudentSerializer with actual model instance"""
        student = Student.objects.create(
            user=self.user,
            first_name='Integration',
            last_name='Test',
            email='integration@test.com',
            phone_number='1111111111',
            roll_number='INT001',
            class_grade='12',
            date_of_birth='2004-01-01',
            admission_date='2024-01-01'
        )
        
        # Test serialization
        serializer = StudentSerializer(student)
        data = serializer.data
        
        self.assertEqual(data['first_name'], 'Integration')
        self.assertEqual(data['roll_number'], 'INT001')
        self.assertEqual(data['class_grade'], '12')
    
    def test_teacher_serializer_model_integration(self):
        """Test TeacherSerializer with actual model instance"""
        teacher = Teacher.objects.create(
            user=self.user,
            first_name='Integration',
            last_name='Teacher',
            email='integration@test.com',
            phone_number='2222222222',
            subject_specialization='Physics',
            employee_id='INT001',
            date_of_joining='2024-01-01'
        )
        
        # Test serialization
        serializer = TeacherSerializer(teacher)
        data = serializer.data
        
        self.assertEqual(data['first_name'], 'Integration')
        self.assertEqual(data['employee_id'], 'INT001')
        self.assertEqual(data['subject_specialization'], 'Physics')
    
    def test_serializer_deserialization_and_save(self):
        """Test serializer deserialization and saving"""
        valid_data = {
            'first_name': 'Deserialized',
            'last_name': 'Student',
            'email': 'deserialized@test.com',
            'phone_number': '3333333333',
            'roll_number': 'DES001',
            'class_grade': '11',
            'date_of_birth': '2005-01-01',
            'admission_date': '2024-01-01',
            'status': 'active'
        }
        
        serializer = StudentCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Verify validated data
        self.assertEqual(serializer.validated_data['first_name'], 'Deserialized')
        self.assertEqual(serializer.validated_data['roll_number'], 'DES001')