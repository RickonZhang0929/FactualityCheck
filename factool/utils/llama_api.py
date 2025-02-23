import requests
def extract_after_marker(text, marker):
    index = text.find(marker)
    if index == -1:
        return ""  # Marker not found
    return text[index + len(marker):].strip()
marker = "assistant\n\n"
url = "http://10.112.17.225:7860/api/predict/"
payload = {
    "data": [[("美国的首都是什么", "")], 163840, 0.6, 0.6]  # max_length, top_p, temperature
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    print(response.json())
    result = response.json()["data"]
    print(f"type result:{type(result)}")
    print(f"shape of result:{len(result)}")
    usr_msg = extract_after_marker(result[0][0][1],marker)
    print("Model response:", usr_msg)
else:
    print("API call failed with status code:", response.status_code)