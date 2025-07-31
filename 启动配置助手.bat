@echo off
chcp 65001 >nul
echo ========================================
echo           券商配置助手工具
echo ========================================
echo.
echo 正在启动配置助手...
echo.

cd /d "%~dp0"
python config_helper.py

if errorlevel 1 (
    echo.
    echo 启动失败，可能的原因：
    echo 1. Python未安装或未添加到PATH
    echo 2. 缺少必要的Python模块
    echo.
    echo 请先运行 install_trading_deps.bat 安装依赖
    pause
)