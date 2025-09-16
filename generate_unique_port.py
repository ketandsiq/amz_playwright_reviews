import uuid
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #checking if the port is already in use
        return s.connect_ex(('localhost', port)) == 0 # returns 0 if the port is already in use

def generate_unique_port(base_port=6000, max_port=7000, max_attempts=50):
    """Generate a unique port, ensuring it is not in use."""
    port_range = max_port - base_port
    attempts = 0

    while attempts < max_attempts: #checking for the available port in the range
        unique_port = base_port + (uuid.uuid4().int % port_range)
        
        if not is_port_in_use(unique_port):
            return unique_port
        
        attempts += 1

    raise RuntimeError("No available ports found in the given range.")
