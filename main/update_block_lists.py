import os
import requests
import re

# Define the paths
block_list_file = os.path.join(os.path.dirname(__file__), '../etc/block_lists.txt')
output_folder = os.path.join(os.path.dirname(__file__), '../etc/block_lists')

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Function to sanitize filenames
def sanitize_filename(url):
    return re.sub(r'[\\/*?:"<>|]', '_', url)

# Read the block list file
with open(block_list_file, 'r') as file:
    urls = file.readlines()

# Fetch each URL and save the result
for url in urls:
    url = url.strip()
    if url:
        sanitized_url = sanitize_filename(url)
        output_file = os.path.join(output_folder, f"{sanitized_url}.txt")
        try:
            print(f"Fetching {url}...")
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            with open(output_file, 'w', encoding='utf-8') as out_file:
                out_file.write(response.text)
            print(f"Saved {url} to {output_file}")
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")