from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import torch
from transformers import (
  AutoProcessor,
  SeamlessM4TModel
)

app = Flask(__name__)
CORS(app)

# Configure Celery and Redis
app.config['CELERY_BROKER_URL'] = 'redis://:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['CELERY_RESULT_BACKEND'] = 'redis://:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Load the model and processor
local_model= "./seamless_m4t_model" # Load the model if it exists in local
model_name= "facebook/hf-seamless-m4t-medium"
processor = AutoProcessor.from_pretrained(local_model)
model = SeamlessM4TModel.from_pretrained(local_model)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") # Run gpu if device have

# Celery task to run the model inference
@celery.task
def run_model_inference(input_data):
  try:
    # Preprocess the input data
    inputs = processor(input_data, src_lang="eng", return_tensors="pt").to(device)
    
    # Run the model inference
    outputs = model.generate(
      **inputs,
      generate_speech=False, 
      tgt_lang="vie",
      num_beams=5, 
      do_sample=True
    )[0].cpu().squeeze().detach().tolist()
    
    # Post_process and return the result
    res_txt = processor.decode(outputs, skip_special_tokens=True)
    
    return res_txt
  except Exception as e:
    return str(e)

# Route to handle translation
@app.route('/translate', methods=['POST'])
def translate():
  req = request.json
  input_text = req.get("text", "")
  
  if not input_text:
    return jsonify({"status": 0, "message": "Input text is required"}), 400
  
  # Call the celery task
  task = run_model_inference.delay(input_text)
  
  # Return the task ID to track the progress
  return jsonify({"status": 1, "task_id": task.id}), 202

# Route to check the task status
@app.route('/status/<task_id>', methods=['GET'])
def task_status(task_id):
  task = run_model_inference.AsyncResult(task_id)
  print(task)
  
  if task.state == 'PENDING':
    res = { 'status': 0, 'state': task.state, 'message': 'Task is still in progress...' }
  elif task.state == 'FAILURE':
    res = { 'status': 0, 'state': task.state, 'message': str(task.info) }
  else:
    res = { 'status': 1, 'state': task.state, 'message': task.result }

  return jsonify(res), 200

# Run the Flask app
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=6767, debug=True, use_reloader=False)