@echo off
echo 正在启动实时股票可视化分析工具 - 金融小白助手...
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

:: 检查必要的模块是否安装
echo 正在检查必要的模块...

python -c "import tushare" >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少tushare模块！
    set /p install=是否要安装tushare模块？(Y/N): 
    if /i "%install%"=="Y" (
        echo 正在安装tushare模块...
        pip install tushare -i https://pypi.tuna.tsinghua.edu.cn/simple
    ) else (
        echo 请手动安装tushare模块后再运行此脚本。
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b
    )
)

python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少pandas模块！
    set /p install=是否要安装pandas模块？(Y/N): 
    if /i "%install%"=="Y" (
        echo 正在安装pandas模块...
        pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
    ) else (
        echo 请手动安装pandas模块后再运行此脚本。
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b
    )
)

python -c "import numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少numpy模块！
    set /p install=是否要安装numpy模块？(Y/N): 
    if /i "%install%"=="Y" (
        echo 正在安装numpy模块...
        pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
    ) else (
        echo 请手动安装numpy模块后再运行此脚本。
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b
    )
)

python -c "import matplotlib" >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少matplotlib模块！
    set /p install=是否要安装matplotlib模块？(Y/N): 
    if /i "%install%"=="Y" (
        echo 正在安装matplotlib模块...
        pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
    ) else (
        echo 请手动安装matplotlib模块后再运行此脚本。
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b
    )
)

python -c "import mplfinance" >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少mplfinance模块！
    set /p install=是否要安装mplfinance模块？(Y/N): 
    if /i "%install%"=="Y" (
        echo 正在安装mplfinance模块...
        pip install mplfinance -i https://pypi.tuna.tsinghua.edu.cn/simple
    ) else (
        echo 请手动安装mplfinance模块后再运行此脚本。
        echo.
        echo 按任意键退出...
        pause >nul
        exit /b
    )
)

:: 禁用代理设置
echo 正在禁用代理设置...
set http_proxy=
set https_proxy=

:: 运行股票可视化工具
echo 所有依赖已满足，正在启动股票可视化工具...
echo.
echo 如果您还没有Tushare API Token，请先访问 https://tushare.pro/register 注册获取
echo.

python realtime_stock_visualizer.py

echo.
echo 程序已结束，按任意键退出...
pause >nul