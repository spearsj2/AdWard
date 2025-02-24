import dnslib
import socket
import threading
import logging
import os
import csv
from logging import getLogger
from datetime import datetime

# Import the logging configuration
from logging_config import setup_logging, get_config_value

# Internal variables
config_file = os.path.join(os.path.dirname(__file__), '../etc/adward.conf')

# List of blocked domains
blocked_domains = ["xavier.edu"] # example domain to block

# Function to load blocked domains from files in block_lists folder
def load_blocked_domains(directory):
    blocked = set()
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                for line in file:
                    if line.startswith('0.0.0.0'): # Matching formatting in the file
                        domain = line.split()[1].strip()
                        blocked.add(domain)
    print(f"Loaded {len(blocked)} blocked domains from {directory}")
    return blocked

# Load additional blocked domains from block lists
block_lists_directory = get_config_value(config_file, 'blockListDir')
if block_lists_directory is None:
    raise ValueError("Configuration value for 'blockListDir' is missing or invalid.")
block_lists_directory = os.path.join(os.path.dirname(__file__), block_lists_directory)
blocked_domains.extend(load_blocked_domains(block_lists_directory))

# CSV logging setup
csv_log_file = get_config_value(config_file, 'logFile')
if csv_log_file is None:
    raise ValueError("Configuration value for 'logFile' is missing or invalid.")
csv_log_file = os.path.join(os.path.dirname(__file__), csv_log_file)
csv_log_fields = ['time', 'action', 'domain']

# Ensure the CSV log file exists and has headers
if not os.path.isfile(csv_log_file):
    with open(csv_log_file, 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=csv_log_fields)
        csv_writer.writeheader()

# Check if logging is enabled
logging_enabled = get_config_value(config_file, 'loggingEnabled')
if logging_enabled is None:
    raise ValueError("Configuration value for 'loggingEnabled' is missing or invalid.")
logging_enabled = logging_enabled == 'True'

def log_to_csv(action, domain):
    global logging_enabled
    if logging_enabled:
        try:
            with open(csv_log_file, 'a', newline='') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=csv_log_fields)
                csv_writer.writerow({
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3], 
                    'action': action, 
                    'domain': domain
                })
        except OSError as e:
            if e.errno == 10054:  # Connection reset by peer
                logging_enabled = False
                logging.error("Socket forcibly closed. Logging disabled.")
            else:
                raise

class DNSServer:
    def __init__(self, host='127.0.0.1', port=None, forwarder=None):
        self.host = host
        self.port = int(port) if port else 53 # Default DNS port
        self.forwarder = forwarder if forwarder else '8.8.8.8' # Google DNS
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.host, self.port))
        self.running = True

    def handle_request(self, data, addr):
        try:
            request = dnslib.DNSRecord.parse(data)
            domain = str(request.q.qname).strip('.')
            
            # Skip logging for reverse DNS lookups for 127.0.0.1
            if domain == '1.0.0.127.in-addr.arpa':
                return

            log_to_csv('Received', domain)

            if domain in blocked_domains:
                # Respond with NXDOMAIN if the domain is blocked
                reply = request.reply()
                reply.header.rcode = dnslib.RCODE.NXDOMAIN
                self.server.sendto(reply.pack(), addr)
                log_to_csv('Blocked', domain)
            else:
                # Forward the request to the external DNS server (8.8.8.8)
                forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                forward_sock.sendto(data, (self.forwarder, 53))
                forward_data, _ = forward_sock.recvfrom(512)
                forward_sock.close()

                # Send the response from the external DNS server back to the client
                self.server.sendto(forward_data, addr)
                log_to_csv('Forwarded', domain)
        except socket.error as e:
            if e.errno == 10054:
                logging.debug("Socket error: [WinError 10054] An existing connection was forcibly closed by the remote host :)")
            else:
                logging.error(f"Socket error: {e}")

    def start(self):
        print(f"Starting DNS server on {self.host}:{self.port}")
        print(f"Forwarding DNS requests to {self.forwarder}")
        while self.running:
            try:
                data, addr = self.server.recvfrom(512)
                threading.Thread(target=self.handle_request, args=(data, addr)).start()
            except socket.error as e:
                if not self.running:
                    break
                if e.errno == 10054:
                    logging.debug("Socket error: [WinError 10054] An existing connection was forcibly closed by the remote host :)")
                else:
                    logging.error(f"Socket error: {e}")

    def stop(self):
        self.running = False
        self.server.close()
        print("DNS server stopped")

if __name__ == "__main__":
    setup_logging(config_file)
    dns_port = get_config_value(config_file, 'dnsPort')
    if dns_port is None:
        raise ValueError("Configuration value for 'dnsPort' is missing or invalid.")
    dns_alternative = get_config_value(config_file, 'dnsAlternative')
    if dns_alternative is None:
        raise ValueError("Configuration value for 'dnsAlternative' is missing or invalid.")
    dns_server = DNSServer(port=dns_port, forwarder=dns_alternative)

    try:
        dns_server.start()
    except KeyboardInterrupt:
        dns_server.stop()
