from flask import Flask, request, jsonify
import os
from factool import Factool
from flask_cors import CORS
from factool.utils.openai_wrapper import OpenAIChat
app = Flask(__name__)
CORS(app)


@app.route('/process', methods=['POST'])
def process():
    if not factool_instance:
        return jsonify({"error": "Factool initialization failed"}), 500

    # Extract the data from the request
    data = request.json
    if not data or not all(k in data for k in ['prompt', 'response', 'category']):
        return jsonify({"error": "Missing required fields"}), 400

    prompt = data['prompt']
    response = data['response']
    category = data['category']

    # Prepare the input for Factool
    inputs = [{
        "prompt": prompt,
        "response": response,
        "category": category
    }]

    try:
        # Run the Factool instance
        response_list = factool_instance.run(inputs)
    except Exception as e:
        app.logger.error("Failed to process input with Factool: %s", str(e))
        return jsonify({"error": "Factool processing failed"}), 500

    # Return the response list as JSON
    return jsonify(response_list)


@app.route('/message', methods=['POST'])
async def message():
    # Extract the data from the request
    data = request.json
    print(data)
    if not data or not all(k in data for k in ['prompt']):
        return jsonify({"error": "Missing required fields"}), 400
    prompt = data['prompt']
    param = [
        {"role": "user", "content": prompt}
    ]
    # 处理请求...
    res = await chat._request_with_openai(param)
    content = extract_content(res)
    print(content)
    return content

class ChatCompletion:
    def __init__(self, id, choices, created, model, object, system_fingerprint, usage):
        self.id = id
        self.choices = choices
        self.created = created
        self.model = model
        self.object = object
        self.system_fingerprint = system_fingerprint
        self.usage = usage

class Choice:
    def __init__(self, finish_reason, index, logprobs, message):
        self.finish_reason = finish_reason
        self.index = index
        self.logprobs = logprobs
        self.message = message

class ChatCompletionMessage:
    def __init__(self, content, role, function_call, tool_calls):
        self.content = content
        self.role = role
        self.function_call = function_call
        self.tool_calls = tool_calls

class CompletionUsage:
    def __init__(self, completion_tokens, prompt_tokens, total_tokens):
        self.completion_tokens = completion_tokens
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens

def extract_content(chat_completion):
    """Extracts content from the first choice of a ChatCompletion object."""
    if chat_completion and chat_completion.choices:
        # Assuming the first choice contains the relevant message
        first_choice = chat_completion.choices[0]
        if first_choice and first_choice.message:
            return first_choice.message.content
    return None

if __name__ == '__main__':
    # Set environment variables for API keys
    os.environ['OPENAI_API_KEY'] = "sk-lH0YfSFt0PrQMSBHTTjM3V03qgGTf1oXAMnG2Mfwkmckuqdl"
    os.environ['SERPER_API_KEY'] = "2f1fd6bf2797ff23cbfad8706b8f3b58f9840879"
    os.environ['SCRAPER_API_KEY'] = "33059e327a34f8ccfa193d16ad45863c"
    os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"

    chat = OpenAIChat(model_name='gpt-3.5-turbo-0125')

    # Try to create a Factool instance safely
    # try:
    factool_instance = Factool("gpt-3.5-turbo-0125")
    # except Exception as e:
    #     app.logger.error("Failed to initialize Factool: %s", str(e))
    #     print("Exception occurred: {}".format(e))
    #     factool_instance = None

    app.run(debug=False, host='0.0.0.0', port=1829)  # You can remove debug=True in production
