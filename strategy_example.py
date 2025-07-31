#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化交易策略示例
基于easyquant框架的简单移动平均策略
"""

import time
import datetime as dt
from dateutil import tz
import pandas as pd
import numpy as np

try:
    from easyquant import StrategyTemplate, DefaultLogHandler
    import easyquant
    import easytrader
    import akshare as ak
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"模块导入失败: {e}")
    MODULES_AVAILABLE = False

class MovingAverageStrategy(StrategyTemplate):
    """
    移动平均策略
    
    策略逻辑：
    1. 计算5日和20日移动平均线
    2. 当5日均线上穿20日均线时买入
    3. 当5日均线下穿20日均线时卖出
    4. 设置止损和止盈点
    """
    
    name = '移动平均策略'
    
    def __init__(self):
        super().__init__()
        # 策略参数
        self.short_window = 5   # 短期均线周期
        self.long_window = 20   # 长期均线周期
        self.stop_loss = 0.05   # 止损比例 5%
        self.take_profit = 0.10 # 止盈比例 10%
        
        # 持仓信息
        self.positions = {}
        self.last_prices = {}
        
        # 股票池（可以根据需要修改）
        self.stock_pool = ['000001', '000002', '000858', '002415', '600036']
        
    def init(self):
        """策略初始化"""
        print(f"初始化策略: {self.name}")
        
        # 注册定时事件
        # 每天开盘后30分钟执行策略
        morning_time = dt.time(9, 30, 0, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment("morning_check", morning_time)
        
        # 每天收盘前30分钟执行策略
        afternoon_time = dt.time(14, 30, 0, tzinfo=tz.tzlocal())
        self.clock_engine.register_moment("afternoon_check", afternoon_time)
        
        # 每5分钟检查一次止损止盈
        self.clock_engine.register_interval("risk_check", 300)  # 300秒 = 5分钟
        
        print("策略初始化完成")
    
    def on_clock_event(self, event):
        """时钟事件处理"""
        clock_type = event.data['clock_type']
        
        if clock_type == "morning_check":
            self.morning_strategy()
        elif clock_type == "afternoon_check":
            self.afternoon_strategy()
        elif clock_type == "risk_check":
            self.risk_management()
    
    def morning_strategy(self):
        """早盘策略"""
        print("执行早盘策略检查...")
        
        for stock_code in self.stock_pool:
            try:
                # 获取历史数据
                data = self.get_stock_data(stock_code)
                if data is None or len(data) < self.long_window:
                    continue
                
                # 计算移动平均线
                data['MA5'] = data['close'].rolling(window=self.short_window).mean()
                data['MA20'] = data['close'].rolling(window=self.long_window).mean()
                
                # 获取最新数据
                latest = data.iloc[-1]
                prev = data.iloc[-2]
                
                # 检查买入信号
                if self.check_buy_signal(latest, prev, stock_code):
                    self.execute_buy(stock_code, latest['close'])
                
                # 检查卖出信号
                elif self.check_sell_signal(latest, prev, stock_code):
                    self.execute_sell(stock_code, latest['close'])
                    
            except Exception as e:
                print(f"处理股票 {stock_code} 时出错: {e}")
    
    def afternoon_strategy(self):
        """午盘策略"""
        print("执行午盘策略检查...")
        # 可以在这里添加午盘特定的策略逻辑
        pass
    
    def risk_management(self):
        """风险管理"""
        """检查止损止盈"""
        for stock_code, position in self.positions.items():
            try:
                # 获取当前价格
                current_price = self.get_current_price(stock_code)
                if current_price is None:
                    continue
                
                buy_price = position['price']
                quantity = position['quantity']
                
                # 计算收益率
                return_rate = (current_price - buy_price) / buy_price
                
                # 止损检查
                if return_rate <= -self.stop_loss:
                    print(f"触发止损: {stock_code}, 收益率: {return_rate:.2%}")
                    self.execute_sell(stock_code, current_price, "止损")
                
                # 止盈检查
                elif return_rate >= self.take_profit:
                    print(f"触发止盈: {stock_code}, 收益率: {return_rate:.2%}")
                    self.execute_sell(stock_code, current_price, "止盈")
                    
            except Exception as e:
                print(f"风险管理检查 {stock_code} 时出错: {e}")
    
    def check_buy_signal(self, latest, prev, stock_code):
        """检查买入信号"""
        # 检查是否已持仓
        if stock_code in self.positions:
            return False
        
        # 金叉信号：5日均线上穿20日均线
        if (latest['MA5'] > latest['MA20'] and 
            prev['MA5'] <= prev['MA20']):
            
            # 额外条件：成交量放大
            volume_ratio = latest['volume'] / data['volume'].rolling(10).mean().iloc[-1]
            if volume_ratio > 1.2:  # 成交量比10日均量大20%
                print(f"发现买入信号: {stock_code}")
                return True
        
        return False
    
    def check_sell_signal(self, latest, prev, stock_code):
        """检查卖出信号"""
        # 检查是否持仓
        if stock_code not in self.positions:
            return False
        
        # 死叉信号：5日均线下穿20日均线
        if (latest['MA5'] < latest['MA20'] and 
            prev['MA5'] >= prev['MA20']):
            print(f"发现卖出信号: {stock_code}")
            return True
        
        return False
    
    def execute_buy(self, stock_code, price):
        """执行买入"""
        try:
            # 计算买入数量（这里简单设置为1000股）
            quantity = 1000
            
            # 执行买入订单
            result = self.trader.buy(stock_code, price=price, amount=quantity)
            
            if result:
                # 记录持仓
                self.positions[stock_code] = {
                    'price': price,
                    'quantity': quantity,
                    'time': dt.datetime.now()
                }
                
                print(f"买入成功: {stock_code}, 价格: {price}, 数量: {quantity}")
                
                # 发送通知（可选）
                self.send_notification(f"买入 {stock_code}")
            
        except Exception as e:
            print(f"买入失败: {stock_code}, 错误: {e}")
    
    def execute_sell(self, stock_code, price, reason="策略信号"):
        """执行卖出"""
        try:
            if stock_code not in self.positions:
                return
            
            position = self.positions[stock_code]
            quantity = position['quantity']
            
            # 执行卖出订单
            result = self.trader.sell(stock_code, price=price, amount=quantity)
            
            if result:
                # 计算收益
                buy_price = position['price']
                profit = (price - buy_price) * quantity
                return_rate = (price - buy_price) / buy_price
                
                print(f"卖出成功: {stock_code}, 价格: {price}, 数量: {quantity}")
                print(f"收益: {profit:.2f}, 收益率: {return_rate:.2%}, 原因: {reason}")
                
                # 移除持仓记录
                del self.positions[stock_code]
                
                # 发送通知（可选）
                self.send_notification(f"卖出 {stock_code}, 收益率: {return_rate:.2%}")
            
        except Exception as e:
            print(f"卖出失败: {stock_code}, 错误: {e}")
    
    def get_stock_data(self, stock_code, days=30):
        """获取股票历史数据"""
        try:
            # 使用akshare获取数据
            end_date = dt.datetime.now().strftime('%Y%m%d')
            start_date = (dt.datetime.now() - dt.timedelta(days=days)).strftime('%Y%m%d')
            
            data = ak.stock_zh_a_hist(symbol=stock_code, 
                                     start_date=start_date, 
                                     end_date=end_date)
            
            if data is not None and not data.empty:
                # 重命名列名
                data.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 
                               'amount', 'amplitude', 'change_pct', 'change', 'turnover']
                data['date'] = pd.to_datetime(data['date'])
                data.set_index('date', inplace=True)
                return data
            
        except Exception as e:
            print(f"获取股票数据失败: {stock_code}, 错误: {e}")
        
        return None
    
    def get_current_price(self, stock_code):
        """获取当前股价"""
        try:
            # 获取实时行情
            realtime_data = ak.stock_zh_a_spot_em()
            stock_info = realtime_data[realtime_data['代码'] == stock_code]
            
            if not stock_info.empty:
                return float(stock_info.iloc[0]['最新价'])
                
        except Exception as e:
            print(f"获取实时价格失败: {stock_code}, 错误: {e}")
        
        return None
    
    def send_notification(self, message):
        """发送通知（可以扩展为微信、邮件等）"""
        timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] 通知: {message}")
    
    def on_quotation_event(self, event):
        """行情事件处理"""
        # 可以在这里处理实时行情数据
        pass

def create_strategy_engine():
    """创建策略引擎"""
    if not MODULES_AVAILABLE:
        print("必要模块未安装，无法运行策略")
        return None
    
    try:
        # 创建交易接口（这里使用雪球模拟盘作为示例）
        trader = easytrader.use('xq')
        trader.prepare('config_examples/xq.json')  # 需要配置文件
        
        # 创建日志处理器
        log_handler = DefaultLogHandler(name='策略日志', 
                                       log_type='file', 
                                       filepath='strategy.log')
        
        # 创建主引擎
        engine = easyquant.MainEngine(trader, 
                                     need_data=['stock'],
                                     log_handler=log_handler)
        
        # 加载策略
        strategy = MovingAverageStrategy()
        engine.load_strategy(strategy)
        
        return engine
        
    except Exception as e:
        print(f"创建策略引擎失败: {e}")
        return None

def main():
    """主函数"""
    print("量化交易策略示例")
    print("==================")
    
    # 创建策略引擎
    engine = create_strategy_engine()
    
    if engine:
        print("策略引擎创建成功，开始运行...")
        print("按 Ctrl+C 停止策略")
        
        try:
            # 启动策略
            engine.start()
        except KeyboardInterrupt:
            print("\n策略已停止")
        except Exception as e:
            print(f"策略运行出错: {e}")
    else:
        print("策略引擎创建失败")

if __name__ == "__main__":
    main()