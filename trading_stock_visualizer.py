#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票可视化分析与交易工具
集成easyquant交易功能，支持华泰、佣金宝、支付宝等券商
基于beautiful_stock_visualizer.py扩展
"""

import sys
import os
import time
import json
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 尝试导入交易相关模块
try:
    import easytrader
    EASYTRADER_AVAILABLE = True
except ImportError:
    EASYTRADER_AVAILABLE = False
    print("警告: easytrader未安装，交易功能将不可用")

try:
    import easyquant
    from easyquant import StrategyTemplate, DefaultLogHandler
    EASYQUANT_AVAILABLE = True
except ImportError:
    EASYQUANT_AVAILABLE = False
    print("警告: easyquant未安装，量化策略功能将不可用")

# 尝试导入数据源
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import adata
    ADATA_AVAILABLE = True
except ImportError:
    ADATA_AVAILABLE = False

class TradingStockVisualizer:
    """股票可视化分析与交易工具主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("股票可视化分析与交易工具")
        self.root.geometry("1400x900")
        
        # 交易相关属性
        self.trader = None
        self.trading_enabled = False
        self.broker_type = None
        self.config_file = None
        
        # 数据相关属性
        self.current_stock_code = None
        self.current_stock_data = None
        self.hot_stocks_data = None
        
        # 创建界面
        self.create_widgets()
        self.show_welcome_message()
        
        # 检查数据源和交易模块可用性
        self.check_modules_availability()
    
    def check_modules_availability(self):
        """检查模块可用性"""
        status_text = "模块状态检查:\n"
        
        # 数据源检查
        if AKSHARE_AVAILABLE:
            status_text += "✓ AKShare数据源可用\n"
        else:
            status_text += "✗ AKShare数据源不可用\n"
            
        if ADATA_AVAILABLE:
            status_text += "✓ AData数据源可用\n"
        else:
            status_text += "✗ AData数据源不可用\n"
        
        # 交易模块检查
        if EASYTRADER_AVAILABLE:
            status_text += "✓ EasyTrader交易模块可用\n"
        else:
            status_text += "✗ EasyTrader交易模块不可用\n"
            
        if EASYQUANT_AVAILABLE:
            status_text += "✓ EasyQuant量化框架可用\n"
        else:
            status_text += "✗ EasyQuant量化框架不可用\n"
        
        print(status_text)
    
    def create_widgets(self):
        """创建主界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧控制面板
        self.create_control_panel(main_frame)
        
        # 创建右侧显示区域
        self.create_display_area(main_frame)
    
    def create_control_panel(self, parent):
        """创建左侧控制面板"""
        control_frame = ttk.Frame(parent, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # 交易配置区域
        self.create_trading_config(control_frame)
        
        # 股票搜索区域
        self.create_stock_search(control_frame)
        
        # 热门股票区域
        self.create_hot_stocks(control_frame)
        
        # 交易操作区域
        self.create_trading_operations(control_frame)
    
    def create_trading_config(self, parent):
        """创建交易配置区域"""
        config_frame = ttk.LabelFrame(parent, text="交易配置", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 券商选择
        ttk.Label(config_frame, text="券商类型:").pack(anchor=tk.W)
        self.broker_var = tk.StringVar(value="华泰证券")
        broker_combo = ttk.Combobox(config_frame, textvariable=self.broker_var, 
                                   values=["华泰证券", "佣金宝", "银河证券", "雪球模拟"], 
                                   state="readonly")
        broker_combo.pack(fill=tk.X, pady=(5, 10))
        
        # 配置文件选择
        ttk.Label(config_frame, text="配置文件:").pack(anchor=tk.W)
        config_file_frame = ttk.Frame(config_frame)
        config_file_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.config_file_var = tk.StringVar()
        config_entry = ttk.Entry(config_file_frame, textvariable=self.config_file_var)
        config_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(config_file_frame, text="选择", 
                  command=self.select_config_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 连接按钮
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.connect_btn = ttk.Button(button_frame, text="连接券商", 
                                     command=self.connect_broker)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.disconnect_btn = ttk.Button(button_frame, text="断开连接", 
                                        command=self.disconnect_broker, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 连接状态显示
        self.status_label = ttk.Label(config_frame, text="状态: 未连接", foreground="red")
        self.status_label.pack(anchor=tk.W, pady=(10, 0))
    
    def create_stock_search(self, parent):
        """创建股票搜索区域"""
        search_frame = ttk.LabelFrame(parent, text="股票搜索", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="股票代码:").pack(anchor=tk.W)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.stock_code_var = tk.StringVar()
        stock_entry = ttk.Entry(search_input_frame, textvariable=self.stock_code_var)
        stock_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        stock_entry.bind('<Return>', lambda e: self.search_stock())
        
        ttk.Button(search_input_frame, text="搜索", 
                  command=self.search_stock).pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_hot_stocks(self, parent):
        """创建热门股票区域"""
        hot_frame = ttk.LabelFrame(parent, text="今日热门股票", padding=10)
        hot_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 刷新按钮
        ttk.Button(hot_frame, text="刷新热门股票", 
                  command=self.refresh_hot_stocks).pack(fill=tk.X, pady=(0, 10))
        
        # 热门股票列表
        columns = ('代码', '名称', '价格', '涨跌幅')
        self.hot_tree = ttk.Treeview(hot_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.hot_tree.heading(col, text=col)
            self.hot_tree.column(col, width=60)
        
        # 滚动条
        hot_scrollbar = ttk.Scrollbar(hot_frame, orient=tk.VERTICAL, command=self.hot_tree.yview)
        self.hot_tree.configure(yscrollcommand=hot_scrollbar.set)
        
        self.hot_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hot_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.hot_tree.bind('<Double-1>', self.on_hot_stock_select)
    
    def create_trading_operations(self, parent):
        """创建交易操作区域"""
        trading_frame = ttk.LabelFrame(parent, text="交易操作", padding=10)
        trading_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 当前股票信息
        self.current_stock_label = ttk.Label(trading_frame, text="当前股票: 未选择")
        self.current_stock_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 交易数量
        ttk.Label(trading_frame, text="交易数量:").pack(anchor=tk.W)
        self.quantity_var = tk.StringVar(value="100")
        ttk.Entry(trading_frame, textvariable=self.quantity_var).pack(fill=tk.X, pady=(5, 10))
        
        # 交易价格
        ttk.Label(trading_frame, text="交易价格:").pack(anchor=tk.W)
        self.price_var = tk.StringVar()
        ttk.Entry(trading_frame, textvariable=self.price_var).pack(fill=tk.X, pady=(5, 10))
        
        # 交易按钮
        button_frame = ttk.Frame(trading_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.buy_btn = ttk.Button(button_frame, text="买入", 
                                 command=self.buy_stock, state=tk.DISABLED)
        self.buy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sell_btn = ttk.Button(button_frame, text="卖出", 
                                  command=self.sell_stock, state=tk.DISABLED)
        self.sell_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 持仓查询按钮
        ttk.Button(trading_frame, text="查询持仓", 
                  command=self.query_positions).pack(fill=tk.X, pady=(10, 0))
    
    def create_display_area(self, parent):
        """创建右侧显示区域"""
        display_frame = ttk.Frame(parent)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建标签页
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 概览标签页
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="概览")
        
        # K线图标签页
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="K线图")
        
        # 技术指标标签页
        self.indicators_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.indicators_frame, text="技术指标")
        
        # 分析报告标签页
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="分析报告")
        
        # 交易记录标签页
        self.trading_log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trading_log_frame, text="交易记录")
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """
【目标】股票可视化分析与交易工具

