from flask import Flask, request, jsonify
from flask_cors import CORS
from utils_llm import make_llama_3_prompt
from task_module.celery_config import celery
from task_module.tasks import add_numbers

app = Flask("test")
CORS(app)

# Configure Celery and Redis
app.config['broker_url'] = 'redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['result_backend'] = 'redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['broker_connection_retry_on_startup'] = True
app.config['result_backend_transport_options'] = {
  'master_name': "mymaster",
  'retry_policy': {'timeout': 5.0}
}
# app.config['include'] = ['task_module.tasks']
celery.conf.update(app.config)

# Create a simple route
@app.route('/add')
def add_task():
  x = 10
  y = 30
  task = add_numbers.apply_async(args=[x, y])
  return jsonify({'task_id': task.id}), 200

# Route to handle model inference requests
@app.route('/process', methods=['POST'])
def generate():
  req = request.json
  input_text = req.get("text", "")
  print("text", input_text)

  if not input_text:
    return jsonify({"status": 0, "message": "Input text is required"}), 400

  # Execute the task asynchronously
  task = execute_llm.apply_async(args=[input_text])
  return jsonify({"status": 1, "task_id": task.id}), 200

# Route to check task status
@app.route("/status/<task_id>")
def task_status(task_id):
  task = add_numbers.AsyncResult(task_id)
  # Revoke the task
  task.revoke(terminate=True, signal='SIGKILL')
  if task.ready():
    result = task.result
  else:
    result = "Running..."
  return jsonify({"status": 1, "message": result}), 200

# Run the Flask app
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=6767, debug=True)