from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Student, Faculty, ClassRoutine
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

admin.site.unregister(Group)
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = ('student_name', 'student_id', 'department', 'intake', 'section', 'blood_group')

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Faculty)
class FacultyAdmin(ModelAdmin):
    list_display = ('name', 'department', 'position', 'email', 'faculty_code')  # show in list view
    search_fields = ('name', 'email', 'faculty_code', 'department')             # enable search bar
    list_filter = ('department', 'position', 'office_building')                 # right-side filter
                                            

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'faculty_code', 'department', 'position', 'picture', 'email')
        }),
        ('Office Info', {
            'fields': ('office_building', 'room_name')
        }),
        ('Background', {
            'classes': ('collapse',),  
            'fields': ('academic_background', 'experience', 'biography'),
        }),
    )

@admin.register(ClassRoutine)
class ClassRoutineAdmin(ModelAdmin):
    list_display = ('class_code', 'department', 'intake', 'section', 'faculty_code', 'day_name', 'start_time', 'end_time', 'build_no', 'room_no')
    list_filter = ('department','intake', 'build_no')
    search_fields = ('class_code', 'faculty_code')

