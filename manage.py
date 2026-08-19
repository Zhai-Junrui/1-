#!/usr/bin/env python
"""Django 的管理入口脚本。"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django，请确认已安装并激活了虚拟环境。"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
