from typing import List

import requests
import asyncio

class LLaMAChat():
    def __init__(self, url, max_length=163840, temperature=0.6, top_p=0.6):
        self.url = url
        self.config = {
            'max_length': max_length,
            'temperature': temperature,
            'top_p': top_p,
        }

    def extract_after_marker(self, text, marker):
        index = text.find(marker)
        if index == -1:
            return ""
        return text[index + len(marker):].strip()

    async def _request_with_llama(self, messages, retry=3):
        payload = {
            "data": [[(messages[0]['content'], "")], self.config['max_length'], self.config['temperature'], self.config['top_p']]
        }
        for _ in range(retry):
            try:
                response = requests.post(self.url, json=payload)
                if response.status_code == 200:
                    result = response.json()["data"]
                    return self.extract_after_marker(result[0][0][1], "assistant\n\n")
                else:
                    print(f'API call failed with status code: {response.status_code}')
            except requests.exceptions.RequestException as e:
                print(f'Request error: {e}')
            await asyncio.sleep(1)

        return None

    async def dispatch_llama_requests(self, messages_list):
        async_responses = [
            self._request_with_llama(messages)
            for messages in messages_list
        ]

        return await asyncio.gather(*async_responses)

    async def async_run(self, messages_list, expected_type):
        retry = 1
        responses = [None for _ in range(len(messages_list))]
        messages_list_cur_index = [i for i in range(len(messages_list))]

        while retry > 0 and len(messages_list_cur_index) > 0:
            print(f'{retry} retry left...')
            messages_list_cur = [messages_list[i] for i in messages_list_cur_index]

            predictions = await self.dispatch_llama_requests(messages_list=messages_list_cur)

            finised_index = []
            for i, pred in enumerate(predictions):
                if pred is not None:
                    responses[messages_list_cur_index[i]] = pred
                    finised_index.append(messages_list_cur_index[i])

            messages_list_cur_index = [i for i in messages_list_cur_index if i not in finised_index]

            retry -= 1

        return responses

if __name__ == "__main__":
    llama_chat = LLaMAChat(url="http://10.112.17.225:7860/api/predict/")
    predictions = asyncio.run(llama_chat.async_run(
        messages_list=[
            [{"role": "user", "content": "美国的首都是什么"}],
        ],
        expected_type=List,  # Modify expected_type according to your need
    ))

    print(predictions)
