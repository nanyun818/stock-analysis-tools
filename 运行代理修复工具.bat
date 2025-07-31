@echo off
echo 正在启动Tushare代理修复工具...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装或未添加到PATH环境变量中！
    echo 请先安装Python并确保将其添加到PATH环境变量。
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b
)

:: 检查tushare模块是否安装
python -c "import tushare" >nul 2>&1
if %errorlevel% neq 0 (
    echo Tushare模块未安装！
    echo 是否要安装Tushare模块？(Y/N)
    set /p install=
    if /i "%install%"=="Y" (
        echo 正在安装Tushare模块...
        pip install tushare pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
    ) else (
        echo 请手动安装Tushare模块后再运行此脚本。
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b
    )
)

:: 检查argparse模块是否安装
python -c "import argparse" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装argparse模块...
    pip install argparse -i https://pypi.tuna.tsinghua.edu.cn/simple
)

:: 运行代理修复工具
echo.
echo 请选择修复方法：
echo 1. 禁用系统代理（推荐）
echo 2. 设置直接连接
echo 3. 修改连接超时时间
echo 4. 尝试使用备用API地址
echo.
set /p method=请输入选项编号(1-4): 

echo.
set /p token=请输入您的Tushare API token（如果没有可以直接回车）: 

if "%token%"=="" (
    python tushare_proxy_fix.py --method %method%
) else (
    python tushare_proxy_fix.py --token %token% --method %method%
)

echo.
echo 程序已结束，按任意键退出...
pause >nul