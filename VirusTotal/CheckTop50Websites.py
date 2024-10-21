from VirusTotal import func_checkurl

with open("top50websites.txt", 'r') as file:
    for line in file:
        url = line.strip()  # Remove any leading/trailing whitespace
        func_checkurl(url, True)