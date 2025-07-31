import asyncio
import os
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.cache_strategy import CacheMode

async def main():
    # 配置浏览器选项
    browser_config = BrowserConfig(
        headless=True,  # 无头模式，设为False可以看到浏览器界面
        verbose=True,   # 显示详细日志
    )
    
    # 创建内容过滤器 - 使用修剪策略去除不相关内容
    content_filter = PruningContentFilter(
        threshold=0.5,        # 过滤阈值
        threshold_type="fixed",  # 固定阈值类型
        min_word_threshold=10    # 最小词数阈值
    )
    
    # 创建Markdown生成器
    md_generator = DefaultMarkdownGenerator(content_filter=content_filter)
    
    # 配置爬虫运行选项
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # 绕过缓存，始终获取新内容
        markdown_generator=md_generator,
        word_count_threshold=10,        # 最小词数阈值
        exclude_external_links=True,    # 排除外部链接
        remove_overlay_elements=True,   # 移除覆盖元素
        process_iframes=True            # 处理iframe内容
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 运行爬虫
        result = await crawler.arun(
            url="https://news.ycombinator.com",  # 示例：Hacker News
            config=run_config
        )
        
        # 打印原始和过滤后的Markdown长度比较
        print(f"原始Markdown长度: {len(result.markdown.raw_markdown)}字符")
        print(f"过滤后Markdown长度: {len(result.markdown.fit_markdown)}字符")
        
        # 保存原始和过滤后的Markdown到文件
        os.makedirs("output", exist_ok=True)
        
        with open("output/raw_output.md", "w", encoding="utf-8") as f:
            f.write(result.markdown.raw_markdown)
        
        with open("output/filtered_output.md", "w", encoding="utf-8") as f:
            f.write(result.markdown.fit_markdown)
        
        print("\nMarkdown内容已保存到 output/raw_output.md 和 output/filtered_output.md")

if __name__ == "__main__":
    asyncio.run(main())