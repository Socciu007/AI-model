from .celery_config import celery
from utils_llm import make_llama_3_prompt
import lamini

lamini.api_key = "ad3d62932bc25b48963dd3413dd94cb3414dd650fc47f735704badeb56cdf9ca"

llm = lamini.Lamini(model_name="meta-llama/Meta-Llama-3-8B-Instruct")

@celery.task()
def execute_llm(user_prompt):
    try:
        system_prompt = "You are a helpful assistant."
        prompt = make_llama_3_prompt(user_prompt, system_prompt)
        res_txt = llm.generate(prompt, max_new_tokens=200)
        return res_txt
    except Exception as e:
        return str(e)

@celery.task()
def add_numbers(x, y):
    return x + y