from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import time, math
from dotenv import load_dotenv
_ = load_dotenv() #load environmental variable LAMINI_API_KEY with key from .env file
from utils_llm import make_llama_3_prompt
import lamini
# Token access to https://app.lamini.ai/tune/
lamini.api_key = "ad3d62932bc25b48963dd3413dd94cb3414dd650fc47f735704badeb56cdf9ca" # Active API Tokens

app = Flask(__name__)
CORS(app)

# Configure Celery and Redis
app.config['CELERY_BROKER_URL'] = 'redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['CELERY_RESULT_BACKEND'] = 'redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'

celery = Celery(
  app.name, 
  broker=app.config['CELERY_BROKER_URL'],
  backend=app.config['CELERY_BROKER_URL']
)
celery.conf.update(app.config)

# Load the llm3 model
llm = lamini.Lamini(model_name="meta-llama/Meta-Llama-3-8B-Instruct")

# Celery task to run the model inference
@Celery.task
def execute_llm(user_prompt):
  system_prompt = "You are a helpful assistant."
  prompt = make_llama_3_prompt(user_prompt, system_prompt)
  res_txt = llm.generate(prompt, max_new_tokens=200)
  return res_txt

# Route test process
# @app.route("/process")
# def process():
#   system_prompt = "You are a helpful assistant."
#   prompt = make_llama_3_prompt("How to you go to China?", system_prompt)
#   res_txt = llm.generate(prompt, max_new_tokens=200)
#   return res_txt
  
# Route to handle model inference requests
@app.route('/process', methods=['POST'])
def generate():
  req = request.json
  input_text = req.get("text", "")
  
  if not input_text:
    return jsonify({"status": 0, "message": "Input text is required"}), 400
  
  task = execute_llm.apply_async(input_text)
  return jsonify({"status": 1, "task_id": task.id}), 200

# Route to check task status
@app.route("/status/<task_id>")
def task_status(task_id):
  task = run_model_task.AsyncResult(task_id)
  
  if task.state == 'PENDING':
    res = {
      "state": task.state,
      "message": "Task is in progress..."
    }
  elif task.state != 'FAILURE':
    res = {
      "state": task.state,
      "result": task.result
    }
  else:
    res = {
      "state": task.state,
      "message": str(task.info)
    }
  
  return jsonify(res), 200

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)