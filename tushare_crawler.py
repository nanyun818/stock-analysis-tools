import tushare as ts
import pandas as pd
import os
from datetime import datetime
import time

# Tushare Pro API示例
# 注意：使用前需要在tushare.pro网站注册并获取token

class TushareCrawler:
    def __init__(self, token=None):
        """初始化Tushare爬虫
        
        Args:
            token: Tushare Pro的API token，可以从https://tushare.pro/register获取
        """
        self.token = token
        self.pro = None
        self.output_dir = 'tushare_data'
        
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
    
    def get_stock_list(self):
        """获取股票列表"""
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        try:
            df = self.pro.stock_basic(exchange='', list_status='L', 
                                    fields='ts_code,symbol,name,area,industry,list_date')
            # 保存数据
            file_path = os.path.join(self.output_dir, 'stock_list.csv')
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"股票列表已保存至 {file_path}")
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return None
    
    def get_daily_data(self, ts_code, start_date=None, end_date=None):
        """获取股票日线数据
        
        Args:
            ts_code: 股票代码（格式：000001.SZ）
            start_date: 开始日期（格式：YYYYMMDD）
            end_date: 结束日期（格式：YYYYMMDD）
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        # 如果未指定日期，默认获取最近一个月的数据
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            # 简单处理，获取近30天数据
            start_date = (datetime.now().replace(day=1)).strftime('%Y%m%d')
        
        try:
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            # 保存数据
            file_name = f"{ts_code.replace('.', '_')}_{start_date}_{end_date}.csv"
            file_path = os.path.join(self.output_dir, file_name)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"{ts_code} 的日线数据已保存至 {file_path}")
            return df
        except Exception as e:
            print(f"获取 {ts_code} 的日线数据失败: {e}")
            return None
    
    def get_financial_data(self, ts_code, period=None):
        """获取财务数据
        
        Args:
            ts_code: 股票代码（格式：000001.SZ）
            period: 报告期（格式：YYYYMM）
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        if not period:
            # 默认获取最近的财务报告
            now = datetime.now()
            if now.month < 4:
                period = f"{now.year-1}1231"  # 上一年年报
            elif now.month < 9:
                period = f"{now.year}0331"    # 一季报
            else:
                period = f"{now.year}0630"    # 中报
        
        try:
            # 获取利润表
            income_df = self.pro.income(ts_code=ts_code, period=period)
            # 获取资产负债表
            balance_df = self.pro.balancesheet(ts_code=ts_code, period=period)
            # 获取现金流量表
            cashflow_df = self.pro.cashflow(ts_code=ts_code, period=period)
            
            # 保存数据
            for name, df in [('income', income_df), ('balance', balance_df), ('cashflow', cashflow_df)]:
                if not df.empty:
                    file_name = f"{ts_code.replace('.', '_')}_{period}_{name}.csv"
                    file_path = os.path.join(self.output_dir, file_name)
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    print(f"{ts_code} 的{name}数据已保存至 {file_path}")
            
            return {
                'income': income_df,
                'balance': balance_df,
                'cashflow': cashflow_df
            }
        except Exception as e:
            print(f"获取 {ts_code} 的财务数据失败: {e}")
            return None
    
    def get_index_data(self, index_code='000001.SH', start_date=None, end_date=None):
        """获取指数数据
        
        Args:
            index_code: 指数代码（默认上证指数：000001.SH）
            start_date: 开始日期（格式：YYYYMMDD）
            end_date: 结束日期（格式：YYYYMMDD）
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        # 如果未指定日期，默认获取最近一个月的数据
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            # 简单处理，获取近30天数据
            start_date = (datetime.now().replace(day=1)).strftime('%Y%m%d')
        
        try:
            df = self.pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
            # 保存数据
            file_name = f"index_{index_code.replace('.', '_')}_{start_date}_{end_date}.csv"
            file_path = os.path.join(self.output_dir, file_name)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"{index_code} 的指数数据已保存至 {file_path}")
            return df
        except Exception as e:
            print(f"获取 {index_code} 的指数数据失败: {e}")
            return None

    def batch_download_stock_data(self, stock_list=None, days=30):
        """批量下载多只股票的历史数据
        
        Args:
            stock_list: 股票代码列表，如果为None则下载所有A股
            days: 获取天数
        """
        if not self.pro:
            print("请先登录Tushare Pro API")
            return
        
        # 如果未提供股票列表，获取所有A股
        if not stock_list:
            all_stocks = self.get_stock_list()
            if all_stocks is None:
                return
            stock_list = all_stocks['ts_code'].tolist()
        
        # 设置日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        # 简单处理，获取近N天数据
        start_date = (datetime.now().replace(day=1)).strftime('%Y%m%d')
        
        # 批量下载
        success_count = 0
        for i, ts_code in enumerate(stock_list):
            try:
                print(f"[{i+1}/{len(stock_list)}] 正在下载 {ts_code} 的数据...")
                self.get_daily_data(ts_code, start_date, end_date)
                success_count += 1
                # 避免请求过于频繁
                time.sleep(0.5)
            except Exception as e:
                print(f"下载 {ts_code} 的数据失败: {e}")
        
        print(f"批量下载完成，成功下载 {success_count}/{len(stock_list)} 只股票的数据")


def main():
    # 使用示例
    print("Tushare金融数据爬虫示例")
    print("-" * 40)
    
    # 创建爬虫实例
    # 请替换为你的token
    token = input("请输入你的Tushare Pro API token: ")
    crawler = TushareCrawler(token)
    
    # 登录
    if not crawler.login():
        return
    
    while True:
        print("\n请选择操作:")
        print("1. 获取股票列表")
        print("2. 获取单只股票日线数据")
        print("3. 获取指数数据")
        print("4. 获取财务数据")
        print("5. 批量下载股票数据")
        print("0. 退出")
        
        choice = input("请输入选项编号: ")
        
        if choice == '1':
            crawler.get_stock_list()
        elif choice == '2':
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            crawler.get_daily_data(ts_code, start_date or None, end_date or None)
        elif choice == '3':
            index_code = input("请输入指数代码(默认上证指数: 000001.SH): ") or '000001.SH'
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            crawler.get_index_data(index_code, start_date or None, end_date or None)
        elif choice == '4':
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            period = input("请输入报告期(YYYYMMDD，可留空): ")
            crawler.get_financial_data(ts_code, period or None)
        elif choice == '5':
            num = input("请输入要下载的股票数量(留空则下载所有): ")
            if num:
                # 获取股票列表的前N只
                stock_list = crawler.get_stock_list()
                if stock_list is not None:
                    stock_list = stock_list['ts_code'].head(int(num)).tolist()
                    crawler.batch_download_stock_data(stock_list)
            else:
                crawler.batch_download_stock_data()
        elif choice == '0':
            print("程序已退出")
            break
        else:
            print("无效的选项，请重新输入")


if __name__ == "__main__":
    main()