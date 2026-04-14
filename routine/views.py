from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from .forms import StudentRegisterForm, FacultyRegisterForm, ClassroomBookingForm, AttendanceForm, AttendanceRecordForm, FacultyNoticeForm
from django.contrib import messages
from .models import Student, Faculty, ClassRoutine, Classroom, ClassroomBooking, Attendance, AttendanceRecord, FacultyNotice, StudentNotification
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.cache import cache
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.views.decorators.http import require_http_methods

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user = request.user
    is_student = hasattr(user, 'student')
    is_faculty = hasattr(user, 'faculty')

    students = []
    faculty_list = []
    routines = []

    # --- Search Student Profile ---
    student_id = request.GET.get('student_id', '').strip()
    name = request.GET.get('name', '').strip()
    if student_id or name:
        students = Student.objects.all()
        if student_id:
            students = students.filter(student_id__icontains=student_id)
        if name:
            students = students.filter(student_name__icontains=name)

    # --- Search Faculty Profile ---
    faculty_name = request.GET.get('faculty_name', '').strip()
    faculty_code = request.GET.get('faculty_code', '').strip()
    if faculty_name or faculty_code:
        faculty_list = Faculty.objects.all()
        if faculty_name:
            faculty_list = faculty_list.filter(name__icontains=faculty_name)
        if faculty_code:
            faculty_list = faculty_list.filter(faculty_code__icontains=faculty_code)

    # --- Search Routine ---
    routine_day = request.GET.get('day', '').strip()
    print(routine_day)
    routines = ClassRoutine.objects.all()

    if is_student and student_id and routine_day:
        routines = routines.filter(
            intake=user.student.intake,
            section=user.student.section,
            day_name__iexact=routine_day
        )

    elif is_faculty and faculty_code and routine_day:
        routines = routines.filter(
            faculty_code__iexact=faculty_code,
            day_name__iexact=routine_day
        )
    else:
        routines = []  

    context = {
        'is_student': is_student,
        'is_faculty': is_faculty,
        'student_results': students,
        'faculty_results': faculty_list,
        'routine_results': routines,
    }

    return render(request, 'dashboard.html', context)


def student_register(request):
    if request.method == 'POST':
        name = request.POST['student_name']
        student_id = request.POST['student_id']
        email = request.POST.get('email', '').strip()
        department = request.POST['department']
        intake = request.POST['intake']
        section = request.POST['section']
        blood_group = request.POST['blood_group']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        picture = request.FILES.get('picture')
        
        # Validation
        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'student_register.html')
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'student_register.html')
        elif User.objects.filter(username=student_id).exists():
            messages.error(request, "Student ID already exists.")
            return render(request, 'student_register.html')
        elif Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'student_register.html')
        else:
            # Create user
            user = User.objects.create_user(username=student_id, password=password1, first_name=name, email=email)
            
            # Link with student profile
            Student.objects.create(
                user=user,
                student_name=name,
                student_id=student_id,
                email=email,
                picture=picture,
                department=department,
                intake=int(intake),
                section=section,
                blood_group=blood_group,
            )
            messages.success(request, "Registration successful! You can now login.")
            return redirect('student-login')

    return render(request, 'student_register.html')


def faculty_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        department = request.POST.get('department')
        position = request.POST.get('position')
        office_building = request.POST.get('office_building')
        room_name = request.POST.get('room_name')
        faculty_code = request.POST.get('faculty_code')
        picture = request.FILES.get('picture')
        academic_background = request.POST.get('academic_background')
        experience = request.POST.get('experience')
        biography = request.POST.get('biography')

        # Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'faculty_register.html')

        # Email uniqueness check
        if Faculty.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'faculty_register.html')
        
        # Faculty code uniqueness check
        if Faculty.objects.filter(faculty_code=faculty_code).exists():
            messages.error(request, "Faculty code already exists.")
            return render(request, 'faculty_register.html')

        user = User.objects.create_user(username=email, email=email, password=password1, first_name=name)
        # Save faculty
        faculty = Faculty.objects.create(
            user=user,
            name=name,
            email=email,
            department=department,
            position=position,
            office_building=office_building,
            room_name=room_name,
            faculty_code=faculty_code,
            picture=picture,
            academic_background=academic_background,
            experience=experience,
            biography=biography
        )
        messages.success(request, "Registration successful! You can now login.")
        return redirect('faculty-login')

    return render(request, 'faculty_register.html')



