@echo off
chcp 65001
echo ========================================
echo 股票交易工具依赖安装脚本
echo ========================================
echo.

echo 正在安装基础依赖...
pip install pandas numpy matplotlib tkinter
echo.

echo 正在安装数据源模块...
pip install akshare
echo.

echo 正在安装交易模块...
pip install easytrader
echo.

echo 正在安装量化框架...
pip install easyquant
echo.

echo 正在安装其他依赖...
pip install requests beautifulsoup4 lxml
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 注意事项：
echo 1. 华泰/佣金宝需要安装额外的验证码识别工具
echo 2. 请根据使用的券商配置对应的JSON文件
echo 3. 首次使用建议先用雪球模拟盘测试
echo.
pause