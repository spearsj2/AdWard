from scapy.all import *

# Initialize a set to store unique DNS names from the file
unique_dns_names = set()

# Load existing DNS names from the file into the set
try:
    with open("scapy/collectedDNS.txt", "r") as fileRead:
        for record in fileRead:
            unique_dns_names.add(record.strip())
except FileNotFoundError:
    pass

def dns_request(packet):
    global unique_dns_names  # Use the global set of unique names
    if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:  # DNS request
        queried_name = packet[DNS].qd.qname.decode('utf-8')  # Extract the queried name
        print(f"{queried_name}")

        # Check if the name is unique and not already in the set
        if queried_name not in unique_dns_names:
            unique_dns_names.add(queried_name)  # Add to the set of unique names

            # Write the new unique name to the file
            with open("scapy/collectedDNS.txt", "a") as fileWrite:
                fileWrite.write(f"{queried_name}\n")

# Start sniffing for DNS requests
sniff(filter="udp port 53", prn=dns_request)
