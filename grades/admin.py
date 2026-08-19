from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "name", "math", "chinese", "english", "total")
    search_fields = ("student_id", "name")
    list_filter = ("updated_at",)
