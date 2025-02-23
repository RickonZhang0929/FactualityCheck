'''
Remember to export you API keys first.
export OPENAI_API_KEY=...
export SERPER_API_KEY=...
export SCRAPER_API_KEY=...
'''

from factool import Factool

import os

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "sk-lH0YfSFt0PrQMSBHTTjM3V03qgGTf1oXAMnG2Mfwkmckuqdl"
os.environ['SERPER_API_KEY'] = "71a9a751fba127c347e7f41bd261d4370beee90b"
os.environ['SCRAPER_API_KEY'] = "73ace7682c4a312c68973be4cc1229f3"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"
# os.environ['OPENAI_API_KEY_PATH'] = "https://api.chatanywhere.tech/v1"

factool_instance = Factool("gpt-3.5-turbo-0125")

# one example input for each category.
inputs = [
            # {
            #     "prompt": "Introduce Graham Neubig",
            #     "response": "Graham Neubig is a professor at MIT",
            #     "category": "kbqa"
            # }
            {
                "prompt": "Introduction to Tsinghua University",
                "response": "Tsinghua University in Beijing",
                "category": "kbqa"
            }
]

response_list = factool_instance.run(inputs)

print(response_list)