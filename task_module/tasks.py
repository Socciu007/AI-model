from celery import Celery
from utils_llm import make_llama_3_prompt
import lamini
lamini.api_key = "ad3d62932bc25b48963dd3413dd94cb3414dd650fc47f735704badeb56cdf9ca" # Set API key for Lamini

celery = Celery(
  'test',
  broker='redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314',  # Use your own broker URL
  backend='redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314'  # Use your own backend URL
)

# Load the LLM model
llm = lamini.Lamini(model_name="meta-llama/Meta-Llama-3-8B-Instruct")

# Task execute llm model in task_module.tasks
@celery.task()
def execute_llm(user_prompt):
  try:
    system_prompt = "You are a helpful assistant."
    prompt = make_llama_3_prompt(user_prompt, system_prompt)
    res_txt = llm.generate(prompt, max_new_tokens=200)
    return res_txt
  except Exception as e:
    return str(e)
  
# Celery task for test
@celery.task()
def add_numbers(x, y):
  return x + y