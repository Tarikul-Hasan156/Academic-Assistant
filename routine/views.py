from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import StudentRegisterForm, FacultyRegisterForm
from django.contrib import messages
from .models import Student, Faculty, ClassRoutine
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'base.html')

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
        routines = []  # prevent showing all routines accidentally if params are incomplete

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
        department = request.POST['department']
        intake = request.POST['intake']
        section = request.POST['section']
        blood_group = request.POST['blood_group']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=student_id).exists():
            messages.error(request, "Student ID already exists.")
        else:
            # Create user
            user = User.objects.create_user(username=student_id, password=password1, first_name=name)
            
            # Link with student profile
            Student.objects.create(
                user=user,
                student_name=name,
                student_id=student_id,
                department=department,
                intake=int(intake),
                section=section,
                blood_group=blood_group,
            )
            messages.success(request, "Registration successful.")
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
            return redirect('faculty_register')

        # Email uniqueness check
        if Faculty.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('faculty_register')

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
        messages.success(request, "Faculty registered successfully!")
        return redirect('faculty-login')

    return render(request, 'faculty_register.html')



def student_login(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        user = authenticate(username=student_id, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
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
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
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