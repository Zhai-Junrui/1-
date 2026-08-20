from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Avg, Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm, TeacherRegistrationForm
from .models import SchoolClass, Student, visible_classes

User = get_user_model()


def admin_required(view_func):
    """仅管理员（role=admin 或超级用户）可访问的视图装饰器。"""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin:
            messages.error(request, "仅管理员可执行此操作。")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def register_view(request):
    """教师注册：允许多名教师各自创建账号并选择任教班级。"""
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"欢迎，{user.username}！账号注册成功。")
            return redirect("dashboard")
    else:
        form = TeacherRegistrationForm()
    return render(request, "grades/register.html", {"form": form})


@login_required
def dashboard(request):
    """成绩仪表盘：仅展示当前教师任教班级的学生，支持班级筛选与搜索。"""
    classes = visible_classes(request.user)

    selected_class = request.GET.get("class", "").strip()
    query = request.GET.get("q", "").strip()

    # 校验班级筛选参数：必须是当前用户可见班级之一
    if selected_class and not (
        selected_class.isdigit() and classes.filter(pk=selected_class).exists()
    ):
        selected_class = ""

    base = Student.objects.filter(school_class__in=classes)
    if selected_class:
        base = base.filter(school_class_id=selected_class)

    students = base.select_related("school_class")
    if query:
        students = students.filter(
            Q(student_id__icontains=query) | Q(name__icontains=query)
        )
    students = students.order_by("school_class__name", "student_id")

    aggregate = base.aggregate(
        avg_math=Avg("math"),
        avg_chinese=Avg("chinese"),
        avg_english=Avg("english"),
        max_total=Max("total"),
    )
    count = base.count()
    top_student = base.order_by("-total", "student_id").first() if count else None

    context = {
        "students": students,
        "classes": classes,
        "selected_class": selected_class,
        "query": query,
        "count": count,
        "avg_math": aggregate["avg_math"],
        "avg_chinese": aggregate["avg_chinese"],
        "avg_english": aggregate["avg_english"],
        "top_student": top_student,
    }
    return render(request, "grades/dashboard.html", context)


@login_required
def student_add(request):
    """添加成绩（对应 C++ 菜单第 1 项）。"""
    if request.method == "POST":
        form = StudentForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                student = form.save()
            except IntegrityError:
                messages.error(request, f"学号 {form.cleaned_data['student_id']} 已存在，请勿重复添加。")
            else:
                messages.success(request, f"已添加学生「{student.name}」。")
                return redirect("dashboard")
        else:
            first_error = next(iter(form.errors.values()))[0]
            messages.error(request, f"添加失败：{first_error}")
    return redirect("dashboard")


@login_required
def student_edit(request, pk):
    """修改记录（对应 C++ 菜单第 6 项）。仅限本班学生。"""
    student = get_object_or_404(
        Student.objects.filter(school_class__in=visible_classes(request.user)), pk=pk
    )
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student, user=request.user)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                messages.error(request, f"学号 {form.cleaned_data['student_id']} 已被其他学生使用。")
            else:
                messages.success(request, f"已修改学生「{student.name}」的记录。")
                return redirect("dashboard")
        else:
            first_error = next(iter(form.errors.values()))[0]
            messages.error(request, f"修改失败：{first_error}")
    return redirect("dashboard")


@login_required
def student_delete(request, pk):
    """删除记录（对应 C++ 菜单第 3 项）。仅限本班学生。"""
    student = get_object_or_404(
        Student.objects.filter(school_class__in=visible_classes(request.user)), pk=pk
    )
    if request.method == "POST":
        name = student.name
        student.delete()
        messages.success(request, f"已删除学生「{name}」的记录。")
    return redirect("dashboard")


@admin_required
def class_manage(request):
    """班级管理（仅管理员）：创建 / 删除班级。"""
    if request.method == "POST":
        action = request.POST.get("action", "")
        name = request.POST.get("name", "").strip()
        if action == "create" and name:
            obj, created = SchoolClass.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"班级「{name}」已创建。")
            else:
                messages.error(request, f"班级「{name}」已存在。")
        elif action == "delete":
            cls = get_object_or_404(SchoolClass, pk=request.POST.get("class_id"))
            name = cls.name
            cls.delete()
            messages.success(request, f"班级「{name}」及其学生记录已删除。")
        return redirect("class_manage")

    classes = SchoolClass.objects.annotate(
        student_count=Count("students", distinct=True),
        teacher_count=Count("teachers", distinct=True),
    )
    return render(request, "grades/class_manage.html", {"classes": classes})


@admin_required
def class_teachers(request, pk):
    """分配教师到指定班级（仅管理员）。"""
    cls = get_object_or_404(SchoolClass, pk=pk)

    teachers = User.objects.filter(role=User.Role.TEACHER).order_by("username")

    if request.method == "POST":
        selected_ids = request.POST.getlist("teachers")
        selected = User.objects.filter(pk__in=selected_ids, role=User.Role.TEACHER)
        cls.teachers.set(selected)
        messages.success(request, f"班级「{cls.name}」的教师已更新。")
        return redirect("class_manage")

    class_teacher_ids = list(cls.teachers.values_list("pk", flat=True))
    return render(
        request,
        "grades/class_teachers.html",
        {"cls": cls, "teachers": teachers, "class_teacher_ids": class_teacher_ids},
    )
