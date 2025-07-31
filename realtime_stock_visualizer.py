import tushare as ts
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
matplotlib.use('TkAgg')

class RealTimeStockVisualizer:
    def __init__(self, token=None):
        """初始化实时股票可视化工具
        
        Args:
            token: Tushare Pro的API token
        """
        self.token = token
        self.pro = None
        self.output_dir = 'stock_visualizer_data'
        self.stock_list = None
        self.current_stock = None
        self.current_data = None
        self.update_thread = None
        self.is_updating = False
        self.update_interval = 60  # 数据更新间隔（秒）
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 禁用代理设置
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''
    
    def login(self):
        """登录Tushare Pro API"""
        if self.token:
            try:
                ts.set_token(self.token)
                self.pro = ts.pro_api(timeout=60)
                print("成功登录Tushare Pro API")
                return True
            except Exception as e:
                print(f"登录失败: {e}")
                return False
        else:
            print("请提供有效的Tushare Pro API token")
            return False
    
    def get_stock_list(self):
        """获取股票列表"""
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        try:
            df = self.pro.stock_basic(exchange='', list_status='L', 
                                    fields='ts_code,symbol,name,area,industry,list_date')
            self.stock_list = df
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return None
    
    def get_realtime_quotes(self, ts_code):
        """获取实时行情
        
        Args:
            ts_code: 股票代码（格式：000001.SZ）
            
        Returns:
            pandas.DataFrame: 实时行情数据
        """
        try:
            # 转换为tushare实时行情所需的代码格式
            symbol = ts_code.split('.')[0]
            if ts_code.endswith('SZ'):
                symbol = symbol
            elif ts_code.endswith('SH'):
                symbol = 'sh' + symbol
            
            # 获取实时行情
            df = ts.get_realtime_quotes(symbol)
            return df
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return None
    
    def get_daily_data(self, ts_code, days=60):
        """获取股票日线数据
        
        Args:
            ts_code: 股票代码（格式：000001.SZ）
            days: 获取天数
            
        Returns:
            pandas.DataFrame: 股票历史数据
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        try:
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            # 按日期升序排序
            df = df.sort_values('trade_date')
            # 将日期设为索引
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            return df
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
        
        return result
    
    def get_stock_news(self, ts_code):
        """获取股票相关新闻
        
        Args:
            ts_code: 股票代码
            
        Returns:
            pandas.DataFrame: 新闻数据
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        try:
            # 获取公司公告
            df = self.pro.anns(ts_code=ts_code, start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'), 
                              end_date=datetime.now().strftime('%Y%m%d'))
            return df
        except Exception as e:
            print(f"获取公司公告失败: {e}")
            return None
    
    def get_stock_info(self, ts_code):
        """获取股票基本信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            dict: 股票基本信息
        """
        if not self.pro or not self.stock_list is not None:
            return None
        
        try:
            # 从股票列表中获取基本信息
            info = self.stock_list[self.stock_list['ts_code'] == ts_code].iloc[0].to_dict()
            
            # 获取公司基本信息
            company_info = self.pro.stock_company(ts_code=ts_code)
            if not company_info.empty:
                for key, value in company_info.iloc[0].to_dict().items():
                    info[key] = value
            
            return info
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return None
    
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
        elif latest['DIF'] > latest['DEA']:
            result['macd'] = "MACD金叉"
            result['macd_advice'] = "MACD指标显示偏多信号"
        elif latest['DIF'] < latest['DEA']:
            result['macd'] = "MACD死叉"
            result['macd_advice'] = "MACD指标显示偏空信号"
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
        
        # BOLL分析
        if latest['close'] > latest['BOLL_UPPER']:
            result['boll'] = "价格突破布林上轨"
            result['boll_advice'] = "股价可能超买，注意回调风险"
        elif latest['close'] < latest['BOLL_LOWER']:
            result['boll'] = "价格跌破布林下轨"
            result['boll_advice'] = "股价可能超卖，可能出现反弹"
        elif latest['close'] > latest['BOLL_MIDDLE']:
            result['boll'] = "价格在布林中轨和上轨之间"
            result['boll_advice'] = "股价偏强，可能继续上涨"
        else:
            result['boll'] = "价格在布林中轨和下轨之间"
            result['boll_advice'] = "股价偏弱，可能继续下跌"
        
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
        
        signal_sum = sum(signals)
        
        if signal_sum >= 2:
            result['overall'] = "买入信号"
            result['advice'] = "技术指标综合显示较强买入信号，可考虑买入或持有"
        elif signal_sum <= -2:
            result['overall'] = "卖出信号"
            result['advice'] = "技术指标综合显示较强卖出信号，建议减仓或观望"
        elif signal_sum > 0:
            result['overall'] = "偏多信号"
            result['advice'] = "技术指标综合显示偏多信号，可小仓位参与"
        elif signal_sum < 0:
            result['overall'] = "偏空信号"
            result['advice'] = "技术指标综合显示偏空信号，建议谨慎参与"
        else:
            result['overall'] = "中性信号"
            result['advice'] = "技术指标综合显示中性信号，建议观望"
        
        # 风险提示
        result['risk_warning'] = "【风险提示】：股市有风险，投资需谨慎。本分析仅供参考，不构成投资建议。"
        
        return result
    
    def create_gui(self):
        """创建图形用户界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("实时股票可视化分析工具 - 金融小白助手")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 创建标题栏
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="实时股票可视化分析工具", 
                              font=("Arial", 18, "bold"), bg='#2c3e50', fg='white')
        title_label.pack(pady=10)
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 股票选择和基本信息
        left_frame = tk.Frame(main_frame, bg='#f0f0f0', width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 股票搜索框
        search_frame = tk.Frame(left_frame, bg='#f0f0f0')
        search_frame.pack(fill=tk.X, pady=5)
        
        search_label = tk.Label(search_frame, text="搜索股票:", bg='#f0f0f0')
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        search_button = tk.Button(search_frame, text="搜索", command=self.search_stock)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # 股票列表
        list_frame = tk.Frame(left_frame, bg='white', bd=1, relief=tk.SOLID)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.stock_listbox = tk.Listbox(list_frame, height=15)
        self.stock_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stock_listbox.bind('<<ListboxSelect>>', self.on_stock_select)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.stock_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stock_listbox.config(yscrollcommand=scrollbar.set)
        
        # 股票基本信息
        info_frame = tk.LabelFrame(left_frame, text="股票基本信息", bg='#f0f0f0', font=("Arial", 10, "bold"))
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右侧面板 - 图表和分析
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 实时行情
        quote_frame = tk.LabelFrame(right_frame, text="实时行情", bg='#f0f0f0', font=("Arial", 10, "bold"))
        quote_frame.pack(fill=tk.X, pady=5)
        
        self.quote_text = tk.Label(quote_frame, text="请选择股票查看实时行情", 
                                 font=("Arial", 12), bg='#f0f0f0', justify=tk.LEFT)
        self.quote_text.pack(fill=tk.X, padx=10, pady=10)
        
        # 图表区域
        chart_frame = tk.LabelFrame(right_frame, text="股票走势图", bg='#f0f0f0', font=("Arial", 10, "bold"))
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建选项卡
        self.tab_control = ttk.Notebook(chart_frame)
        
        self.tab1 = tk.Frame(self.tab_control, bg='#f0f0f0')
        self.tab2 = tk.Frame(self.tab_control, bg='#f0f0f0')
        self.tab3 = tk.Frame(self.tab_control, bg='#f0f0f0')
        
        self.tab_control.add(self.tab1, text='K线图')
        self.tab_control.add(self.tab2, text='技术指标')
        self.tab_control.add(self.tab3, text='分析建议')
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # K线图
        self.fig1 = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.tab1)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 技术指标图
        self.fig2 = plt.Figure(figsize=(10, 6), dpi=100)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.tab2)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 分析建议
        self.analysis_text = scrolledtext.ScrolledText(self.tab3, wrap=tk.WORD, font=("Arial", 11))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 底部状态栏
        status_frame = tk.Frame(self.root, bg='#2c3e50', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, text="准备就绪", bg='#2c3e50', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.update_time_label = tk.Label(status_frame, text="", bg='#2c3e50', fg='white')
        self.update_time_label.pack(side=tk.RIGHT, padx=10)
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def search_stock(self):
        """搜索股票"""
        search_text = self.search_var.get().strip()
        if not search_text or self.stock_list is None:
            return
        
        # 清空列表
        self.stock_listbox.delete(0, tk.END)
        
        # 搜索匹配的股票
        matched_stocks = self.stock_list[
            (self.stock_list['ts_code'].str.contains(search_text, case=False)) | 
            (self.stock_list['name'].str.contains(search_text, case=False)) | 
            (self.stock_list['symbol'].str.contains(search_text, case=False))
        ]
        
        # 显示搜索结果
        for _, row in matched_stocks.iterrows():
            self.stock_listbox.insert(tk.END, f"{row['name']} ({row['ts_code']})")
        
        self.status_label.config(text=f"找到 {len(matched_stocks)} 个匹配的股票")
    
    def on_stock_select(self, event):
        """股票选择事件处理"""
        selection = self.stock_listbox.curselection()
        if not selection:
            return
        
        # 获取选中的股票
        stock_text = self.stock_listbox.get(selection[0])
        ts_code = stock_text.split('(')[1].split(')')[0]
        
        self.current_stock = ts_code
        self.status_label.config(text=f"正在加载 {stock_text} 的数据...")
        
        # 获取股票数据
        self.update_stock_data()
    
    def update_stock_data(self):
        """更新股票数据"""
        if not self.current_stock:
            return
        
        # 获取日线数据
        daily_data = self.get_daily_data(self.current_stock)
        if daily_data is None:
            messagebox.showerror("错误", "获取股票数据失败")
            return
        
        # 计算技术指标
        self.current_data = self.calculate_indicators(daily_data)
        
        # 获取实时行情
        realtime_data = self.get_realtime_quotes(self.current_stock)
        
        # 获取股票基本信息
        stock_info = self.get_stock_info(self.current_stock)
        
        # 更新界面
        self.update_info_panel(stock_info)
        self.update_quote_panel(realtime_data)
        self.update_charts()
        self.update_analysis()
        
        # 更新状态
        self.update_time_label.config(text=f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.status_label.config(text="数据加载完成")
    
    def update_info_panel(self, info):
        """更新股票基本信息面板"""
        if info is None:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "无法获取股票基本信息")
            return
        
        self.info_text.delete(1.0, tk.END)
        
        # 格式化显示基本信息
        self.info_text.insert(tk.END, f"股票名称: {info.get('name', '未知')}\n")
        self.info_text.insert(tk.END, f"股票代码: {info.get('ts_code', '未知')}\n")
        self.info_text.insert(tk.END, f"所属行业: {info.get('industry', '未知')}\n")
        self.info_text.insert(tk.END, f"所属地区: {info.get('area', '未知')}\n")
        self.info_text.insert(tk.END, f"上市日期: {info.get('list_date', '未知')}\n")
        
        if 'chairman' in info:
            self.info_text.insert(tk.END, f"\n公司信息:\n")
            self.info_text.insert(tk.END, f"董事长: {info.get('chairman', '未知')}\n")
            self.info_text.insert(tk.END, f"总经理: {info.get('manager', '未知')}\n")
            self.info_text.insert(tk.END, f"注册资本: {info.get('reg_capital', '未知')}\n")
            self.info_text.insert(tk.END, f"员工人数: {info.get('employees', '未知')}\n")
            self.info_text.insert(tk.END, f"主营业务: {info.get('main_business', '未知')}\n")
            self.info_text.insert(tk.END, f"公司网址: {info.get('website', '未知')}\n")
    
    def update_quote_panel(self, quote):
        """更新实时行情面板"""
        if quote is None or quote.empty:
            self.quote_text.config(text="无法获取实时行情")
            return
        
        # 获取第一行数据
        data = quote.iloc[0]
        
        # 计算涨跌幅
        price = float(data['price'])
        pre_close = float(data['pre_close'])
        change = price - pre_close
        change_pct = change / pre_close * 100
        
        # 设置颜色
        if change > 0:
            color = "#d9534f"  # 红色
            change_str = f"+{change:.2f} (+{change_pct:.2f}%)"
        elif change < 0:
            color = "#5cb85c"  # 绿色
            change_str = f"{change:.2f} ({change_pct:.2f}%)"
        else:
            color = "black"
            change_str = "0.00 (0.00%)"
        
        # 格式化显示实时行情
        quote_text = f"股票: {data['name']} ({data['code']})\n"
        quote_text += f"当前价格: {price:.2f}  涨跌: {change_str}\n"
        quote_text += f"今开: {data['open']}  昨收: {data['pre_close']}\n"
        quote_text += f"最高: {data['high']}  最低: {data['low']}\n"
        quote_text += f"成交量: {int(float(data['volume'])/100):,} 手  成交额: {int(float(data['amount'])/10000):,} 万元\n"
        quote_text += f"更新时间: {data['date']} {data['time']}"
        
        self.quote_text.config(text=quote_text, fg=color)
    
    def update_charts(self):
        """更新图表"""
        if self.current_data is None or self.current_data.empty:
            return
        
        # 清除图表
        self.fig1.clear()
        self.fig2.clear()
        
        # 准备数据
        data = self.current_data.copy()
        # 转换为mplfinance可用的格式
        data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'})
        
        # 绘制K线图
        ax1 = self.fig1.add_subplot(111)
        mpf.plot(data[-60:], type='candle', style='yahoo', 
                mav=(5, 10, 20), ax=ax1, volume=True, 
                title=f"{self.current_stock} K线图", 
                ylabel='价格', ylabel_lower='成交量')
        
        # 绘制技术指标
        # MACD
        ax2 = self.fig2.add_subplot(311)
        ax2.plot(data.index[-60:], data['DIF'][-60:], label='DIF')
        ax2.plot(data.index[-60:], data['DEA'][-60:], label='DEA')
        ax2.bar(data.index[-60:], data['MACD'][-60:], label='MACD', alpha=0.5)
        ax2.set_title('MACD')
        ax2.legend()
        ax2.grid(True)
        
        # KDJ
        ax3 = self.fig2.add_subplot(312)
        ax3.plot(data.index[-60:], data['K'][-60:], label='K')
        ax3.plot(data.index[-60:], data['D'][-60:], label='D')
        ax3.plot(data.index[-60:], data['J'][-60:], label='J')
        ax3.set_title('KDJ')
        ax3.legend()
        ax3.grid(True)
        
        # BOLL
        ax4 = self.fig2.add_subplot(313)
        ax4.plot(data.index[-60:], data['close'][-60:], label='收盘价')
        ax4.plot(data.index[-60:], data['BOLL_UPPER'][-60:], label='上轨')
        ax4.plot(data.index[-60:], data['BOLL_MIDDLE'][-60:], label='中轨')
        ax4.plot(data.index[-60:], data['BOLL_LOWER'][-60:], label='下轨')
        ax4.set_title('BOLL')
        ax4.legend()
        ax4.grid(True)
        
        self.fig1.tight_layout()
        self.fig2.tight_layout()
        
        # 更新画布
        self.canvas1.draw()
        self.canvas2.draw()
    
    def update_analysis(self):
        """更新分析建议"""
        if self.current_data is None or self.current_data.empty:
            return
        
        # 分析股票
        analysis = self.analyze_stock(self.current_data)
        if analysis is None:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, "无法生成分析建议")
            return
        
        # 清除文本
        self.analysis_text.delete(1.0, tk.END)
        
        # 插入标题
        self.analysis_text.insert(tk.END, f"{self.current_stock} 技术分析报告\n", "title")
        self.analysis_text.insert(tk.END, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 插入总体建议
        self.analysis_text.insert(tk.END, "【总体建议】\n", "section")
        self.analysis_text.insert(tk.END, f"信号: {analysis['overall']}\n")
        self.analysis_text.insert(tk.END, f"{analysis['advice']}\n\n")
        
        # 插入趋势分析
        self.analysis_text.insert(tk.END, "【趋势分析】\n", "section")
        self.analysis_text.insert(tk.END, f"当前趋势: {analysis['trend']}\n")
        self.analysis_text.insert(tk.END, f"建议: {analysis['trend_advice']}\n\n")
        
        # 插入MACD分析
        self.analysis_text.insert(tk.END, "【MACD指标】\n", "section")
        self.analysis_text.insert(tk.END, f"状态: {analysis['macd']}\n")
        self.analysis_text.insert(tk.END, f"建议: {analysis['macd_advice']}\n\n")
        
        # 插入KDJ分析
        self.analysis_text.insert(tk.END, "【KDJ指标】\n", "section")
        self.analysis_text.insert(tk.END, f"状态: {analysis['kdj']}\n")
        self.analysis_text.insert(tk.END, f"建议: {analysis['kdj_advice']}\n\n")
        
        # 插入BOLL分析
        self.analysis_text.insert(tk.END, "【BOLL指标】\n", "section")
        self.analysis_text.insert(tk.END, f"状态: {analysis['boll']}\n")
        self.analysis_text.insert(tk.END, f"建议: {analysis['boll_advice']}\n\n")
        
        # 插入风险提示
        self.analysis_text.insert(tk.END, "\n" + analysis['risk_warning'] + "\n", "warning")
        
        # 设置标签样式
        self.analysis_text.tag_configure("title", font=("Arial", 14, "bold"))
        self.analysis_text.tag_configure("section", font=("Arial", 12, "bold"))
        self.analysis_text.tag_configure("warning", font=("Arial", 10, "italic"), foreground="red")
    
    def start_auto_update(self):
        """开始自动更新数据"""
        if self.is_updating:
            return
        
        self.is_updating = True
        self.update_thread = threading.Thread(target=self._auto_update_thread)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def _auto_update_thread(self):
        """自动更新线程"""
        while self.is_updating:
            if self.current_stock:
                # 在主线程中更新UI
                self.root.after(0, self.update_stock_data)
            
            # 等待指定时间
            time.sleep(self.update_interval)
    
    def on_closing(self):
        """窗口关闭事件处理"""
        self.is_updating = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(1)  # 等待线程结束，最多等待1秒
        self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        # 创建GUI
        self.create_gui()
        
        # 登录Tushare
        if not self.token:
            self.token = tk.simpledialog.askstring("Tushare API Token", 
                                                "请输入你的Tushare Pro API token:")
        
        if not self.token or not self.login():
            messagebox.showerror("错误", "无法登录Tushare Pro API，请检查token是否正确")
            return
        
        # 获取股票列表
        self.status_label.config(text="正在获取股票列表...")
        stock_list = self.get_stock_list()
        
        if stock_list is None:
            messagebox.showerror("错误", "获取股票列表失败")
            return
        
        # 显示股票列表
        for _, row in stock_list.head(100).iterrows():  # 只显示前100只股票
            self.stock_listbox.insert(tk.END, f"{row['name']} ({row['ts_code']})")
        
        self.status_label.config(text="准备就绪，请选择股票")
        
        # 开始自动更新
        self.start_auto_update()
        
        # 运行主循环
        self.root.mainloop()


def main():
    print("实时股票可视化分析工具 - 金融小白助手")
    print("-" * 50)
    
    # 创建可视化工具实例
    token = input("请输入你的Tushare Pro API token (可以从https://tushare.pro/register获取): ")
    visualizer = RealTimeStockVisualizer(token)
    
    # 运行应用程序
    visualizer.run()


if __name__ == "__main__":
    main()