from flask import Flask, request, jsonify
from celery import Celery
import torch
from huggingface_hub import login
from transformers import (
  AutoModelForCausalLM,
  AutoTokenizer,
  BitsAndBytesConfig,
  AutoTokenizer,
)

app = Flask(__name__)

# Configure Celery and Redis
app.config['CELERY_BROKER_URL'] = 'redis://:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'
app.config['CELERY_RESULT_BACKEND'] = 'redis://:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

huggingface_hub_token = "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"

login(token = huggingface_hub_token)
# Configure
# local_model = "unsloth/Meta-Llama-3.1-8B-bnb-4bit"
local_model = "meta-llama/Meta-Llama-3-8B-Instruct"
device_map = {"": "cuda:0"}
bnb_config = BitsAndBytesConfig(
  load_in_4bit=True,
  bnb_4bit_quant_type="nf4",
  bnb_4bit_compute_dtype="float16",
  bnb_4bit_use_double_quant=True
)
attn_implementation = "eager"

#  Load model, tokenizer
model = AutoModelForCausalLM.from_pretrained(
    local_model,
    quantization_config=bnb_config,
    device_map=device_map,
    attn_implementation=attn_implementation
)
tokenizer = AutoTokenizer.from_pretrained(local_model)

# Celery task to run the model inference
@Celery.task
def run_model_task(input_text):
  inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
  outputs = model.generate(inputs["input_ids"])
  res_txt = tokenizer.decode(outputs[0], skip_special_tokens=True)
  return res_txt

# Route to handle model inference requests
@app.route('/generate', methods=['POST'])
def generate():
  req = request.json
  input_text = req.get("input_text", "")
  
  if not input_text:
    return jsonify({"status": 0, "message": "Input text is required"}), 400
  
  task = run_model_task.delay(input_text)
  return jsonify({"status": 1, "task_id": task.id}), 202

# Route to check task status
@app.route("/status/<task_id>", methods=['GET'])
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
  app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)