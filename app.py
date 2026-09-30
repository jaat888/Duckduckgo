from flask import Flask, request, jsonify
from duckduckgo_search import DDGS

app = Flask(__name__)

# Yahan aap apni pasand ki koi bhi secret API key set kar sakte hain
MY_SECRET_KEY = "sk-jaat"

@app.route('/api/chat', methods=['GET', 'POST'])
def chat_api():
    provided_key = None

    # 1. API Key ko pakadne ka system (Headers, JSON, ya URL Parameter se)
    # Professional APIs Header mein Bearer token leti hain
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        provided_key = auth_header.split(' ')[1]

    if request.method == 'POST':
        data = request.get_json() or {}
        # Agar header mein nahi hai, toh JSON body mein check karo
        if not provided_key:
            provided_key = data.get('api_key')
        user_prompt = data.get('prompt')
        selected_model = data.get('model', 'claude-3-haiku')
    else:
        # GET request ke liye URL parameter check karo
        if not provided_key:
            provided_key = request.args.get('api_key')
        user_prompt = request.args.get('prompt')
        selected_model = request.args.get('model', 'claude-3-haiku')

    # 2. API Key Authentication (Security Check)
    if provided_key != MY_SECRET_KEY:
        # Asli API jaisa error message
        return jsonify({
            "error": {
                "code": 401,
                "message": "Invalid API key provided. Please use a valid 'sk-jaat' key.",
                "status": "UNAUTHENTICATED"
            }
        }), 401

    # 3. Prompt validation
    if not user_prompt:
        return jsonify({
            "error": {
                "code": 400,
                "message": "Prompt is missing. Please provide a 'prompt' parameter.",
                "status": "INVALID_ARGUMENT"
            }
        }), 400

    # 4. Main AI Request Server ko bhejna
    try:
        response = DDGS().chat(user_prompt, model=selected_model)
        
        return jsonify({
            "status": "success",
            "model_used": selected_model,
            "answer": response
        }), 200

    except Exception as e:
        # Original DuckDuckGo/Server ka exact error wapas bhejenge
        return jsonify({
            "error": {
                "code": 500,
                "message": str(e),
                "status": "INTERNAL_SERVER_ERROR"
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
