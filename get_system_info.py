import os
import psutil
import subprocess
import getpass

def get_ipv4_address():
    try:
        
        output = subprocess.run("hostname -I", shell=True, capture_output=True, text=True).stdout
        matches = output.strip().split()

        # Prioritize 172.16.x.x IPs
        for ip in matches:
            if ip.startswith("172.16."):
                return ip

        return matches[0] if matches else "No valid IP found"

    except Exception as e:
        return {"error":{str(e)}}


def get_system_info():
    """Collect system information."""
    try:
        system_name = os.environ.get("COMPUTERNAME", os.uname().nodename)
        # Windows/Linux support
        ip_address = get_ipv4_address()  # Extract using os + subprocess
        cpu_cores = psutil.cpu_count(logical=True)  # Virtual cores (Logical CPUs)
        physical_cores = psutil.cpu_count(logical=False)  # Physical cores
        system_user = getpass.getuser()

        data = {
            "system_name": system_name,
            "system_ip": ip_address,
            "system_user": system_user,
            "physical_cores": physical_cores,
            "cpu_cores": cpu_cores
        }
        return data

    except Exception as e:
        return {"error": str(e)}
