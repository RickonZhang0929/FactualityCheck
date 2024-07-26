import os
import json
import asyncio
from factool import Factool
import nest_asyncio

# 允许在现有事件循环中嵌套运行新的异步代码
nest_asyncio.apply()

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "sk-lH0YfSFt0PrQMSBHTTjM3V03qgGTf1oXAMnG2Mfwkmckuqdl"
os.environ['SERPER_API_KEY'] = "2f1fd6bf2797ff23cbfad8706b8f3b58f9840879"
os.environ['SCRAPER_API_KEY'] = "33059e327a34f8ccfa193d16ad45863c"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"
# os.environ['OPENAI_API_KEY_PATH'] = "https://api.chatanywhere.tech/v1"

factool_instance = Factool("gpt-3.5-turbo-0125")


async def process_message(prompt, response):
    input_data = {
        "prompt": prompt,
        "response": response,
        "category": "kbqa"
    }
    try:
        result = factool_instance.run([input_data])
        return result
    except Exception as e:
        print(f"Error processing message: {e}")
        return None


async def main():
    # 读取问题列表
    with open('prompts_resp0.jsonl', 'r', encoding='utf-8') as infile:
        questions = [json.loads(line) for line in infile]

    output_file = 'detect.jsonl'

    # 确保文件存在，并在开始前清空文件内容
    open(output_file, 'w').close()

    count = 0

    for question in questions:
        prompt = question["prompt"]
        response = question["response"]

        result = await process_message(prompt, response)  # 使用 await 等待 process_message
        if result is not None:
            output = {
                "prompt": prompt,
                "response": response,
                "output": result
            }

            with open(output_file, 'a', encoding='utf-8') as outfile:
                json.dump(output, outfile, ensure_ascii=False)
                outfile.write('\n')

            count += 1
            print(f"Written {count} responses to {output_file}")
        else:
            print(f"Failed to process question: {prompt}")

        await asyncio.sleep(1)  # 防止请求过快

if __name__ == "__main__":
    # 使用现有的事件循环来运行 main 函数
    asyncio.get_event_loop().run_until_complete(main())
