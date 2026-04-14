from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/student/', views.student_register, name='student-register'),
    path('register/faculty/', views.faculty_register, name='faculty-register'),
    path('login/student/', views.student_login, name='student-login'),
    path('login/faculty/', views.faculty_login, name='faculty-login'),
    path('logout/', views.user_logout, name='logout'),  
    path('student/profile/', views.student_profile, name='student-profile'),
    path('faculty/profile/', views.faculty_profile, name='faculty-profile'),
    path('student/change-password/', views.student_change_password, name='student-change-password'),
    path('faculty/change-password/', views.faculty_change_password, name='faculty-change-password'),
    
    # Forgot Password Routes
    path('student/forgot-password/', views.student_forgot_password, name='student-forgot-password'),
    path('student/verify-otp/<str:email>/', views.student_verify_otp, name='student-verify-otp'),
    path('student/reset-password/<str:email>/', views.student_reset_password, name='student-reset-password'),
    
    path('faculty/forgot-password/', views.faculty_forgot_password, name='faculty-forgot-password'),
    path('faculty/verify-otp/<str:email>/', views.faculty_verify_otp, name='faculty-verify-otp'),
    path('faculty/reset-password/<str:email>/', views.faculty_reset_password, name='faculty-reset-password'),
    
    # Classroom Booking Routes
    path('faculty/classroom-booking/', views.classroom_booking_dashboard, name='classroom-booking-dashboard'),
    path('faculty/book-classroom/', views.book_classroom, name='book-classroom'),
    path('faculty/my-bookings/', views.my_classroom_bookings, name='my-classroom-bookings'),
    path('faculty/cancel-booking/<int:booking_id>/', views.cancel_classroom_booking, name='cancel-classroom-booking'),
    path('api/classroom-availability/', views.view_classroom_availability, name='classroom-availability-api'),
    
    # Attendance Routes
    path('faculty/attendance/', views.attendance_dashboard, name='attendance-dashboard'),
    path('faculty/attendance/mark/', views.attendance_mark, name='attendance-mark'),
    path('faculty/attendance/mark/<int:attendance_id>/', views.attendance_mark_students, name='attendance-mark-students'),
    path('faculty/attendance/history/', views.attendance_history, name='attendance-history'),
    path('faculty/attendance/view/<int:attendance_id>/', views.attendance_view_details, name='attendance-view-details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)