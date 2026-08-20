from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import SchoolClass, Student

User = get_user_model()


class StudentFlowTests(TestCase):
    def setUp(self):
        self.class_a = SchoolClass.objects.create(name="一班")
        self.class_b = SchoolClass.objects.create(name="二班")
        self.user = User.objects.create_user(username="teacher1", password="secret123")
        self.user.classes.add(self.class_a)
        self.client.login(username="teacher1", password="secret123")

    def make_student(self, school_class, student_id, name="张三", math=90, chinese=85, english=88):
        return Student.objects.create(
            school_class=school_class,
            student_id=student_id,
            name=name,
            math=math,
            chinese=chinese,
            english=english,
        )

    def make_admin(self, username="admin"):
        return User.objects.create_user(
            username=username, password="secret123", role=User.Role.ADMIN
        )

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)

    def test_add_student_computes_total(self):
        resp = self.client.post(
            reverse("student_add"),
            {
                "school_class": self.class_a.pk,
                "student_id": 2023001,
                "name": "张三",
                "math": 90,
                "chinese": 85,
                "english": 88,
            },
        )
        self.assertEqual(resp.status_code, 302)
        s = Student.objects.get(student_id=2023001)
        self.assertEqual(s.school_class, self.class_a)
        self.assertEqual(s.total, 263)

    def test_dashboard_renders(self):
        self.make_student(self.class_a, 1, "甲", 100, 100, 100)
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "学生人数")
        self.assertContains(resp, "甲")

    def test_query_filters_by_name(self):
        self.make_student(self.class_a, 1, "王小明")
        self.make_student(self.class_a, 2, "李华")
        resp = self.client.get(reverse("dashboard"), {"q": "王小明"})
        self.assertContains(resp, "王小明")
        self.assertNotContains(resp, "李华")

    def test_edit_student(self):
        s = self.make_student(self.class_a, 1, "旧名", 10, 10, 10)
        resp = self.client.post(
            reverse("student_edit", args=[s.pk]),
            {
                "school_class": self.class_a.pk,
                "student_id": 1,
                "name": "新名",
                "math": 90,
                "chinese": 80,
                "english": 70,
            },
        )
        self.assertEqual(resp.status_code, 302)
        s.refresh_from_db()
        self.assertEqual(s.name, "新名")
        self.assertEqual(s.total, 240)

    def test_delete_student(self):
        s = self.make_student(self.class_a, 1, "待删除")
        resp = self.client.post(reverse("student_delete", args=[s.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Student.objects.filter(pk=s.pk).exists())

    def test_duplicate_student_id_rejected(self):
        self.make_student(self.class_a, 1, "甲", 1, 1, 1)
        resp = self.client.post(
            reverse("student_add"),
            {
                "school_class": self.class_a.pk,
                "student_id": 1,
                "name": "乙",
                "math": 2,
                "chinese": 2,
                "english": 2,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Student.objects.filter(student_id=1).count(), 1)

    def test_teacher_sees_only_own_class_students(self):
        self.make_student(self.class_a, 1, "甲")
        self.make_student(self.class_b, 2, "乙")
        resp = self.client.get(reverse("dashboard"))
        self.assertContains(resp, "甲")
        self.assertNotContains(resp, "乙")

    def test_cannot_edit_student_in_other_class(self):
        s = self.make_student(self.class_b, 2, "乙")
        resp = self.client.post(
            reverse("student_edit", args=[s.pk]),
            {
                "school_class": self.class_b.pk,
                "student_id": 2,
                "name": "改名",
                "math": 1,
                "chinese": 1,
                "english": 1,
            },
        )
        self.assertEqual(resp.status_code, 404)

    def test_cannot_delete_student_in_other_class(self):
        s = self.make_student(self.class_b, 2, "乙")
        resp = self.client.post(reverse("student_delete", args=[s.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_class_manage_requires_admin(self):
        resp = self.client.get(reverse("class_manage"))
        self.assertEqual(resp.status_code, 302)

    def test_class_teachers_requires_admin(self):
        resp = self.client.get(reverse("class_teachers", args=[self.class_a.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_class_manage_page_renders_for_admin(self):
        self.client.force_login(self.make_admin())
        resp = self.client.get(reverse("class_manage"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "创建班级")

    def test_class_teachers_page_renders_for_admin(self):
        self.client.force_login(self.make_admin())
        resp = self.client.get(reverse("class_teachers", args=[self.class_a.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "分配教师")

    def test_admin_assign_teacher_to_class(self):
        teacher2 = User.objects.create_user(username="teacher2", password="secret123")
        admin = self.make_admin()
        self.client.force_login(admin)
        resp = self.client.post(
            reverse("class_teachers", args=[self.class_a.pk]),
            {"teachers": [teacher2.pk]},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.class_a, teacher2.classes.all())

    def test_admin_sees_all_classes(self):
        self.make_student(self.class_a, 1, "甲")
        self.make_student(self.class_b, 2, "乙")
        self.client.force_login(self.make_admin())
        resp = self.client.get(reverse("dashboard"))
        self.assertContains(resp, "甲")
        self.assertContains(resp, "乙")

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

    def test_register_creates_teacher_role(self):
        self.client.logout()
        resp = self.client.post(
            reverse("register"),
            {"username": "teacher2", "password1": "SecretPass123", "password2": "SecretPass123"},
        )
        self.assertEqual(resp.status_code, 302)
        u = User.objects.get(username="teacher2")
        self.assertEqual(u.role, User.Role.TEACHER)
        self.assertFalse(u.is_admin)

    def test_superuser_created_with_admin_role(self):
        su = User.objects.create_superuser(username="root", password="secret123")
        self.assertEqual(su.role, User.Role.ADMIN)
        self.assertTrue(su.is_admin)
