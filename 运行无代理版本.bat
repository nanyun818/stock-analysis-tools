@echo off
echo 正在启动Tushare无代理版本...
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

:: 运行无代理版本的Tushare爬虫
python tushare_no_proxy.py

echo.
echo 程序已结束，按任意键退出...
pause >nul