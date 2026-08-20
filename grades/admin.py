from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import SchoolClass, Student, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    search_fields = ("username",)
    filter_horizontal = ("classes",)
    fieldsets = UserAdmin.fieldsets + (
        ("角色与班级", {"fields": ("role", "classes")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("角色与班级", {"fields": ("role", "classes")}),
    )


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "name", "school_class", "math", "chinese", "english", "total")
    search_fields = ("student_id", "name")
    list_filter = ("school_class",)
