from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()

# Create a Celery object
celery = Celery('test')

# Update the Celery configuration
celery.conf.update(
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('REDIS_URL'),
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

# Autodiscover tasks in the specified module
celery.autodiscover_tasks(['task_module.tasks'])