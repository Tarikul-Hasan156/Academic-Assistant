from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Student, Faculty, ClassRoutine, Classroom, ClassroomBooking, Attendance, AttendanceRecord, FacultyNotice, StudentNotification
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
    list_display = ('class_code', 'get_faculty_name', 'department', 'intake', 'section', 'day_name', 'start_time', 'end_time', 'build_no', 'room_no')
    list_filter = ('department', 'intake', 'build_no', 'faculty')
    search_fields = ('class_code', 'faculty__name', 'faculty__faculty_code')
    
    fieldsets = (
        ('Course Information', {
            'fields': ('class_code', 'department', 'intake', 'section')
        }),
        ('Assign Faculty', {
            'fields': ('faculty', 'faculty_code'),
            'description': 'Select a faculty member to assign this course. Faculty code will be auto-filled.'
        }),
        ('Schedule', {
            'fields': ('day_name', 'start_time', 'end_time')
        }),
        ('Location', {
            'fields': ('build_no', 'room_no')
        }),
    )
    
    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else obj.faculty_code
    get_faculty_name.short_description = 'Faculty'
    
    def save_model(self, request, obj, form, change):
        # Auto-fill faculty_code from selected faculty
        if obj.faculty:
            obj.faculty_code = obj.faculty.faculty_code
        super().save_model(request, obj, form, change)


@admin.register(Classroom)
class ClassroomAdmin(ModelAdmin):
    list_display = ('room_number', 'building', 'capacity', 'floor', 'is_available')
    list_filter = ('building', 'is_available')
    search_fields = ('room_number', 'building')
    
    fieldsets = (
        ('Classroom Information', {
            'fields': ('room_number', 'building', 'floor', 'capacity')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
            'description': 'Automatically managed'
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ClassroomBooking)
class ClassroomBookingAdmin(ModelAdmin):
    list_display = ('get_classroom', 'get_faculty', 'booking_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'booking_date', 'classroom__building')
    search_fields = ('classroom__room_number', 'faculty__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('classroom', 'faculty', 'booking_date', 'start_time', 'end_time')
        }),
        ('Additional Information', {
            'fields': ('reason', 'status')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
            'description': 'Automatically managed'
        }),
    )
    
    def get_classroom(self, obj):
        return f"{obj.classroom.building} - Room {obj.classroom.room_number}"
    get_classroom.short_description = 'Classroom'
    
    def get_faculty(self, obj):
        return obj.faculty.name
    get_faculty.short_description = 'Faculty'


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ('get_course', 'attendance_date', 'get_faculty', 'intake', 'section', 'status', 'can_modify_display')
    list_filter = ('status', 'attendance_date', 'faculty')
    search_fields = ('class_routine__course_code', 'faculty__name')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at')
    
    fieldsets = (
        ('Attendance Session', {
            'fields': ('faculty', 'class_routine', 'attendance_date', 'intake', 'section', 'num_classes')
        }),
        ('Status', {
            'fields': ('status', 'submitted_at')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
            'description': 'Automatically managed'
        }),
    )
    
    def get_course(self, obj):
        return f"{obj.class_routine.class_code}"
    get_course.short_description = 'Course'
    
    def get_faculty(self, obj):
        return obj.faculty.name
    get_faculty.short_description = 'Faculty'
    
    def can_modify_display(self, obj):
        if obj.status == 'SUBMITTED':
            return '✓ Yes' if obj.can_modify() else '✗ No'
        return '—'
    can_modify_display.short_description = 'Can Modify'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(ModelAdmin):
    list_display = ('get_student', 'get_attendance', 'is_present_display', 'get_date')
    list_filter = ('is_present', 'attendance__attendance_date')
    search_fields = ('student__student_name', 'student__roll_no', 'attendance__class_routine__class_code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Record Information', {
            'fields': ('attendance', 'student', 'is_present')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
            'description': 'Automatically managed'
        }),
    )
    
    def get_student(self, obj):
        return f"{obj.student.student_name} ({obj.student.roll_no})"
    get_student.short_description = 'Student'
    
    def get_attendance(self, obj):
        return f"{obj.attendance.class_routine.class_code} - {obj.attendance.attendance_date}"
    get_attendance.short_description = 'Attendance Session'
    
    def get_date(self, obj):
        return obj.attendance.attendance_date
    get_date.short_description = 'Date'
    
    def is_present_display(self, obj):
        return '✓ Present' if obj.is_present else '✗ Absent'
    is_present_display.short_description = 'Status'


@admin.register(FacultyNotice)
class FacultyNoticeAdmin(ModelAdmin):
    list_display = ('title', 'get_faculty', 'get_course', 'notice_type', 'posted_date', 'is_active')
    list_filter = ('notice_type', 'posted_date', 'is_active', 'faculty')
    search_fields = ('title', 'faculty__name', 'class_routine__class_code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Notice Information', {
            'fields': ('faculty', 'class_routine', 'title', 'notice_type')
        }),
        ('Content', {
            'fields': ('content', 'document')
        }),
        ('Schedule', {
            'fields': ('posted_date', 'is_active')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
            'description': 'Automatically managed'
        }),
    )
    
    def get_faculty(self, obj):
        return obj.faculty.name
    get_faculty.short_description = 'Faculty'
    
    def get_course(self, obj):
        return obj.class_routine.class_code
    get_course.short_description = 'Course'


@admin.register(StudentNotification)
class StudentNotificationAdmin(ModelAdmin):
    list_display = ('get_student', 'get_notice_title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'notice__notice_type')
    search_fields = ('student__student_name', 'notice__title')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Notification', {
            'fields': ('student', 'notice', 'is_read')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at',),
            'description': 'Automatically managed'
        }),
    )
    
    def get_student(self, obj):
        return obj.student.student_name
    get_student.short_description = 'Student'
    
    def get_notice_title(self, obj):
        return obj.notice.title
    get_notice_title.short_description = 'Notice'

