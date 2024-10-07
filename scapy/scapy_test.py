import scapy.all as scapy

def send_dns_query(domain):
    # Create a DNS query packet
    dns_query = (
        scapy.IP(dst="8.8.8.8") /  # Using Google's public DNS
        scapy.UDP(dport=53) /
        scapy.DNS(rd=1, qd=scapy.DNSQR(qname=domain, qtype='A'))
    )

    # Send the DNS query and capture the response
    response = scapy.sr1(dns_query, verbose=0)

    if response:
        # Print the response summary
        print(f"DNS Response for {domain}:")
        response.show()
    else:
        print("No response received.")

# Send a DNS request to youtooz.com
send_dns_query("example.com")