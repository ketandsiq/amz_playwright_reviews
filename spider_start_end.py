import requests
import os
from get_system_info import get_system_info



def task_started(task_logger_id, celery_id, output_file):
    """Triggered when the spider starts running."""
    # self.error_handler.log_signal(spider=spider.name, signal_code=4007)

    # telnet_port = self.crawler.settings.get("TELNETCONSOLE_PORT") 
    api_url = f"{os.getenv('DSIQ_BASE_API_URL')}/task_started"
    system_info = get_system_info()
    system_info["output_file"] = output_file
    # system_info['telnet_port'] = telnet_port[0] if telnet_port else None
    payload = {
        "task_logger_id": task_logger_id,
        "system_info": system_info,
        "celery_id": celery_id
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            print("Response JSON:", response.json())  # Correct way to get response data
        else:
            print(f"API call failed with status {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Error calling API: {e}")


def task_completed(close_reason, tl_id):
    """Logs when the Scrapy engine stops."""
    # spider = self.crawler.spider.name
    # self.error_handler.log_signal(signal_code=4002, spider=spider)
    # self.error_handler.shutdown() # method for clossing the error handler thread 
    api_url = f"{os.getenv('DSIQ_BASE_API_URL')}/task_completed"

    payload = {
        "task_logger_id": tl_id,
        "spider_close_reason": str(close_reason)
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            print("Response JSON:", response.json())
        else:
            print(f"API call failed with status {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Error calling API: {e}")