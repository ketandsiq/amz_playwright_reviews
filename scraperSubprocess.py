import subprocess
import logging
from celery_config import celery
from filenaming import generate_filename
from generate_unique_port import generate_unique_port
import json

@celery.task(bind=True, name="start_scraper_task")
def start_scraper_task(self, task_data):
    """
    Celery task to start a scraper subprocess.
    """
    celery_id = self.request.id
    task_data = json.loads(task_data)
    
    signal_log,errors_log,output_data = generate_filename(task_data['task_id'], (celery_id))
    telnet_port = generate_unique_port()
    telnet_port = str(telnet_port) if type(telnet_port) == int else None
    logging.info(f"Starting scraper with celery_id: {celery_id}")
    urls = task_data['task_url']

    #we need to save it to file because there is limit of argument and we are now exceeding that limit so we need to write it to a file and later read in run_spider.py
    url_file_path = output_data.replace("_output.json", "_urls.json")
    with open(url_file_path, "w") as f:
        json.dump(urls, f)

    signal_log = f"{task_data['destination']}/{signal_log.split('_')[2]}/{signal_log}" #folder name is now the date so it will be stored in the same folder in storage worker
    errors_log = f"{task_data['destination']}/{errors_log.split('_')[2]}/{errors_log}"
    output_data = f"{task_data['destination']}/{output_data.split('_')[2]}/{output_data}"

    command = [
        "venv/bin/python",f"{task_data["task_name"]}.py", "--urls", url_file_path, "--output", output_data, 
    ] #Make Sure that the name of virtual environment is "venv"  example: venv/bin/python

    if task_data.get("is_playwright"):
        command.insert(0, "--auto-servernum")
        command.insert(0, "xvfb-run")
        print("Starting Playwright Scraper")

    try:
        subprocess.Popen(
            command,
            shell=False,
            # stdout=subprocess.DEVNULL, #the default behaviour works like it inherits the celery stdout so in terminal we are seeing the print statments of the subprocess ie scrapy
            # stderr=subprocess.DEVNULL,# so we are disable that but in future you can comment these out to debug the problems if any 
        )

        return {'status': 'success'}

    except Exception as e:
        logging.exception(f"Exception occurred while starting scraper for task_url: {e}")
        return {'status': 'error', 'exception': str(e)}
