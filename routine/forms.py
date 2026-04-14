from django import forms
from .models import Student, Faculty, ClassRoutine, ClassroomBooking, Classroom, Attendance, AttendanceRecord
from django.contrib.auth.models import User


class StudentRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:

        
        model = Student
        fields = ['student_name', 'student_id', 'department', 'intake', 'section', 'blood_group']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['student_id'],
            password=self.cleaned_data['password1']
        )
        student.user = user
        if commit:
            student.save()
        return student


class FacultyRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Faculty
        fields = ['name', 'email', 'department', 'position', 'faculty_code']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        faculty = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        faculty.user = user
        if commit:
            faculty.save()
        return faculty


class ClassroomBookingForm(forms.ModelForm):
    """Form for faculty to book classrooms"""
    
    class Meta:
        model = ClassroomBooking
        fields = ['classroom', 'booking_date', 'start_time', 'end_time', 'reason']
        widgets = {
            'classroom': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'booking_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True,
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'required': True,
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'required': True,
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Extra class, Seminar, Lab session',
                'maxlength': '255',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        booking_date = cleaned_data.get('booking_date')
        classroom = cleaned_data.get('classroom')
        
        # Validate end time is after start time
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")
        
        # Check for existing bookings in the same time slot
        if classroom and booking_date and start_time and end_time:
            from django.db.models import Q
            overlapping = ClassroomBooking.objects.filter(
                Q(classroom=classroom) &
                Q(booking_date=booking_date) &
                Q(status__in=['CONFIRMED', 'PENDING', 'ONGOING']) &
                Q(start_time__lt=end_time) &
                Q(end_time__gt=start_time)
            )
            if overlapping.exists():
                raise forms.ValidationError(
                    "This classroom is already booked for the selected time slot."
                )
        
        return cleaned_data


class AttendanceForm(forms.ModelForm):
    """Form for selecting course, intake, section, and number of classes for attendance"""
    
    class Meta:
        model = Attendance
        fields = ['class_routine', 'attendance_date', 'intake', 'section', 'num_classes']
        widgets = {
            'class_routine': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'attendance_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True,
            }),
            'intake': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': True,
                'min': '1',
            }),
            'section': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A, B, C',
                'required': True,
            }),
            'num_classes': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': True,
                'min': '1',
                'value': '1',
            }),
        }
    
    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always filter class_routine to show only the provided faculty's courses
        if faculty:
            self.fields['class_routine'].queryset = ClassRoutine.objects.filter(
                faculty=faculty
            ).order_by('class_code')
        else:
            # Show all if no faculty provided
            self.fields['class_routine'].queryset = ClassRoutine.objects.all().order_by('class_code')


class AttendanceRecordForm(forms.ModelForm):
    """Form for marking individual student attendance"""
    
    class Meta:
        model = AttendanceRecord
        fields = ['is_present']
        widgets = {
            'is_present': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 cursor-pointer',
            }),
        }