【功能特点】:
• 实时股票行情获取与分析
• K线图、技术指标可视化
• 智能分析报告生成
• 支持华泰、佣金宝等券商交易
• 量化策略回测与实盘交易

【使用指南】:

第一步：配置交易账户
   • 选择券商类型（华泰、佣金宝等）
   • 配置对应的JSON配置文件
   • 点击"连接券商"建立连接

第二步：选择股票
   • 在搜索框输入股票代码
   • 或从热门股票列表中选择
   • 双击热门股票快速选择

第三步：分析股票
   • 查看K线图和技术指标
   • 阅读智能分析报告
   • 参考买卖建议

第四步：执行交易
   • 设置交易数量和价格
   • 点击买入或卖出按钮
   • 查看交易记录和持仓

【重要提示】:
• 请确保已安装easytrader和easyquant
• 交易前请仔细配置券商信息
• 投资有风险，决策需谨慎
• 建议先使用雪球模拟盘测试

【配置文件说明】:
• 华泰证券: 需要ht.json配置文件
• 佣金宝: 需要yjb.json配置文件
• 银河证券: 需要yh.json配置文件
• 雪球模拟: 需要xq.json配置文件
"""
        
        # 在概览标签页显示欢迎信息
        welcome_label = ttk.Label(self.overview_frame, text=welcome_text, 
                                 justify=tk.LEFT, font=('Microsoft YaHei', 10))
        welcome_label.pack(padx=20, pady=20, anchor=tk.NW)
    
    def select_config_file(self):
        """选择配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择券商配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.config_file_var.set(file_path)
            self.config_file = file_path
    
    def connect_broker(self):
        """连接券商"""
        if not EASYTRADER_AVAILABLE:
            messagebox.showerror("错误", "easytrader模块未安装，无法连接券商")
            return
        
        if not self.config_file:
            messagebox.showerror("错误", "请先选择配置文件")
            return
        
        try:
            broker_type = self.broker_var.get()
            
            # 根据券商类型选择对应的连接方式
            if broker_type == "华泰证券":
                self.trader = easytrader.use('ht')
            elif broker_type == "佣金宝":
                self.trader = easytrader.use('yjb')
            elif broker_type == "银河证券":
                self.trader = easytrader.use('yh')
            elif broker_type == "雪球模拟":
                self.trader = easytrader.use('xq')
            else:
                messagebox.showerror("错误", "不支持的券商类型")
                return
            
            # 准备配置
            self.trader.prepare(self.config_file)
            
            self.trading_enabled = True
            self.broker_type = broker_type
            
            # 更新界面状态
            self.status_label.config(text=f"状态: 已连接 ({broker_type})", foreground="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.buy_btn.config(state=tk.NORMAL)
            self.sell_btn.config(state=tk.NORMAL)
            
            messagebox.showinfo("成功", f"已成功连接到{broker_type}")
            
        except Exception as e:
            messagebox.showerror("连接失败", f"连接券商失败: {str(e)}")
    
    def disconnect_broker(self):
        """断开券商连接"""
        self.trader = None
        self.trading_enabled = False
        self.broker_type = None
        
        # 更新界面状态
        self.status_label.config(text="状态: 未连接", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.buy_btn.config(state=tk.DISABLED)
        self.sell_btn.config(state=tk.DISABLED)
        
        messagebox.showinfo("提示", "已断开券商连接")
    
    def search_stock(self):
        """搜索股票"""
        stock_code = self.stock_code_var.get().strip()
        if not stock_code:
            messagebox.showwarning("警告", "请输入股票代码")
            return
        
        self.load_stock_data(stock_code)
    
    def load_stock_data(self, stock_code):
        """加载股票数据"""
        try:
            self.current_stock_code = stock_code
            
            # 获取股票基本信息和实时数据
            if AKSHARE_AVAILABLE:
                # 获取实时行情
                realtime_data = ak.stock_zh_a_spot_em()
                stock_info = realtime_data[realtime_data['代码'] == stock_code]
                
                if not stock_info.empty:
                    stock_name = stock_info.iloc[0]['名称']
                    current_price = stock_info.iloc[0]['最新价']
                    
                    self.current_stock_label.config(text=f"当前股票: {stock_code} {stock_name}")
                    self.price_var.set(str(current_price))
                    
                    # 获取历史数据
                    end_date = datetime.now().strftime('%Y%m%d')
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                    
                    hist_data = ak.stock_zh_a_hist(symbol=stock_code, 
                                                  start_date=start_date, 
                                                  end_date=end_date)
                    
                    self.current_stock_data = hist_data
                    
                    # 更新显示
                    self.update_chart_display()
                    self.update_indicators_display()
                    self.update_analysis_display()
                    
                else:
                    messagebox.showerror("错误", "未找到该股票代码")
            else:
                messagebox.showerror("错误", "数据源不可用")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载股票数据失败: {str(e)}")
    
    def refresh_hot_stocks(self):
        """刷新热门股票"""
        try:
            if AKSHARE_AVAILABLE:
                # 获取涨跌幅排行
                hot_data = ak.stock_zh_a_spot_em()
                hot_data = hot_data.sort_values('涨跌幅', ascending=False).head(20)
                
                # 清空现有数据
                for item in self.hot_tree.get_children():
                    self.hot_tree.delete(item)
                
                # 添加新数据
                for _, row in hot_data.iterrows():
                    self.hot_tree.insert('', 'end', values=(
                        row['代码'], row['名称'], 
                        f"{row['最新价']:.2f}", f"{row['涨跌幅']:.2f}%"
                    ))
                
                self.hot_stocks_data = hot_data
                
            else:
                messagebox.showwarning("警告", "数据源不可用，无法获取热门股票")
                
        except Exception as e:
            messagebox.showerror("错误", f"获取热门股票失败: {str(e)}")
    
    def on_hot_stock_select(self, event):
        """热门股票选择事件"""
        selection = self.hot_tree.selection()
        if selection:
            item = self.hot_tree.item(selection[0])
            stock_code = item['values'][0]
            self.stock_code_var.set(stock_code)
            self.load_stock_data(stock_code)
    
    def update_chart_display(self):
        """更新K线图显示"""
        if self.current_stock_data is None:
            return
        
        # 清空现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # 创建图表
        fig = Figure(figsize=(12, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        # 绘制K线图
        data = self.current_stock_data.tail(60)  # 显示最近60天
        
        for i, (_, row) in enumerate(data.iterrows()):
            open_price = row['开盘']
            close_price = row['收盘']
            high_price = row['最高']
            low_price = row['最低']
            
            # 确定颜色
            color = 'red' if close_price >= open_price else 'green'
            
            # 绘制影线
            ax.plot([i, i], [low_price, high_price], color='black', linewidth=0.5)
            
            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            rect = Rectangle((i-0.3, bottom), 0.6, height, 
                           facecolor=color, alpha=0.7)
            ax.add_patch(rect)
        
        ax.set_title(f"{self.current_stock_code} K线图")
        ax.set_xlabel("时间")
        ax.set_ylabel("价格")
        ax.grid(True, alpha=0.3)
        
        # 嵌入到tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_indicators_display(self):
        """更新技术指标显示"""
        if self.current_stock_data is None:
            return
        
        # 清空现有内容
        for widget in self.indicators_frame.winfo_children():
            widget.destroy()
        
        # 计算技术指标
        data = self.current_stock_data.copy()
        
        # 计算移动平均线
        data['MA5'] = data['收盘'].rolling(window=5).mean()
        data['MA10'] = data['收盘'].rolling(window=10).mean()
        data['MA20'] = data['收盘'].rolling(window=20).mean()
        
        # 计算RSI
        delta = data['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # 显示最新指标值
        latest = data.iloc[-1]
        
        indicators_text = f"""
技术指标分析 ({self.current_stock_code})

移动平均线:
• MA5:  {latest['MA5']:.2f}
• MA10: {latest['MA10']:.2f}
• MA20: {latest['MA20']:.2f}

相对强弱指标:
• RSI:  {latest['RSI']:.2f}

当前价格: {latest['收盘']:.2f}
涨跌幅: {((latest['收盘'] - latest['开盘']) / latest['开盘'] * 100):.2f}%
"""
        
        ttk.Label(self.indicators_frame, text=indicators_text, 
                 justify=tk.LEFT, font=('Microsoft YaHei', 11)).pack(padx=20, pady=20, anchor=tk.NW)
    
    def update_analysis_display(self):
        """更新分析报告显示"""
        if self.current_stock_data is None:
            return
        
        # 清空现有内容
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
        
        # 生成分析报告
        data = self.current_stock_data
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # 计算一些基本指标
        price_change = latest['收盘'] - prev['收盘']
        price_change_pct = (price_change / prev['收盘']) * 100
        
        # 计算波动率
        volatility = data['收盘'].pct_change().std() * 100
        
        # 生成建议
        if price_change_pct > 2:
            suggestion = "【强烈看涨】建议适量买入"
        elif price_change_pct > 0:
            suggestion = "【温和看涨】可考虑买入"
        elif price_change_pct > -2:
            suggestion = "【震荡整理】建议观望"
        else:
            suggestion = "【看跌趋势】建议谨慎"
        
        analysis_text = f"""
智能分析报告 ({self.current_stock_code})

【基本面分析】:
• 当前价格: {latest['收盘']:.2f} 元
• 价格变动: {price_change:+.2f} 元 ({price_change_pct:+.2f}%)
• 成交量: {latest['成交量']:,.0f} 手
• 换手率: {latest['换手率']:.2f}%

【技术面分析】:
• 波动率: {volatility:.2f}%
• 最高价: {latest['最高']:.2f} 元
• 最低价: {latest['最低']:.2f} 元
• 振幅: {((latest['最高'] - latest['最低']) / prev['收盘'] * 100):.2f}%

【投资建议】:
{suggestion}

【风险提示】:
• 股市有风险，投资需谨慎
• 本分析仅供参考，不构成投资建议
• 请结合自身风险承受能力做出投资决策
"""
        
        ttk.Label(self.analysis_frame, text=analysis_text, 
                 justify=tk.LEFT, font=('Microsoft YaHei', 11)).pack(padx=20, pady=20, anchor=tk.NW)
    
    def buy_stock(self):
        """买入股票"""
        if not self.trading_enabled:
            messagebox.showerror("错误", "请先连接券商")
            return
        
        if not self.current_stock_code:
            messagebox.showerror("错误", "请先选择股票")
            return
        
        try:
            stock_code = self.current_stock_code
            quantity = int(self.quantity_var.get())
            price = float(self.price_var.get())
            
            # 确认交易
            result = messagebox.askyesno("确认交易", 
                                       f"确认买入 {stock_code}\n数量: {quantity} 股\n价格: {price} 元")
            
            if result:
                # 执行买入
                order_result = self.trader.buy(stock_code, price=price, amount=quantity)
                
                # 记录交易
                self.log_trade("买入", stock_code, quantity, price, order_result)
                
                messagebox.showinfo("交易成功", f"买入订单已提交\n订单结果: {order_result}")
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量和价格")
        except Exception as e:
            messagebox.showerror("交易失败", f"买入失败: {str(e)}")
    
    def sell_stock(self):
        """卖出股票"""
        if not self.trading_enabled:
            messagebox.showerror("错误", "请先连接券商")
            return
        
        if not self.current_stock_code:
            messagebox.showerror("错误", "请先选择股票")
            return
        
        try:
            stock_code = self.current_stock_code
            quantity = int(self.quantity_var.get())
            price = float(self.price_var.get())
            
            # 确认交易
            result = messagebox.askyesno("确认交易", 
                                       f"确认卖出 {stock_code}\n数量: {quantity} 股\n价格: {price} 元")
            
            if result:
                # 执行卖出
                order_result = self.trader.sell(stock_code, price=price, amount=quantity)
                
                # 记录交易
                self.log_trade("卖出", stock_code, quantity, price, order_result)
                
                messagebox.showinfo("交易成功", f"卖出订单已提交\n订单结果: {order_result}")
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量和价格")
        except Exception as e:
            messagebox.showerror("交易失败", f"卖出失败: {str(e)}")
    
    def query_positions(self):
        """查询持仓"""
        if not self.trading_enabled:
            messagebox.showerror("错误", "请先连接券商")
            return
        
        try:
            # 查询持仓
            positions = self.trader.position
            
            # 显示持仓信息
            if positions:
                pos_text = "当前持仓:\n\n"
                for pos in positions:
                    pos_text += f"股票: {pos.get('证券代码', 'N/A')} {pos.get('证券名称', 'N/A')}\n"
                    pos_text += f"数量: {pos.get('股票余额', 'N/A')} 股\n"
                    pos_text += f"成本: {pos.get('成本价', 'N/A')} 元\n"
                    pos_text += f"市值: {pos.get('市值', 'N/A')} 元\n\n"
            else:
                pos_text = "暂无持仓"
            
            messagebox.showinfo("持仓查询", pos_text)
            
        except Exception as e:
            messagebox.showerror("查询失败", f"查询持仓失败: {str(e)}")
    
    def log_trade(self, action, stock_code, quantity, price, result):
        """记录交易日志"""
        # 清空现有内容
        for widget in self.trading_log_frame.winfo_children():
            widget.destroy()
        
        # 创建交易记录表格
        columns = ('时间', '操作', '股票代码', '数量', '价格', '状态')
        trade_tree = ttk.Treeview(self.trading_log_frame, columns=columns, show='headings')
        
        for col in columns:
            trade_tree.heading(col, text=col)
            trade_tree.column(col, width=100)
        
        # 添加交易记录
        current_time = datetime.now().strftime('%H:%M:%S')
        status = "成功" if result else "失败"
        
        trade_tree.insert('', 'end', values=(
            current_time, action, stock_code, quantity, price, status
        ))
        
        trade_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def run(self):
        """运行主程序"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动股票可视化分析与交易工具...")
    
    app = TradingStockVisualizer()
    app.run()

if __name__ == "__main__":
    main()