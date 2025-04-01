import subprocess
from CloudFlare import CloudFlare
from dotenv import load_dotenv
import os
load_dotenv()

cf_email = os.getenv("cf_email")
cf_api_key = os.getenv("cf_api_key")
cf_zone_id = os.getenv("cf_zone_id")
cf_domain = os.getenv("cf_domain")


# Function to resolve IP address using dig command
def resolve_domain_ip(domain):
    try:
        result = subprocess.run(['dig', domain, 'A', '+short'], capture_output=True, text=True)
        ip_address = result.stdout.strip()
        return ip_address
    except Exception as e:
        print(f"Error resolving IP address for {domain}: {e}")
        return None


# Function to add a DNS record to Cloudflare
def add_dns_record(email, api_key, zone_id, domain, subdomain, ipv4_address):
    cf = CloudFlare(email=email, token=api_key)
    #cf._base.api_token = None  # IDK WHY BUT I HAD TO DO THIS!
    try:
        dns_record = {
            'name': subdomain,
            'type': 'A',
            'content': ipv4_address,
            'ttl': 60,  # Adjust TTL as needed
        }

        cf.zones.dns_records.post(zone_id, data=dns_record)
        print(f"DNS record added successfully: {subdomain}.{domain} => {ipv4_address}")
        return True
    except Exception as e:
        print(f"Error adding DNS record: {e}")
        return None


# Function to remove a DNS record from Cloudflare
def remove_dns_record(email, api_key, zone_id, domain, subdomain, ipv4_address):
    cf = CloudFlare(email=email, token=api_key)
    #cf._base.api_token = None  # IDK WHY BUT I HAD TO DO THIS!
    try:
        dns_records = cf.zones.dns_records.get(zone_id, params={'name': f"{subdomain}.{domain}", 'type': 'A'})
        for record in dns_records:
            if record['content'] == ipv4_address:
                cf.zones.dns_records.delete(zone_id, record['id'])
                print(f"DNS record removed successfully: {subdomain}.{domain} => {ipv4_address}")
                return True
                break
        else:
            print(f"No matching DNS record found for {subdomain}.{domain} => {ipv4_address}")
            return False
    except Exception as e:
        print(f"Error removing DNS record: {e}")
        return None

def remove_dns_record_byID(email, api_key, zone_id, id):
    print("[INFO] Removing DNS Record.")
    print(f"[INFO] ID: {id}")
    print("... ")
    cf = CloudFlare(email=email, token=api_key)
    #cf._base.api_token = None  # IDK WHY BUT I HAD TO DO THIS!
    try:
        cf.zones.dns_records.delete(zone_id,id)
        print("Success")
        return True
    except Exception as e:
        print(f"Error removing DNS record: {e}")
        return None

def survey():
    print("Choose option:\n"
          "1. Add IPv4 to subdomain.domain\n"
          "2. Remove IPv4 from subdomain.domain\n"
          "3. Resolve address and add to subdomain.domain")
    inp = input("")
    while True:
        if inp == "1":
            ip_address = input('Enter IPv4:')
            subdomain = input('Enter subdomain:')
            domain = input('Enter domain:')
            add_dns_record(cf_email, cf_api_key, cf_zone_id, domain, subdomain, ip_address)
            break
        elif inp == "2":
            ip_address = input('Enter IPv4:')
            subdomain = input('Enter subdomain:')
            domain = input('Enter domain:')
            remove_dns_record(cf_email, cf_api_key, cf_zone_id, domain, subdomain, ip_address)
            break
        elif inp == "3":
            target_domain = input('Enter target resolve address:')
            ip_address = resolve_domain_ip(target_domain)
            subdomain = input('Enter subdomain:')
            domain = input('Enter domain:')
            remove_dns_record(cf_email, cf_api_key, cf_zone_id, domain, subdomain, ip_address)
            break
        else: print("Wrong. Try again.")
    input("Done.")

def get_all_dns_records(email, api_key, zone_id):
    print("Chechking DNS Records... ", end="")
    cf = CloudFlare(email=email, token=api_key)
    #cf._base.api_token = None   # IDK WHY BUT I HAD TO DO THIS!
    try:
        # Retrieve all DNS records for the specified zone_id
        dns_records = cf.zones.dns_records.get(zone_id)

        # Extract relevant information from each DNS record
        records_info = []
        for record in dns_records:
            record_info = {
                'id': record['id'],
                'name': record['name'],
                'type': record['type'],
                'content': record['content'],
            }
            records_info.append(record_info)
        print("Success")
        return records_info
    except Exception as e:
        print(f"Error retrieving DNS records: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # survey()
    records = get_all_dns_records(cf_email, cf_api_key, cf_zone_id)
    pass