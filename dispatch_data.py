from celery_config import celery

def dispatch_data(output_buffer, output_file, last_chunk=False):
    """Dispatch data to the celery."""
    # if log_type == "signal":
    #     if self.signal_buffer:
    #         celery.send_task("log_data", args=[{"data":self.signal_buffer, "file_name":self.signal_log_file, "last_chunk":last_chunk}], queue="signals") # sending the signal to the celery task to send to the server
    #         self.signal_buffer = []  # Clear the buffer after dispatching
    # elif log_type == "error":
    #     if self.error_buffer:
    #         celery.send_task("log_data", args=[{"data":self.error_buffer, "file_name":self.log_file, "last_chunk":last_chunk}], queue="errors")
    #         self.error_buffer = []  
    # elif log_type == "output":
    try:
        celery.send_task("log_data", args=[{"data":output_buffer, "file_name":output_file, "last_chunk":last_chunk}], queue="output")
    except Exception as e:
        print("Exception in dispatch output data: ", e)