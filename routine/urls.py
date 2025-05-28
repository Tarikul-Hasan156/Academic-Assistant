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
    path('faculty/profile/', views.faculty_profile, name='faculty-profile')
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)