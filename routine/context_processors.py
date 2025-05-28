def user_type(request):
    user = request.user
    is_student = False
    is_faculty = False
    if user.is_authenticated:
        is_student = hasattr(user, 'student')
        is_faculty = hasattr(user, 'faculty')
    return {
        'is_student': is_student,
        'is_faculty': is_faculty,
    }
