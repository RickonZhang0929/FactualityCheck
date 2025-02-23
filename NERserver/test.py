import requests
import json

# 定义Flask接口的URL
url = 'http://127.0.0.1:5000/ner'


def test_ner_api(sentence):
    # 设置请求头
    headers = {'Content-Type': 'application/json'}

    # 构造请求数据
    data = {
        "sentence": sentence
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, json=data)

    # 输出响应结果
    if response.status_code == 200:
        result = response.json()
        print("Entities extracted:", result.get('entities'))
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


def main():
    # 输入要测试的句子
    sentence = "Apple is looking at buying U.K. startup for $1 billion"

    # 调用测试函数
    test_ner_api(sentence)


if __name__ == '__main__':
    main()
