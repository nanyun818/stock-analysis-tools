import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    # 创建一个异步网络爬虫实例
    async with AsyncWebCrawler() as crawler:
        # 运行爬虫获取网页内容
        result = await crawler.arun(
            url="https://www.example.com",  # 示例网址，可以替换为任何你想爬取的网站
        )
        # 打印提取的Markdown内容
        print("\n=== 提取的Markdown内容 ===\n")
        print(result.markdown)

        # 保存Markdown到文件
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print("\nMarkdown内容已保存到 output.md")

if __name__ == "__main__":
    asyncio.run(main())