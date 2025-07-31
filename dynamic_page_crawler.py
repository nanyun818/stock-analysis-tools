import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    # 配置浏览器选项
    browser_config = BrowserConfig(
        headless=True,  # 无头模式，设为False可以看到浏览器界面
        verbose=True,   # 显示详细日志
    )
    
    # 配置爬虫运行选项 - 处理动态页面
    run_config = CrawlerRunConfig(
        # 在页面加载后执行的JavaScript代码
        js_code="""
        // 滚动到页面底部以加载懒加载内容
        async function scrollToBottom() {
            const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
            
            // 初始滚动位置
            let lastScrollTop = 0;
            
            // 滚动多次，每次等待内容加载
            for (let i = 0; i < 5; i++) {
                // 滚动到当前可见区域底部
                window.scrollTo(0, document.body.scrollHeight);
                
                // 等待内容加载
                await delay(1000);
                
                // 检查是否已经到达底部（滚动位置不再变化）
                if (document.documentElement.scrollTop === lastScrollTop) {
                    break;
                }
                
                // 更新上次滚动位置
                lastScrollTop = document.documentElement.scrollTop;
            }
            
            // 滚动回顶部
            window.scrollTo(0, 0);
            return true;
        }
        
        // 执行滚动函数并返回结果
        return await scrollToBottom();
        """,
        
        # 等待特定元素出现，确保页面完全加载
        wait_for=".content-loaded",  # 替换为实际网站上表示内容已加载的选择器
        
        # 等待时间（毫秒）
        wait_time=5000,  # 等待5秒，确保动态内容加载完成
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 运行爬虫 - 爬取包含无限滚动的页面
        result = await crawler.arun(
            # 替换为你想爬取的实际动态网页URL
            url="https://www.reddit.com/r/Python/",  # 示例：Reddit Python板块
            config=run_config
        )
        
        # 打印提取的Markdown内容
        print("\n=== 提取的Markdown内容（前500字符）===\n")
        print(result.markdown[:500] + "...")
        
        # 保存Markdown到文件
        with open("output/dynamic_page.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print("\nMarkdown内容已保存到 output/dynamic_page.md")

# 处理点击"加载更多"按钮的示例
async def load_more_example():
    browser_config = BrowserConfig(headless=False, verbose=True)
    
    run_config = CrawlerRunConfig(
        js_code="""
        async function clickLoadMore() {
            const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
            
            // 点击"加载更多"按钮多次
            for (let i = 0; i < 3; i++) {
                // 查找加载更多按钮
                const loadMoreButton = document.querySelector('.load-more-button');
                
                // 如果找不到按钮，则停止
                if (!loadMoreButton) break;
                
                // 点击按钮
                loadMoreButton.click();
                
                // 等待新内容加载
                await delay(2000);
            }
            
            return true;
        }
        
        return await clickLoadMore();
        """,
        wait_time=8000,  # 等待8秒，确保所有内容加载完成
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 替换为包含"加载更多"按钮的实际网页URL
        result = await crawler.arun(
            url="https://example.com/with-load-more",  # 替换为实际URL
            config=run_config
        )
        
        with open("output/load_more_example.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        
        print("\n'加载更多'示例内容已保存到 output/load_more_example.md")

if __name__ == "__main__":
    # 创建输出目录
    import os
    os.makedirs("output", exist_ok=True)
    
    # 运行主示例
    asyncio.run(main())
    
    # 如果需要运行"加载更多"示例，取消下面的注释
    # asyncio.run(load_more_example())