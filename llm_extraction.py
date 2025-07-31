import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field

# 定义产品数据模型
class Product(BaseModel):
    name: str = Field(..., description="产品名称")
    price: str = Field(..., description="产品价格")
    description: str = Field(None, description="产品描述")

async def main():
    # 检查是否设置了OpenAI API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量。请设置后再运行此示例。")
        print("您可以使用以下命令设置环境变量:")
        print("  Windows (CMD): set OPENAI_API_KEY=your_api_key_here")
        print("  Windows (PowerShell): $env:OPENAI_API_KEY='your_api_key_here'")
        print("  Linux/Mac: export OPENAI_API_KEY=your_api_key_here")
        return
    
    # 创建LLM提取策略
    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o",  # 使用OpenAI的GPT-4o模型
        api_token=api_key,        # 使用环境变量中的API密钥
        schema=Product.schema(),  # 使用Product模型的schema
        extraction_type="schema", # 使用schema提取
        instruction="""从爬取的内容中，提取所有提到的产品信息，包括名称、价格和描述。
        不要遗漏任何产品。每个提取的产品JSON格式应该如下所示：
        {"name": "产品名称", "price": "¥199.99", "description": "产品描述"}
        """
    )
    
    # 配置爬虫运行选项
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        word_count_threshold=1,  # 最小词数阈值设为1，确保捕获所有内容
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler() as crawler:
        # 运行爬虫 - 替换为实际的电商网站URL
        result = await crawler.arun(
            url="https://www.example.com/products",  # 替换为实际的产品页面URL
            config=run_config
        )
        
        # 获取提取的结构化内容
        extracted_data = result.extracted_content
        
        # 打印提取的数据
        print("\n=== 使用LLM提取的产品数据 ===\n")
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        
        # 保存提取的数据到JSON文件
        os.makedirs("output", exist_ok=True)
        with open("output/llm_extracted_products.json", "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        print("\nLLM提取的产品数据已保存到 output/llm_extracted_products.json")

# 使用开源模型的示例
async def open_source_llm_example():
    # 创建使用开源模型的LLM提取策略
    extraction_strategy = LLMExtractionStrategy(
        provider="ollama/llama3",  # 使用Ollama的Llama3模型
        schema=Product.schema(),  # 使用Product模型的schema
        extraction_type="schema", # 使用schema提取
        instruction="从爬取的内容中，提取所有提到的产品信息，包括名称、价格和描述。"
    )
    
    # 配置爬虫运行选项
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler() as crawler:
        # 运行爬虫
        result = await crawler.arun(
            url="https://www.example.com/products",  # 替换为实际的产品页面URL
            config=run_config
        )
        
        # 获取提取的结构化内容
        extracted_data = result.extracted_content
        
        # 保存提取的数据到JSON文件
        with open("output/open_source_llm_products.json", "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        print("\n开源LLM提取的产品数据已保存到 output/open_source_llm_products.json")

# 使用自然语言问题的示例
async def natural_language_extraction():
    # 创建使用自然语言问题的LLM提取策略
    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o",
        api_token=os.getenv("OPENAI_API_KEY"),
        extraction_type="natural_language",  # 使用自然语言提取
        instruction="这个网站上最畅销的产品是什么？它们的价格是多少？"
    )
    
    # 配置爬虫运行选项
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy
    )
    
    # 创建爬虫实例
    async with AsyncWebCrawler() as crawler:
        # 运行爬虫
        result = await crawler.arun(
            url="https://www.example.com/products",  # 替换为实际的产品页面URL
            config=run_config
        )
        
        # 获取提取的内容
        extracted_text = result.extracted_content
        
        # 打印提取的数据
        print("\n=== 自然语言提取结果 ===\n")
        print(extracted_text)
        
        # 保存提取的数据到文件
        with open("output/natural_language_extraction.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)
        
        print("\n自然语言提取结果已保存到 output/natural_language_extraction.txt")

if __name__ == "__main__":
    # 创建输出目录
    os.makedirs("output", exist_ok=True)
    
    # 运行主示例
    asyncio.run(main())
    
    # 如果需要运行其他示例，取消下面的注释
    # asyncio.run(open_source_llm_example())
    # asyncio.run(natural_language_extraction())