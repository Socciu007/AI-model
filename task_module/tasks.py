from .celery_config import celery
from utils_llm import make_llama_3_prompt
import lamini
import os
from dotenv import load_dotenv
load_dotenv()

lamini.api_key = os.getenv('LAMINI_API_KEY')
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

@celery.task()
def process_data(data):
    # Giả sử đây là một tác vụ xử lý dữ liệu phức tạp
    processed_data = [item.upper() for item in data if isinstance(item, str)]
    return processed_data