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

# Ashare是单文件库，我们可以直接下载使用
try:
    from Ashare import get_price
    ASHARE_AVAILABLE = True
except ImportError:
    ASHARE_AVAILABLE = False
    print("Ashare未安装，请从GitHub下载Ashare.py文件")

class FreeStockVisualizer:
    def __init__(self):
        """初始化免费股票可视化工具"""
        self.output_dir = 'free_stock_data'
        self.stock_list = None
        self.current_stock = None
        self.current_data = None
        self.update_thread = None
        self.is_updating = False
        self.update_interval = 60  # 数据更新间隔（秒）
        
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
    
    def get_stock_list(self, source='auto'):
        """获取股票列表
        
        Args:
            source: 数据源 ('akshare', 'adata', 'auto')
            
        Returns:
            pandas.DataFrame: 股票列表
        """
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        if not source:
            print("没有可用的数据源")
            return None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                # 使用AKShare获取股票列表
                df = ak.stock_zh_a_spot()
                # 标准化列名
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
            
            elif source == 'adata' and ADATA_AVAILABLE:
                # 使用AData获取股票列表
                df = adata.stock.info.all_code()
                # 标准化列名
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
        """获取实时行情
        
        Args:
            stock_code: 股票代码
            source: 数据源
            
        Returns:
            dict: 实时行情数据
        """
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                # 使用AKShare获取实时行情
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
            
            elif source == 'adata' and ADATA_AVAILABLE:
                # 使用AData获取实时行情（通过日线数据的最新一天）
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
            return None
    
    def get_daily_data(self, stock_code, days=60, source='auto'):
        """获取股票日线数据
        
        Args:
            stock_code: 股票代码
            days: 获取天数
            source: 数据源
            
        Returns:
            pandas.DataFrame: 股票历史数据
        """
        if source == 'auto':
            source = self.available_sources[0] if self.available_sources else None
        
        try:
            if source == 'akshare' and AKSHARE_AVAILABLE:
                # 使用AKShare获取历史数据
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
                
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                       start_date=start_date, end_date=end_date, adjust="")
                
                if not df.empty:
                    # 标准化列名
                    df = df.rename(columns={
                        '日期': 'trade_date',
                        '开盘': 'open',
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'vol',
                        '成交额': 'amount'
                    })
                    
                    # 设置日期索引
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    return df
            
            elif source == 'adata' and ADATA_AVAILABLE:
                # 使用AData获取历史数据
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                df = adata.stock.market.get_market(stock_code=stock_code, k_type=1, start_date=start_date)
                
                if not df.empty:
                    # 标准化列名和格式
                    df = df.rename(columns={
                        'trade_time': 'trade_date'
                    })
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    return df
            
            elif source == 'ashare' and ASHARE_AVAILABLE:
                # 使用Ashare获取历史数据
                # 转换股票代码格式
                if stock_code.startswith('6'):
                    symbol = f'sh{stock_code}'
                else:
                    symbol = f'sz{stock_code}'
                
                df = get_price(symbol, frequency='1d', count=days)
                
                if not df.empty:
                    # 重置索引并标准化列名
                    df.reset_index(inplace=True)
                    df = df.rename(columns={
                        'index': 'trade_date',
                        'volume': 'vol'
                    })
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    df.set_index('trade_date', inplace=True)
                    return df
            
            return None
            
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return None
    
    def calculate_indicators(self, df):
        """计算技术指标
        
        Args:
            df: 股票历史数据DataFrame
            
        Returns:
            pandas.DataFrame: 添加了技术指标的DataFrame
        """
        if df is None or df.empty:
            return None
        
        # 复制DataFrame以避免修改原始数据
        result = df.copy()
        
        # 计算移动平均线
        result['MA5'] = result['close'].rolling(window=5).mean()
        result['MA10'] = result['close'].rolling(window=10).mean()
        result['MA20'] = result['close'].rolling(window=20).mean()
        
        # 计算MACD
        result['EMA12'] = result['close'].ewm(span=12, adjust=False).mean()
        result['EMA26'] = result['close'].ewm(span=26, adjust=False).mean()
        result['DIF'] = result['EMA12'] - result['EMA26']
        result['DEA'] = result['DIF'].ewm(span=9, adjust=False).mean()
        result['MACD'] = 2 * (result['DIF'] - result['DEA'])
        
        # 计算KDJ
        low_min = result['low'].rolling(window=9).min()
        high_max = result['high'].rolling(window=9).max()
        result['RSV'] = (result['close'] - low_min) / (high_max - low_min) * 100
        result['K'] = result['RSV'].ewm(com=2).mean()
        result['D'] = result['K'].ewm(com=2).mean()
        result['J'] = 3 * result['K'] - 2 * result['D']
        
        # 计算BOLL指标
        result['BOLL_MIDDLE'] = result['close'].rolling(window=20).mean()
        result['BOLL_STD'] = result['close'].rolling(window=20).std()
        result['BOLL_UPPER'] = result['BOLL_MIDDLE'] + 2 * result['BOLL_STD']
        result['BOLL_LOWER'] = result['BOLL_MIDDLE'] - 2 * result['BOLL_STD']
        
        # 计算RSI
        delta = result['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        result['RSI'] = 100 - (100 / (1 + rs))
        
        return result
    
    def analyze_stock(self, df):
        """分析股票走势并给出建议
        
        Args:
            df: 带有技术指标的股票数据
            
        Returns:
            dict: 分析结果和建议
        """
        if df is None or df.empty:
            return None
        
        result = {}
        latest = df.iloc[-1]
        
        # 趋势分析
        if latest['close'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
            result['trend'] = "强势上涨趋势"
            result['trend_advice'] = "市场呈现强势上涨趋势，可考虑持有或适量买入"
        elif latest['close'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
            result['trend'] = "强势下跌趋势"
            result['trend_advice'] = "市场呈现强势下跌趋势，建议观望或减仓"
        elif latest['close'] > latest['MA5'] and latest['MA5'] > latest['MA10']:
            result['trend'] = "短期上涨趋势"
            result['trend_advice'] = "短期呈现上涨趋势，可适量参与"
        elif latest['close'] < latest['MA5'] and latest['MA5'] < latest['MA10']:
            result['trend'] = "短期下跌趋势"
            result['trend_advice'] = "短期呈现下跌趋势，建议谨慎参与"
        else:
            result['trend'] = "震荡整理"
            result['trend_advice'] = "市场处于震荡整理阶段，建议观望或轻仓参与"
        
        # MACD分析
        if latest['DIF'] > latest['DEA'] and latest['MACD'] > 0:
            result['macd'] = "MACD金叉且柱线为正"
            result['macd_advice'] = "MACD指标显示买入信号"
        elif latest['DIF'] < latest['DEA'] and latest['MACD'] < 0:
            result['macd'] = "MACD死叉且柱线为负"
            result['macd_advice'] = "MACD指标显示卖出信号"
        else:
            result['macd'] = "MACD中性"
            result['macd_advice'] = "MACD指标显示中性信号"
        
        # KDJ分析
        if latest['K'] > latest['D'] and latest['J'] > latest['D']:
            result['kdj'] = "KDJ金叉"
            result['kdj_advice'] = "KDJ指标显示买入信号"
        elif latest['K'] < latest['D'] and latest['J'] < latest['D']:
            result['kdj'] = "KDJ死叉"
            result['kdj_advice'] = "KDJ指标显示卖出信号"
        else:
            result['kdj'] = "KDJ中性"
            result['kdj_advice'] = "KDJ指标显示中性信号"
        
        # RSI分析
        if latest['RSI'] > 70:
            result['rsi'] = "RSI超买"
            result['rsi_advice'] = "RSI指标显示超买，注意回调风险"
        elif latest['RSI'] < 30:
            result['rsi'] = "RSI超卖"
            result['rsi_advice'] = "RSI指标显示超卖，可能出现反弹"
        else:
            result['rsi'] = "RSI正常"
            result['rsi_advice'] = "RSI指标显示正常区间"
        
        # 综合建议
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
            
        if "买入" in result['kdj_advice']:
            signals.append(1)
        elif "卖出" in result['kdj_advice']:
            signals.append(-1)
        else:
            signals.append(0)
        
        avg_signal = sum(signals) / len(signals)
        
        if avg_signal > 0.3:
            result['overall'] = "偏多信号"
            result['overall_advice'] = "综合技术指标偏多，可考虑适量买入，但请注意风险控制"
        elif avg_signal < -0.3:
            result['overall'] = "偏空信号"
            result['overall_advice'] = "综合技术指标偏空，建议观望或减仓"
        else:
            result['overall'] = "中性信号"
            result['overall_advice'] = "综合技术指标中性，建议观望等待更明确信号"
        
        return result

class FreeStockVisualizerGUI:
    def __init__(self):
        """初始化GUI界面"""
        self.visualizer = FreeStockVisualizer()
        self.root = tk.Tk()
        self.root.title("免费股票可视化分析工具")
        self.root.geometry("1200x800")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        self.setup_gui()
        
    def setup_gui(self):
        """设置GUI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 右侧显示区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 数据源选择
        source_frame = ttk.LabelFrame(left_frame, text="数据源选择")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_var = tk.StringVar(value='auto')
        sources = ['auto'] + self.visualizer.available_sources
        for source in sources:
            ttk.Radiobutton(source_frame, text=source, variable=self.source_var, value=source).pack(anchor=tk.W)
        
        # 股票搜索
        search_frame = ttk.LabelFrame(left_frame, text="股票搜索")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="股票代码:").pack(anchor=tk.W)
        self.stock_entry = ttk.Entry(search_frame)
        self.stock_entry.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(search_frame, text="搜索股票", command=self.search_stock).pack(fill=tk.X)
        
        # 股票列表
        list_frame = ttk.LabelFrame(left_frame, text="股票列表")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        self.stock_tree = ttk.Treeview(list_frame, columns=('name', 'price', 'change'), show='tree headings')
        self.stock_tree.heading('#0', text='代码')
        self.stock_tree.heading('name', text='名称')
        self.stock_tree.heading('price', text='价格')
        self.stock_tree.heading('change', text='涨跌幅')
        
        self.stock_tree.column('#0', width=80)
        self.stock_tree.column('name', width=80)
        self.stock_tree.column('price', width=60)
        self.stock_tree.column('change', width=60)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stock_tree.bind('<Double-1>', self.on_stock_select)
        
        # 操作按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="刷新列表", command=self.refresh_stock_list).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="开始自动更新", command=self.start_auto_update).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="停止自动更新", command=self.stop_auto_update).pack(fill=tk.X)
        
        # 右侧显示区域
        # 创建Notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息标签页
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="基本信息")
        
        self.info_text = scrolledtext.ScrolledText(self.info_frame, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # K线图标签页
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="K线图")
        
        # 技术指标标签页
        self.indicator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.indicator_frame, text="技术指标")
        
        # 分析建议标签页
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="分析建议")
        
        self.analysis_text = scrolledtext.ScrolledText(self.analysis_frame, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始化显示
        self.show_welcome_message()
        
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_msg = f"""
欢迎使用免费股票可视化分析工具！

可用数据源：{', '.join(self.visualizer.available_sources) if self.visualizer.available_sources else '无'}

使用说明：
1. 点击"刷新列表"获取股票列表
2. 在股票列表中双击选择股票
3. 查看K线图和技术指标
4. 参考分析建议进行投资决策

注意事项：
- 本工具使用免费数据源，数据仅供参考
- 投资有风险，决策需谨慎
- 建议结合多种分析方法

如果没有可用数据源，请安装：
pip install akshare
pip install adata
        """
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, welcome_msg)
        
    def refresh_stock_list(self):
        """刷新股票列表"""
        try:
            source = self.source_var.get()
            df = self.visualizer.get_stock_list(source)
            
            if df is not None:
                # 清空现有列表
                for item in self.stock_tree.get_children():
                    self.stock_tree.delete(item)
                
                # 添加股票到列表（限制显示数量以提高性能）
                for i, (_, row) in enumerate(df.head(100).iterrows()):
                    if i >= 100:  # 限制显示100只股票
                        break
                    
                    code = row.get('ts_code', '')
                    name = row.get('name', '')
                    price = row.get('close', 0)
                    change = row.get('pct_chg', 0)
                    
                    # 根据涨跌设置颜色
                    if change > 0:
                        tags = ('positive',)
                    elif change < 0:
                        tags = ('negative',)
                    else:
                        tags = ('neutral',)
                    
                    self.stock_tree.insert('', tk.END, text=code, 
                                         values=(name, f"{price:.2f}", f"{change:.2f}%"),
                                         tags=tags)
                
                # 设置标签颜色
                self.stock_tree.tag_configure('positive', foreground='red')
                self.stock_tree.tag_configure('negative', foreground='green')
                self.stock_tree.tag_configure('neutral', foreground='black')
                
                messagebox.showinfo("成功", f"已加载 {min(len(df), 100)} 只股票")
            else:
                messagebox.showerror("错误", "获取股票列表失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新股票列表失败: {e}")
    
    def search_stock(self):
        """搜索股票"""
        stock_code = self.stock_entry.get().strip()
        if not stock_code:
            messagebox.showwarning("警告", "请输入股票代码")
            return
        
        self.load_stock_data(stock_code)
    
    def on_stock_select(self, event):
        """股票选择事件"""
        selection = self.stock_tree.selection()
        if selection:
            item = self.stock_tree.item(selection[0])
            stock_code = item['text']
            self.load_stock_data(stock_code)
    
    def load_stock_data(self, stock_code):
        """加载股票数据"""
        try:
            source = self.source_var.get()
            
            # 获取实时行情
            realtime_data = self.visualizer.get_realtime_quotes(stock_code, source)
            
            # 获取历史数据
            df = self.visualizer.get_daily_data(stock_code, days=120, source=source)
            
            if df is not None:
                # 计算技术指标
                df_with_indicators = self.visualizer.calculate_indicators(df)
                
                # 更新显示
                self.update_info_display(stock_code, realtime_data, df_with_indicators)
                self.update_chart_display(stock_code, df_with_indicators)
                self.update_analysis_display(df_with_indicators)
                
                self.visualizer.current_stock = stock_code
                self.visualizer.current_data = df_with_indicators
                
            else:
                messagebox.showerror("错误", f"获取股票 {stock_code} 数据失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载股票数据失败: {e}")
    
    def update_info_display(self, stock_code, realtime_data, df):
        """更新基本信息显示"""
        info_text = f"股票代码: {stock_code}\n\n"
        
        if realtime_data:
            info_text += f"股票名称: {realtime_data.get('name', 'N/A')}\n"
            info_text += f"最新价格: {realtime_data.get('price', 'N/A')}\n"
            info_text += f"涨跌额: {realtime_data.get('change', 'N/A')}\n"
            info_text += f"涨跌幅: {realtime_data.get('pct_change', 'N/A')}%\n"
            info_text += f"成交量: {realtime_data.get('volume', 'N/A')}\n"
            info_text += f"成交额: {realtime_data.get('amount', 'N/A')}\n"
            info_text += f"最高价: {realtime_data.get('high', 'N/A')}\n"
            info_text += f"最低价: {realtime_data.get('low', 'N/A')}\n"
            info_text += f"开盘价: {realtime_data.get('open', 'N/A')}\n\n"
        
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            info_text += "技术指标（最新）:\n"
            info_text += f"MA5: {latest.get('MA5', 'N/A'):.2f}\n"
            info_text += f"MA10: {latest.get('MA10', 'N/A'):.2f}\n"
            info_text += f"MA20: {latest.get('MA20', 'N/A'):.2f}\n"
            info_text += f"MACD: {latest.get('MACD', 'N/A'):.4f}\n"
            info_text += f"KDJ K: {latest.get('K', 'N/A'):.2f}\n"
            info_text += f"KDJ D: {latest.get('D', 'N/A'):.2f}\n"
            info_text += f"KDJ J: {latest.get('J', 'N/A'):.2f}\n"
            info_text += f"RSI: {latest.get('RSI', 'N/A'):.2f}\n"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)
    
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
            fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            
            # K线图
            mpf.plot(df_plot.tail(60), type='candle', ax=axes[0], volume=axes[1],
                    mav=(5, 10, 20), style='charles', title=f'{stock_code} K线图')
            
            # 嵌入到tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            error_label = ttk.Label(self.chart_frame, text=f"图表显示错误: {e}")
            error_label.pack(expand=True)
    
    def update_analysis_display(self, df):
        """更新分析建议显示"""
        if df is None or df.empty:
            return
        
        analysis = self.visualizer.analyze_stock(df)
        
        if analysis:
            analysis_text = "股票分析报告\n" + "="*50 + "\n\n"
            
            analysis_text += f"趋势分析: {analysis.get('trend', 'N/A')}\n"
            analysis_text += f"建议: {analysis.get('trend_advice', 'N/A')}\n\n"
            
            analysis_text += f"MACD分析: {analysis.get('macd', 'N/A')}\n"
            analysis_text += f"建议: {analysis.get('macd_advice', 'N/A')}\n\n"
            
            analysis_text += f"KDJ分析: {analysis.get('kdj', 'N/A')}\n"
            analysis_text += f"建议: {analysis.get('kdj_advice', 'N/A')}\n\n"
            
            analysis_text += f"RSI分析: {analysis.get('rsi', 'N/A')}\n"
            analysis_text += f"建议: {analysis.get('rsi_advice', 'N/A')}\n\n"
            
            analysis_text += "综合分析\n" + "-"*30 + "\n"
            analysis_text += f"综合信号: {analysis.get('overall', 'N/A')}\n"
            analysis_text += f"投资建议: {analysis.get('overall_advice', 'N/A')}\n\n"
            
            analysis_text += "风险提示\n" + "-"*30 + "\n"
            analysis_text += "1. 本分析仅基于技术指标，不构成投资建议\n"
            analysis_text += "2. 投资有风险，入市需谨慎\n"
            analysis_text += "3. 请结合基本面分析和市场环境做出决策\n"
            analysis_text += "4. 建议设置止损点，控制投资风险\n"
            
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, analysis_text)
    
    def start_auto_update(self):
        """开始自动更新"""
        if not self.visualizer.is_updating and self.visualizer.current_stock:
            self.visualizer.is_updating = True
            self.visualizer.update_thread = threading.Thread(target=self.auto_update_worker)
            self.visualizer.update_thread.daemon = True
            self.visualizer.update_thread.start()
            messagebox.showinfo("信息", "已开始自动更新")
        else:
            messagebox.showwarning("警告", "请先选择股票或已在更新中")
    
    def stop_auto_update(self):
        """停止自动更新"""
        self.visualizer.is_updating = False
        messagebox.showinfo("信息", "已停止自动更新")
    
    def auto_update_worker(self):
        """自动更新工作线程"""
        while self.visualizer.is_updating:
            try:
                if self.visualizer.current_stock:
                    # 在主线程中更新UI
                    self.root.after(0, lambda: self.load_stock_data(self.visualizer.current_stock))
                
                # 等待更新间隔
                for _ in range(self.visualizer.update_interval):
                    if not self.visualizer.is_updating:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"自动更新错误: {e}")
                break
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动免费股票可视化分析工具...")
    
    # 检查依赖
    missing_deps = []
    
    try:
        import matplotlib
        import pandas
        import numpy
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        print("缺少必要依赖:")
        for dep in missing_deps:
            print(f"  {dep}")
        print("\n请安装缺少的依赖后重试")
        return
    
    # 启动GUI
    app = FreeStockVisualizerGUI()
    app.run()

if __name__ == "__main__":
    main()