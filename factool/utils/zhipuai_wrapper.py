import ast
import json
from typing import List

from zhipuai import ZhipuAI
import asyncio


class ZhipuAIChat:
    def __init__(
            self,
            api_key,
            model_name='glm-4-0520',
    ):
        self.client = ZhipuAI(api_key=api_key)
        self.model_name = model_name

    async def _async_invoke(self, messages):
        response = self.client.chat.asyncCompletions.create(
            model=self.model_name,
            messages=messages
        )
        # 从响应中获取任务ID
        task_id = response.id  # 直接访问 `id` 属性
        return task_id

    async def _fetch_result(self, task_id):
        for _ in range(10):  # 轮询获取结果
            result = self.client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
            if result.task_status == 'SUCCESS':
                # 直接访问 CompletionChoice 对象的属性
                return result.choices[0].message.content
            elif result.task_status == 'FAIL':
                return None
            await asyncio.sleep(3)  # 等待3秒后再请求

        return None

    def _type_check(self, output, expected_type):
        """
        Checks if the output is of the expected type.
        """
        try:
            # 如果输出是字符串或 JSON 字符串，尝试将其转换为预期类型
            if expected_type == List and isinstance(output, str):
                output = eval(output)
            elif expected_type == dict and isinstance(output, str):
                output = eval(output)

            if isinstance(output, expected_type):
                return output
        except (SyntaxError, ValueError, TypeError):
            pass
        return None

    def _type_check2(self, output, expected_type):
        """
        Checks if the output is of the expected type.
        """
        try:
            # 处理字符串输出，并尝试将其解析为预期类型
            if isinstance(output, str):
                # 尝试将字符串解析为 JSON 对象
                output = json.loads(output)

            # 检查输出是否为预期类型
            if isinstance(output, expected_type):
                return output
        except (json.JSONDecodeError, SyntaxError, ValueError, TypeError) as e:
            print(f"Type check failed: {e}")
            return None
        return None

    def _boolean_fix(self, output):
        """
        Fixes boolean values in a string to match Python's boolean literals.
        """
        return output.replace("true", "True").replace("false", "False")

    def _type_check3(self, output, expected_type):
        """
        Checks if the output is of the expected type after evaluating it.
        """
        try:
            # 修正布尔值，并尝试将字符串转换为 Python 对象
            output_eval = ast.literal_eval(self._boolean_fix(output))

            # 检查转换后的对象是否为预期类型
            if not isinstance(output_eval, expected_type):
                return None
            return output_eval
        except (ValueError, SyntaxError, TypeError) as e:
            print(f"Type check failed: {e}")
            return None

    async def async_run(self, messages_list, expected_type):
        retry = 1
        responses = [None for _ in range(len(messages_list))]
        messages_list_cur_index = [i for i in range(len(messages_list))]

        while retry > 0 and len(messages_list_cur_index) > 0:
            print(f'{retry} retry left...')
            messages_list_cur = [messages_list[i] for i in messages_list_cur_index]

            # 使用智谱API发送异步请求
            task_ids = await asyncio.gather(*[self._async_invoke(messages) for messages in messages_list_cur])
            print(f'Task IDs: {task_ids}')  # 打印 task_ids
            # 获取结果
            predictions = await asyncio.gather(*[self._fetch_result(task_id) for task_id in task_ids])
            print(f'Predictions: {predictions}')  # 打印 predictions
            # 类型检查和过滤
            preds = [self._type_check3(prediction, expected_type) if prediction is not None else None for prediction in
                     predictions]

            finished_index = []
            for i, pred in enumerate(preds):
                if pred is not None:
                    responses[messages_list_cur_index[i]] = pred
                    finished_index.append(messages_list_cur_index[i])

            messages_list_cur_index = [i for i in messages_list_cur_index if i not in finished_index]

            retry -= 1

        return responses



if __name__ == "__main__":
    api_key = "ea833bbecf3ee7771fc5bb9b15486fb4.NeDaYr1io0KkM08o"  # 替换为你的实际API Key
    chat = ZhipuAIChat(api_key=api_key, model_name='glm-4-air')

    messages_list = [
                        [{
                            "role": "user",
                            "content": "作为一名营销专家，请为智谱开放平台创作一个吸引人的slogan"
                        }]
                    ]  # 这里创建一个包含5个相同消息的列表

    predictions = asyncio.run(chat.async_run(messages_list, List))
    print(predictions)
