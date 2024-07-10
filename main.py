import psutil, time
import subprocess
import socket
import re

pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}:\d+\b"

def ip_to_dns(ip_address):
    try:
        host_name, alias_list, ip_list = socket.gethostbyaddr(ip_address)
        return host_name
    except socket.herror as e:
        return f"Could not resolve DNS for IP {ip_address}: {e}"

def find_process_pid(process_name):
    """Find PID for the given process name."""
    for proc in psutil.process_iter(['name']):
        if process_name.lower() in proc.info['name'].lower():
            return proc.pid
    return None

def monitor_network(process_name):
    # Use netstat to find connections, filtering by the process name
    # Note: This does not directly correlate to PID due to netstat's limitations
    while True:
        pid = find_process_pid(process_name)
        result = subprocess.run(['netstat', '-aon'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if str(pid) in line:
                # Extract the foreign address (assuming it's the second column)
                parts = line.split()
                if len(parts) > 2:
                    foreign_address = parts[2]
                    ip = foreign_address.split(':')[0]  # Extract IP from IP:port
                    try:
                        # Attempt to resolve the IP to a DNS name
                        dns_name = socket.gethostbyaddr(ip)[0]
                    except:
                        # If DNS resolution fails, use a placeholder
                        dns_name = "DNS resolution failed"
                    # Append the DNS name to the line
                    line += f" {dns_name}"
                if re.search(pattern, parts[2]):
                    print(line)
                
        time.sleep(1)
    

# Example usage
process_name = 'clickshare'  # Replace with your process name
monitor_network(process_name)