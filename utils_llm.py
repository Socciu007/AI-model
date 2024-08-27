import logging
from argparse import ArgumentParser
import jsonlines
import random

def setup_logging():
  # Remove all handlers associated with the root logger object
  for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
    logging.basicConfig(
      level=logging.WARNING,
      format="%(asctime)s [%(levelname)s] %(message)s",
      handlers=[logging.StreamHandler()],
    )
    
# Defines several arguments that can be passed to a script from the command line
def parse_arguments():
  parser = ArgumentParser()
  
  # The max number of examples to evaluate
  parser.add_argument(
    "--max-examples",
    type=int,
    default=1000,
    help="The maximum number of examples to evaluate (default: 1000)",
    required=False
  )
  
  # The model to use for text to sql
  parser.add_argument(
    "--sql-model-name",
    type=str,
    default="meta-llama/Meta-Llama-3-8B_Instruct",
    help="The model to use for text2sql",
    required=False,
  )
  
  # The gold dataset to use as seed
  parser.add_argument(
    "--gold-file-name",
    type=str,
    default="gold-test-set.jsonl",
    help="The gold dataset to use as seed",
    required=False,
  )
  
  # Refers to the training dataset file name
  parser.add_argument(
    "--training-file-name",
    type=str,
    default="generated_queries.jsonl",
    help="The training dataset",
    required=False,
  )
  
  return parser.parse_args()

# Default finetune argument
def get_default_finetune_args():
  return {
    "learning_rate": 3e-4,
    "max_steps": 3000,
    "early_stopping": False,
    "load_best_model_at_end": False,
    "use_cached_models": False,
    "peft_args": { "r_value": 32 }
  }
  
def get_schema():
  return """\
  0|team|TEXT eg. "Toronto Raptors"
  1|name|TEXT eg. "Otto Porter Jr."
  2|jersey|TEXT eg. "0" and when null has a value "NA"
  3|pos|TEXT eg. "PF"
  4|age|INT eg. "22" in years
  5|ht|TEXT eg. `6' 7"` or `6' 10"`
  6|wt|TEXT eg. "232 lbs" 
  7|college|TEXT eg. "Michigan" and when null has a value "--"
  8|salary|TEXT eg. "$9,945,830" and when null has a value "--"
  """

#slightly modified schema to match filming
def get_schema_s():
  return """\
  0|team|TEXT eg. "Toronto Raptors"
  1|name|TEXT eg. "Otto Porter Jr."
  2|jersey|TEXT eg. "0" and when null has a value "NA"
  3|pos|TEXT eg. "PF"
  4|age|INT eg. "22" in years
  5|ht|TEXT eg. `6' 7"` or `6' 10"` castable to int
  6|wt|TEXT eg. "232 lbs" 
  7|college|TEXT eg. "Michigan" and when null has a value "--"
  8|salary|TEXT eg. "$9,945,830" and when null has a value "--"
  """
  
def get_rubric():
  prompt = (
    "Read this scoring rubric carefully and follow the instructions precisely:\n"
  )
  prompt += (
    "A score of 5 means that model's value is the same as the gold answer's id.\n"
  )
  prompt += "A score of 4 means that the model's answer is the same or a paraphrase of the gold answer, but the value may not be an exact match.\n"
  prompt += "A score of 3 means that the model's answer is similar as the gold answer's description, but the value may be wrong. Both answers may indicate that revenue is increased but the gold says 12 percent and the model say 50 million USD.\n"
  prompt += "A score of 2 means that the model's answer is not similar to the gold answer, but the answer is plausible.\n"
  prompt += "A score of 1 means that the model's answer is not similar to the gold answer, and the answer doesn't make sense.\n"

  prompt += "Assign a 5 for a correct value even if other fields are missing.\n"

  return prompt
  
def load_training_data(args, make_question):
  path = f"data/training_data/{args.training_file_name}"

  limit = 1000

  with jsonlines.open(path) as reader:
    for index, obj in enumerate(reversed(list(reader))):
      if index >= limit:
        break

      yield {
        "input": make_llama_3_prompt(**make_question(obj)),
        "output": obj["sql"] + "<|eot_id|>",
      }

def get_dataset(args, make_question):
  if args.training_file_name == "archive/generated_queries.jsonl":
    return "407d05ea9d8f119f214ada0bde018225dbae16b589f5680f745ea12098f1fd4f"
  elif (
    args.training_file_name == "archive/generated_queries_v2_large_filtered_cleaned.jsonl"
  ):
    return "72e8d7d3a94f4d180b1b95f9b0ac5c9cf4476c132e02f301ed7f50164e09c961"
  
  dataset = list(load_training_data(args, make_question))

  return dataset

# Meta Llama 3 Instruct uses a prompt template, with special tags used to indicate the user query and system prompt.
def make_llama_3_prompt(user, system=""):
  system_prompt = ""
  if system != "":
    system_prompt = (
      f"<|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>"
    )
  return f"<|begin_of_text|>{system_prompt}<|start_header_id|>user<|end_header_id|>\n\n{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"