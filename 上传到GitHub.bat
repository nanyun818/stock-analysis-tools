@echo off
chcp 65001 >nul
echo ========================================
echo         GitHub项目上传工具
echo ========================================
echo.
echo 本工具将帮助您将股票分析工具项目上传到GitHub
echo.

:: 检查Git是否安装
echo [1/6] 检查Git安装状态...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装！
    echo.
    echo 请先安装Git：
    echo 1. 访问 https://git-scm.com/download/win
    echo 2. 下载并安装Git
    echo 3. 重启命令行后再运行此脚本
    echo.
    pause
    exit /b 1
)
echo ✅ Git已安装

:: 检查Git配置
echo.
echo [2/6] 检查Git配置...
git config --global user.name >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git用户信息未配置
    echo.
    set /p username="请输入您的Git用户名: "
    set /p email="请输入您的Git邮箱: "
    
    git config --global user.name "!username!"
    git config --global user.email "!email!"
    echo ✅ Git用户信息配置完成
) else (
    echo ✅ Git用户信息已配置
)

:: 切换到项目目录
echo.
echo [3/6] 切换到项目目录...
cd /d "%~dp0"
echo ✅ 当前目录: %CD%

:: 初始化Git仓库
echo.
echo [4/6] 初始化Git仓库...
if exist ".git" (
    echo ✅ Git仓库已存在
) else (
    git init
    if errorlevel 1 (
        echo ❌ Git仓库初始化失败
        pause
        exit /b 1
    )
    echo ✅ Git仓库初始化成功
)

:: 添加文件到暂存区
echo.
echo [5/6] 添加文件到Git...
git add .
if errorlevel 1 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)
echo ✅ 文件添加成功

:: 检查是否有文件需要提交
git diff --cached --quiet
if not errorlevel 1 (
    echo ⚠️  没有文件需要提交
    echo.
    echo 可能的原因：
    echo 1. 所有文件都已经提交过了
    echo 2. 所有文件都被.gitignore排除了
    echo.
    set /p continue="是否继续？(y/n): "
    if /i not "!continue!"=="y" (
        echo 操作已取消
        pause
        exit /b 0
    )
)

:: 提交文件
echo.
echo 提交文件到本地仓库...
git commit -m "初始提交：股票分析与交易工具集 - 完整的股票数据分析、可视化和程序化交易解决方案"
if errorlevel 1 (
    echo ⚠️  提交可能失败，但这可能是正常的（如果没有新的更改）
else
    echo ✅ 文件提交成功
)

:: 获取GitHub仓库URL
echo.
echo [6/6] 配置GitHub远程仓库...
echo.
echo 请确保您已经在GitHub上创建了仓库！
echo 如果还没有创建，请：
echo 1. 访问 https://github.com
echo 2. 点击右上角的 + 号
echo 3. 选择 New repository
echo 4. 填写仓库名称（建议：stock-analysis-tools）
echo 5. 选择公开或私有
echo 6. 不要勾选任何初始化选项
echo 7. 点击 Create repository
echo.

set /p repo_url="请输入您的GitHub仓库URL（例如：https://github.com/username/stock-analysis-tools.git）: "

if "%repo_url%"=="" (
    echo ❌ 仓库URL不能为空
    pause
    exit /b 1
)

:: 检查是否已经添加了远程仓库
git remote get-url origin >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  远程仓库已存在，正在更新...
    git remote set-url origin "%repo_url%"
) else (
    echo 添加远程仓库...
    git remote add origin "%repo_url%"
)

if errorlevel 1 (
    echo ❌ 添加远程仓库失败
    pause
    exit /b 1
)
echo ✅ 远程仓库配置成功

:: 设置主分支
echo.
echo 设置主分支为main...
git branch -M main
if errorlevel 1 (
    echo ⚠️  设置主分支可能失败，但这通常不影响上传
)

:: 推送到GitHub
echo.
echo 正在推送到GitHub...
echo 注意：如果这是第一次推送，可能需要输入GitHub用户名和密码/Token
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ❌ 推送失败！
    echo.
    echo 可能的原因和解决方案：
    echo 1. 网络连接问题 - 检查网络连接
    echo 2. 认证失败 - GitHub已不支持密码认证，需要使用Personal Access Token
    echo 3. 仓库URL错误 - 检查仓库URL是否正确
    echo 4. 权限问题 - 确保您有仓库的写入权限
    echo.
    echo 设置Personal Access Token的步骤：
    echo 1. 访问 https://github.com/settings/tokens
    echo 2. 点击 Generate new token (classic)
    echo 3. 选择适当的权限（至少需要repo权限）
    echo 4. 生成Token并复制
    echo 5. 在推送时使用Token代替密码
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo           🎉 上传成功！
echo ========================================
echo.
echo ✅ 项目已成功上传到GitHub！
echo.
echo 您的项目地址：
echo %repo_url:~0,-4%
echo.
echo 接下来您可以：
echo 1. 访问GitHub查看您的项目
echo 2. 编辑README.md添加更多说明
echo 3. 设置项目的描述和标签
echo 4. 邀请其他开发者协作
echo.
echo 如需更新项目，请使用以下命令：
echo git add .
echo git commit -m "更新说明"
echo git push
echo.
echo 感谢使用股票分析工具集！
echo.
pause