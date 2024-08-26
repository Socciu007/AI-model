## Table of Contents
- [Hyper Parameter Tuning](#hyper-parameter-tuning)
- [Model: llm3, seamless](#model-llm3-seamlessM4T)
  - [1. Llama3](#1-llama3)
  - [2. SeamlessM4T](#2-seamlessM4T)
- [Quick SeamlessM4T Demo](#quick-SeamlessM4T-demo)
  - [1. Installation](#1-installation)
  - [2. Run the demo Seamless server](#2-run-the-demo-seamless-server)

## Hyper Parameter Tuning
Hyperparameters are set before training starts, can be tuned through grid search or related methods
- Values are set beforehand
- External to the model
- Not a part of the trained model and hence the values are not saved
- Independent of the dataset
Load data --> Build Hyper Model with Hyper Parameter --> Select Tuner/Grid Search --> Tuning to get best HP --> Build model with best HP --> Train model with data
## Model: llm3, seamlessM4T
### 1. Llama3
Llama3 is a large language model (LLM) developed by Meta based on transformer architecture. Llama 3 is designed to serve a variety of purposes in the field of natural language processing (NLP).

### 2. SeamlessM4T
SeamlessM4T is a multimedia AI model developed by Meta to support multilingual speech recognition and translation. This is one of the advanced models designed to handle a variety of language and audio related tasks, including: Speech-to-speech translation (S2ST), Speech-to-text translation (S2TT), Text-to-speech translation (T2ST), Text-to-text translation(T2TT) and Automatic speech recognition (ASR) 
## Quick SeamlessM4T Demo
This repository provides a quick demonstration of using a SeamlessM4T model for real-time speech translation. The project includes steps to set up the environment, download the necessary model weights, and run the demo.

### 1. Installation
```bash
pip install waitress
```
### 2. Run the demo Seamless server
First, create and activate a new conda environment.

```bash
waitress-serve seamless_server:app
```
Or

```bash
python seamless_server.py
```
