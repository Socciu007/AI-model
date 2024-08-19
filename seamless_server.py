from flask import Flask, request, jsonify
from transformers import (
  SeamlessM4TModel,
  AutoProcessor
)
import torch
import numpy as np
import torchaudio
import gradio as gr

from lang_list_pkg import (
  TEXT_SOURCE_LANGUAGE_NAMES,
  S2ST_TARGET_LANGUAGE_NAMES,
  T2TT_TARGET_LANGUAGE_NAMES,
  S2TT_TARGET_LANGUAGE_NAMES,
  LANGUAGE_CODE_TO_NAME,
  LANG_TO_SPKR_ID
)

app = Flask(__name__)

# Load the model and tokenizer
model_name= "./seamless_m4t_model"
processor = AutoProcessor.from_pretrained(model_name)
model = SeamlessM4TModel.from_pretrained(model_name)

TASK_NAMES = [
  "S2ST (Speech to Speech translation)",
  "S2TT (Speech to Text translation)",
  "T2ST (Text to Speech translation)",
  "T2TT (Text to Text translation)",
  "ASR (Automatic Speech Recognition)",
] # Tasks that the model can perform

AUDIO_SAMPLE_RATE = 16000.0 # Sampling rate of the input audio (Compatible with a fixed sampling rate parameter trained using the SeamlessM4T model)

MAX_INPUT_AUDIO_LENGTH = 60  # Maximum length of input audio, in seconds

DEFAULT_TARGET_LANGUAGE = "English" # Default output target language: English

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") # Run gpu if device have

def predict(
  task_name: str,
  audio_source: str,
  input_audio_mic: str | None,
  input_audio_file: str | None,
  input_text: str | None,
  source_language: str | None,
  target_language: str | None
) -> tuple[tuple[int, np.ndarray] | None, str]:
  task_name = task_name.split()[0]
  source_language_code = LANGUAGE_CODE_TO_NAME[source_language] if source_language else None
  target_language_code = LANGUAGE_CODE_TO_NAME[target_language]
  
  # Input cases are audio
  if task_name in ["S2ST", "S2TT", "ASR"]:
    # Check case is microphone audio and cases are different audio
    if audio_source == "microphone":
      input_data = input_audio_mic
    else: 
      input_data = input_audio_file
    
    # Load the input audio with a tensor containing the audio data and the original sampling frequency of the audio input
    # arr: Tensor([nums_channels, n_samples]), org_sr: int
    arr, org_sr = torchaudio.load(input_data)
    
    # Adjusts the input audio sample frequency to match the model's audio sampling rate
    new_arr = torchaudio.functional.resample(arr, orig_freq=org_sr, new_freq=AUDIO_SAMPLE_RATE)
    
    max_length = int(MAX_INPUT_AUDIO_LENGTH * AUDIO_SAMPLE_RATE)
    # Check if the number of samples 
    if new_arr.shape[1] > max_length:
      new_arr = new_arr[:, :max_length]
      gr.warning(f"Input audio is too long. Only the first {MAX_INPUT_AUDIO_LENGTH} seconds is used.")
    
    # Convert and format audio data before feeding it into the model for processing
    input_data = processor(
      audios=new_arr,
      sampling_rate=AUDIO_SAMPLE_RATE,
      return_tensors="pt"
    ).to(device)
  else: 
    input_data = processor(
      text=input_text,
      src_lang=source_language_code,
      return_tensors="pt"
    ).to(device)
    
  # Generate tokens from the model based on pre-preprared input data according to each task instance
  if task_name in ["S2TT", "T2TT"]:
    tokens_ids = model.generate(
      **input_data,
      generate_speech=False,
      tgt_lang=target_language_code,
      num_beams=5,
      do_sample=True
    )[0].cpu().squeeze().detach().tolist()
  else: 
    output = model.generate(
      **input_data,
      return_intermediate_token_ids=True,
      tgt_lang=target_language_code,
      num_beams=5,
      do_sample=True,
      spkr_id=LANG_TO_SPKR_ID[target_language_code][0]
    )
    
    waveform = output.waveform.cpu().squeeze().detach().numpy()
    tokens_ids = output.sequences.cpu().squeeze().detach().tolist()
  
  # Decode the tokens IDs into texts
  text_out = processor.decode(tokens_ids, skip_special_tokens=True)
  
  if task_name in ["S2ST", "T2ST"]:
    return (AUDIO_SAMPLE_RATE, waveform), text_out
  else:
    return None, text_out

