from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Student, visible_classes

User = get_user_model()


class TeacherRegistrationForm(UserCreationForm):
    """教师注册表单：仅用户名与密码，角色默认为教师，任教班级由管理员统一分配。"""

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input w-full"


class StudentForm(forms.ModelForm):
    """新增 / 编辑学生成绩的表单（班级限定为当前教师可见范围）。"""

    class Meta:
        model = Student
        fields = ["school_class", "student_id", "name", "math", "chinese", "english"]
        widgets = {
            "school_class": forms.Select(attrs={"class": "select w-full"}),
            "student_id": forms.NumberInput(attrs={"class": "input w-full"}),
            "name": forms.TextInput(attrs={"class": "input w-full"}),
            "math": forms.NumberInput(attrs={"class": "input w-full", "min": 0, "max": 150}),
            "chinese": forms.NumberInput(attrs={"class": "input w-full", "min": 0, "max": 150}),
            "english": forms.NumberInput(attrs={"class": "input w-full", "min": 0, "max": 150}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["school_class"].queryset = visible_classes(user)
            self.fields["school_class"].empty_label = None

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
