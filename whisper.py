from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
client = OpenAI()

audio_file = open("./audio/receive/08u6svzd5glp.wav", "rb")
# audio_file = open("./data/audio/preamble10.wav", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)

print(transcription.text)

app = Flask(__name__)
CORS(app)

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
    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
    )
    print("Translate", transcription.text)
    return transcription.text, 200
  return "Audio chunk received", 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)