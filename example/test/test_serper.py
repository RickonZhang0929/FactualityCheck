import http.client
import json

conn = http.client.HTTPSConnection("google.serper.dev")
payload = json.dumps({
    "q": "apple inc",
    "gl": "cn"
})
headers = {
    'X-API-KEY': '2f1fd6bf2797ff23cbfad8706b8f3b58f9840879',
    'Content-Type': 'application/json'
}
conn.request("POST", "/search", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))