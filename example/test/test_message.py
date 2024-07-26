import os
import asyncio  # 引入 asyncio 库
from factool.utils.openai_wrapper import OpenAIChat

os.environ['OPENAI_API_KEY'] = "your-api-key-here"
os.environ['SERPER_API_KEY'] = "your-serper-api-key-here"
os.environ['SCRAPER_API_KEY'] = "your-scraper-api-key-here"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"

chat = OpenAIChat(model_name='gpt-3.5-turbo-0125')

async def process_message(data):
    if not data or not all(k in data for k in ['message']):
        return {"error": "Missing required fields"}, 400
    message = data['message']
    res = await chat._request_with_openai(message)  # 确保这里也是异步的调用
    return res

async def main():
    # 测试数据
    test_data = {
    "message": [
        {"role": "user", "content": "清华大学在哪里"}
    ]
}


    # 处理消息并等待结果
    result = await process_message(test_data)  # 使用 await 等待 process_message

    # 打印结果
    print(result)

if __name__ == "__main__":
    asyncio.run(main())  # 使用 asyncio.run 来运行 main 函数
