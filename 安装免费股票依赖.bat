@echo off
chcp 65001 >nul
echo ========================================
echo     免费股票可视化工具依赖安装脚本
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境！
    echo 请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境检查通过！
echo.

echo 开始安装依赖包...
echo ========================================

echo 正在安装基础依赖...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
python -m pip install pandas numpy matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo.
echo 正在安装金融数据可视化库...
python -m pip install mplfinance -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo.
echo 正在安装免费股票数据库...
echo 1. 安装AKShare（推荐）...
python -m pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo.
echo 2. 安装AData（备选）...
python -m pip install adata -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo.
echo 3. 下载Ashare（轻量级）...
if not exist "Ashare.py" (
    echo 正在下载Ashare.py...
    python -c "import urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/mpquant/Ashare/main/Ashare.py', 'Ashare.py')"
    if exist "Ashare.py" (
        echo Ashare.py下载成功！
    ) else (
        echo Ashare.py下载失败，请手动下载
        echo 下载地址：https://github.com/mpquant/Ashare
    )
) else (
    echo Ashare.py已存在
)

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.

echo 检查安装结果...
echo 正在验证pandas...
python -c "import pandas; print('pandas版本:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ pandas安装失败
) else (
    echo ✅ pandas安装成功
)

echo 正在验证numpy...
python -c "import numpy; print('numpy版本:', numpy.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ numpy安装失败
) else (
    echo ✅ numpy安装成功
)

echo 正在验证matplotlib...
python -c "import matplotlib; print('matplotlib版本:', matplotlib.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ matplotlib安装失败
) else (
    echo ✅ matplotlib安装成功
)

echo 正在验证mplfinance...
python -c "import mplfinance; print('mplfinance安装成功')" 2>nul
if errorlevel 1 (
    echo ❌ mplfinance安装失败
) else (
    echo ✅ mplfinance安装成功
)

echo 正在验证akshare...
python -c "import akshare; print('akshare版本:', akshare.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ akshare安装失败
) else (
    echo ✅ akshare安装成功
)

echo 正在验证adata...
python -c "import adata; print('adata安装成功')" 2>nul
if errorlevel 1 (
    echo ❌ adata安装失败
) else (
    echo ✅ adata安装成功
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用说明：
echo 1. 运行 "启动免费股票工具.bat" 启动程序
echo 2. 或者直接运行：python free_stock_visualizer.py
echo.
echo 数据源说明：
echo - AKShare：功能最全面，推荐使用
echo - AData：轻量级，专注A股数据
echo - Ashare：单文件库，简单易用
echo.
echo 注意事项：
echo - 所有数据源均为免费，无需API密钥
echo - 数据来源于公开数据，仅供参考
echo - 投资有风险，决策需谨慎
echo.
pause