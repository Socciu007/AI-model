1. Hyper Parameter Tuning
Hyperparameters are set before training starts, can be tuned through grid search or related methods
- Values are set beforehand
- External to the model
- Not a part of the trained model and hence the values are not saved
- Independent of the dataset
Load data --> Build Hyper Model with Hyper Parameter --> Select Tuner/Grid Search --> Tuning to get best HP --> Build model with best HP --> Train model with data
2. Model: llm3, seamless