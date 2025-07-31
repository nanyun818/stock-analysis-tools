import asyncio
import os
import json
from datetime import datetime
import pandas as pd
import tushare as ts
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy


class FinanceCrawler:
    def __init__(self, tushare_token=None):
        """初始化财经爬虫
        
        Args:
            tushare_token: Tushare Pro的API token
        """
        self.tushare_token = tushare_token
        self.pro = None
        self.output_dir = 'finance_data'
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def login_tushare(self):
        """登录Tushare Pro API"""
        if self.tushare_token:
            ts.set_token(self.tushare_token)
            self.pro = ts.pro_api()
            print("成功登录Tushare Pro API")
            return True
        else:
            print("未提供Tushare Pro API token，部分功能将不可用")
            return False
    
    async def crawl_stock_news(self, stock_code=None, pages=1):
        """爬取股票相关新闻
        
        Args:
            stock_code: 股票代码，如果为None则爬取财经首页新闻
            pages: 爬取的页面数量
        """
        # 根据是否有股票代码决定爬取的URL
        if stock_code:
            # 这里使用东方财富网的股票新闻页面，实际URL可能需要调整
            base_url = f"http://finance.eastmoney.com/a/{stock_code}.html"
        else:
            # 使用新浪财经首页
            base_url = "https://finance.sina.com.cn/"
        
        # 创建爬虫配置
        config = CrawlerRunConfig(
            cache_mode="memory",  # 使用内存缓存
            browser_options={"headless": True},  # 无头浏览器模式
            extraction_strategy=JsonCssExtractionStrategy({
                "news": {
                    "items": ".news-item",  # 新闻项的CSS选择器
                    "fields": {
                        "title": ".news-title",
                        "summary": ".news-summary",
                        "time": ".news-time",
                        "source": ".news-source",
                        "url": {"selector": "a", "attribute": "href"}
                    }
                }
            })
        )
        
        # 创建爬虫实例
        async with AsyncWebCrawler() as crawler:
            print(f"正在爬取 {base_url} 的新闻...")
            result = await crawler.arun(url=base_url, config=config)
            
            # 保存提取的数据
            if result.extracted_data and 'news' in result.extracted_data:
                news_data = result.extracted_data['news']
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"news_{stock_code or 'finance'}_{timestamp}.json"
                file_path = os.path.join(self.output_dir, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(news_data, f, ensure_ascii=False, indent=2)
                print(f"新闻数据已保存至 {file_path}")
                
                # 同时保存Markdown格式的内容
                md_file_path = os.path.join(self.output_dir, f"news_{stock_code or 'finance'}_{timestamp}.md")
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# 财经新闻 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for item in news_data:
                        f.write(f"## {item.get('title', '无标题')}\n")
                        f.write(f"来源: {item.get('source', '未知')} | 时间: {item.get('time', '未知')}\n\n")
                        f.write(f"{item.get('summary', '无摘要')}\n\n")
                        f.write(f"[阅读全文]({item.get('url', '#')})\n\n---\n\n")
                print(f"新闻数据(Markdown格式)已保存至 {md_file_path}")
                
                return news_data
            else:
                print("未能提取到新闻数据")
                return None
    
    async def crawl_stock_forum(self, stock_code):
        """爬取股票论坛讨论
        
        Args:
            stock_code: 股票代码
        """
        # 这里使用东方财富股吧作为示例
        url = f"http://guba.eastmoney.com/list,{stock_code}.html"
        
        # 创建爬虫配置
        config = CrawlerRunConfig(
            cache_mode="memory",
            browser_options={"headless": True},
            extraction_strategy=JsonCssExtractionStrategy({
                "posts": {
                    "items": ".article_item",  # 帖子项的CSS选择器
                    "fields": {
                        "title": ".article_title",
                        "author": ".article_author",
                        "time": ".article_time",
                        "views": ".article_views",
                        "url": {"selector": "a", "attribute": "href"}
                    }
                }
            })
        )
        
        # 创建爬虫实例
        async with AsyncWebCrawler() as crawler:
            print(f"正在爬取 {url} 的论坛讨论...")
            result = await crawler.arun(url=url, config=config)
            
            # 保存提取的数据
            if result.extracted_data and 'posts' in result.extracted_data:
                posts_data = result.extracted_data['posts']
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"forum_{stock_code}_{timestamp}.json"
                file_path = os.path.join(self.output_dir, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(posts_data, f, ensure_ascii=False, indent=2)
                print(f"论坛数据已保存至 {file_path}")
                
                return posts_data
            else:
                print("未能提取到论坛数据")
                return None
    
    def get_stock_data(self, stock_code, start_date=None, end_date=None):
        """获取股票历史数据
        
        Args:
            stock_code: 股票代码（格式：000001.SZ）
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
            df = self.pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
            # 保存数据
            file_name = f"{stock_code.replace('.', '_')}_{start_date}_{end_date}.csv"
            file_path = os.path.join(self.output_dir, file_name)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"{stock_code} 的历史数据已保存至 {file_path}")
            return df
        except Exception as e:
            print(f"获取 {stock_code} 的历史数据失败: {e}")
            return None
    
    async def analyze_stock_sentiment(self, stock_code):
        """分析股票相关新闻和论坛的情感
        
        Args:
            stock_code: 股票代码
        """
        # 爬取新闻和论坛数据
        news_data = await self.crawl_stock_news(stock_code)
        forum_data = await self.crawl_stock_forum(stock_code)
        
        # 这里可以添加情感分析的代码
        # 简单示例：统计标题中的关键词
        positive_keywords = ['涨', '利好', '增长', '突破', '机会', '看好']
        negative_keywords = ['跌', '利空', '下跌', '风险', '警惕', '担忧']
        
        sentiment_results = {
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'total_count': 0
        }
        
        # 分析新闻情感
        if news_data:
            for item in news_data:
                title = item.get('title', '')
                sentiment_results['total_count'] += 1
                
                is_positive = any(keyword in title for keyword in positive_keywords)
                is_negative = any(keyword in title for keyword in negative_keywords)
                
                if is_positive and not is_negative:
                    sentiment_results['positive_count'] += 1
                elif is_negative and not is_positive:
                    sentiment_results['negative_count'] += 1
                else:
                    sentiment_results['neutral_count'] += 1
        
        # 分析论坛情感
        if forum_data:
            for item in forum_data:
                title = item.get('title', '')
                sentiment_results['total_count'] += 1
                
                is_positive = any(keyword in title for keyword in positive_keywords)
                is_negative = any(keyword in title for keyword in negative_keywords)
                
                if is_positive and not is_negative:
                    sentiment_results['positive_count'] += 1
                elif is_negative and not is_positive:
                    sentiment_results['negative_count'] += 1
                else:
                    sentiment_results['neutral_count'] += 1
        
        # 保存情感分析结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"sentiment_{stock_code}_{timestamp}.json"
        file_path = os.path.join(self.output_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sentiment_results, f, ensure_ascii=False, indent=2)
        print(f"情感分析结果已保存至 {file_path}")
        
        # 打印简单的情感分析报告
        print("\n情感分析报告:")
        print(f"总计分析条目: {sentiment_results['total_count']}")
        if sentiment_results['total_count'] > 0:
            positive_percent = sentiment_results['positive_count'] / sentiment_results['total_count'] * 100
            negative_percent = sentiment_results['negative_count'] / sentiment_results['total_count'] * 100
            neutral_percent = sentiment_results['neutral_count'] / sentiment_results['total_count'] * 100
            
            print(f"积极情感: {sentiment_results['positive_count']} ({positive_percent:.1f}%)")
            print(f"消极情感: {sentiment_results['negative_count']} ({negative_percent:.1f}%)")
            print(f"中性情感: {sentiment_results['neutral_count']} ({neutral_percent:.1f}%)")
            
            # 简单的情感判断
            if positive_percent > negative_percent + 10:
                print("整体情感: 积极 😊")
            elif negative_percent > positive_percent + 10:
                print("整体情感: 消极 😞")
            else:
                print("整体情感: 中性 😐")
        
        return sentiment_results


async def main():
    print("财经数据爬虫与分析示例")
    print("-" * 40)
    
    # 创建爬虫实例
    token = input("请输入你的Tushare Pro API token (可留空): ")
    crawler = FinanceCrawler(token)
    
    # 尝试登录Tushare
    crawler.login_tushare()
    
    while True:
        print("\n请选择操作:")
        print("1. 爬取财经新闻")
        print("2. 爬取股票论坛讨论")
        print("3. 获取股票历史数据 (需要Tushare token)")
        print("4. 股票情感分析")
        print("0. 退出")
        
        choice = input("请输入选项编号: ")
        
        if choice == '1':
            stock_code = input("请输入股票代码(可留空爬取财经首页): ")
            await crawler.crawl_stock_news(stock_code or None)
        elif choice == '2':
            stock_code = input("请输入股票代码(如: 000001): ")
            if stock_code:
                await crawler.crawl_stock_forum(stock_code)
            else:
                print("股票代码不能为空")
        elif choice == '3':
            if not crawler.pro:
                print("此功能需要Tushare Pro API token")
                continue
                
            ts_code = input("请输入股票代码(如: 000001.SZ): ")
            start_date = input("请输入开始日期(YYYYMMDD，可留空): ")
            end_date = input("请输入结束日期(YYYYMMDD，可留空): ")
            if ts_code:
                crawler.get_stock_data(ts_code, start_date or None, end_date or None)
            else:
                print("股票代码不能为空")
        elif choice == '4':
            stock_code = input("请输入股票代码(如: 000001): ")
            if stock_code:
                await crawler.analyze_stock_sentiment(stock_code)
            else:
                print("股票代码不能为空")
        elif choice == '0':
            print("程序已退出")
            break
        else:
            print("无效的选项，请重新输入")


if __name__ == "__main__":
    asyncio.run(main())