# The function converts the audio sound to the required audio
def process_s2st(
  input_audio_file: str,
  target_language: str
) -> tuple[tuple[int, np.ndarray] | None, str]:
  return predict(
    task_name="S2ST",
    audio_source="file",
    input_audio_mic=None,
    input_audio_file=input_audio_file,
    input_text=None,
    source_language=None,
    target_language=target_language
  )
  
# The function converts the audio sound to the required text
def process_s2tt(
  input_audio_file: str,
  target_language: str
) -> tuple[tuple[int, np.ndarray] | None, str]:
  return predict(
    task_name="S2TT",
    audio_source="file",
    input_audio_mic=None,
    input_audio_file=input_audio_file,
    input_text=None,
    source_language=None,
    target_language=target_language
  )
  
# The function converts the text to the required audio
def process_t2st(
  input_text: str,
  source_language: str,
  target_language: str
) -> tuple[tuple[int, np.ndarray] | None, str]:
  return predict(
    task_name="T2ST",
    audio_source="",
    input_audio_mic=None,
    input_audio_file=None,
    input_text=input_text,
    source_language=source_language,
    target_language=target_language
  )
  
# The function converts the text to the required text
def process_t2tt(
  input_text: str,
  source_language: str,
  target_language: str
) -> tuple[tuple[int, np.ndarray] | None, str]:
  return predict(
    task_name="T2TT",
    audio_source="",
    input_audio_mic=None,
    input_audio_file=None,
    input_text=input_text,
    source_language=source_language,
    target_language=target_language
  )
  
# The function automatic speech recognition
def process_asr(
  input_audio_file: str,
  target_language: str
) -> tuple[tuple[int, np.ndarray] | None, str]:
  return predict(
    task_name="ASR",
    audio_source="file",
    input_audio_mic=None,
    input_audio_file=input_audio_file,
    input_text=None,
    source_language=None,
    target_language=target_language
  )

@app.route('/s2st', methods=['POST'])
def s2st():
  data = request.json
  input_audio_file = data['input_audio_file']
  target_language = data['target_language']
  
  audio, text_output = process_s2st(input_audio_file, target_language)
  res = {
    'audio_sample_rate': audio[0] if audio else None,
    'audio_wareform': audio[1].tolist() if audio else None,
    'text_output': text_output
  }
  return jsonify(res)

@app.route('/s2tt', methods=['POST'])
def s2tt():
  data = request.json
  print('oke')
  print(data)
  input_audio_file = data['input_audio_file']
  target_language = data['target_language']
  
  _, text_output = process_s2tt(input_audio_file, target_language)
  res = {
    'text_output': text_output
  }
  return jsonify(res)

@app.route('/t2st', methods=['POST'])
def t2st():
  data = request.json
  input_text = data['input_text']
  source_language = data['source_language']
  target_language = data['target_language']
  
  audio, text_output = process_t2st(input_text, source_language, target_language)
  res = {
    'audio_sample_rate': audio[0] if audio else None,
    'audio_wareform': audio[1].tolist() if audio else None,
    'text_output': text_output
  }
  return jsonify(res)

@app.route('/t2tt', methods=['POST'])
def t2tt():
  data = request.json
  input_text = data['input_text']
  source_language = data['source_language']
  target_language = data['target_language']
  
  _, text_output = process_t2tt(input_text, source_language, target_language)
  res = {
    'text_output': text_output
  }
  return jsonify(res)

@app.route('/asr', methods=['POST'])
def asr():
  data = request.json
  input_audio_file = data['input_audio_file']
  target_language = data['target_language']
   
  _, text_output = process_asr(input_audio_file, target_language)
  res = {
    'recognized_text': text_output
  }
  return jsonify(res)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)