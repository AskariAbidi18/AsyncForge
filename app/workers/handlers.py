import time
import random
from app.utils.constants import TaskTypes
    
def send_email_handler(payload): 
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    
    if "to" not in payload or "body" not in payload:
        raise ValueError("Missing 'to' or 'body' in payload")
    
    time.sleep(random.randint(1,2))

    if random.random() < 0.2:
        raise Exception("Simulated email sending failure")

def generate_report_handler(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    if "report_id" not in payload:
        raise ValueError("Missing 'report_id' in payload")
    
    time.sleep(random.randint(3,5))

    if random.random() < 0.2:
        raise Exception("Simulated report generation failure")
    
def process_image_handler(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    if "image_path" not in payload:
        raise ValueError("Missing 'image_path' in payload")
    
    time.sleep(random.randint(2,4))

    if random.random() < 0.2:
        raise Exception("Simulated image processing failure")
    
def webhook_call_handler(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")
    if "url" not in payload or "data" not in payload:
        raise ValueError("Missing 'url' or 'data' in payload")
    
    time.sleep(random.randint(1,2))

    if random.random() < 0.2:
        raise Exception("Simulated webhook call failure")

HANDLERS = {
    TaskTypes.SEND_EMAIL: send_email_handler,
    TaskTypes.GENERATE_REPORT: generate_report_handler,
    TaskTypes.PROCESS_IMAGE: process_image_handler,
    TaskTypes.WEBHOOK_CALL: webhook_call_handler
}

def get_handler(task_type):
    if task_type not in HANDLERS:
        raise ValueError(f"No handler found for task type: {task_type}")
    return HANDLERS[task_type]