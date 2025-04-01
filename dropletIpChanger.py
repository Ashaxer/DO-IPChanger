import time
import socks
import requests
# from winsound import Beep
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("do_api_key")
base_url = os.getenv("do_base_url")
proxy = os.getenv("proxy")

requests = requests.session()
def ask(txt):
    YES = ['y','yes']
    NO = ['n','no']
    while True:
        # Beep(3000, 500)
        q = input(txt).lower()
        if q in YES: return True
        elif q in NO: return False

#if ask('Use port 2080 as socks proxy? '): proxy = {'http':f'socks5h://{proxy}','https':f'socks5h://{proxy}'}
#else: proxy = {}

proxy = {
   'http': proxy,
   'https': proxy,
}



headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
}


# Function to get the ID of a Droplet by its name
def get_droplet_id_by_name(name):
    print(f'[INFO]Getting droplet id of {name}')
    droplets_url = f'{base_url}droplets'
    response = requests.get(droplets_url, headers=headers, proxies=proxy)
    droplets = response.json().get('droplets', [])

    for droplet in droplets:
        if droplet['name'] == name:
            print(f'[INFO]Droplet id of {name} is {droplet["id"]}')
            return droplet['id']

# Function to get the current Reserved Floating IP for a Droplet
def get_reserved_floating_ip(droplet_id):
    print(f'[INFO]Getting IP of {droplet_id}')
    floating_ips_url = f'{base_url}floating_ips'
    response = requests.get(floating_ips_url, headers=headers, proxies=proxy)
    floating_ips = response.json().get('floating_ips', [])

    for ip in floating_ips:
        if ip['droplet']['id'] == droplet_id:
            print(f'[INFO]Droplet IP of {droplet_id} is {ip["ip"]}')
            return ip['ip']


# Function to delete a Floating IP by its ID
def delete_floating_ip(ip_id):
    print(f'[INFO]Deleting IP_ID: {ip_id}')
    delete_url = f'{base_url}floating_ips/{ip_id}'
    response = requests.delete(delete_url, headers=headers, proxies=proxy)
    return response.status_code


# Function to create a new Floating IP and assign it to a Droplet
def create_and_assign_floating_ip(droplet_id):
    print(f'[INFO]Generating new IP for {droplet_id}')
    create_url = f'{base_url}floating_ips'
    data = {'droplet_id': droplet_id}
    response = requests.post(create_url, headers=headers, json=data, proxies=proxy)
    new_ip = response.json().get('floating_ip', {}).get('ip')
    print(f"[INFO]New IP Generated: {new_ip}")
    return new_ip

# Get Droplet ID
def renew_ip(droplet_id):
    if droplet_id:
        # Get current Reserved Floating IP
        current_ip = get_reserved_floating_ip(droplet_id)

        # Delete current Floating IP
        if current_ip:
            delete_status = delete_floating_ip(current_ip)
            if delete_status == 204:
                print('[INFO]Deleted Reserved Floating IP successfully.')
                print('[INFO]Waiting 45 seconds before generating new IP...')
                time.sleep(45)
                # Create and assign a new Floating IP
                new_ip = create_and_assign_floating_ip(droplet_id)
                while not new_ip:
                    time.sleep(5)
                    new_ip = create_and_assign_floating_ip(droplet_id)
            else:
                print(f'[ERROR]Failed to delete Floating IP. Status code: {delete_status}')
        else:
            new_ip = create_and_assign_floating_ip(droplet_id)
            while not new_ip:
                time.sleep(5)
                new_ip = create_and_assign_floating_ip(droplet_id)
        print('[INFO]Waiting 10 seconds to Assign IP to Droplet')
        time.sleep(10)
        return new_ip
    else:
        print(f'[ERROR]Droplet "{droplet_id}" not found.')