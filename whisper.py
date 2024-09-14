from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
from openai import OpenAI
client = OpenAI()

# audio_file = open("./audio/receive/08u6svzd5glp.wav", "rb")
# # audio_file = open("./data/audio/preamble10.wav", "rb")
# transcription = client.audio.transcriptions.create(
#   model="whisper-1", 
#   file=audio_file
# )
# print(transcription.text)

app = Flask(__name__)
CORS(app)

# Configure Celery and Redis
app.config['CELERY_BROKER_URL'] = 'redis://:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task()
def run_model_whisper(file_path):
  try:
    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
    )
    return transcription.text
  except Exception as e:
    return str(e)

@app.route('/receive-audio', methods=['GET', 'POST'])
def receive_audio():
  file_name = request.headers.get('File-Name')
  if not file_name:
    return jsonify({"status": 0, "message": "File name header missing"}), 404
  
  # Save the audio into the file local
  file_path = f'./audio/receive/{file_name}'
  with open(file_path, 'ab') as f:
    f.write(request.data)
  print(f"Received and saved chunk to {file_path}")
  
  # After receiving the full audio file, translate it
  if request.headers.get('Recording-Complete'):
    print("Starting translation")
    task = run_model_whisper.delay(file_path)  # Call Celery task
    return jsonify({"task_id": task.id}), 200
  return "Audio chunk received", 200

@app.route('/check-status/<task_id>', methods=['GET'])
def check_status(task_id):
  task = run_model_whisper.AsyncResult(task_id)
  if task.state == 'PENDING':
    return jsonify({"state": task.state}), 202
  elif task.state != 'FAILURE':
    return jsonify({"state": task.state, "result": task.result}), 200
  else:
    return jsonify({"state": task.state, "error": str(task.info)}), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)