def student_login(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        user = authenticate(username=student_id, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Student ID or password.")
    return render(request, 'student_login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


def faculty_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'faculty_login.html')


@login_required
def student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None

    return render(request, 'student_profile.html', {'student': student})

@login_required
def faculty_profile(request):
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        faculty = None

    return render(request, 'faculty_profile.html', {'faculty': faculty})


# Forgot Password Views
def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def student_forgot_password(request):
    """Step 1: Student enters their email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'student_forgot_password.html')
        
        try:
            # Try to find student by email
            student = Student.objects.get(email=email)
            user = student.user
            
            # Generate OTP
            otp = generate_otp()
            
            # Store OTP in cache for 10 minutes
            cache.set(f'student_otp_{email}', otp, timeout=600)
            
            # Send OTP via email
            try:
                send_mail(
                    'Password Reset OTP - Academic Assistant',
                    f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nIf you did not request this, please ignore this email.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f'OTP sent to {email}. Check your inbox.')
                return redirect('student-verify-otp', email=email)
            except Exception as e:
                messages.error(request, 'Failed to send OTP. Please check your email address and try again.')
                
        except Student.DoesNotExist:
            messages.error(request, 'Email not registered. Please check and try again.')
    
    return render(request, 'student_forgot_password.html')


def student_verify_otp(request, email):
    """Step 2: Student verifies OTP"""
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        
        if not otp:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'student_verify_otp.html', {'email': email})
        
        # Verify OTP
        stored_otp = cache.get(f'student_otp_{email}')
        
        if stored_otp and stored_otp == otp:
            messages.success(request, 'OTP verified successfully!')
            return redirect('student-reset-password', email=email)
        else:
            messages.error(request, 'Invalid or expired OTP.')
    
    return render(request, 'student_verify_otp.html', {'email': email})


def student_reset_password(request, email):
    """Step 3: Student resets password"""
    if request.method == 'POST':
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        
        if not password1 or not password2:
            messages.error(request, 'Please enter both passwords.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            try:
                student = Student.objects.get(email=email)
                user = student.user
                user.set_password(password1)
                user.save()
                
                # Clear cache
                cache.delete(f'student_otp_{email}')
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('student-login')
            except Student.DoesNotExist:
                messages.error(request, 'Student not found.')
    
    return render(request, 'student_reset_password.html', {'email': email})


def faculty_forgot_password(request):
    """Step 1: Faculty enters their email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            # Try to find faculty by email
            faculty = Faculty.objects.get(email=email)
            user = faculty.user
            
            # Generate OTP
            otp = generate_otp()
            
            # Store OTP in cache for 10 minutes
            cache.set(f'faculty_otp_{email}', otp, timeout=600)
            
            # Send OTP via email
            try:
                send_mail(
                    'Password Reset OTP - Academic Assistant',
                    f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f'OTP sent to {email}')
                return redirect('faculty-verify-otp', email=email)
            except Exception as e:
                messages.error(request, 'Failed to send OTP. Please try again.')
                
        except Faculty.DoesNotExist:
            messages.error(request, 'Email not found.')
    
    return render(request, 'faculty_forgot_password.html')


def faculty_verify_otp(request, email):
    """Step 2: Faculty verifies OTP"""
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        
        # Verify OTP
        stored_otp = cache.get(f'faculty_otp_{email}')
        
        if stored_otp and stored_otp == otp:
            messages.success(request, 'OTP verified successfully!')
            return redirect('faculty-reset-password', email=email)
        else:
            messages.error(request, 'Invalid or expired OTP.')
    
    return render(request, 'faculty_verify_otp.html', {'email': email})


def faculty_reset_password(request, email):
    """Step 3: Faculty resets password"""
    if request.method == 'POST':
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        
        if not password1 or not password2:
            messages.error(request, 'Please enter both passwords.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            try:
                faculty = Faculty.objects.get(email=email)
                user = faculty.user
                user.set_password(password1)
                user.save()
                
                # Clear cache
                cache.delete(f'faculty_otp_{email}')
                
                messages.success(request, 'Password reset successfully! You can now login.')
                return redirect('faculty-login')
            except Faculty.DoesNotExist:
                messages.error(request, 'Faculty not found.')
    
    return render(request, 'faculty_reset_password.html', {'email': email})


def student_change_password(request):
    """Change password for logged-in student"""
    # Check if user is logged in, redirect to student login if not
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in first.')
        return redirect('student-login')
    
    # Check if user is a student
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Only students can access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '').strip()
        new_password1 = request.POST.get('new_password1', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()
        
        user = request.user
        
        # Validate current password
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'student_change_password.html')
        
        # Validate new passwords
        if not new_password1 or not new_password2:
            messages.error(request, 'Please enter both new passwords.')
            return render(request, 'student_change_password.html')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'student_change_password.html')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'student_change_password.html')
        
        if current_password == new_password1:
            messages.error(request, 'New password must be different from current password.')
            return render(request, 'student_change_password.html')
        
        # Update password
        user.set_password(new_password1)
        user.save()
        
        # Keep user logged in after password change
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('student-profile')
    
    return render(request, 'student_change_password.html')


