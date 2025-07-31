import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Tushare金融数据爬虫工具')
    parser.add_argument('action', choices=['basic', 'finance', 'analysis', 'help'],
                        help='要执行的操作: basic(基本爬虫), finance(财经网站爬虫), analysis(股票分析), help(显示帮助)')
    parser.add_argument('--token', '-t', help='Tushare Pro API token')
    parser.add_argument('--stock', '-s', help='股票代码，如000001.SZ')
    parser.add_argument('--start', help='开始日期，格式YYYYMMDD')
    parser.add_argument('--end', help='结束日期，格式YYYYMMDD')
    parser.add_argument('--output', '-o', help='输出目录')
    
    # 解析命令行参数
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # 显示帮助信息
    if args.action == 'help':
        show_help()
        return
    
    # 检查Python环境
    try:
        import tushare
        import pandas
        if args.action == 'finance':
            from crawl4ai import AsyncWebCrawler
        if args.action == 'analysis':
            import matplotlib
            import numpy
    except ImportError as e:
        print(f"错误: 缺少必要的依赖包 - {e}")
        print("请先运行 'pip install -r requirements.txt' 安装依赖")
        return
    
    # 执行相应的操作
    if args.action == 'basic':
        run_basic_crawler(args)
    elif args.action == 'finance':
        run_finance_crawler(args)
    elif args.action == 'analysis':
        run_stock_analysis(args)


def show_help():
    """显示详细的帮助信息"""
    help_text = """
    Tushare金融数据爬虫工具使用指南
    ============================
    
    本工具提供了三种不同的功能模块：
    
    1. 基本爬虫 (basic)
       使用Tushare API获取股票、指数等基础金融数据
       
       示例:
       python run_tushare.py basic -t YOUR_TOKEN -s 000001.SZ
       python run_tushare.py basic -t YOUR_TOKEN -s 000001.SZ --start 20230101 --end 20231231
    
    2. 财经网站爬虫 (finance)
       结合Tushare API和crawl4ai网页爬虫功能，爬取财经新闻和论坛
       
       示例:
       python run_tushare.py finance -t YOUR_TOKEN -s 000001
    
    3. 股票分析 (analysis)
       使用Tushare数据进行技术分析并生成报告
       
       示例:
       python run_tushare.py analysis -t YOUR_TOKEN -s 000001.SZ
       python run_tushare.py analysis -t YOUR_TOKEN -s 000001.SZ --start 20230101 --end 20231231
    
    参数说明:
    -t, --token    Tushare Pro API token (必需)
    -s, --stock    股票代码 (必需)
    --start        开始日期，格式YYYYMMDD (可选)
    --end          结束日期，格式YYYYMMDD (可选)
    -o, --output   输出目录 (可选)
    
    获取Tushare API Token:
    1. 访问 https://tushare.pro/register 注册账号
    2. 登录后在个人中心获取token
    
    注意事项:
    - 使用前请确保已安装所需依赖: pip install -r requirements.txt
    - Tushare Pro API的使用受到积分限制，请合理使用
    - 网页爬虫请遵守网站的robots.txt规则和使用条款
    """
    print(help_text)


def run_basic_crawler(args):
    """运行基本的Tushare爬虫"""
    if not args.token:
        print("错误: 使用基本爬虫需要提供Tushare Pro API token")
        print("使用 --token 或 -t 参数提供token")
        return
    
    if not args.stock:
        print("错误: 请提供股票代码")
        print("使用 --stock 或 -s 参数提供股票代码")
        return
    
    print(f"正在启动基本爬虫模块...")
    print(f"股票代码: {args.stock}")
    
    # 导入tushare_crawler模块
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from tushare_crawler import TushareCrawler
        
        # 创建爬虫实例
        crawler = TushareCrawler(args.token)
        if not crawler.login():
            return
        
        # 获取股票数据
        if args.stock:
            print(f"\n获取 {args.stock} 的日线数据...")
            crawler.get_daily_data(args.stock, args.start, args.end)
            
            print(f"\n获取 {args.stock} 的财务数据...")
            crawler.get_financial_data(args.stock)
    
    except Exception as e:
        print(f"运行基本爬虫时出错: {e}")


def run_finance_crawler(args):
    """运行财经网站爬虫"""
    if not args.stock:
        print("错误: 请提供股票代码")
        print("使用 --stock 或 -s 参数提供股票代码")
        return
    
    print(f"正在启动财经网站爬虫模块...")
    print(f"股票代码: {args.stock}")
    
    # 导入finance_crawler模块
    try:
        import asyncio
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from finance_crawler import FinanceCrawler
        
        # 创建爬虫实例
        crawler = FinanceCrawler(args.token)
        if args.token:
            crawler.login_tushare()
        
        # 定义异步主函数
        async def run():
            print(f"\n爬取 {args.stock} 相关新闻...")
            await crawler.crawl_stock_news(args.stock)
            
            print(f"\n爬取 {args.stock} 论坛讨论...")
            await crawler.crawl_stock_forum(args.stock)
            
            if crawler.pro:
                print(f"\n获取 {args.stock} 的历史数据...")
                crawler.get_stock_data(args.stock, args.start, args.end)
            
            print(f"\n分析 {args.stock} 的情感...")
            await crawler.analyze_stock_sentiment(args.stock)
        
        # 运行异步函数
        asyncio.run(run())
    
    except Exception as e:
        print(f"运行财经网站爬虫时出错: {e}")


def run_stock_analysis(args):
    """运行股票分析"""
    if not args.token:
        print("错误: 使用股票分析需要提供Tushare Pro API token")
        print("使用 --token 或 -t 参数提供token")
        return
    
    if not args.stock:
        print("错误: 请提供股票代码")
        print("使用 --stock 或 -s 参数提供股票代码")
        return
    
    print(f"正在启动股票分析模块...")
    print(f"股票代码: {args.stock}")
    
    # 导入stock_analysis模块
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from stock_analysis import StockAnalyzer
        
        # 创建分析器实例
        analyzer = StockAnalyzer(args.token)
        if not analyzer.login():
            return
        
        # 获取股票数据并计算指标
        print(f"\n获取 {args.stock} 的历史数据并计算技术指标...")
        df = analyzer.get_stock_data(args.stock, args.start, args.end)
        if df is not None:
            df_with_indicators = analyzer.calculate_technical_indicators(df)
            
            # 绘制图表
            print("\n绘制技术分析图表...")
            analyzer.plot_stock_price(df_with_indicators, args.stock)
            analyzer.plot_volume(df_with_indicators, args.stock)
            analyzer.plot_macd(df_with_indicators, args.stock)
            analyzer.plot_kdj(df_with_indicators, args.stock)
            analyzer.plot_boll(df_with_indicators, args.stock)
            
            # 生成分析报告
            print("\n生成分析报告...")
            analyzer.generate_analysis_report(df_with_indicators, args.stock)
    
    except Exception as e:
        print(f"运行股票分析时出错: {e}")


if __name__ == "__main__":
    main()