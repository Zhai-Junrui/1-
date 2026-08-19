from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Avg, Max, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm, TeacherRegistrationForm
from .models import Student


def register_view(request):
    """教师注册：允许多名教师各自创建账号。"""
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
    """成绩仪表盘：统计 + 列表 + 按学号 / 姓名查询。"""
    students = Student.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        # 学号精确 / 包含匹配，姓名不区分大小写
        students = students.filter(
            Q(student_id__icontains=query) | Q(name__icontains=query)
        )
    students = students.order_by("student_id")

    aggregate = Student.objects.aggregate(
        avg_math=Avg("math"),
        avg_chinese=Avg("chinese"),
        avg_english=Avg("english"),
        max_total=Max("total"),
    )
    count = Student.objects.count()

    top_student = None
    if count:
        top_student = Student.objects.order_by("-total", "student_id").first()

    context = {
        "students": students,
        "query": query,
        "count": count,
        "avg_math": aggregate["avg_math"],
        "avg_chinese": aggregate["avg_chinese"],
        "avg_english": aggregate["avg_english"],
        "top_student": top_student,
        "form": StudentForm(),
    }
    return render(request, "grades/dashboard.html", context)


@login_required
def student_add(request):
    """添加成绩（对应 C++ 菜单第 1 项）。"""
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            try:
                student = form.save()
            except IntegrityError:
                messages.error(request, f"学号 {form.cleaned_data['student_id']} 已存在，请勿重复添加。")
            else:
                messages.success(request, f"已添加学生「{student.name}」。")
                return redirect("dashboard")
        else:
            # 取第一条错误提示展示
            first_error = next(iter(form.errors.values()))[0]
            messages.error(request, f"添加失败：{first_error}")
    return redirect("dashboard")


@login_required
def student_edit(request, pk):
    """修改记录（对应 C++ 菜单第 6 项）。"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
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
    """删除记录（对应 C++ 菜单第 3 项）。"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        name = student.name
        student.delete()
        messages.success(request, f"已删除学生「{name}」的记录。")
    return redirect("dashboard")
