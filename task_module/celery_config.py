from celery import Celery
from task_module.tasks import *

celery = Celery(
  'test',
  broker='redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314', # Use your own broker URL
  result_backend='redis://default:A3HP3clCHRuqnqW71pGK1s4AvJGKjgRu@redis-13314.c1.asia-northeast1-1.gce.redns.redis-cloud.com:13314', # Use your own backend URL
  accept_content=['json'],
  task_serializer='json',
  result_serializer='json',
  timezone='UTC',
  enable_utc=True
)