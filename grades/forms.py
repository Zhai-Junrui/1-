from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student


class TeacherRegistrationForm(UserCreationForm):
    """教师注册表单：只保留用户名与密码。"""

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input w-full"


class StudentForm(forms.ModelForm):
    """新增 / 编辑学生成绩的表单。"""

    class Meta:
        model = Student
        fields = ["student_id", "name", "math", "chinese", "english"]
        widgets = {
            "student_id": forms.NumberInput(attrs={"class": "input w-full"}),
            "name": forms.TextInput(attrs={"class": "input w-full"}),
            "math": forms.NumberInput(attrs={"class": "input w-full", "min": 0, "max": 150}),
            "chinese": forms.NumberInput(attrs={"class": "input w-full", "min": 0, "max": 150}),
            "english": forms.NumberInput(attrs={"class": "input w-full", "min": 0, "max": 150}),
        }

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"]
        if student_id <= 0:
            raise forms.ValidationError("学号必须为正整数")
        return student_id

    def clean(self):
        cleaned = super().clean()
        for field in ("math", "chinese", "english"):
            value = cleaned.get(field)
            if value is not None and not (0 <= value <= 150):
                self.add_error(field, "成绩需在 0 到 150 之间")
        return cleaned
