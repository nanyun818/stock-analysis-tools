@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🚀 股票可视化分析工具
echo ========================================
echo.

echo 📋 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo 📋 检查必要模块...

echo 检查pandas...
python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo ❌ pandas未安装，请运行安装依赖脚本
    pause
    exit /b 1
)
echo ✅ pandas已安装

echo 检查numpy...
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo ❌ numpy未安装，请运行安装依赖脚本
    pause
    exit /b 1
)
echo ✅ numpy已安装

echo 检查matplotlib...
python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo ❌ matplotlib未安装，请运行安装依赖脚本
    pause
    exit /b 1
)
echo ✅ matplotlib已安装

echo 检查mplfinance...
python -c "import mplfinance" >nul 2>&1
if errorlevel 1 (
    echo ❌ mplfinance未安装，请运行安装依赖脚本
    pause
    exit /b 1
)
echo ✅ mplfinance已安装

echo 检查tkinter...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter未安装，请安装完整版Python
    pause
    exit /b 1
)
echo ✅ tkinter已安装

echo 检查PIL...
python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo ❌ Pillow未安装，请运行安装依赖脚本
    pause
    exit /b 1
)
echo ✅ Pillow已安装

echo.
echo 📋 检查数据源...

echo 检查akshare...
python -c "import akshare" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ akshare未安装，建议安装: pip install akshare
) else (
    echo ✅ akshare已安装
)

echo 检查adata...
python -c "import adata" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ adata未安装，可选安装: pip install adata
) else (
    echo ✅ adata已安装
)

echo 检查Ashare...
if exist "Ashare.py" (
    echo ✅ Ashare.py文件存在
) else (
    echo ⚠️ Ashare.py文件不存在，可从GitHub下载
)

echo.
echo 📋 禁用代理设置...
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
echo ✅ 代理设置已禁用

echo.
echo 🚀 启动股票可视化分析工具...
echo.

if exist "beautiful_stock_visualizer.py" (
    python beautiful_stock_visualizer.py
) else (
    echo ❌ 找不到beautiful_stock_visualizer.py文件
    echo 请确保文件在当前目录下
    pause
    exit /b 1
)

echo.
echo 程序已退出
pause