import yaml

from factool.utils.llama_wrapper import LLaMAChat
from factool.utils.openai_wrapper import OpenAIChat
import os
import pathlib

from factool.utils.zhipuai_wrapper import ZhipuAIChat


class pipeline():
    def __init__(self, domain, foundation_model):
        #if foundation_model == 'gpt-3.5-turbo' or foundation_model == 'gpt-4':
        self.company = 'openai'
        self.chat = OpenAIChat(model_name=foundation_model)
        api_key = "ea833bbecf3ee7771fc5bb9b15486fb4.NeDaYr1io0KkM08o"  # 替换为你的实际API Key
        self.chat_glm = ZhipuAIChat(api_key=api_key, model_name="glm-4-air")
        # 备注：切换API模型，以chat为主
        self.chat = self.chat_glm
        self.chat_llama = LLaMAChat(url="http://10.112.17.225:7860/api/predict/")
        self.prompts_path = os.path.join(os.path.dirname(pathlib.Path(__file__)), "../prompts/")

        # with open(os.path.join(self.prompts_path, "self_check.yaml"), 'r') as file:
        #     data = yaml.load(file, Loader=yaml.FullLoader)
        # self.self_check_prompt = data[domain]