#!/usr/bin/env python3
"""
清理构建和开发文件的工具
"""

import os
import shutil
import glob

def clean_directory(directory="."):
    """清理指定目录中的构建文件"""

    # 需要清理的文件和目录模式
    patterns = [
        # Python 编译文件
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache",
        "**/.mypy_cache",
        "**/.coverage",
        "**/*.cover",

        # 构建产物
        "build/",
        "dist/",
        "*.egg-info",
        "*.egg",

        # 测试报告
        "htmlcov/",
        ".coverage",
        ".coverage.*",

        # 编辑器缓存
        ".vscode/",
        "**/*.swp",
        "**/*.swo",
        "**/*~",

        # macOS
        "**/.DS_Store",

        # setuptools_scm 生成的文件
        "xpyun_sdk/_version.py",

        # 自动生成的文件
        "**/.eggs/",
    ]

    cleaned_files = []

    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                    cleaned_files.append(f"📁 {match}")
                else:
                    os.remove(match)
                    cleaned_files.append(f"📄 {match}")
            except (OSError, PermissionError):
                print(f"⚠️  跳过: {match}")

    return cleaned_files

def clean_build():
    """执行完整的构建清理"""
    print("🧹 开始清理构建文件...")

    # 执行清理
    cleaned_files = clean_directory()

    if cleaned_files:
        print(f"\n✅ 已清理 {len(cleaned_files)} 个项目:")
        for file_info in cleaned_files[:10]:  # 只显示前10个
            print(f"   {file_info}")

        if len(cleaned_files) > 10:
            print(f"   ... 和另外 {len(cleaned_files) - 10} 个文件")
    else:
        print("✅ 无需清理，项目已很干净")

    print(f"\n🎯 项目状态:")
    print("   - Python 代码文件: 已保留")
    print("   - 配置和文档: 已保留")
    print("   - 测试脚本: 已保留")
    print("   - 构建产物: 已清理")
    print("   - 编译文件: 已清理")

    print("\n🛠️  清理完成！准备进行新的构建")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("用途: 清理Python项目的构建和临时文件")
        print("用法: python clean_build.py")
        print()
        print("会清理的文件包括:")
        print("  - __pycache__ / *.pyc 编译文件")
        print("  - build/ dist/ 构建目录")
        print("  - *.egg-info 包信息文件")
        print("  - .coverage htmlcov 测试覆盖率报告")
        print("  - .pytest_cache .mypy_cache 缓存文件")
        print("  - 其他临时和编辑器文件")
        sys.exit(0)

    clean_build()