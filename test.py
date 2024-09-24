from flask import Flask, request, jsonify
from flask_cors import CORS
from task_module.celery_config import celery
from task_module.tasks import add_numbers, execute_llm
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask("test")
CORS(app)

# Config Celery and Redis
app.config.update(
  broker_url=os.getenv('REDIS_URL'),
  broker_read_url=os.getenv('REDIS_URL'),
  broker_write_url=os.getenv('REDIS_URL'),
  result_backend=os.getenv('REDIS_URL'),
  broker_connection_retry_on_startup=True,
  result_backend_transport_options={
    'master_name': "mymaster",
    'retry_policy': {'timeout': 5.0}
  }
)
celery.conf.update(app.config)
print(celery.conf)
# Create a simple route
@app.route('/add', methods=['POST'])
def add_task():
  data = request.json
  x = data.get('x', 10)
  y = data.get('y', 30)
  
  task = add_numbers.apply_async(args=[x, y])
  
  return jsonify({
    'task_id': task.id,
    'status': 'Task đã được gửi',
    'message': f'Đang thực hiện phép cộng {x} + {y}'
  }), 202

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
    response = {'state': task.state, 'status': 'Đang chờ xử lý...'}
  elif task.state == 'SUCCESS':
    response = {'state': task.state, 'status': 'Hoàn thành', 'result': task.result}
  elif task.state == 'FAILURE':
    response = {'state': task.state, 'status': 'Thất bại', 'error': str(task.info)}
  else:
    response = {'state': task.state, 'status': 'Đang xử lý...', 'info': str(task.info)}
  return jsonify(response), 200

# Run the Flask app
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=6767, debug=True)