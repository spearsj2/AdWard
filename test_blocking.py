import os
import subprocess
# import time

def nslookup(domain):
    try:
        result = subprocess.run(['nslookup', domain, '127.0.0.1'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

def process_block_list_file(filepath):
    with open(filepath, 'r') as file:
        for line in file:
            if line.startswith('0.0.0.0'):
                domain = line.split()[1].strip()
                print(f"Performing nslookup for: {domain}")
                lookup_result = nslookup(domain)
                print(lookup_result)
                # time.sleep(1)

def process_block_lists_directory(directory):
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            process_block_list_file(filepath)

if __name__ == "__main__":
    # Start the server.py script
    server_script_path = os.path.join(os.path.dirname(__file__), './main/server.py')
    server_process = subprocess.Popen(['python', server_script_path])

    try:
        block_lists_directory = os.path.join(os.path.dirname(__file__), './etc/block_lists')
        process_block_lists_directory(block_lists_directory)
    finally:
        # Stop the server.py script
        server_process.terminate()
        server_process.wait()