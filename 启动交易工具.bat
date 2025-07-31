@echo off
chcp 65001
echo ========================================
echo 启动股票可视化分析与交易工具
echo ========================================
echo.
echo 正在启动程序...
echo.

cd /d "%~dp0"
python trading_stock_visualizer.py

echo.
echo 程序已退出
pause