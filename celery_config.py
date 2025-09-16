from celery import Celery
#import celery_signals
from dotenv import load_dotenv
import os

load_dotenv()
celery_broker = os.getenv("CELERY_BROKER")
celery = Celery(__name__, broker=celery_broker) 

celery.autodiscover_tasks(['scraperSubprocess'], force=True)


 
 
