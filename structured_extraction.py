import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 创建CSS选择器提取策略
    # 这个例子将从Hacker News提取文章标题和链接
    extraction_strategy = JsonCssExtractionStrategy(
        selectors={
            "articles": {
                "selector": ".athing",  # 文章容器的CSS选择器
                "type": "list",
                "children": {
                    "title": {
                        "selector": ".titleline > a",  # 标题选择器
                        "type": "text"
                    },
                    "link": {
                        "selector": ".titleline > a",  # 链接选择器
                        "type": "attribute",
                        "attribute": "href"
                    },
                    "rank": {
                        "selector": ".rank",  # 排名选择器
                        "type": "text"
                    }
                }
            }
        }
    )
    
    # 配置爬虫运行选项
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler() as crawler:
        # 运行爬虫
        result = await crawler.arun(
            url="https://news.ycombinator.com",  # Hacker News
            config=run_config
        )
        
        # 获取提取的结构化内容
        extracted_data = result.extracted_content
        
        # 打印提取的数据
        print("\n=== 提取的结构化数据 ===\n")
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        
        # 保存提取的数据到JSON文件
        os.makedirs("output", exist_ok=True)
        with open("output/extracted_data.json", "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        print("\n结构化数据已保存到 output/extracted_data.json")

if __name__ == "__main__":
    asyncio.run(main())