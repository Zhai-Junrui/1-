from django.db import models


class Student(models.Model):
    """学生成绩记录，对应原 C++ 程序中的 Student 结构体。"""

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
        ordering = ["student_id"]

    def save(self, *args, **kwargs):
        # 总分由三科成绩自动求和，保持与 C++ 版一致
        self.total = self.math + self.chinese + self.english
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.name}"
