import requests


def call_openai(api_key, base_url, prompt):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    data = {
        'prompt': prompt,
        'max_tokens': 100
    }

    try:
        response = requests.post(base_url, json=data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}


def main():
    api_key = input("sk-lH0YfSFt0PrQMSBHTTjM3V03qgGTf1oXAMnG2Mfwkmckuqdl")
    base_url = input("https://api.chatanywhere.tech/v1")

    while True:
        prompt = input("Enter the prompt (or type 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break

        result = call_openai(api_key, base_url, prompt)
        if 'error' in result:
            print("Error calling OpenAI:", result['error'])
        else:
            print("Response from OpenAI:", result)


if __name__ == '__main__':
    main()
