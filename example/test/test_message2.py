import os
import asyncio
from factool.utils.openai_wrapper import OpenAIChat

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "your-api-key-here"
os.environ['SERPER_API_KEY'] = "your-serper-api-key-here"
os.environ['SCRAPER_API_KEY'] = "your-scraper-api-key-here"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"

# 创建OpenAIChat实例
chat = OpenAIChat(model_name='gpt-3.5-turbo-0125')

# 测试数据
test_data = {"message": "中国的首都是哪里"}

async def main():
    # 调用异步方法并等待其结果
    res = await chat._request_with_openai(test_data)
    # 打印结果
    print(res)

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
