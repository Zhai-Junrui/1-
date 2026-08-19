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

## 说明

- 学号唯一，不可重复；总分由「数学 + 语文 + 英语」自动计算。
- 三科成绩限制在 0~150 之间。
- 学生数据为全体教师共享。
- 运行测试：`python manage.py test grades`
