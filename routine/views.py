from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from .forms import StudentRegisterForm, FacultyRegisterForm
from django.contrib import messages
from .models import Student, Faculty, ClassRoutine
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.cache import cache

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