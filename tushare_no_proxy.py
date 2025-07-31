import tushare as ts
import pandas as pd
import os
from datetime import datetime
import time
import urllib3

# 禁用代理设置
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# 禁用urllib3的警告
urllib3.disable_warnings()

class TushareCrawlerNoProxy:
    def __init__(self, token=None):
        """初始化Tushare爬虫（无代理版本）
        
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
            # 设置无代理连接
            ts.set_token(self.token)
            try:
                self.pro = ts.pro_api(timeout=30)
                print("成功登录Tushare Pro API")
                return True
            except Exception as e:
                print(f"登录失败: {e}")
                print("尝试使用备用连接方式...")
                try:
                    # 备用连接方式
                    self.pro = ts.pro_api(timeout=60)
                    print("成功使用备用方式登录Tushare Pro API")
                    return True
                except Exception as e2:
                    print(f"备用连接也失败: {e2}")
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
            # 保存数据
            file_path = os.path.join(self.output_dir, 'stock_list.csv')
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"股票列表已保存至 {file_path}")
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return None

def main():
    # 使用示例
    print("Tushare金融数据爬虫示例（无代理版本）")
    print("-" * 40)
    
    # 创建爬虫实例
    token = input("请输入你的Tushare Pro API token: ")
    crawler = TushareCrawlerNoProxy(token)
    
    # 登录
    if not crawler.login():
        return
    
    while True:
        print("\n请选择操作:")
        print("1. 获取股票列表")
        print("0. 退出")
        
        choice = input("请输入选项编号: ")
        
        if choice == '1':
            crawler.get_stock_list()
        elif choice == '0':
            print("程序已退出")
            break
        else:
            print("无效的选项，请重新输入")


if __name__ == "__main__":
    main()