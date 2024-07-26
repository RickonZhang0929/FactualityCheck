import requests

def send_message():
    url = 'http://127.0.0.1:1829/message'  # 替换为你的服务地址
    data = {'message': '加拿大的首都是什么'}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 将抛出HTTP错误异常
        print("Message request was successful.")
        print("Response from server:")
        print(response.text)
    except requests.exceptions.HTTPError as errh:
        print('Http Error:', errh)
        print("Status code:", response.status_code)
        print("Response text:", response.text)
    except requests.exceptions.ConnectionError as errc:
        print('Error Connecting:', errc)
    except requests.exceptions.Timeout as errt:
        print('Timeout Error:', errt)
    except requests.exceptions.RequestException as err:
        print('Oops: Something Else', err)

def process_data():
    url = 'http://127.0.0.1:1829/process'  # Flask app 的地址
    data = {
        "prompt": "Introduction to Tsinghua University",
        "response": "Tsinghua University is in Beijing",
        "category": "kbqa"
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 将抛出HTTP错误异常
        print("Process request was successful.")
        print("Response from server:")
        print(response.json())  # 确保这里使用了括号 ()
    except requests.exceptions.HTTPError as errh:
        print('Http Error:', errh)
        print("Status code:", response.status_code)
        print("Response text:", response.text)
    except requests.exceptions.ConnectionError as errc:
        print('Error Connecting:', errc)
    except requests.exceptions.Timeout as errt:
        print('Timeout Error:', errt)
    except requests.exceptions.RequestException as err:
        print('Oops: Something Else', err)

def main():
    # Call to send a simple message
    # send_message()

    # Call to process data
    process_data()

if __name__ == '__main__':
    main()
