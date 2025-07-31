@echo off
echo 实时股票可视化分析工具 - 依赖安装脚本
echo ======================================
echo.

:: 检查Python是否安装
echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python未安装或未添加到PATH环境变量中！
    echo 请先访问 https://www.python.org/downloads/ 下载并安装Python
    echo 安装时请务必勾选"Add Python to PATH"选项
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b
) else (
    python --version
    echo [成功] Python环境检查通过
)

echo.
echo 正在安装必要的依赖包...
echo ======================================

:: 使用清华镜像源安装依赖
echo 正在安装tushare...
pip install tushare -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 正在安装pandas...
pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 正在安装numpy...
pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 正在安装matplotlib...
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 正在安装mplfinance...
pip install mplfinance -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 依赖安装完成！
echo ======================================
echo.
echo 现在您可以运行"启动股票可视化工具.bat"来启动程序
echo.
echo 如果您还没有Tushare API Token，请先访问以下网址注册获取：
echo https://tushare.pro/register
echo.
echo 按任意键退出...
pause >nul