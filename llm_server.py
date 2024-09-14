from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import time, math
from dotenv import load_dotenv
_ = load_dotenv()  # Load environment variables
from utils_llm import make_llama_3_prompt

app = Flask(__name__)
CORS(app)

# Configure Redis for Celery
app.config['broker_url'] = 'redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['result_backend'] = 'redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['include'] = ['task_module.tasks']
celery = Celery(app.name, broker=app.config['broker_url'], backend=app.config['result_backend'])
celery.conf.update(app.config)

# Route to handle model inference requests
@app.route('/process', methods=['POST'])
def generate():
  req = request.json
  input_text = req.get("text", "")

  if not input_text:
    return jsonify({"status": 0, "message": "Input text is required"}), 400

  # Execute the task asynchronously
  task = celery.send_task('task_module.tasks.execute_llm', args=[input_text])
  return jsonify({"status": 1, "task_id": task.id}), 200

# Route to check task status
@app.route("/status/<task_id>")
def task_status(task_id):
  task = celery.AsyncResult(task_id)
  
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