## Table of Contents
- [Hyper Parameter Tuning](#hyper-parameter-tuning)
- [Model: llm3, seamless](#model-llm3-seamless)
- [Quick Demo](#quick-demo)
  - [1. Installation](#1-installation)
  - [2. Run the demo Seamless server](#2-run-the-demo-seamless-server)

## Hyper Parameter Tuning
Hyperparameters are set before training starts, can be tuned through grid search or related methods
- Values are set beforehand
- External to the model
- Not a part of the trained model and hence the values are not saved
- Independent of the dataset
Load data --> Build Hyper Model with Hyper Parameter --> Select Tuner/Grid Search --> Tuning to get best HP --> Build model with best HP --> Train model with data
## Model: llm3, seamless

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