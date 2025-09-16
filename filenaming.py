from datetime import datetime

def generate_filename(task_id, celery_id):
    try:
        formatted_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")  # Fix datetime formatting
        filename = f"{task_id}_{celery_id}_{formatted_time}"
        return filename+"_signals.json", filename+"_errors.json", filename+"_output.json"
    except Exception as e:
        return(str(e))
