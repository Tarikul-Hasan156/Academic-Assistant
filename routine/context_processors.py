def user_type(request):
    from .models import Student, StudentNotification
    from django.utils import timezone
    
    user = request.user
    is_student = False
    is_faculty = False
    unread_count = 0
    
    if user.is_authenticated:
        is_student = hasattr(user, 'student')
        is_faculty = hasattr(user, 'faculty')
        
        # Get unread notification count for students
        if is_student:
            try:
                student = Student.objects.get(user=user)
                today = timezone.now().date()
                unread_count = StudentNotification.objects.filter(
                    student=student,
                    is_read=False,
                    notice__is_active=True,
                    notice__posted_date__gte=today
                ).count()
            except Student.DoesNotExist:
                pass
    
    return {
        'is_student': is_student,
        'is_faculty': is_faculty,
        'unread_count': unread_count,
    }
