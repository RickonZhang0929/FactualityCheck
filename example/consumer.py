# consumer_service.py
import redis
from flask_cors import CORS
from flask import Flask, Response
import json

app = Flask(__name__)
CORS(app)
# 初始化 Redis 客户端
r = redis.Redis(host='localhost', port=6379, db=0)
pubsub = r.pubsub()

# 订阅四个频道
channels = ['claims_channel', 'evidences_channel', 'verifications']
pubsub.subscribe(channels)

def generate():
    for message in pubsub.listen():
        if message['type'] == 'message':
            channel = message['channel'].decode('utf-8')
            data = json.loads(message['data'].decode('utf-8'))
            print(f"Channel: {channel}, Data: {data}")  # 打印处理后的消息
            yield f"data: {json.dumps({'channel': channel, 'data': data})}\n\n"

@app.route('/events')
def sse():
    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