def faculty_change_password(request):
    """Change password for logged-in faculty"""
    # Check if user is logged in, redirect to faculty login if not
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in first.')
        return redirect('faculty-login')
    
    # Check if user is faculty
    if not hasattr(request.user, 'faculty'):
        messages.error(request, 'Only faculty members can access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '').strip()
        new_password1 = request.POST.get('new_password1', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()
        
        user = request.user
        
        # Validate current password
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'faculty_change_password.html')
        
        # Validate new passwords
        if not new_password1 or not new_password2:
            messages.error(request, 'Please enter both new passwords.')
            return render(request, 'faculty_change_password.html')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'faculty_change_password.html')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'faculty_change_password.html')
        
        if current_password == new_password1:
            messages.error(request, 'New password must be different from current password.')
            return render(request, 'faculty_change_password.html')
        
        # Update password
        user.set_password(new_password1)
        user.save()
        
        # Keep user logged in after password change
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('faculty-profile')
    
    return render(request, 'faculty_change_password.html')


# ======================== CLASSROOM BOOKING VIEWS ========================

@login_required
def classroom_booking_dashboard(request):
    """Faculty dashboard for booking classrooms"""
    # Check if user is faculty
    if not hasattr(request.user, 'faculty'):
        messages.error(request, 'Only faculty members can access this page.')
        return redirect('dashboard')
    
    faculty = request.user.faculty
    booking_date = request.GET.get('booking_date')
    building = request.GET.get('building')
    
    # Mark bookings as expired if necessary
    _update_expired_bookings()
    
    # Get all classrooms
    all_classrooms = Classroom.objects.all()
    
    if building:
        all_classrooms = all_classrooms.filter(building=building)
    
    # Filter available classrooms based on date
    available_classrooms = all_classrooms
    booked_classrooms = []
    
    if booking_date:
        # Find all classrooms booked on this date
        booked_classroom_ids = ClassroomBooking.objects.filter(
            booking_date=booking_date,
            status__in=['CONFIRMED', 'PENDING', 'ONGOING']
        ).values_list('classroom_id', flat=True).distinct()
        
        booked_classrooms = all_classrooms.filter(id__in=booked_classroom_ids)
        available_classrooms = all_classrooms.exclude(id__in=booked_classroom_ids)
    
    # Get faculty's bookings
    faculty_bookings = ClassroomBooking.objects.filter(faculty=faculty).select_related('classroom').order_by('-booking_date', '-start_time')
    
    # Get faculty's bookings for the selected date if specified
    faculty_bookings_for_date = faculty_bookings
    if booking_date:
        faculty_bookings_for_date = faculty_bookings.filter(booking_date=booking_date)
    
    context = {
        'available_classrooms': available_classrooms,
        'booked_classrooms': booked_classrooms,
        'faculty_bookings': faculty_bookings,
        'faculty_bookings_for_date': faculty_bookings_for_date,
        'booking_date': booking_date,
        'building': building,
        'building_choices': Classroom.BUILDING_CHOICES,
    }
    
    return render(request, 'classroom_booking_dashboard.html', context)


