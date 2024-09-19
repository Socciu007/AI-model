from flask import Flask, request, jsonify
from flask_cors import CORS
from task_module.celery_config import celery
from task_module.tasks import add_numbers, execute_llm

app = Flask("test")
CORS(app)

# Cấu hình Celery và Redis
app.config.update(
    CELERY_BROKER_URL='redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314',
    CELERY_RESULT_BACKEND='redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314',
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP=True,
    result_backend_transport_options={
        'master_name': "mymaster",
        'retry_policy': {'timeout': 5.0}
    }
)

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
  task = celery.AsyncResult(task_id)
  if task.state == 'PENDING':
    response = {'state': task.state, 'status': 'Pending...'}
  elif task.state != 'FAILURE':
    response = {'state': task.state, 'status': str(task.info)}
  else:
    response = {'state': task.state, 'status': str(task.info)}
  return jsonify(response), 200

# Run the Flask app
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=6767, debug=True)