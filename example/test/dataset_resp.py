import os
import json
import asyncio
from factool.utils.openai_wrapper import OpenAIChat

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "your-api-key-here"
os.environ['SERPER_API_KEY'] = "your-serper-api-key-here"
os.environ['SCRAPER_API_KEY'] = "your-scraper-api-key-here"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"

chat = OpenAIChat(model_name='gpt-3.5-turbo-0125')


async def process_message(question):
    message = [{"role": "user", "content": question}]
    res = await chat._request_with_openai(message)  # 确保这里也是异步的调用
    return res.choices[0].message.content if res.choices else "No response"


async def main():
    # 读取问题列表
    with open('prompts_list0.json', 'r', encoding='utf-8') as infile:
        questions = json.load(infile)

    results = []
    batch_size = 10
    output_file = 'prompts_resp.jsonl'

    # 确保文件存在，并在开始前清空文件内容
    open(output_file, 'w').close()

    for i, question in enumerate(questions):
        response = await process_message(question)  # 使用 await 等待 process_message
        results.append({"prompt": question, "response": response})

        # 每10条写入一次文件
        if (i + 1) % batch_size == 0:
            with open(output_file, 'a', encoding='utf-8') as outfile:
                for result in results:
                    json.dump(result, outfile, ensure_ascii=False)
                    outfile.write('\n')
            print(f"Written {i + 1} responses to {output_file}")
            results = []  # 清空 results 列表

        await asyncio.sleep(1)  # 防止请求过快

    # 写入剩余的结果
    if results:
        with open(output_file, 'a', encoding='utf-8') as outfile:
            for result in results:
                json.dump(result, outfile, ensure_ascii=False)
                outfile.write('\n')
        print(f"Written remaining {len(results)} responses to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())  # 使用 asyncio.run 来运行 main 函数
