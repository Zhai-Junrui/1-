from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Student


class StudentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher1", password="secret123")
        self.client.login(username="teacher1", password="secret123")

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)

    def test_add_student_computes_total(self):
        resp = self.client.post(
            reverse("student_add"),
            {"student_id": 2023001, "name": "张三", "math": 90, "chinese": 85, "english": 88},
        )
        self.assertEqual(resp.status_code, 302)
        s = Student.objects.get(student_id=2023001)
        self.assertEqual(s.total, 263)

    def test_dashboard_renders(self):
        Student.objects.create(student_id=1, name="甲", math=100, chinese=100, english=100)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "学生人数")
        self.assertContains(resp, "甲")

    def test_query_filters_by_name(self):
        Student.objects.create(student_id=1, name="王小明", math=80, chinese=80, english=80)
        Student.objects.create(student_id=2, name="李华", math=70, chinese=70, english=70)
        resp = self.client.get(reverse("dashboard"), {"q": "王小明"})
        self.assertContains(resp, "王小明")
        self.assertNotContains(resp, "李华")

    def test_edit_student(self):
        s = Student.objects.create(student_id=1, name="旧名", math=10, chinese=10, english=10)
        resp = self.client.post(
            reverse("student_edit", args=[s.pk]),
            {"student_id": 1, "name": "新名", "math": 90, "chinese": 80, "english": 70},
        )
        self.assertEqual(resp.status_code, 302)
        s.refresh_from_db()
        self.assertEqual(s.name, "新名")
        self.assertEqual(s.total, 240)

    def test_delete_student(self):
        s = Student.objects.create(student_id=1, name="待删除", math=10, chinese=10, english=10)
        resp = self.client.post(reverse("student_delete", args=[s.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Student.objects.filter(pk=s.pk).exists())

    def test_duplicate_student_id_rejected(self):
        Student.objects.create(student_id=1, name="甲", math=1, chinese=1, english=1)
        resp = self.client.post(
            reverse("student_add"),
            {"student_id": 1, "name": "乙", "math": 2, "chinese": 2, "english": 2},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Student.objects.filter(student_id=1).count(), 1)

    def test_login_page_renders(self):
        self.client.logout()
        resp = self.client.get(reverse("login"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "教师登录")

    def test_register_page_renders(self):
        self.client.logout()
        resp = self.client.get(reverse("register"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "注册教师账号")

    def test_register_teacher(self):
        self.client.logout()
        resp = self.client.post(
            reverse("register"),
            {"username": "teacher2", "password1": "SecretPass123", "password2": "SecretPass123"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="teacher2").exists())
