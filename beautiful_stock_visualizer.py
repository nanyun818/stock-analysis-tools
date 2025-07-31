import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import matplotlib
import requests
import json
from PIL import Image, ImageTk
import tkinter.font as tkFont
matplotlib.use('TkAgg')

# 尝试导入免费的股票数据库
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("AKShare未安装，请运行: pip install akshare")

try:
    import adata
    ADATA_AVAILABLE = True
except ImportError:
    ADATA_AVAILABLE = False
    print("AData未安装，请运行: pip install adata")

try:
    from Ashare import get_price
    ASHARE_AVAILABLE = True
except ImportError:
    ASHARE_AVAILABLE = False
    print("Ashare未安装，请从GitHub下载Ashare.py文件")

class BeautifulStockVisualizer:
    def __init__(self):
        """初始化美化版股票可视化工具"""
        self.output_dir = 'beautiful_stock_data'
        self.stock_list = None
        self.current_stock = None
        self.current_data = None
        self.update_thread = None
        self.is_updating = False
        self.update_interval = 60
        self.hot_stocks = []  # 热门股票列表
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 检查可用的数据源
        self.available_sources = []
        if AKSHARE_AVAILABLE:
            self.available_sources.append('akshare')
        if ADATA_AVAILABLE:
            self.available_sources.append('adata')
        if ASHARE_AVAILABLE:
            self.available_sources.append('ashare')
        
        if not self.available_sources:
            print("警告：没有可用的数据源，请安装至少一个免费股票数据库")
            print("推荐安装：pip install akshare")
    
    def get_hot_stocks(self, source='auto'):
        """获取当日热门股票
        
        Args:
            source: 数据源
            
        Returns:
            list: 热门股票列表
        """
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                # 添加重试机制
                for attempt in range(3):
                    try:
                        # 获取涨跌幅排行榜
                        df_up = ak.stock_zh_a_spot()
                        if not df_up.empty:
                            # 按涨跌幅排序，取前20名
                            df_sorted = df_up.sort_values('涨跌幅', ascending=False).head(20)
                            hot_stocks = []
                            for _, row in df_sorted.iterrows():
                                hot_stocks.append({
                                    'code': row['代码'],
                                    'name': row['名称'],
                                    'price': row['最新价'],
                                    'change': row['涨跌幅'],
                                    'volume': row['成交量'],
                                    'amount': row['成交额']
                                })
                            self.hot_stocks = hot_stocks
                            return hot_stocks
                        break
                    except Exception as retry_e:
                        if attempt < 2:  # 前两次失败时等待重试
                            time.sleep(1)
                            continue
                        else:
                            raise retry_e
            
            # 如果无法获取实时数据，返回模拟数据
            return self.get_demo_hot_stocks()
            
        except Exception as e:
            print(f"获取热门股票失败: {e}")
            return self.get_demo_hot_stocks()
    
    def get_demo_hot_stocks(self):
        """获取演示用热门股票数据"""
        return [
            {'code': '000001', 'name': '平安银行', 'price': 12.50, 'change': 2.15, 'volume': 1000000, 'amount': 12500000},
            {'code': '000002', 'name': '万科A', 'price': 18.30, 'change': 1.85, 'volume': 800000, 'amount': 14640000},
            {'code': '600000', 'name': '浦发银行', 'price': 8.90, 'change': 1.50, 'volume': 1200000, 'amount': 10680000},
            {'code': '600036', 'name': '招商银行', 'price': 35.20, 'change': 1.20, 'volume': 600000, 'amount': 21120000},
            {'code': '000858', 'name': '五粮液', 'price': 168.50, 'change': 0.95, 'volume': 300000, 'amount': 50550000}
        ]
    
    def get_stock_list(self, source='auto'):
        """获取股票列表"""
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        if not source:
            print("没有可用的数据源")
            return None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                # 添加重试机制
                for attempt in range(3):
                    try:
                        df = ak.stock_zh_a_spot()
                        df = df.rename(columns={
                            '代码': 'ts_code',
                            '名称': 'name',
                            '最新价': 'close',
                            '涨跌幅': 'pct_chg',
                            '涨跌额': 'change',
                            '成交量': 'vol',
                            '成交额': 'amount'
                        })
                        self.stock_list = df
                        return df
                    except Exception as retry_e:
                        if attempt < 2:
                            time.sleep(1)
                            continue
                        else:
                            raise retry_e
            
            elif source == 'adata' and ADATA_AVAILABLE:
                df = adata.stock.info.all_code()
                df = df.rename(columns={
                    'stock_code': 'ts_code',
                    'short_name': 'name'
                })
                self.stock_list = df
                return df
            
            else:
                print(f"数据源 {source} 不可用")
                return None
                
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return None
    
    def get_realtime_quotes(self, stock_code, source='auto'):
        """获取实时行情"""
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                # 添加重试机制
                for attempt in range(3):
                    try:
                        df = ak.stock_zh_a_spot()
                        stock_data = df[df['代码'] == stock_code]
                        if not stock_data.empty:
                            return {
                                'name': stock_data.iloc[0]['名称'],
                                'price': stock_data.iloc[0]['最新价'],
                                'change': stock_data.iloc[0]['涨跌额'],
                                'pct_change': stock_data.iloc[0]['涨跌幅'],
                                'volume': stock_data.iloc[0]['成交量'],
                                'amount': stock_data.iloc[0]['成交额'],
                                'high': stock_data.iloc[0]['最高'],
                                'low': stock_data.iloc[0]['最低'],
                                'open': stock_data.iloc[0]['今开']
                            }
                        break
                    except Exception as retry_e:
                        if attempt < 2:
                            time.sleep(1)
                            continue
                        else:
                            raise retry_e
                
                # 如果在实时数据中找不到，返回模拟数据
                return self.get_demo_stock_data(stock_code)
            
            elif source == 'adata' and ADATA_AVAILABLE:
                df = adata.stock.market.get_market(stock_code=stock_code, k_type=1)
                if not df.empty:
                    latest = df.iloc[-1]
                    return {
                        'name': stock_code,
                        'price': latest['close'],
                        'change': latest['close'] - latest['pre_close'],
                        'pct_change': (latest['close'] - latest['pre_close']) / latest['pre_close'] * 100,
                        'volume': latest['vol'],
                        'amount': latest['amount'],
                        'high': latest['high'],
                        'low': latest['low'],
                        'open': latest['open']
                    }
            
            return None
            
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return self.get_demo_stock_data(stock_code)
    
    def get_demo_stock_data(self, stock_code):
        """获取演示用股票数据"""
        # 根据股票代码返回不同的模拟数据
        demo_data = {
            '000001': {'name': '平安银行', 'price': 12.50, 'change': 0.15, 'pct_change': 1.22},
            '000002': {'name': '万科A', 'price': 18.30, 'change': 0.33, 'pct_change': 1.84},
            '600000': {'name': '浦发银行', 'price': 8.90, 'change': 0.13, 'pct_change': 1.48},
            '600036': {'name': '招商银行', 'price': 35.20, 'change': 0.42, 'pct_change': 1.21},
            '000858': {'name': '五粮液', 'price': 168.50, 'change': 1.58, 'pct_change': 0.95}
        }
        
        if stock_code in demo_data:
            data = demo_data[stock_code]
            return {
                'name': data['name'],
                'price': data['price'],
                'change': data['change'],
                'pct_change': data['pct_change'],
                'volume': 1000000,
                'amount': data['price'] * 1000000,
                'high': data['price'] * 1.02,
                'low': data['price'] * 0.98,
                'open': data['price'] * 0.99
            }
        else:
            return {
                'name': f'股票{stock_code}',
                'price': 10.00,
                'change': 0.10,
                'pct_change': 1.01,
                'volume': 500000,
                'amount': 5000000,
                'high': 10.20,
                'low': 9.80,
                'open': 9.90
            }
    
    def get_daily_data(self, stock_code, days=60, source='auto'):
        """获取股票日线数据"""
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
                
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                       start_date=start_date, end_date=end_date, adjust="")
                
                if not df.empty:
                    df = df.rename(columns={
                        '日期': 'trade_date',
                        '开盘': 'open',
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'vol',
                        '成交额': 'amount'
                    })
                    
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    return df
            
            elif source == 'adata' and ADATA_AVAILABLE:
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                df = adata.stock.market.get_market(stock_code=stock_code, k_type=1, start_date=start_date)
                
                if not df.empty:
                    df = df.rename(columns={'trade_time': 'trade_date'})
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    return df
            
            return None
            
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return None
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        if df is None or df.empty:
            return None
        
        result = df.copy()
        
        # 移动平均线
        result['MA5'] = result['close'].rolling(window=5).mean()
        result['MA10'] = result['close'].rolling(window=10).mean()
        result['MA20'] = result['close'].rolling(window=20).mean()
        
        # MACD
        result['EMA12'] = result['close'].ewm(span=12, adjust=False).mean()
        result['EMA26'] = result['close'].ewm(span=26, adjust=False).mean()
        result['DIF'] = result['EMA12'] - result['EMA26']
        result['DEA'] = result['DIF'].ewm(span=9, adjust=False).mean()
        result['MACD'] = 2 * (result['DIF'] - result['DEA'])
        
        # KDJ
        low_min = result['low'].rolling(window=9).min()
        high_max = result['high'].rolling(window=9).max()
        result['RSV'] = (result['close'] - low_min) / (high_max - low_min) * 100
        result['K'] = result['RSV'].ewm(com=2).mean()
        result['D'] = result['K'].ewm(com=2).mean()
        result['J'] = 3 * result['K'] - 2 * result['D']
        
        # BOLL
        result['BOLL_MIDDLE'] = result['close'].rolling(window=20).mean()
        result['BOLL_STD'] = result['close'].rolling(window=20).std()
        result['BOLL_UPPER'] = result['BOLL_MIDDLE'] + 2 * result['BOLL_STD']
        result['BOLL_LOWER'] = result['BOLL_MIDDLE'] - 2 * result['BOLL_STD']
        
        # RSI
        delta = result['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        result['RSI'] = 100 - (100 / (1 + rs))
        
        return result
    
    def analyze_stock(self, df):
        """分析股票走势并给出建议"""
        if df is None or df.empty:
            return None
        
        result = {}
        latest = df.iloc[-1]
        
        # 趋势分析
        if latest['close'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
            result['trend'] = "强势上涨趋势"
            result['trend_advice'] = "市场呈现强势上涨趋势，可考虑持有或适量买入"
            result['trend_color'] = "#FF4444"
        elif latest['close'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
            result['trend'] = "强势下跌趋势"
            result['trend_advice'] = "市场呈现强势下跌趋势，建议观望或减仓"
            result['trend_color'] = "#00AA00"
        elif latest['close'] > latest['MA5'] and latest['MA5'] > latest['MA10']:
            result['trend'] = "短期上涨趋势"
            result['trend_advice'] = "短期呈现上涨趋势，可适量参与"
            result['trend_color'] = "#FF6666"
        elif latest['close'] < latest['MA5'] and latest['MA5'] < latest['MA10']:
            result['trend'] = "短期下跌趋势"
            result['trend_advice'] = "短期呈现下跌趋势，建议谨慎参与"
            result['trend_color'] = "#66AA66"
        else:
            result['trend'] = "震荡整理"
            result['trend_advice'] = "市场处于震荡整理阶段，建议观望或轻仓参与"
            result['trend_color'] = "#888888"
        
        # MACD分析
        if latest['DIF'] > latest['DEA'] and latest['MACD'] > 0:
            result['macd'] = "MACD金叉且柱线为正"
            result['macd_advice'] = "MACD指标显示买入信号"
            result['macd_color'] = "#FF4444"
        elif latest['DIF'] < latest['DEA'] and latest['MACD'] < 0:
            result['macd'] = "MACD死叉且柱线为负"
            result['macd_advice'] = "MACD指标显示卖出信号"
            result['macd_color'] = "#00AA00"
        else:
            result['macd'] = "MACD中性"
            result['macd_advice'] = "MACD指标显示中性信号"
            result['macd_color'] = "#888888"
        
        # 综合评分
        signals = []
        if "上涨" in result['trend']:
            signals.append(1)
        elif "下跌" in result['trend']:
            signals.append(-1)
        else:
            signals.append(0)
            
        if "买入" in result['macd_advice']:
            signals.append(1)
        elif "卖出" in result['macd_advice']:
            signals.append(-1)
        else:
            signals.append(0)
        
        avg_signal = sum(signals) / len(signals)
        result['score'] = int((avg_signal + 1) * 50)  # 转换为0-100分
        
        if avg_signal > 0.3:
            result['overall'] = "偏多信号"
            result['overall_advice'] = "综合技术指标偏多，可考虑适量买入"
            result['overall_color'] = "#FF4444"
        elif avg_signal < -0.3:
            result['overall'] = "偏空信号"
            result['overall_advice'] = "综合技术指标偏空，建议观望或减仓"
            result['overall_color'] = "#00AA00"
        else:
            result['overall'] = "中性信号"
            result['overall_advice'] = "综合技术指标中性，建议观望等待"
            result['overall_color'] = "#888888"
        
        return result

class BeautifulStockVisualizerGUI:
    def __init__(self):
        """初始化美化版GUI界面"""
        self.visualizer = BeautifulStockVisualizer()
        self.root = tk.Tk()
        self.root.title("🚀 股票可视化分析工具")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # 设置应用图标和样式
        self.setup_styles()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        self.setup_gui()
        
    def setup_styles(self):
        """设置界面样式"""
        # 创建自定义样式
        self.style = ttk.Style()
        
        # 设置主题
        try:
            self.style.theme_use('clam')
        except:
            pass
        
        # 自定义颜色
        self.colors = {
            'primary': '#2196F3',
            'secondary': '#FFC107',
            'success': '#4CAF50',
            'danger': '#F44336',
            'warning': '#FF9800',
            'info': '#00BCD4',
            'light': '#F5F5F5',
            'dark': '#212121',
            'background': '#FAFAFA',
            'surface': '#FFFFFF'
        }
        
        # 配置样式
        self.style.configure('Title.TLabel', 
                           font=('Microsoft YaHei', 16, 'bold'),
                           foreground=self.colors['primary'])
        
        self.style.configure('Subtitle.TLabel',
                           font=('Microsoft YaHei', 12, 'bold'),
                           foreground=self.colors['dark'])
        
        self.style.configure('Card.TFrame',
                           background=self.colors['surface'],
                           relief='solid',
                           borderwidth=1)
        
        self.style.configure('Primary.TButton',
                           font=('Microsoft YaHei', 10),
                           foreground='white')
        
        self.style.map('Primary.TButton',
                      background=[('active', '#1976D2'), ('!active', self.colors['primary'])])
        
        # 热门股票样式
        self.style.configure('Hot.Treeview',
                           background='#FFF3E0',
                           foreground='#E65100',
                           fieldbackground='#FFF3E0')
        
        self.style.configure('Hot.Treeview.Heading',
                           background='#FF9800',
                           foreground='white',
                           font=('Microsoft YaHei', 10, 'bold'))
    
    def setup_gui(self):
        """设置GUI界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 标题栏
        self.create_header(main_container)
        
        # 主要内容区域
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # 左侧面板
        left_panel = tk.Frame(content_frame, bg=self.colors['background'], width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # 右侧面板
        right_panel = tk.Frame(content_frame, bg=self.colors['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建左侧面板内容
        self.create_left_panel(left_panel)
        
        # 创建右侧面板内容
        self.create_right_panel(right_panel)
        
        # 初始化显示
        self.show_welcome_message()
        
    def create_header(self, parent):
        """创建标题栏"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(header_frame, 
                              text="🚀 股票可视化分析工具",
                              font=('Microsoft YaHei', 20, 'bold'),
                              fg='white',
                              bg=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # 状态信息
        status_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        status_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # 数据源状态
        sources_text = f"可用数据源: {len(self.visualizer.available_sources)}"
        sources_label = tk.Label(status_frame,
                               text=sources_text,
                               font=('Microsoft YaHei', 10),
                               fg='white',
                               bg=self.colors['primary'])
        sources_label.pack(anchor=tk.E)
        
        # 时间显示
        time_text = f"更新时间: {datetime.now().strftime('%H:%M:%S')}"
        self.time_label = tk.Label(status_frame,
                                 text=time_text,
                                 font=('Microsoft YaHei', 10),
                                 fg='white',
                                 bg=self.colors['primary'])
        self.time_label.pack(anchor=tk.E)
        
        # 定时更新时间显示
        self.update_time_display()
    
    def update_time_display(self):
        """更新时间显示"""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.config(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_time_display)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # 数据源选择卡片
        self.create_source_card(parent)
        
        # 股票搜索卡片
        self.create_search_card(parent)
        
        # 热门股票卡片
        self.create_hot_stocks_card(parent)
        
        # 操作按钮卡片
        self.create_control_card(parent)
    
    def create_source_card(self, parent):
        """创建数据源选择卡片"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 卡片标题
        title_frame = tk.Frame(card_frame, bg=self.colors['primary'], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="📡 数据源选择",
                              font=('Microsoft YaHei', 12, 'bold'),
                              fg='white',
                              bg=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 内容区域
        content_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.source_var = tk.StringVar(value='auto')
        # 数据源选项和说明
        source_options = [
            ('auto', '🔄 自动选择 (推荐)'),
            ('akshare', '📊 AKShare (主要数据源)')
        ]
        
        # 添加其他可用数据源
        for src in self.visualizer.available_sources:
            if src != 'akshare':
                source_options.append((src, f"📊 {src}"))
        
        sources = source_options
        
        for value, text in sources:
            rb = tk.Radiobutton(content_frame,
                               text=text,
                               variable=self.source_var,
                               value=value,
                               font=('Microsoft YaHei', 10),
                               bg=self.colors['surface'],
                               activebackground=self.colors['light'],
                               selectcolor=self.colors['primary'])
            rb.pack(anchor=tk.W, pady=2)
        
        # 添加数据源说明
        info_frame = tk.Frame(content_frame, bg=self.colors['light'], relief='solid', borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = """💡 数据源说明:
• 自动选择: 系统自动选择最佳可用数据源
• AKShare: 主要免费数据源，功能最完整
• 其他源: 备用数据源，提供基础数据"""
        
        info_label = tk.Label(info_frame,
                             text=info_text,
                             font=('Microsoft YaHei', 9),
                             bg=self.colors['light'],
                             justify=tk.LEFT,
                             wraplength=300)
        info_label.pack(padx=10, pady=8)
    
    def create_search_card(self, parent):
        """创建搜索卡片"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 卡片标题
        title_frame = tk.Frame(card_frame, bg=self.colors['secondary'], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🔍 股票搜索",
                              font=('Microsoft YaHei', 12, 'bold'),
                              fg='white',
                              bg=self.colors['secondary'])
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 内容区域
        content_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 搜索输入
        search_frame = tk.Frame(content_frame, bg=self.colors['surface'])
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame,
                text="股票代码:",
                font=('Microsoft YaHei', 10),
                bg=self.colors['surface']).pack(anchor=tk.W)
        
        self.stock_entry = tk.Entry(search_frame,
                                   font=('Microsoft YaHei', 11),
                                   relief='solid',
                                   borderwidth=1)
        self.stock_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 搜索按钮
        search_btn = tk.Button(content_frame,
                              text="🔍 搜索股票",
                              font=('Microsoft YaHei', 10, 'bold'),
                              bg=self.colors['secondary'],
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              command=self.search_stock)
        search_btn.pack(fill=tk.X)
    
    def create_hot_stocks_card(self, parent):
        """创建热门股票卡片"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 卡片标题
        title_frame = tk.Frame(card_frame, bg=self.colors['danger'], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🔥 当日热门股票",
                              font=('Microsoft YaHei', 12, 'bold'),
                              fg='white',
                              bg=self.colors['danger'])
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 刷新按钮
        refresh_btn = tk.Button(title_frame,
                               text="🔄",
                               font=('Microsoft YaHei', 10),
                               bg=self.colors['danger'],
                               fg='white',
                               relief='flat',
                               cursor='hand2',
                               command=self.refresh_hot_stocks)
        refresh_btn.pack(side=tk.RIGHT, padx=15, pady=5)
        
        # 内容区域
        content_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 热门股票列表
        columns = ('code', 'name', 'price', 'change')
        self.hot_tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题
        self.hot_tree.heading('code', text='代码')
        self.hot_tree.heading('name', text='名称')
        self.hot_tree.heading('price', text='价格')
        self.hot_tree.heading('change', text='涨跌幅')
        
        # 设置列宽
        self.hot_tree.column('code', width=80)
        self.hot_tree.column('name', width=100)
        self.hot_tree.column('price', width=80)
        self.hot_tree.column('change', width=80)
        
        # 滚动条
        hot_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.hot_tree.yview)
        self.hot_tree.configure(yscrollcommand=hot_scrollbar.set)
        
        self.hot_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hot_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.hot_tree.bind('<Double-1>', self.on_hot_stock_select)
    
    def create_control_card(self, parent):
        """创建控制按钮卡片"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card_frame.pack(fill=tk.X)
        
        # 卡片标题
        title_frame = tk.Frame(card_frame, bg=self.colors['info'], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="⚙️ 操作控制",
                              font=('Microsoft YaHei', 12, 'bold'),
                              fg='white',
                              bg=self.colors['info'])
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 内容区域
        content_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 按钮样式
        button_style = {
            'font': ('Microsoft YaHei', 10, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'height': 2
        }
        
        # 刷新列表按钮
        refresh_btn = tk.Button(content_frame,
                               text="📊 刷新股票列表",
                               bg=self.colors['success'],
                               fg='white',
                               command=self.refresh_stock_list,
                               **button_style)
        refresh_btn.pack(fill=tk.X, pady=(0, 8))
        
        # 自动更新按钮
        self.auto_update_btn = tk.Button(content_frame,
                                        text="🔄 开始自动更新",
                                        bg=self.colors['primary'],
                                        fg='white',
                                        command=self.toggle_auto_update,
                                        **button_style)
        self.auto_update_btn.pack(fill=tk.X, pady=(0, 8))
        
        # 状态指示器
        self.status_label = tk.Label(content_frame,
                                    text="状态: 就绪",
                                    font=('Microsoft YaHei', 9),
                                    fg=self.colors['success'],
                                    bg=self.colors['surface'])
        self.status_label.pack(anchor=tk.W)
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 创建选项卡
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 股票概览标签页
        self.create_overview_tab()
        
        # K线图标签页
        self.create_chart_tab()
        
        # 技术指标标签页
        self.create_indicators_tab()
        
        # 分析报告标签页
        self.create_analysis_tab()
    
    def create_overview_tab(self):
        """创建股票概览标签页"""
        self.overview_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(self.overview_frame, text="📈 股票概览")
        
        # 创建滚动区域
        canvas = tk.Canvas(self.overview_frame, bg=self.colors['background'])
        scrollbar = ttk.Scrollbar(self.overview_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_chart_tab(self):
        """创建K线图标签页"""
        self.chart_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(self.chart_frame, text="📊 K线图")
    
    def create_indicators_tab(self):
        """创建技术指标标签页"""
        self.indicators_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(self.indicators_frame, text="📉 技术指标")
    
    def create_analysis_tab(self):
        """创建分析报告标签页"""
        self.analysis_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(self.analysis_frame, text="📋 分析报告")
        
        self.analysis_text = scrolledtext.ScrolledText(self.analysis_frame, 
                                                      wrap=tk.WORD,
                                                      font=('Microsoft YaHei', 11),
                                                      bg=self.colors['surface'])
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        # 清空概览区域
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 欢迎卡片
        welcome_card = tk.Frame(self.scrollable_frame, bg=self.colors['surface'], relief='solid', borderwidth=1)
        welcome_card.pack(fill=tk.X, padx=20, pady=20)
        
        # 标题
        title_frame = tk.Frame(welcome_card, bg=self.colors['primary'], height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="🎉 欢迎使用股票可视化分析工具",
                              font=('Microsoft YaHei', 16, 'bold'),
                              fg='white',
                              bg=self.colors['primary'])
        title_label.pack(expand=True)
        
        # 内容
        content_frame = tk.Frame(welcome_card, bg=self.colors['surface'])
        content_frame.pack(fill=tk.X, padx=20, pady=20)
        
        welcome_text = f"""
🚀 功能特点：
• 完全免费，无需API密钥
• 支持多个数据源：{', '.join(self.visualizer.available_sources) if self.visualizer.available_sources else '无'}
• 实时股票数据和K线图
• 多种技术指标分析
• 智能投资建议
• 当日热门股票推荐

📖 详细使用指南：

【第一步：获取股票数据】
• 点击"刷新热门股票"按钮获取当日热门榜单
• 或者在"股票搜索"框中输入6位股票代码（如：000001）

【第二步：选择股票】
• 双击"当日热门股票"列表中的任意股票
• 或点击"搜索股票"按钮查找特定股票
• 系统会自动加载该股票的完整数据

【第三步：查看分析结果】
选择股票后，右侧会显示4个标签页：
• 📈 股票概览：基本信息、实时价格、关键指标
• 📊 K线图：价格走势图表，包含移动平均线
• 📉 技术指标：MACD、KDJ、BOLL、RSI等专业指标
• 📋 分析报告：AI智能分析和具体投资建议

【第四步：深度分析】
• K线图显示价格趋势和支撑阻力位
• 技术指标帮助判断买卖时机
• 分析报告提供具体的操作建议

💡 快速体验：
建议先点击热门股票中的"平安银行"或"万科A"，
然后依次查看各个标签页，体验完整功能！

💡 关于"无法获取"：
• 网络连接问题：检查网络是否正常
• 数据源限制：免费数据源可能有访问限制
• 股票代码错误：请输入正确的6位股票代码
• 交易时间：非交易时间可能无法获取实时数据
• 遇到问题时，工具会自动使用演示数据

⚠️ 风险提示：
• 本工具提供的分析仅供参考，不构成投资建议
• 投资有风险，决策需谨慎
• 建议结合多种分析方法进行综合判断
        """
        
        welcome_label = tk.Label(content_frame,
                               text=welcome_text,
                               font=('Microsoft YaHei', 11),
                               bg=self.colors['surface'],
                               justify=tk.LEFT)
        welcome_label.pack(anchor=tk.W)
    
    def refresh_hot_stocks(self):
        """刷新热门股票"""
        try:
            self.status_label.config(text="状态: 获取热门股票中...", fg=self.colors['warning'])
            self.root.update()
            
            source = self.source_var.get()
            hot_stocks = self.visualizer.get_hot_stocks(source)
            
            # 清空现有列表
            for item in self.hot_tree.get_children():
                self.hot_tree.delete(item)
            
            if hot_stocks:
                for stock in hot_stocks[:15]:  # 显示前15只
                    change_color = 'red' if stock['change'] > 0 else 'green' if stock['change'] < 0 else 'black'
                    
                    item = self.hot_tree.insert('', tk.END, values=(
                        stock['code'],
                        stock['name'][:6],  # 限制名称长度
                        f"{stock['price']:.2f}",
                        f"{stock['change']:.2f}%"
                    ))
                    
                    # 设置颜色
                    if stock['change'] > 0:
                        self.hot_tree.set(item, 'change', f"+{stock['change']:.2f}%")
                
                self.status_label.config(text=f"状态: 已加载 {len(hot_stocks)} 只热门股票", fg=self.colors['success'])
            else:
                self.status_label.config(text="状态: 获取热门股票失败", fg=self.colors['danger'])
                
        except Exception as e:
            self.status_label.config(text=f"状态: 错误 - {str(e)[:20]}...", fg=self.colors['danger'])
            messagebox.showerror("错误", f"刷新热门股票失败: {e}")
    
    def refresh_stock_list(self):
        """刷新股票列表"""
        try:
            self.status_label.config(text="状态: 刷新股票列表中...", fg=self.colors['warning'])
            self.root.update()
            
            source = self.source_var.get()
            df = self.visualizer.get_stock_list(source)
            
            if df is not None:
                self.status_label.config(text=f"状态: 已加载 {len(df)} 只股票", fg=self.colors['success'])
                messagebox.showinfo("成功", f"已加载 {len(df)} 只股票")
            else:
                self.status_label.config(text="状态: 获取股票列表失败", fg=self.colors['danger'])
                messagebox.showerror("错误", "获取股票列表失败")
                
        except Exception as e:
            self.status_label.config(text=f"状态: 错误 - {str(e)[:20]}...", fg=self.colors['danger'])
            messagebox.showerror("错误", f"刷新股票列表失败: {e}")
    
    def search_stock(self):
        """搜索股票"""
        stock_code = self.stock_entry.get().strip()
        if not stock_code:
            messagebox.showwarning("警告", "请输入股票代码")
            return
        
        self.load_stock_data(stock_code)
    
    def on_hot_stock_select(self, event):
        """热门股票选择事件"""
        selection = self.hot_tree.selection()
        if selection:
            item = self.hot_tree.item(selection[0])
            stock_code = item['values'][0]
            self.load_stock_data(stock_code)
    
    def load_stock_data(self, stock_code):
        """加载股票数据"""
        try:
            self.status_label.config(text=f"状态: 加载 {stock_code} 数据中...", fg=self.colors['warning'])
            self.root.update()
            
            source = self.source_var.get()
            
            # 获取实时行情
            realtime_data = self.visualizer.get_realtime_quotes(stock_code, source)
            
            # 获取历史数据
            df = self.visualizer.get_daily_data(stock_code, days=120, source=source)
            
            if df is not None:
                # 计算技术指标
                df_with_indicators = self.visualizer.calculate_indicators(df)
                
                # 更新显示
                self.update_overview_display(stock_code, realtime_data, df_with_indicators)
                self.update_chart_display(stock_code, df_with_indicators)
                self.update_analysis_display(df_with_indicators)
                
                self.visualizer.current_stock = stock_code
                self.visualizer.current_data = df_with_indicators
                
                self.status_label.config(text=f"状态: {stock_code} 数据加载完成", fg=self.colors['success'])
            else:
                self.status_label.config(text=f"状态: {stock_code} 数据加载失败", fg=self.colors['danger'])
                messagebox.showerror("错误", f"获取股票 {stock_code} 数据失败")
                
        except Exception as e:
            self.status_label.config(text=f"状态: 加载失败 - {str(e)[:15]}...", fg=self.colors['danger'])
            messagebox.showerror("错误", f"加载股票数据失败: {e}")
    
    def update_overview_display(self, stock_code, realtime_data, df):
        """更新概览显示"""
        # 清空现有内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 股票基本信息卡片
        self.create_stock_info_card(stock_code, realtime_data)
        
        # 技术指标卡片
        if df is not None and not df.empty:
            self.create_indicators_card(df)
            
            # 分析结果卡片
            analysis = self.visualizer.analyze_stock(df)
            if analysis:
                self.create_analysis_card(analysis)
    
    def create_stock_info_card(self, stock_code, realtime_data):
        """创建股票信息卡片"""
        card = tk.Frame(self.scrollable_frame, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # 标题
        title_frame = tk.Frame(card, bg=self.colors['primary'], height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_text = f"📊 {stock_code}"
        if realtime_data:
            title_text += f" - {realtime_data.get('name', 'N/A')}"
        
        title_label = tk.Label(title_frame,
                              text=title_text,
                              font=('Microsoft YaHei', 14, 'bold'),
                              fg='white',
                              bg=self.colors['primary'])
        title_label.pack(expand=True)
        
        # 内容
        if realtime_data:
            content_frame = tk.Frame(card, bg=self.colors['surface'])
            content_frame.pack(fill=tk.X, padx=20, pady=20)
            
            # 价格信息
            price_frame = tk.Frame(content_frame, bg=self.colors['surface'])
            price_frame.pack(fill=tk.X, pady=(0, 15))
            
            # 当前价格
            price = realtime_data.get('price', 0)
            change = realtime_data.get('pct_change', 0)
            
            price_color = self.colors['danger'] if change > 0 else self.colors['success'] if change < 0 else self.colors['dark']
            
            price_label = tk.Label(price_frame,
                                  text=f"¥{price:.2f}",
                                  font=('Microsoft YaHei', 24, 'bold'),
                                  fg=price_color,
                                  bg=self.colors['surface'])
            price_label.pack(side=tk.LEFT)
            
            change_text = f"{change:+.2f}%"
            change_label = tk.Label(price_frame,
                                   text=change_text,
                                   font=('Microsoft YaHei', 16, 'bold'),
                                   fg=price_color,
                                   bg=self.colors['surface'])
            change_label.pack(side=tk.LEFT, padx=(20, 0))
            
            # 详细信息网格
            info_grid = tk.Frame(content_frame, bg=self.colors['surface'])
            info_grid.pack(fill=tk.X)
            
            info_items = [
                ("开盘价", f"{realtime_data.get('open', 'N/A')}"),
                ("最高价", f"{realtime_data.get('high', 'N/A')}"),
                ("最低价", f"{realtime_data.get('low', 'N/A')}"),
                ("成交量", f"{realtime_data.get('volume', 'N/A')}"),
                ("成交额", f"{realtime_data.get('amount', 'N/A')}"),
                ("涨跌额", f"{realtime_data.get('change', 'N/A')}"),
            ]
            
            for i, (label, value) in enumerate(info_items):
                row = i // 2
                col = i % 2
                
                item_frame = tk.Frame(info_grid, bg=self.colors['light'], relief='solid', borderwidth=1)
                item_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
                
                tk.Label(item_frame,
                        text=label,
                        font=('Microsoft YaHei', 10),
                        bg=self.colors['light']).pack()
                
                tk.Label(item_frame,
                        text=str(value),
                        font=('Microsoft YaHei', 11, 'bold'),
                        bg=self.colors['light']).pack()
            
            # 配置网格权重
            info_grid.grid_columnconfigure(0, weight=1)
            info_grid.grid_columnconfigure(1, weight=1)
    
    def create_indicators_card(self, df):
        """创建技术指标卡片"""
        card = tk.Frame(self.scrollable_frame, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        # 标题
        title_frame = tk.Frame(card, bg=self.colors['secondary'], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="📈 技术指标",
                              font=('Microsoft YaHei', 12, 'bold'),
                              fg='white',
                              bg=self.colors['secondary'])
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 内容
        content_frame = tk.Frame(card, bg=self.colors['surface'])
        content_frame.pack(fill=tk.X, padx=20, pady=15)
        
        latest = df.iloc[-1]
        
        indicators = [
            ("MA5", f"{latest.get('MA5', 0):.2f}"),
            ("MA10", f"{latest.get('MA10', 0):.2f}"),
            ("MA20", f"{latest.get('MA20', 0):.2f}"),
            ("MACD", f"{latest.get('MACD', 0):.4f}"),
            ("KDJ-K", f"{latest.get('K', 0):.2f}"),
            ("KDJ-D", f"{latest.get('D', 0):.2f}"),
            ("RSI", f"{latest.get('RSI', 0):.2f}"),
            ("BOLL上轨", f"{latest.get('BOLL_UPPER', 0):.2f}"),
        ]
        
        for i, (name, value) in enumerate(indicators):
            row = i // 4
            col = i % 4
            
            indicator_frame = tk.Frame(content_frame, bg=self.colors['light'], relief='solid', borderwidth=1)
            indicator_frame.grid(row=row, column=col, padx=3, pady=3, sticky='ew')
            
            tk.Label(indicator_frame,
                    text=name,
                    font=('Microsoft YaHei', 9),
                    bg=self.colors['light']).pack()
            
            tk.Label(indicator_frame,
                    text=value,
                    font=('Microsoft YaHei', 10, 'bold'),
                    bg=self.colors['light']).pack()
        
        # 配置网格权重
        for i in range(4):
            content_frame.grid_columnconfigure(i, weight=1)
    
    def create_analysis_card(self, analysis):
        """创建分析结果卡片"""
        card = tk.Frame(self.scrollable_frame, bg=self.colors['surface'], relief='solid', borderwidth=1)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        # 标题
        title_frame = tk.Frame(card, bg=self.colors['info'], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text=f"🎯 智能分析 (评分: {analysis.get('score', 50)}/100)",
                              font=('Microsoft YaHei', 12, 'bold'),
                              fg='white',
                              bg=self.colors['info'])
        title_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 内容
        content_frame = tk.Frame(card, bg=self.colors['surface'])
        content_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # 综合建议
        overall_frame = tk.Frame(content_frame, bg=analysis.get('overall_color', '#888888'), relief='solid', borderwidth=2)
        overall_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(overall_frame,
                text=f"💡 {analysis.get('overall', 'N/A')}",
                font=('Microsoft YaHei', 14, 'bold'),
                fg='white',
                bg=analysis.get('overall_color', '#888888')).pack(pady=10)
        
        tk.Label(overall_frame,
                text=analysis.get('overall_advice', 'N/A'),
                font=('Microsoft YaHei', 11),
                fg='white',
                bg=analysis.get('overall_color', '#888888'),
                wraplength=400).pack(pady=(0, 10))
        
        # 详细分析
        details_frame = tk.Frame(content_frame, bg=self.colors['surface'])
        details_frame.pack(fill=tk.X)
        
        details = [
            ("趋势分析", analysis.get('trend', 'N/A'), analysis.get('trend_advice', 'N/A')),
            ("MACD分析", analysis.get('macd', 'N/A'), analysis.get('macd_advice', 'N/A')),
        ]
        
        for i, (title, status, advice) in enumerate(details):
            detail_frame = tk.Frame(details_frame, bg=self.colors['light'], relief='solid', borderwidth=1)
            detail_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(detail_frame,
                    text=f"{title}: {status}",
                    font=('Microsoft YaHei', 10, 'bold'),
                    bg=self.colors['light']).pack(anchor=tk.W, padx=10, pady=(5, 0))
            
            tk.Label(detail_frame,
                    text=advice,
                    font=('Microsoft YaHei', 9),
                    bg=self.colors['light'],
                    wraplength=400).pack(anchor=tk.W, padx=10, pady=(0, 5))
    
    def update_chart_display(self, stock_code, df):
        """更新K线图显示"""
        # 清空现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if df is None or df.empty:
            return
        
        try:
            # 准备数据
            df_plot = df.copy()
            df_plot.index = pd.to_datetime(df_plot.index)
            
            # 创建图表
            fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
            fig.patch.set_facecolor('#FAFAFA')
            
            # K线图
            mpf.plot(df_plot.tail(60), type='candle', ax=axes[0], volume=axes[1],
                    mav=(5, 10, 20), style='charles', title=f'{stock_code} K线图')
            
            # 设置图表样式
            axes[0].set_facecolor('#FFFFFF')
            axes[1].set_facecolor('#FFFFFF')
            
            # 嵌入到Tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            plt.close(fig)
            
        except Exception as e:
            error_label = tk.Label(self.chart_frame,
                                 text=f"图表显示错误: {e}",
                                 font=('Microsoft YaHei', 12),
                                 fg=self.colors['danger'],
                                 bg=self.colors['background'])
            error_label.pack(expand=True)
    
    def update_analysis_display(self, df):
        """更新分析报告显示"""
        if df is None or df.empty:
            return
        
        analysis = self.visualizer.analyze_stock(df)
        if not analysis:
            return
        
        # 清空现有内容
        self.analysis_text.delete(1.0, tk.END)
        
        # 生成分析报告
        report = f"""
📊 股票分析报告
{'='*50}

📈 趋势分析
{'-'*30}
状态: {analysis.get('trend', 'N/A')}
建议: {analysis.get('trend_advice', 'N/A')}

📉 MACD分析
{'-'*30}
状态: {analysis.get('macd', 'N/A')}
建议: {analysis.get('macd_advice', 'N/A')}

🎯 综合评价
{'-'*30}
评分: {analysis.get('score', 50)}/100
结论: {analysis.get('overall', 'N/A')}
建议: {analysis.get('overall_advice', 'N/A')}

⚠️ 风险提示
{'-'*30}
• 本分析仅供参考，不构成投资建议
• 股市有风险，投资需谨慎
• 建议结合多种分析方法进行决策
• 请根据自身风险承受能力进行投资

📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.analysis_text.insert(tk.END, report)
    
    def toggle_auto_update(self):
        """切换自动更新"""
        if self.visualizer.is_updating:
            self.stop_auto_update()
        else:
            self.start_auto_update()
    
    def start_auto_update(self):
        """开始自动更新"""
        if not self.visualizer.current_stock:
            messagebox.showwarning("警告", "请先选择一只股票")
            return
        
        self.visualizer.is_updating = True
        self.auto_update_btn.config(text="⏸️ 停止自动更新", bg=self.colors['warning'])
        self.status_label.config(text="状态: 自动更新中...", fg=self.colors['info'])
        
        def update_worker():
            while self.visualizer.is_updating:
                try:
                    if self.visualizer.current_stock:
                        self.root.after(0, lambda: self.load_stock_data(self.visualizer.current_stock))
                    time.sleep(self.visualizer.update_interval)
                except Exception as e:
                    print(f"自动更新错误: {e}")
                    break
        
        self.visualizer.update_thread = threading.Thread(target=update_worker, daemon=True)
        self.visualizer.update_thread.start()
    
    def stop_auto_update(self):
        """停止自动更新"""
        self.visualizer.is_updating = False
        self.auto_update_btn.config(text="🔄 开始自动更新", bg=self.colors['primary'])
        self.status_label.config(text="状态: 已停止自动更新", fg=self.colors['success'])
    
    def run(self):
        """运行GUI"""
        # 启动时自动刷新热门股票
        self.root.after(1000, self.refresh_hot_stocks)
        
        # 启动主循环
        self.root.mainloop()

def main():
    """主函数"""
    print("🚀 启动股票可视化分析工具...")
    
    # 检查数据源
    available_sources = []
    if AKSHARE_AVAILABLE:
        available_sources.append('AKShare')
    if ADATA_AVAILABLE:
        available_sources.append('AData')
    if ASHARE_AVAILABLE:
        available_sources.append('Ashare')
    
    if available_sources:
        print(f"✅ 可用数据源: {', '.join(available_sources)}")
    else:
        print("❌ 没有可用的数据源，请安装至少一个免费股票数据库")
        print("推荐安装: pip install akshare")
        return
    
    # 启动GUI
    try:
        app = BeautifulStockVisualizerGUI()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()