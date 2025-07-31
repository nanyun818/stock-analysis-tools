#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub项目上传脚本
自动化上传项目到GitHub仓库
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_git_installed():
    """检查Git是否已安装"""
    success, stdout, stderr = run_command("git --version")
    if success:
        print(f"✅ Git已安装: {stdout.strip()}")
        return True
    else:
        print("❌ Git未安装或未配置到环境变量")
        print("请先安装Git: https://git-scm.com/download/win")
        return False

def setup_git_config():
    """配置Git用户信息"""
    print("\n🔧 配置Git用户信息...")
    
    # 检查是否已配置
    success, stdout, stderr = run_command("git config --global user.name")
    if not success or not stdout.strip():
        name = input("请输入您的用户名: ")
        run_command(f'git config --global user.name "{name}"')
    
    success, stdout, stderr = run_command("git config --global user.email")
    if not success or not stdout.strip():
        email = input("请输入您的邮箱: ")
        run_command(f'git config --global user.email "{email}"')
    
    print("✅ Git用户信息配置完成")

def init_and_upload_repo():
    """初始化并上传仓库"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    repo_url = "https://github.com/nanyun818/stock-analysis-tools.git"
    
    print(f"\n📁 项目目录: {project_dir}")
    print(f"🌐 仓库地址: {repo_url}")
    
    # 检查是否已经是Git仓库
    if os.path.exists(os.path.join(project_dir, '.git')):
        print("📦 检测到已存在的Git仓库")
        choice = input("是否重新初始化? (y/N): ")
        if choice.lower() == 'y':
            import shutil
            shutil.rmtree(os.path.join(project_dir, '.git'))
        else:
            print("使用现有仓库...")
    
    # 初始化Git仓库
    if not os.path.exists(os.path.join(project_dir, '.git')):
        print("\n🚀 初始化Git仓库...")
        success, stdout, stderr = run_command("git init", project_dir)
        if not success:
            print(f"❌ 初始化失败: {stderr}")
            return False
        print("✅ Git仓库初始化成功")
    
    # 添加文件
    print("\n📝 添加文件到Git...")
    success, stdout, stderr = run_command("git add .", project_dir)
    if not success:
        print(f"❌ 添加文件失败: {stderr}")
        return False
    print("✅ 文件添加成功")
    
    # 提交更改
    print("\n💾 提交更改...")
    commit_message = "📈 股票分析与交易工具集 - 初始版本发布\n\n✨ 功能特色:\n- 多数据源支持 (AKShare, Tushare)\n- 实时可视化图表\n- 程序化交易功能\n- 量化策略框架\n- 图形化配置助手\n- 一键部署脚本"
    
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"', project_dir)
    if not success:
        if "nothing to commit" in stderr:
            print("ℹ️ 没有新的更改需要提交")
        else:
            print(f"❌ 提交失败: {stderr}")
            return False
    else:
        print("✅ 更改提交成功")
    
    # 添加远程仓库
    print("\n🔗 配置远程仓库...")
    success, stdout, stderr = run_command("git remote remove origin", project_dir)
    success, stdout, stderr = run_command(f"git remote add origin {repo_url}", project_dir)
    if not success:
        print(f"❌ 添加远程仓库失败: {stderr}")
        return False
    print("✅ 远程仓库配置成功")
    
    # 推送到GitHub
    print("\n🚀 推送到GitHub...")
    print("注意: 如果是第一次推送，可能需要输入GitHub用户名和密码")
    
    # 设置默认分支为main
    run_command("git branch -M main", project_dir)
    
    success, stdout, stderr = run_command("git push -u origin main", project_dir)
    if not success:
        print(f"❌ 推送失败: {stderr}")
        print("\n💡 可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 确认GitHub仓库已创建")
        print("3. 检查GitHub用户名和密码")
        print("4. 如果启用了2FA，需要使用Personal Access Token")
        return False
    
    print("✅ 项目成功上传到GitHub!")
    print(f"\n🌐 访问您的项目: {repo_url.replace('.git', '')}")
    return True

def main():
    """主函数"""
    print("🚀 GitHub项目上传工具")
    print("=" * 50)
    
    # 检查Git安装
    if not check_git_installed():
        input("\n按Enter键退出...")
        return
    
    # 配置Git
    setup_git_config()
    
    # 上传项目
    if init_and_upload_repo():
        print("\n🎉 恭喜! 项目已成功上传到GitHub")
        print("\n📋 后续步骤:")
        print("1. 访问GitHub仓库页面")
        print("2. 编辑仓库描述和标签")
        print("3. 设置仓库为公开(如需要)")
        print("4. 添加更多文档和示例")
    else:
        print("\n❌ 上传过程中出现错误")
        print("请检查错误信息并重试")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()