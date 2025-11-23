from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Student(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    DEPARTMENT_CHOICES = [
        ('EEE', 'EEE'),
        ('CSE', 'CSE'),
        ('BBA', 'BBA'),
        ('CIVIL', 'CIVIL'),
        ('Economics', 'Economics'),
        ('English', 'English'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    student_name = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    picture = models.ImageField(upload_to='student_pics/', blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    intake = models.IntegerField(blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.student_name or 'Unnamed'} ({self.student_id or 'No ID'})"
    
    class Meta:
        verbose_name_plural = 'Student'


class Faculty(models.Model):
    POSITION_CHOICES = [
        ('Lecturer', 'Lecturer'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Professor', 'Professor'),
        ('Chairman', 'Chairman'),
        ('Vice-Chancellor', 'Vice-Chancellor'),
        ('Dean', 'Dean'),
    ]

    OFFICE_BUILDING_CHOICES = [
        ('B-1', 'B-1'),
        ('B-2', 'B-2'),
        ('B-3', 'B-3'),
        ('B-4', 'B-4'),
    ]
    DEPARTMENT_CHOICES = [
        ('EEE', 'EEE'),
        ('CSE', 'CSE'),
        ('BBA', 'BBA'),
        ('MATH', 'MATH'),
        ('CIVIL', 'CIVIL'),
        ('Economics', 'Economics'),
        ('English', 'English'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, blank=True, null=True)
    picture = models.ImageField(upload_to='faculty_pics/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    office_building = models.CharField(max_length=100, choices=OFFICE_BUILDING_CHOICES, blank=True, null=True)
    room_name = models.CharField(max_length=100, blank=True, null=True)
    academic_background = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    faculty_code = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name or 'Unnamed'} ({self.faculty_code or 'No Code'})"
    
    # @property
    # def picture_url(self, obj):
    #     if self.picture:
    #         return self.picture.url
    #     return None
    
    class Meta:
        verbose_name_plural = 'Faculty'




class ClassRoutine(models.Model):
   
    DEPARTMENT_CHOICES = [
        ('EEE', 'EEE'),
        ('CSE', 'CSE'),
        ('BBA', 'BBA'),
        ('CIVIL', 'CIVIL'),
        ('Economics', 'Economics'),
        ('English', 'English'),
    ]

    START_TIME_CHOICES = [
        ('08:00 AM', '08:00 AM'),
        ('09:15 AM', '09:15 AM'),
        ('10:30 AM', '10:30 AM'),
        ('11:45 AM', '11:45 AM'),
        ('01:30 PM', '01:30 PM'),
        ('02:45 PM', '02:45 PM'),
        ('04:00 PM', '04:00 PM'),
        ('05:15 PM', '05:15 PM'),
    ]

    END_TIME_CHOICES = [
        ('09:15 AM', '09:15 AM'),
        ('10:30 AM', '10:30 AM'),
        ('11:45 AM', '11:45 AM'),
        ('01:00 PM', '01:00 PM'),
        ('02:45 PM', '02:45 PM'),
        ('04:00 PM', '04:00 PM'),
        ('05:15 PM', '05:15 PM'),
        ('06:30 PM', '06:30 PM'),
    ]

    DAY_CHOICES = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
    ]

    

    BUILDING_CHOICES = [
        ('B-1', 'B-1'),
        ('B-2', 'B-2'),
        ('B-3', 'B-3'),
        ('B-4', 'B-4'),
    ]

    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    intake = models.IntegerField(blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    class_code = models.CharField(max_length=50, blank=True, null=True)
    faculty_code = models.CharField(max_length=20, blank=True, null=True)
    start_time = models.CharField(max_length=20, choices=START_TIME_CHOICES, blank=True, null=True)
    end_time = models.CharField(max_length=20, choices=END_TIME_CHOICES, blank=True, null=True)
    day_name = models.CharField(max_length=20, choices=DAY_CHOICES, blank=True, null=True)
    build_no = models.CharField(max_length=10, choices=BUILDING_CHOICES, blank=True, null=True)
    room_no = models.CharField(max_length=10, blank=True, null=True)

    def clean(self):
      
        if self.faculty_code and not Faculty.objects.filter(faculty_code=self.faculty_code).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError({'faculty_code': 'Faculty code does not exist.'})
        if self.intake and self.section:
            from django.core.exceptions import ValidationError
            if not Student.objects.filter(intake=self.intake, section=self.section).exists():
                raise ValidationError({'section': 'Intake and section combination does not exist in students.'})

    def __str__(self):
        return f"{self.class_code} ({self.day_name} {self.start_time}-{self.end_time})"
    
    class Meta:
        verbose_name_plural = 'Class Routine'

