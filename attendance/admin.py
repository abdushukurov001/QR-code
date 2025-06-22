from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Class, Subject, Lesson, QRCode, Attendance

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'phone_number', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'full_name', 'phone_number']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'full_name')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'full_name')}),
    )

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['students']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher']
    list_filter = ['teacher']
    search_fields = ['name', 'teacher__full_name']
    filter_horizontal = ['classes']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['subject', 'class_room', 'start_time', 'end_time']
    list_filter = ['subject', 'class_room', 'start_time']
    search_fields = ['subject__name', 'class_room__name']

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'code', 'created_at']
    list_filter = ['lesson__subject', 'lesson__class_room']
    search_fields = ['student__full_name', 'code']
    readonly_fields = ['code']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'status', 'marked_at']
    list_filter = ['status', 'lesson__subject', 'lesson__class_room']
    search_fields = ['student__full_name', 'lesson__subject__name']
