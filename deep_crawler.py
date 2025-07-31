import asyncio
import os
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.deep_crawl_strategy import DeepCrawlStrategy, DeepCrawlMode

async def main():
    # 创建深度爬取策略
    deep_crawl_strategy = DeepCrawlStrategy(
        mode=DeepCrawlMode.BFS,  # 广度优先搜索模式
        max_pages=5,             # 最多爬取5个页面
        max_depth=2,             # 最大深度为2
        # 只爬取包含特定路径的URL
        url_patterns=["docs.crawl4ai.com"],
        # 排除包含特定路径的URL
        exclude_patterns=["github.com", "discord.gg"]
    )
    
    # 配置爬虫运行选项
    run_config = CrawlerRunConfig(
        deep_crawl_strategy=deep_crawl_strategy
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler() as crawler:
        # 运行爬虫
        result = await crawler.arun(
            url="https://docs.crawl4ai.com",  # 起始URL
            config=run_config
        )
        
        # 打印爬取的页面数量
        print(f"\n共爬取了 {len(result.deep_crawl_results)} 个页面")
        
        # 创建输出目录
        output_dir = "output/deep_crawl"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存每个页面的Markdown内容到单独的文件
        for i, page_result in enumerate(result.deep_crawl_results):
            # 创建安全的文件名
            safe_filename = f"page_{i+1}.md"
            file_path = os.path.join(output_dir, safe_filename)
            
            # 写入Markdown内容
            with open(file_path, "w", encoding="utf-8") as f:
                # 添加页面URL作为标题
                f.write(f"# {page_result.url}\n\n")
                f.write(page_result.markdown)
            
            print(f"保存页面 {i+1}: {page_result.url} 到 {file_path}")
        
        # 创建索引文件
        index_path = os.path.join(output_dir, "index.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# 深度爬取结果索引\n\n")
            for i, page_result in enumerate(result.deep_crawl_results):
                f.write(f"{i+1}. [{page_result.url}](page_{i+1}.md)\n")
        
        print(f"\n索引文件已保存到 {index_path}")

if __name__ == "__main__":
    asyncio.run(main())