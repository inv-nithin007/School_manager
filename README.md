# School Management System API

A Django REST API for managing students and teachers with JWT authentication.

## Features

- JWT Authentication
- Teacher Management (CRUD operations)
- Student Management (CRUD operations)
- Filtering and Search functionality
- Pagination
- Admin interface

## Setup Instructions

### 1. Clone and navigate to the project
```bash
cd school_manager
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser
```bash
python manage.py createsuperuser
```

### 6. Run the server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with username/password
- `POST /api/auth/register/` - Register new user
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Teachers
- `GET /api/teachers/` - List all teachers (with pagination)
- `POST /api/teachers/` - Create new teacher
- `GET /api/teachers/{id}/` - Get teacher details
- `PUT /api/teachers/{id}/` - Update teacher
- `DELETE /api/teachers/{id}/` - Delete teacher
- `GET /api/teachers/{id}/students/` - List students under teacher

### Students
- `GET /api/students/` - List all students (with pagination)
- `POST /api/students/` - Create new student
- `GET /api/students/{id}/` - Get student details
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student

### Filtering and Search
- Add `?search=keyword` to search in names, emails, etc.
- Add `?status=active` to filter by status
- Add `?class_grade=10` to filter students by class
- Add `?assigned_teacher=1` to filter students by teacher

## Testing with Postman

1. **Login**: POST to `/api/auth/login/` with username/password
2. **Get Token**: Copy the access token from response
3. **Set Authorization**: Add `Bearer <token>` to Authorization header
4. **Test APIs**: Use the token to access protected endpoints

## Models

### Teacher
- First Name, Last Name, Email, Phone
- Employee ID, Subject Specialization
- Date of Joining, Status (Active/Inactive)

### Student
- First Name, Last Name, Email, Phone
- Roll Number, Class/Grade, Date of Birth
- Admission Date, Status, Assigned Teacher

## Admin Interface

Access at `/admin/` after creating a superuser to manage data through Django admin.