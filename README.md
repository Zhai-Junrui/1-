# 学生成绩管理系统

- 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成数据库表
python manage.py migrate

# 3. （可选）创建管理员，用于 /admin 后台
python manage.py createsuperuser

# 4. 启动服务
python manage.py runserver
```

打开 http://127.0.0.1:8000/ ，首次使用请点击「立即注册」创建教师账号。

## 项目结构

```
config/           # 配置
grades/           # 业务
templates/        
manage.py
requirements.txt
```

## 使用流程

1. 教师先注册账号。
2. 管理员登录后在「班级管理」中创建班级，并为每个班级「分配教师」。
3. 教师登录后即可在首页录入、查询、修改、删除本班学生的成绩。

## 说明

- 用户通过 `role` 字段区分身份：`admin` 管理员（可见全部班级、可管理班级）、`teacher` 教师；注册默认是教师。
- 创建管理员：`python manage.py createsuperuser`（自动设为 admin），或在 `/admin` 中修改用户 role。
- 一个班级可有多名教师和多名学生；教师仅能查看 / 操作自己任教班级的学生，管理员可见全部班级。
- 学号全局唯一，不可重复；总分由「数学 + 语文 + 英语」自动计算。
- 三科成绩限制在 0~150 之间。
- 运行测试：`python manage.py test grades`
