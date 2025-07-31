@echo off
chcp 65001 >nul
echo ========================================
echo     免费股票可视化分析工具
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境！
    echo 请先安装Python或运行 "安装免费股票依赖.bat"
    pause
    exit /b 1
)

echo Python环境检查通过！
echo.

echo 正在检查必要的Python模块...
set "missing_modules="

echo 检查pandas...
python -c "import pandas" 2>nul
if errorlevel 1 (
    echo ❌ pandas未安装
    set "missing_modules=pandas %missing_modules%"
) else (
    echo ✅ pandas已安装
)

echo 检查numpy...
python -c "import numpy" 2>nul
if errorlevel 1 (
    echo ❌ numpy未安装
    set "missing_modules=numpy %missing_modules%"
) else (
    echo ✅ numpy已安装
)

echo 检查matplotlib...
python -c "import matplotlib" 2>nul
if errorlevel 1 (
    echo ❌ matplotlib未安装
    set "missing_modules=matplotlib %missing_modules%"
) else (
    echo ✅ matplotlib已安装
)

echo 检查mplfinance...
python -c "import mplfinance" 2>nul
if errorlevel 1 (
    echo ❌ mplfinance未安装
    set "missing_modules=mplfinance %missing_modules%"
) else (
    echo ✅ mplfinance已安装
)

echo.
echo 检查免费股票数据源...
set "data_sources=0"

echo 检查akshare...
python -c "import akshare" 2>nul
if errorlevel 1 (
    echo ❌ akshare未安装
) else (
    echo ✅ akshare已安装
    set /a "data_sources+=1"
)

echo 检查adata...
python -c "import adata" 2>nul
if errorlevel 1 (
    echo ❌ adata未安装
) else (
    echo ✅ adata已安装
    set /a "data_sources+=1"
)

if exist "Ashare.py" (
    echo ✅ Ashare.py已存在
    set /a "data_sources+=1"
) else (
    echo ❌ Ashare.py不存在
)

echo.
if not "%missing_modules%"=="" (
    echo 发现缺少必要模块：%missing_modules%
    echo 请运行 "安装免费股票依赖.bat" 安装依赖
    pause
    exit /b 1
)

if %data_sources% equ 0 (
    echo 警告：未找到任何股票数据源！
    echo 请运行 "安装免费股票依赖.bat" 安装数据源
    echo 或者手动安装：
    echo   pip install akshare
    echo   pip install adata
    pause
    exit /b 1
)

echo 找到 %data_sources% 个可用数据源
echo.

echo 正在禁用代理设置（避免网络问题）...
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "http_proxy="
set "https_proxy="

echo 代理已禁用
echo.

echo 正在检查程序文件...
if not exist "free_stock_visualizer.py" (
    echo 错误：找不到 free_stock_visualizer.py 文件！
    echo 请确保文件存在于当前目录
    pause
    exit /b 1
)

echo 程序文件检查通过！
echo.

echo ========================================
echo 启动免费股票可视化分析工具...
echo ========================================
echo.
echo 使用说明：
echo 1. 点击"刷新列表"获取股票列表
echo 2. 双击股票代码选择股票
echo 3. 查看K线图和技术指标
echo 4. 参考分析建议进行决策
echo.
echo 数据源说明：
echo - 本工具使用免费数据源
echo - 无需注册或API密钥
echo - 数据仅供参考，投资需谨慎
echo.
echo 正在启动程序...
echo.

python free_stock_visualizer.py

echo.
echo 程序已退出
pause