@login_required
def book_classroom(request):
    """View for faculty to book a classroom"""
    # Check if user is faculty
    if not hasattr(request.user, 'faculty'):
        messages.error(request, 'Only faculty members can access this page.')
        return redirect('dashboard')
    
    faculty = request.user.faculty
    classroom_id = request.GET.get('classroom_id')
    booking_date = request.GET.get('booking_date')
    
    if request.method == 'POST':
        form = ClassroomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.faculty = faculty
            booking.status = 'CONFIRMED'
            booking.save()
            messages.success(request, 'Classroom booked successfully!')
            return redirect('classroom-booking-dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Pre-fill form if classroom_id and booking_date are provided
        initial_data = {}
        if classroom_id:
            try:
                initial_data['classroom'] = Classroom.objects.get(id=classroom_id)
            except Classroom.DoesNotExist:
                pass
        if booking_date:
            initial_data['booking_date'] = booking_date
        
        form = ClassroomBookingForm(initial=initial_data)
    
    # Get all classrooms
    classrooms = Classroom.objects.all()
    
    context = {
        'form': form,
        'classrooms': classrooms,
    }
    
    return render(request, 'book_classroom.html', context)


@login_required
def view_classroom_availability(request):
    """API endpoint to check classroom availability"""
    # Check if user is faculty
    if not hasattr(request.user, 'faculty'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    booking_date = request.GET.get('booking_date')
    classroom_id = request.GET.get('classroom_id')
    
    if not booking_date or not classroom_id:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    try:
        classroom = Classroom.objects.get(id=classroom_id)
    except Classroom.DoesNotExist:
        return JsonResponse({'error': 'Classroom not found'}, status=404)
    
    # Mark bookings as expired if necessary
    _update_expired_bookings()
    
    # Get bookings for the selected date
    bookings = ClassroomBooking.objects.filter(
        classroom=classroom,
        booking_date=booking_date,
        status__in=['CONFIRMED', 'PENDING', 'ONGOING']
    ).order_by('start_time')
    
    booked_slots = [
        {
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'faculty': booking.faculty.name,
        }
        for booking in bookings
    ]
    
    return JsonResponse({
        'classroom': {
            'id': classroom.id,
            'name': f"{classroom.building} - Room {classroom.room_number}",
            'capacity': classroom.capacity,
        },
        'date': booking_date,
        'booked_slots': booked_slots,
    })


@login_required
def cancel_classroom_booking(request, booking_id):
    """Cancel a classroom booking"""
    # Check if user is faculty
    if not hasattr(request.user, 'faculty'):
        messages.error(request, 'Only faculty members can access this page.')
        return redirect('dashboard')
    
    faculty = request.user.faculty
    
    try:
        booking = ClassroomBooking.objects.get(id=booking_id, faculty=faculty)
    except ClassroomBooking.DoesNotExist:
        messages.error(request, 'Booking not found or you do not have permission to cancel it.')
        return redirect('classroom-booking-dashboard')
    
    # Don't allow cancellation if already completed
    if booking.status in ['COMPLETED', 'CANCELLED']:
        messages.error(request, f'Cannot cancel a {booking.status.lower()} booking.')
        return redirect('classroom-booking-dashboard')
    
    booking.status = 'CANCELLED'
    booking.save()
    messages.success(request, 'Classroom booking cancelled successfully!')
    return redirect('classroom-booking-dashboard')


@login_required
def my_classroom_bookings(request):
    """View all bookings made by the logged-in faculty"""
    # Check if user is faculty
    if not hasattr(request.user, 'faculty'):
        messages.error(request, 'Only faculty members can access this page.')
        return redirect('dashboard')
    
    faculty = request.user.faculty
    
    # Mark bookings as expired if necessary
    _update_expired_bookings()
    
    # Get faculty's bookings, grouped by status
    bookings = ClassroomBooking.objects.filter(faculty=faculty).select_related('classroom').order_by('-booking_date', '-start_time')
    
    # Separate bookings by status
    upcoming_bookings = bookings.filter(status__in=['CONFIRMED', 'PENDING']).order_by('booking_date', 'start_time')
    completed_bookings = bookings.filter(status='COMPLETED').order_by('-booking_date', '-start_time')
    cancelled_bookings = bookings.filter(status='CANCELLED').order_by('-booking_date', '-start_time')
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    
    return render(request, 'my_classroom_bookings.html', context)


def _update_expired_bookings():
    """Update bookings that have expired (end_time passed)"""
    
    now = timezone.now()
    
    # Get all CONFIRMED bookings
    bookings = ClassroomBooking.objects.filter(
        status__in=['CONFIRMED', 'PENDING', 'ONGOING']
    )
    
    for booking in bookings:
        # Create timezone-aware datetime for booking end
        booking_end_naive = datetime.combine(booking.booking_date, booking.end_time)
        booking_end = timezone.make_aware(booking_end_naive)
        
        # Create timezone-aware datetime for booking start
        booking_start_naive = datetime.combine(booking.booking_date, booking.start_time)
        booking_start = timezone.make_aware(booking_start_naive)
        
        # If end time has passed, mark as COMPLETED
        if now > booking_end and booking.status != 'COMPLETED':
            booking.status = 'COMPLETED'
            booking.save()
        
        # If currently ongoing, mark as ONGOING
        elif booking_start <= now <= booking_end and booking.status != 'ONGOING':
            booking.status = 'ONGOING'
            booking.save()


# ====================== ATTENDANCE VIEWS ======================

@login_required
def attendance_dashboard(request):
    """Faculty dashboard for managing attendance"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, 'Access denied. Only teachers can access this feature.')
        return redirect('home')
    
    # Get faculty's class routines (available courses)
    class_routines = ClassRoutine.objects.filter(faculty=faculty).distinct()
    
    context = {
        'class_routines': class_routines,
        'page_title': 'Attendance Management',
    }
    
    return render(request, 'attendance_dashboard.html', context)


@login_required
def attendance_mark(request):
    """Mark attendance for a class"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, 'Access denied. Only teachers can access this feature.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, faculty=faculty)
        if form.is_valid():
            class_routine = form.cleaned_data['class_routine']
            attendance_date = form.cleaned_data['attendance_date']
            intake = form.cleaned_data['intake']
            section = form.cleaned_data['section']
            num_classes = form.cleaned_data['num_classes']
            
            # Check if attendance already exists for this session
            try:
                attendance = Attendance.objects.get(
                    faculty=faculty,
                    class_routine=class_routine,
                    attendance_date=attendance_date
                )
                messages.info(request, 'Attendance record found. Updating...')
            except Attendance.DoesNotExist:
                attendance = Attendance(
                    faculty=faculty,
                    class_routine=class_routine,
                    attendance_date=attendance_date,
                    intake=intake,
                    section=section,
                    num_classes=num_classes
                )
                attendance.save()
            
            return redirect('attendance-mark-students', attendance_id=attendance.id)
    else:
        form = AttendanceForm(faculty=faculty)
    
    # Get faculty's courses explicitly for template rendering
    faculty_courses = ClassRoutine.objects.filter(faculty=faculty).order_by('class_code')
    
    context = {
        'form': form,
        'faculty_courses': faculty_courses,
        'page_title': 'Mark Attendance - Select Course',
    }
    
    return render(request, 'attendance_mark.html', context)


@login_required
def attendance_mark_students(request, attendance_id):
    """Mark attendance for individual students"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, 'Access denied. Only teachers can access this feature.')
        return redirect('home')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id, faculty=faculty)
    except Attendance.DoesNotExist:
        messages.error(request, 'Attendance record not found.')
        return redirect('attendance-dashboard')
    
    # Check if attendance is locked for modification
    if attendance.status == 'SUBMITTED' and not attendance.can_modify():
        messages.error(request, 'Attendance record cannot be modified. Modification window has expired (2 hours).')
        return redirect('attendance-history')
    
    # Get students in this course/intake/section
    students = Student.objects.filter(
        department=attendance.class_routine.department,
        intake=attendance.intake,
        section=attendance.section
    ).order_by('student_id')
    
    if request.method == 'POST':
        # Process attendance marking
        marked_count = 0
        for student in students:
            is_present = request.POST.get(f'student_{student.id}') == 'on'
            record, created = AttendanceRecord.objects.update_or_create(
                attendance=attendance,
                student=student,
                defaults={'is_present': is_present}
            )
            marked_count += 1
        
        # Update status if first time marking
        if attendance.status == 'DRAFT':
            attendance.status = 'SUBMITTED'
            attendance.submitted_at = timezone.now()
            attendance.save()
        
        messages.success(request, f'Attendance marked for {marked_count} students successfully!')
        return redirect('attendance-history')
    
    # Get existing records
    attendance_records = AttendanceRecord.objects.filter(attendance=attendance)
    record_dict = {record.student_id: record.is_present for record in attendance_records}
    
    # Prepare student data with attendance status
    student_data = []
    for student in students:
        student_data.append({
            'student': student,
            'is_present': record_dict.get(student.id, False),
        })
    
    context = {
        'attendance': attendance,
        'student_data': student_data,
        'total_students': len(students),
        'total_present': sum(1 for s in student_data if s['is_present']),
        'can_modify': attendance.can_modify() if attendance.status == 'SUBMITTED' else True,
        'modification_locked': attendance.is_modification_locked(),
        'page_title': 'Mark Attendance - Students',
    }
    
    return render(request, 'attendance_mark_students.html', context)


@login_required
def attendance_history(request):
    """View attendance history"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, 'Access denied. Only teachers can access this feature.')
        return redirect('home')
    
    # Get all attendance records for this faculty
    attendances = Attendance.objects.filter(faculty=faculty).order_by('-attendance_date')
    
    # Filtering
    class_routine_id = request.GET.get('class_routine')
    if class_routine_id:
        attendances = attendances.filter(class_routine_id=class_routine_id)
    
    date_from = request.GET.get('date_from')
    if date_from:
        attendances = attendances.filter(attendance_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        attendances = attendances.filter(attendance_date__lte=date_to)
    
    # Get class routines for filter dropdown
    class_routines = ClassRoutine.objects.filter(faculty=faculty).distinct()
    
    context = {
        'attendances': attendances,
        'class_routines': class_routines,
        'page_title': 'Attendance History',
    }
    
    return render(request, 'attendance_history.html', context)


@login_required
def attendance_view_details(request, attendance_id):
    """View detailed attendance for a session"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, 'Access denied. Only teachers can access this feature.')
        return redirect('home')
    
    try:
        attendance = Attendance.objects.get(id=attendance_id, faculty=faculty)
    except Attendance.DoesNotExist:
        messages.error(request, 'Attendance record not found.')
        return redirect('attendance-history')
    
    # Get all attendance records for this session
    records = AttendanceRecord.objects.filter(attendance=attendance).select_related('student')
    
    # Calculate individual attendance percentage for each student
    records_with_percentage = []
    for record in records:
        # Get all attendance records for this student in this course/class
        student_total_records = AttendanceRecord.objects.filter(
            attendance__class_routine=attendance.class_routine,
            attendance__faculty=faculty,
            student=record.student
        ).count()
        
        student_present = AttendanceRecord.objects.filter(
            attendance__class_routine=attendance.class_routine,
            attendance__faculty=faculty,
            student=record.student,
            is_present=True
        ).count()
        
        attendance_pct = (student_present / student_total_records * 100) if student_total_records > 0 else 0
        
        records_with_percentage.append({
            'record': record,
            'present_count': student_present,
            'total_count': student_total_records,
            'attendance_percentage': attendance_pct
        })
    
    # Statistics for this session
    total_students = records.count()
    present_count = records.filter(is_present=True).count()
    absent_count = total_students - present_count
    attendance_percentage = (present_count / total_students * 100) if total_students > 0 else 0
    
    context = {
        'attendance': attendance,
        'records': records,
        'records_with_percentage': records_with_percentage,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
        'can_modify': attendance.can_modify() if attendance.status == 'SUBMITTED' else True,
        'modification_locked': attendance.is_modification_locked(),
        'page_title': 'Attendance Details',
    }
    
    return render(request, 'attendance_view_details.html', context)


# Faculty Notice Views

@login_required
def faculty_post_notice(request):
    """Faculty posts important notices (CT date, assignments, etc.)"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = FacultyNoticeForm(request.POST, request.FILES, faculty=faculty)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.faculty = faculty
            notice.save()
            
            # Create notifications for all students in the course
            students = Student.objects.filter(
                intake=notice.class_routine.intake,
                department=notice.class_routine.department,
                section=notice.class_routine.section
            )
            
            for student in students:
                StudentNotification.objects.get_or_create(
                    student=student,
                    notice=notice
                )
            
            messages.success(request, f"Notice '{notice.title}' posted successfully!")
            return redirect('faculty-notices-list')
    else:
        form = FacultyNoticeForm(faculty=faculty)
    
    context = {
        'form': form,
        'page_title': 'Post New Notice',
    }
    return render(request, 'faculty_post_notice.html', context)


@login_required
def faculty_notices_list(request):
    """Faculty view their posted notices"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('dashboard')
    
    notices = FacultyNotice.objects.filter(faculty=faculty).order_by('-posted_date', '-created_at')
    
    # Filter by notice type if provided
    notice_type = request.GET.get('type')
    if notice_type:
        notices = notices.filter(notice_type=notice_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        notices = notices.filter(is_active=True)
    elif status == 'inactive':
        notices = notices.filter(is_active=False)
    
    context = {
        'notices': notices,
        'notice_types': FacultyNotice.NOTICE_TYPE_CHOICES,
        'page_title': 'My Notices',
    }
    return render(request, 'faculty_notices_list.html', context)


@login_required
def faculty_edit_notice(request, notice_id):
    """Faculty edit their notice"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('dashboard')
    
    try:
        notice = FacultyNotice.objects.get(id=notice_id, faculty=faculty)
    except FacultyNotice.DoesNotExist:
        messages.error(request, "Notice not found or you don't have permission to edit it.")
        return redirect('faculty-notices-list')
    
    if request.method == 'POST':
        form = FacultyNoticeForm(request.POST, request.FILES, instance=notice, faculty=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, f"Notice '{notice.title}' updated successfully!")
            return redirect('faculty-notices-list')
    else:
        form = FacultyNoticeForm(instance=notice, faculty=faculty)
    
    context = {
        'form': form,
        'notice': notice,
        'page_title': f'Edit Notice - {notice.title}',
    }
    return render(request, 'faculty_edit_notice.html', context)


@login_required
def faculty_delete_notice(request, notice_id):
    """Faculty delete their notice"""
    try:
        faculty = Faculty.objects.get(user=request.user)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('dashboard')
    
    try:
        notice = FacultyNotice.objects.get(id=notice_id, faculty=faculty)
    except FacultyNotice.DoesNotExist:
        messages.error(request, "Notice not found or you don't have permission to delete it.")
        return redirect('faculty-notices-list')
    
    if request.method == 'POST':
        title = notice.title
        # Also delete associated notifications
        StudentNotification.objects.filter(notice=notice).delete()
        notice.delete()
        messages.success(request, f"Notice '{title}' deleted successfully!")
        return redirect('faculty-notices-list')
    
    context = {
        'notice': notice,
        'page_title': f'Delete Notice - {notice.title}',
    }
    return render(request, 'faculty_delete_notice.html', context)


# Student Notice Views

@login_required
def student_notices(request):
    """Student view important notices"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')
    
    # Get today's date
    today = timezone.now().date()
    
    # Get notices for the student's section
    notices = FacultyNotice.objects.filter(
        class_routine__intake=student.intake,
        class_routine__department=student.department,
        class_routine__section=student.section,
        is_active=True,
        posted_date__gte=today  # Only show notices that haven't expired yet
    ).order_by('-posted_date', '-created_at')
    
    # Get notifications for this student
    notifications = StudentNotification.objects.filter(
        student=student,
        notice__is_active=True,
        notice__posted_date__gte=today  # Only show non-expired notices
    ).select_related('notice').order_by('-created_at')
    
    # Mark unread count
    unread_count = notifications.filter(is_read=False).count()
    
    # Filter by notice type
    notice_type = request.GET.get('type')
    if notice_type:
        notices = notices.filter(notice_type=notice_type)
    
    context = {
        'notices': notices,
        'notifications': notifications,
        'unread_count': unread_count,
        'notice_types': FacultyNotice.NOTICE_TYPE_CHOICES,
        'page_title': 'Important Notices',
    }
    return render(request, 'student_notices.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)
    
    try:
        notification = StudentNotification.objects.get(id=notification_id, student=student)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})
    except StudentNotification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)