from factool.factool_confidence import FactoolConfidence

import os

# 设置环境变量
os.environ['OPENAI_API_KEY'] = "sk-lH0YfSFt0PrQMSBHTTjM3V03qgGTf1oXAMnG2Mfwkmckuqdl"
os.environ['SERPER_API_KEY'] = "2f1fd6bf2797ff23cbfad8706b8f3b58f9840879"
os.environ['SCRAPER_API_KEY'] = "33059e327a34f8ccfa193d16ad45863c"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"

factool_instance = FactoolConfidence("gpt-3.5-turbo-0125")

# one example input for each category.
inputs = [
            # {
            #     "prompt": "为什么o型血的人比a型或b型血的人更容易患胃溃疡",
            #     "response": "O型血的人比A型或B型血的人更容易患胃溃疡的原因可能与其不同的遗传特质有关。O型血的人相对于其他血型的人群更易感染幽门螺杆菌，这是引起胃溃疡的主要因素之一。幽门螺杆菌是一种常见的细菌，可通过口口传播和粪口传播，O型血的人对其感染的易感性较高。O型血的人分泌的凝血因子水平较低,这意味着在受伤或手术时,他们的血液可能难以凝结和止血，这可能增加出血和溃疡的风险。总之，O型血的人患胃溃疡的风险可能比其他血型的人群更高，这可能与他们的遗传特质有关。然而，这并不意味着所有O型血的人都会患上胃溃疡。胃溃疡还受到其他因素的影响，如饮食、生活方式、环境等。",
            #     "category": "kbqa"
            # }
    {
        "prompt": "金州勇士拿过几次NBA冠军？",
        "response": "金州勇士拿过7次NBA冠军，分别是：2015年1次，2017年1次，2018年3次，2020年2次，2021-2022赛季第六次赢得总冠军。",
        "category": "kbqa"
    }

]

response_list = factool_instance.run(inputs)

print(response_list)
