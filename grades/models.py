from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class SchoolClass(models.Model):
    """班级：一个班级可有多名教师和多名学生。"""

    name = models.CharField(max_length=50, unique=True, verbose_name="班级名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "班级"
        verbose_name_plural = "班级"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserManager(DjangoUserManager):
    """自定义用户管理器：创建超级用户时默认角色为管理员。"""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """自定义用户：通过 role 字段区分管理员与教师。"""

    class Role(models.TextChoices):
        ADMIN = "admin", "管理员"
        TEACHER = "teacher", "教师"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.TEACHER,
        verbose_name="角色",
    )
    classes = models.ManyToManyField(
        "SchoolClass", related_name="teachers", blank=True, verbose_name="任教班级"
    )

    objects = UserManager()

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    @property
    def is_admin(self):
        """管理员（超级用户或角色为 admin）返回 True。"""
        return self.is_superuser or self.role == self.Role.ADMIN

    def __str__(self):
        return self.username


class Student(models.Model):
    """学生成绩记录，对应原 C++ 程序中的 Student 结构体。"""

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name="班级",
    )
    student_id = models.BigIntegerField(unique=True, verbose_name="学号")
    name = models.CharField(max_length=50, verbose_name="姓名")
    math = models.IntegerField(verbose_name="数学")
    chinese = models.IntegerField(verbose_name="语文")
    english = models.IntegerField(verbose_name="英语")
    total = models.IntegerField(verbose_name="总分", blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "学生成绩"
        verbose_name_plural = "学生成绩"
        ordering = ["school_class__name", "student_id"]

    def save(self, *args, **kwargs):
        # 总分由三科成绩自动求和，保持与 C++ 版一致
        self.total = self.math + self.chinese + self.english
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school_class.name} - {self.student_id} - {self.name}"


def visible_classes(user):
    """返回指定用户可见（任教）的班级集合。

    管理员可见全部班级；普通教师仅可见其任教班级；未分配班级的教师返回空集。
    """
    if not user.is_authenticated:
        return SchoolClass.objects.none()
    if user.is_admin:
        return SchoolClass.objects.all()
    return user.classes.all()
