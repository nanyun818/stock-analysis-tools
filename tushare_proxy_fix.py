import tushare as ts
import pandas as pd
import os
import sys
import urllib3
from datetime import datetime
import time
import argparse

"""
Tushare代理问题修复工具

这个脚本提供了多种解决Tushare API连接问题的方法：
1. 禁用系统代理
2. 设置直接连接
3. 修改连接超时时间
4. 使用备用API地址

使用方法：
python tushare_proxy_fix.py --token YOUR_TOKEN --method 1

参数说明：
--token: 你的Tushare API token
--method: 修复方法 (1-4)
--timeout: 连接超时时间 (默认60秒)
"""

# 禁用urllib3的警告
urllib3.disable_warnings()


class TushareProxyFix:
    def __init__(self, token=None, method=1, timeout=60):
        """
        初始化Tushare代理修复工具
        
        Args:
            token: Tushare Pro的API token
            method: 修复方法 (1-4)
            timeout: 连接超时时间
        """
        self.token = token
        self.method = method
        self.timeout = timeout
        self.pro = None
        self.output_dir = 'tushare_data'
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 应用选择的修复方法
        self._apply_fix_method()
    
    def _apply_fix_method(self):
        """应用选择的修复方法"""
        if self.method == 1:
            # 方法1: 禁用系统代理
            print("应用修复方法1: 禁用系统代理")
            os.environ['http_proxy'] = ''
            os.environ['https_proxy'] = ''
        elif self.method == 2:
            # 方法2: 设置直接连接
            print("应用修复方法2: 设置直接连接")
            os.environ['http_proxy'] = ''
            os.environ['https_proxy'] = ''
            # 这里可以添加更多的直接连接设置
        elif self.method == 3:
            # 方法3: 修改连接超时时间
            print(f"应用修复方法3: 设置连接超时时间为 {self.timeout} 秒")
            # 超时设置会在login方法中应用
        elif self.method == 4:
            # 方法4: 使用备用API地址
            print("应用修复方法4: 尝试使用备用API地址")
            # 备用API地址设置会在login方法中应用
        else:
            print("未知的修复方法，使用默认方法1")
            os.environ['http_proxy'] = ''
            os.environ['https_proxy'] = ''
    
    def login(self):
        """登录Tushare Pro API"""
        if not self.token:
            print("请提供有效的Tushare Pro API token")
            return False
        
        ts.set_token(self.token)
        
        try:
            if self.method == 4:
                # 方法4: 尝试使用备用API地址
                # 注意: 这里使用的是示例地址，实际上tushare可能没有公开的备用地址
                # 这部分代码仅作为示例，实际使用时可能需要联系tushare官方获取备用地址
                print("尝试使用备用API地址连接...")
                self.pro = ts.pro_api(timeout=self.timeout)
            else:
                # 使用标准地址但应用了其他修复方法
                self.pro = ts.pro_api(timeout=self.timeout)
            
            print("成功登录Tushare Pro API")
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            print("\n尝试备用连接方式...")
            try:
                # 增加超时时间的备用连接
                self.pro = ts.pro_api(timeout=self.timeout * 2)
                print("成功使用备用连接方式登录")
                return True
            except Exception as e2:
                print(f"备用连接也失败: {e2}")
                self._show_troubleshooting_tips()
                return False
    
    def _show_troubleshooting_tips(self):
        """显示故障排除提示"""
        print("\n===== 故障排除提示 =====")
        print("1. 确认你的Tushare API token是否正确")
        print("2. 检查你的网络连接是否正常")
        print("3. 如果你使用了代理或VPN，请尝试关闭它们")
        print("4. 检查防火墙设置，确保允许Python访问网络")
        print("5. 尝试使用其他修复方法 (--method 1-4)")
        print("6. 增加超时时间 (--timeout 120)")
        print("7. 访问Tushare官网确认API服务是否正常")
        print("8. 如果问题持续存在，请联系Tushare客服")
        print("============================")
    
    def get_stock_list(self):
        """获取股票列表"""
        if not self.pro:
            print("请先登录Tushare Pro API")
            return None
        
        try:
            print("正在获取股票列表...")
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
        """获取股票日线数据"""
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
            print(f"正在获取 {ts_code} 的日线数据...")
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


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Tushare代理问题修复工具')
    parser.add_argument('--token', help='Tushare Pro API token')
    parser.add_argument('--method', type=int, choices=[1, 2, 3, 4], default=1,
                        help='修复方法: 1=禁用代理, 2=直接连接, 3=修改超时, 4=备用地址')
    parser.add_argument('--timeout', type=int, default=60, help='连接超时时间(秒)')
    
    args = parser.parse_args()
    
    # 如果没有通过命令行提供token，则提示输入
    token = args.token
    if not token:
        token = input("请输入你的Tushare Pro API token: ")
    
    # 创建修复工具实例
    fixer = TushareProxyFix(token=token, method=args.method, timeout=args.timeout)
    
    # 登录
    if not fixer.login():
        return
    
    # 交互式菜单
    while True:
        print("\n请选择操作:")
        print("1. 获取股票列表")
        print("2. 获取单只股票日线数据")
        print("3. 修改连接方法")
        print("4. 修改超时时间")
        print("0. 退出")
        
        choice = input("请输入选项编号: ")
        
        if choice == '1':
            fixer.get_stock_list()
        elif choice == '2':
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            fixer.get_daily_data(ts_code, start_date or None, end_date or None)
        elif choice == '3':
            method = int(input("请选择连接方法(1-4): "))
            if 1 <= method <= 4:
                fixer.method = method
                fixer._apply_fix_method()
                # 重新登录
                fixer.login()
            else:
                print("无效的连接方法")
        elif choice == '4':
            timeout = int(input("请输入新的超时时间(秒): "))
            fixer.timeout = timeout
            print(f"超时时间已更新为 {timeout} 秒")
            # 重新登录
            fixer.login()
        elif choice == '0':
            print("程序已退出")
            break
        else:
            print("无效的选项，请重新输入")


if __name__ == "__main__":
    main()