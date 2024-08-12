from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import speech_recognition as sr

app = Flask(__name__)

# Load the model and tokenizer
model_name = "facebook/hf-seamless-m4t-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Recognize speech from audio file
def recognize_speech(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
    return text

# Translate text
def translate_text(text, target_lang="vi"):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(inputs.input_ids, max_length=512)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text

@app.route('/translate', methods=['POST'])
def translate():
    file = request.files['file']
    text = recognize_speech(file)
    target_lang = request.form.get('target_lang', 'vi')
    translated_text = translate_text(text, target_lang)
    return jsonify({'translated_text': translated_text})

if __name__ == '__main__':
    app.run(debug=True)