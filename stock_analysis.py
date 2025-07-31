import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
from datetime import datetime, timedelta


class StockAnalyzer:
    def __init__(self, token=None):
        """初始化股票分析器
        
        Args:
            token: Tushare Pro的API token
        """
        self.token = token
        self.pro = None
        self.output_dir = 'analysis_results'
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def login(self):
        """登录Tushare Pro API"""
        if self.token:
            ts.set_token(self.token)
            self.pro = ts.pro_api()
            print("成功登录Tushare Pro API")
            return True
        else:
            print("请提供有效的Tushare Pro API token")
            return False
    
    def get_stock_data(self, ts_code, start_date=None, end_date=None):
        """获取股票历史数据
        
        Args:
            ts_code: 股票代码（格式：000001.SZ）
            start_date: 开始日期（格式：YYYYMMDD）
            end_date: 结束日期（格式：YYYYMMDD）
            
        Returns:
            pandas.DataFrame: 股票历史数据
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        # 如果未指定日期，默认获取最近一年的数据
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            # 获取一年的数据
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        try:
            # 获取日线数据
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            # 按日期升序排序
            df = df.sort_values('trade_date')
            # 将日期设为索引
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            
            print(f"成功获取 {ts_code} 从 {start_date} 到 {end_date} 的历史数据")
            return df
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
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
        result['MA30'] = result['close'].rolling(window=30).mean()
        
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
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        result['RSI'] = 100 - (100 / (1 + rs))
        
        return result
    
    def plot_stock_price(self, df, ts_code, save=True):
        """绘制股票价格走势图
        
        Args:
            df: 股票历史数据DataFrame
            ts_code: 股票代码
            save: 是否保存图表
        """
        if df is None or df.empty:
            print("没有数据可供绘图")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['close'], label='收盘价')
        plt.plot(df.index, df['MA5'], label='5日均线')
        plt.plot(df.index, df['MA10'], label='10日均线')
        plt.plot(df.index, df['MA20'], label='20日均线')
        plt.plot(df.index, df['MA30'], label='30日均线')
        
        plt.title(f'{ts_code} 股价走势图')
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True)
        
        if save:
            file_path = os.path.join(self.output_dir, f"{ts_code.replace('.', '_')}_price.png")
            plt.savefig(file_path)
            print(f"股价走势图已保存至 {file_path}")
        
        plt.show()
    
    def plot_volume(self, df, ts_code, save=True):
        """绘制成交量图
        
        Args:
            df: 股票历史数据DataFrame
            ts_code: 股票代码
            save: 是否保存图表
        """
        if df is None or df.empty:
            print("没有数据可供绘图")
            return
        
        plt.figure(figsize=(12, 4))
        plt.bar(df.index, df['vol'], color='blue', alpha=0.7)
        
        plt.title(f'{ts_code} 成交量')
        plt.xlabel('日期')
        plt.ylabel('成交量')
        plt.grid(True)
        
        if save:
            file_path = os.path.join(self.output_dir, f"{ts_code.replace('.', '_')}_volume.png")
            plt.savefig(file_path)
            print(f"成交量图已保存至 {file_path}")
        
        plt.show()
    
    def plot_macd(self, df, ts_code, save=True):
        """绘制MACD图
        
        Args:
            df: 股票历史数据DataFrame
            ts_code: 股票代码
            save: 是否保存图表
        """
        if df is None or df.empty:
            print("没有数据可供绘图")
            return
        
        plt.figure(figsize=(12, 4))
        plt.plot(df.index, df['DIF'], label='DIF')
        plt.plot(df.index, df['DEA'], label='DEA')
        
        # 绘制MACD柱状图
        colors = ['red' if x > 0 else 'green' for x in df['MACD']]
        plt.bar(df.index, df['MACD'], color=colors, alpha=0.7)
        
        plt.title(f'{ts_code} MACD')
        plt.xlabel('日期')
        plt.ylabel('值')
        plt.legend()
        plt.grid(True)
        
        if save:
            file_path = os.path.join(self.output_dir, f"{ts_code.replace('.', '_')}_macd.png")
            plt.savefig(file_path)
            print(f"MACD图已保存至 {file_path}")
        
        plt.show()
    
    def plot_kdj(self, df, ts_code, save=True):
        """绘制KDJ图
        
        Args:
            df: 股票历史数据DataFrame
            ts_code: 股票代码
            save: 是否保存图表
        """
        if df is None or df.empty:
            print("没有数据可供绘图")
            return
        
        plt.figure(figsize=(12, 4))
        plt.plot(df.index, df['K'], label='K')
        plt.plot(df.index, df['D'], label='D')
        plt.plot(df.index, df['J'], label='J')
        
        plt.title(f'{ts_code} KDJ')
        plt.xlabel('日期')
        plt.ylabel('值')
        plt.legend()
        plt.grid(True)
        
        if save:
            file_path = os.path.join(self.output_dir, f"{ts_code.replace('.', '_')}_kdj.png")
            plt.savefig(file_path)
            print(f"KDJ图已保存至 {file_path}")
        
        plt.show()
    
    def plot_boll(self, df, ts_code, save=True):
        """绘制布林带图
        
        Args:
            df: 股票历史数据DataFrame
            ts_code: 股票代码
            save: 是否保存图表
        """
        if df is None or df.empty:
            print("没有数据可供绘图")
            return
        
        plt.figure(figsize=(12, 4))
        plt.plot(df.index, df['close'], label='收盘价')
        plt.plot(df.index, df['BOLL_UPPER'], label='上轨')
        plt.plot(df.index, df['BOLL_MIDDLE'], label='中轨')
        plt.plot(df.index, df['BOLL_LOWER'], label='下轨')
        
        plt.title(f'{ts_code} 布林带')
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.legend()
        plt.grid(True)
        
        if save:
            file_path = os.path.join(self.output_dir, f"{ts_code.replace('.', '_')}_boll.png")
            plt.savefig(file_path)
            print(f"布林带图已保存至 {file_path}")
        
        plt.show()
    
    def generate_analysis_report(self, df, ts_code):
        """生成分析报告
        
        Args:
            df: 股票历史数据DataFrame
            ts_code: 股票代码
        """
        if df is None or df.empty:
            print("没有数据可供分析")
            return
        
        # 获取最新数据
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 计算涨跌幅
        change_pct = (latest['close'] - prev['close']) / prev['close'] * 100
        
        # 生成报告
        report = f"# {ts_code} 股票分析报告\n\n"
        report += f"## 基本信息\n\n"
        report += f"- 股票代码: {ts_code}\n"
        report += f"- 分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- 数据区间: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}\n\n"
        
        report += f"## 最新交易日数据\n\n"
        report += f"- 日期: {df.index[-1].strftime('%Y-%m-%d')}\n"
        report += f"- 开盘价: {latest['open']:.2f}\n"
        report += f"- 最高价: {latest['high']:.2f}\n"
        report += f"- 最低价: {latest['low']:.2f}\n"
        report += f"- 收盘价: {latest['close']:.2f}\n"
        report += f"- 涨跌幅: {change_pct:.2f}%\n"
        report += f"- 成交量: {latest['vol']}\n\n"
        
        report += f"## 技术指标分析\n\n"
        
        # 移动平均线分析
        report += f"### 移动平均线\n\n"
        ma5 = latest['MA5']
        ma10 = latest['MA10']
        ma20 = latest['MA20']
        ma30 = latest['MA30']
        close = latest['close']
        
        report += f"- MA5: {ma5:.2f}\n"
        report += f"- MA10: {ma10:.2f}\n"
        report += f"- MA20: {ma20:.2f}\n"
        report += f"- MA30: {ma30:.2f}\n\n"
        
        if close > ma5 > ma10 > ma20 > ma30:
            report += "移动平均线呈多头排列，股价处于上升趋势。\n\n"
        elif close < ma5 < ma10 < ma20 < ma30:
            report += "移动平均线呈空头排列，股价处于下降趋势。\n\n"
        elif close > ma5 and close > ma10 and ma5 > ma10:
            report += "短期均线向上，可能有上涨动能。\n\n"
        elif close < ma5 and close < ma10 and ma5 < ma10:
            report += "短期均线向下，可能有下跌压力。\n\n"
        else:
            report += "均线交叉，趋势不明确。\n\n"
        
        # MACD分析
        report += f"### MACD\n\n"
        dif = latest['DIF']
        dea = latest['DEA']
        macd = latest['MACD']
        
        report += f"- DIF: {dif:.4f}\n"
        report += f"- DEA: {dea:.4f}\n"
        report += f"- MACD: {macd:.4f}\n\n"
        
        if dif > dea and macd > 0:
            report += "MACD金叉且柱线为正，可能是买入信号。\n\n"
        elif dif < dea and macd < 0:
            report += "MACD死叉且柱线为负，可能是卖出信号。\n\n"
        elif dif > dea and macd < 0:
            report += "MACD金叉但柱线仍为负，趋势可能即将转变。\n\n"
        elif dif < dea and macd > 0:
            report += "MACD死叉但柱线仍为正，趋势可能即将转变。\n\n"
        else:
            report += "MACD指标显示趋势不明确。\n\n"
        
        # KDJ分析
        report += f"### KDJ\n\n"
        k = latest['K']
        d = latest['D']
        j = latest['J']
        
        report += f"- K值: {k:.2f}\n"
        report += f"- D值: {d:.2f}\n"
        report += f"- J值: {j:.2f}\n\n"
        
        if k > d and j > 0:
            report += "KDJ金叉，可能是买入信号。\n\n"
        elif k < d and j < 100:
            report += "KDJ死叉，可能是卖出信号。\n\n"
        elif k > 80 and d > 80 and j > 80:
            report += "KDJ三线都处于超买区域，可能面临回调。\n\n"
        elif k < 20 and d < 20 and j < 20:
            report += "KDJ三线都处于超卖区域，可能有反弹机会。\n\n"
        else:
            report += "KDJ指标显示趋势不明确。\n\n"
        
        # 布林带分析
        report += f"### 布林带\n\n"
        upper = latest['BOLL_UPPER']
        middle = latest['BOLL_MIDDLE']
        lower = latest['BOLL_LOWER']
        
        report += f"- 上轨: {upper:.2f}\n"
        report += f"- 中轨: {middle:.2f}\n"
        report += f"- 下轨: {lower:.2f}\n\n"
        
        if close > upper:
            report += "股价突破布林带上轨，可能处于强势，但也有回调风险。\n\n"
        elif close < lower:
            report += "股价跌破布林带下轨，可能处于弱势，但也有反弹机会。\n\n"
        elif close > middle and close < upper:
            report += "股价位于布林带上半轨，呈现偏强走势。\n\n"
        elif close < middle and close > lower:
            report += "股价位于布林带下半轨，呈现偏弱走势。\n\n"
        else:
            report += "股价位于布林带中轨附近，趋势不明确。\n\n"
        
        # RSI分析
        report += f"### RSI\n\n"
        rsi = latest['RSI']
        
        report += f"- RSI: {rsi:.2f}\n\n"
        
        if rsi > 70:
            report += "RSI处于超买区域，可能面临回调。\n\n"
        elif rsi < 30:
            report += "RSI处于超卖区域，可能有反弹机会。\n\n"
        elif rsi > 50 and rsi < 70:
            report += "RSI处于强势区域，但未达超买。\n\n"
        elif rsi > 30 and rsi < 50:
            report += "RSI处于弱势区域，但未达超卖。\n\n"
        else:
            report += "RSI指标显示趋势中性。\n\n"
        
        # 综合分析
        report += f"## 综合分析\n\n"
        
        # 简单的综合分析逻辑
        bullish_signals = 0
        bearish_signals = 0
        
        # 均线信号
        if close > ma5 > ma10 > ma20 > ma30:
            bullish_signals += 2
        elif close < ma5 < ma10 < ma20 < ma30:
            bearish_signals += 2
        elif close > ma5 and close > ma10:
            bullish_signals += 1
        elif close < ma5 and close < ma10:
            bearish_signals += 1
        
        # MACD信号
        if dif > dea and macd > 0:
            bullish_signals += 2
        elif dif < dea and macd < 0:
            bearish_signals += 2
        elif dif > dea:
            bullish_signals += 1
        elif dif < dea:
            bearish_signals += 1
        
        # KDJ信号
        if k > d and j > 0:
            bullish_signals += 1
        elif k < d and j < 100:
            bearish_signals += 1
        elif k < 20 and d < 20 and j < 20:
            bullish_signals += 1
        elif k > 80 and d > 80 and j > 80:
            bearish_signals += 1
        
        # 布林带信号
        if close > upper:
            bullish_signals += 1
            bearish_signals += 1  # 也有回调风险
        elif close < lower:
            bearish_signals += 1
            bullish_signals += 1  # 也有反弹机会
        elif close > middle:
            bullish_signals += 1
        elif close < middle:
            bearish_signals += 1
        
        # RSI信号
        if rsi > 70:
            bearish_signals += 1
        elif rsi < 30:
            bullish_signals += 1
        elif rsi > 50:
            bullish_signals += 0.5
        elif rsi < 50:
            bearish_signals += 0.5
        
        # 输出综合分析结果
        if bullish_signals > bearish_signals + 2:
            report += "**综合技术指标显示强烈的看涨信号。**\n\n"
        elif bearish_signals > bullish_signals + 2:
            report += "**综合技术指标显示强烈的看跌信号。**\n\n"
        elif bullish_signals > bearish_signals:
            report += "**综合技术指标偏向看涨，但信号不够强烈。**\n\n"
        elif bearish_signals > bullish_signals:
            report += "**综合技术指标偏向看跌，但信号不够强烈。**\n\n"
        else:
            report += "**综合技术指标显示趋势不明确，建议观望。**\n\n"
        
        report += "*注意：本分析报告仅基于技术指标生成，不构成投资建议。投资决策需结合基本面分析和市场环境等多方面因素。*\n"
        
        # 保存报告
        file_path = os.path.join(self.output_dir, f"{ts_code.replace('.', '_')}_analysis_report.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"分析报告已保存至 {file_path}")
        
        return report


def main():
    print("股票技术分析工具")
    print("-" * 40)
    
    # 创建分析器实例
    token = input("请输入你的Tushare Pro API token: ")
    analyzer = StockAnalyzer(token)
    
    # 登录
    if not analyzer.login():
        return
    
    while True:
        print("\n请选择操作:")
        print("1. 获取股票数据并分析")
        print("2. 绘制技术指标图表")
        print("3. 生成分析报告")
        print("0. 退出")
        
        choice = input("请输入选项编号: ")
        
        if choice == '1':
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            
            if ts_code:
                # 获取股票数据
                df = analyzer.get_stock_data(ts_code, start_date or None, end_date or None)
                if df is not None:
                    # 计算技术指标
                    df_with_indicators = analyzer.calculate_technical_indicators(df)
                    print("\n技术指标计算完成，最新数据:")
                    print(df_with_indicators.tail(1))
            else:
                print("股票代码不能为空")
        
        elif choice == '2':
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            
            if ts_code:
                # 获取股票数据并计算指标
                df = analyzer.get_stock_data(ts_code, start_date or None, end_date or None)
                if df is not None:
                    df_with_indicators = analyzer.calculate_technical_indicators(df)
                    
                    # 绘制各种图表
                    analyzer.plot_stock_price(df_with_indicators, ts_code)
                    analyzer.plot_volume(df_with_indicators, ts_code)
                    analyzer.plot_macd(df_with_indicators, ts_code)
                    analyzer.plot_kdj(df_with_indicators, ts_code)
                    analyzer.plot_boll(df_with_indicators, ts_code)
            else:
                print("股票代码不能为空")
        
        elif choice == '3':
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            
            if ts_code:
                # 获取股票数据并计算指标
                df = analyzer.get_stock_data(ts_code, start_date or None, end_date or None)
                if df is not None:
                    df_with_indicators = analyzer.calculate_technical_indicators(df)
                    
                    # 生成分析报告
                    report = analyzer.generate_analysis_report(df_with_indicators, ts_code)
                    print("\n分析报告摘要:")
                    # 打印报告的前500个字符
                    print(report[:500] + "...")
            else:
                print("股票代码不能为空")
        
        elif choice == '0':
            print("程序已退出")
            break
        
        else:
            print("无效的选项，请重新输入")


if __name__ == "__main__":
    main()