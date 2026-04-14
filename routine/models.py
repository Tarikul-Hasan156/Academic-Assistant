from django.db import models
from django.contrib.auth.models import User
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
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_routines')
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


class Classroom(models.Model):
    """Model for managing classroom information"""
    BUILDING_CHOICES = [
        ('B-1', 'B-1'),
        ('B-2', 'B-2'),
        ('B-3', 'B-3'),
        ('B-4', 'B-4'),
    ]

    room_number = models.CharField(max_length=20)
    building = models.CharField(max_length=10, choices=BUILDING_CHOICES)
    capacity = models.IntegerField(default=50)
    floor = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Classrooms'
        ordering = ['building', 'room_number']
        unique_together = [['building', 'room_number']]

    def __str__(self):
        return f"{self.building} - Room {self.room_number}"


class ClassroomBooking(models.Model):
    """Model for classroom bookings by faculty"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='bookings')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='classroom_bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    reason = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Classroom Bookings'
        ordering = ['-booking_date', 'start_time']
        unique_together = [['classroom', 'booking_date', 'start_time']]

    def __str__(self):
        return f"{self.classroom} - {self.faculty.name} ({self.booking_date} {self.start_time}-{self.end_time})"

    def is_ongoing(self):
        """Check if booking is currently ongoing"""
        from django.utils import timezone
        from datetime import datetime
        
        now = timezone.now()
        booking_start_naive = datetime.combine(self.booking_date, self.start_time)
        booking_end_naive = datetime.combine(self.booking_date, self.end_time)
        
        booking_start = timezone.make_aware(booking_start_naive)
        booking_end = timezone.make_aware(booking_end_naive)
        
        return booking_start <= now <= booking_end

    def is_expired(self):
        """Check if booking end time has passed"""
        from django.utils import timezone
        from datetime import datetime
        
        now = timezone.now()
        booking_end_naive = datetime.combine(self.booking_date, self.end_time)
        booking_end = timezone.make_aware(booking_end_naive)
        
        return now > booking_end


class Attendance(models.Model):
    """Model for tracking attendance sessions"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='attendance_sessions')
    class_routine = models.ForeignKey(ClassRoutine, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField(help_text="Date for which attendance is being marked")
    intake = models.IntegerField()
    section = models.CharField(max_length=10)
    num_classes = models.IntegerField(default=1, help_text="Number of classes taken on this date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Attendance Sessions'
        ordering = ['-attendance_date', '-created_at']
        unique_together = [['faculty', 'class_routine', 'attendance_date']]

    def __str__(self):
        return f"{self.class_routine.class_code} - {self.attendance_date}"

    def can_modify(self):
        """Check if attendance can still be modified (within 2 hours of submission)"""
        if self.status != 'SUBMITTED' or not self.submitted_at:
            return True
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        two_hours_ago = now - timedelta(hours=2)
        
        return self.submitted_at >= two_hours_ago

    def is_modification_locked(self):
        """Check if modification time has expired"""
        return not self.can_modify()


class AttendanceRecord(models.Model):
    """Model for individual student attendance records"""
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    is_present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Attendance Records'
        ordering = ['student__student_name']
        unique_together = [['attendance', 'student']]

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.student_name} - {status}"

