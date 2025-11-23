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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)