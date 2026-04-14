#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_assistant.settings')
django.setup()

from routine.models import ClassRoutine, Faculty
from django.contrib.auth.models import User

# Get the user
user = User.objects.get(username='tarikulhasandipu@gmail.com')
print(f"User: {user.username}")

# Get their faculty
try:
    faculty = Faculty.objects.get(user=user)
    print(f"Faculty: {faculty.name}")
    print(f"Faculty ID: {faculty.id}")
    print(f"Faculty Code: {faculty.faculty_code}")
    
    # Check courses
    courses = ClassRoutine.objects.filter(faculty=faculty)
    print(f"\nCourses with faculty={faculty} (direct filter): {courses.count()}")
    for c in courses:
        print(f"  - {c.class_code}")
    
    # Try filter by ID
    courses_by_id = ClassRoutine.objects.filter(faculty_id=faculty.id)
    print(f"\nCourses with faculty_id={faculty.id}: {courses_by_id.count()}")
    for c in courses_by_id:
        print(f"  - {c.class_code}")
    
    # Check all ClassRoutine records
    all_courses = ClassRoutine.objects.all()
    print(f"\nTotal courses in database: {all_courses.count()}")
    for c in all_courses:
        print(f"  {c.class_code} -> faculty_id={c.faculty_id}, faculty={c.faculty}")
        
except Faculty.DoesNotExist:
    print("Faculty not found!")
