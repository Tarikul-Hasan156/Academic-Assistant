#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_assistant.settings')
django.setup()

from routine.models import ClassRoutine, Faculty
from routine.forms import AttendanceForm
from django.contrib.auth.models import User

# Get the user
user = User.objects.get(username='tarikulhasandipu@gmail.com')
faculty = Faculty.objects.get(user=user)

print(f"Faculty: {faculty.name} (ID: {faculty.id})")

# Create form with faculty parameter
form = AttendanceForm(faculty=faculty)

print(f"\nForm class_routine field queryset:")
print(f"Queryset: {form.fields['class_routine'].queryset}")
print(f"Count: {form.fields['class_routine'].queryset.count()}")

for course in form.fields['class_routine'].queryset:
    print(f"  - {course.id}: {course.class_code}")

# Check the widget
print(f"\nForm HTML rendering:")
widget = form.fields['class_routine'].widget
print(f"Widget type: {type(widget)}")

# Render the field
print(f"\nRendered HTML (first 500 chars):")
html = str(form['class_routine'])
print(html[:500])
