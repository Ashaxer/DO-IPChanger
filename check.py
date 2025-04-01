import json
import time

import requests
from dotenv import get_key

# from winsound import Beep
import cloudFlare
import dropletIpChanger
from checkHost import check_ip_connectivity
from dropletIpChanger import renew_ip, get_droplet_id_by_name, get_reserved_floating_ip

cf_email = get_key(".env","cf_email")
cf_api_key = get_key(".env","cf_api_key")
cf_zone_id = get_key(".env","cf_zone_id")
cf_domain = get_key(".env","cf_domain")
cf_subdomain = get_key(".env","cf_subdomain")
acceptable_connectivity = int(get_key(".env","acceptable_connectivity"))

token = get_key(".env","bot_token")
log_token = get_key(".env","wh_bot_token")
chat_ids = [get_key(".env","chat_id")]
droplets = []
domain_cheatsheet = json.loads(get_key(".env","domain_cheatsheet"))
for dro, subdo in domain_cheatsheet.items():
    droplets.append(dro)

def check_connectivity(IP,times,sleep_time):
    total_connectivity_percent = 0
    for i in range(int(times)):
        connectivity_percent = check_ip_connectivity(IP,sleep_time)
        print(f"[DEBUG]Connectivity percent: {connectivity_percent}%")
        total_connectivity_percent += connectivity_percent
    connectivity_percent = total_connectivity_percent // times
    return connectivity_percent

def tg(token, chat_ids, text):
    for chat_id in chat_ids:
        print(text)
        params = {'chat_id': chat_id, 'text': text}
        proxy = dropletIpChanger.proxy
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        response = requests.get(url, params=params, proxies=proxy)
        if 'RENEWED' in text:
          url = f'https://api.telegram.org/bot{token}/pinChatMessage'
          params = {'chat_id': chat_id, 'message_id': response.json()['result']['message_id']}
          response = requests.get(url, params=params, proxies=proxy)

def check_droplet_connectivity(droplet):
    droplet_id = get_droplet_id_by_name(droplet)
    IP = get_reserved_floating_ip(droplet_id)
    return check_connectivity(IP,1, 15)

def change_ip(droplet, tg_token = None, tg_chat_ids = None):
    global acceptable_connectivity
    droplet_id = get_droplet_id_by_name(droplet)
    while True:
        new_ip = renew_ip(droplet_id)
        if acceptable_connectivity <= 0:
            acceptable_connectivity = check_connectivity("8.8.8.8", 1, 10) + acceptable_connectivity
            log = f"[DEBUG]Acceptable Connectivity set to: {acceptable_connectivity}%"
            if tg_token is not None and tg_chat_ids is not None: tg(tg_token, tg_chat_ids, log)
        connectivity_percent = check_connectivity(new_ip, 1, 15)
        if connectivity_percent > acceptable_connectivity:
            while True:
                all_dns_records = cloudFlare.get_all_dns_records(cf_email, cf_api_key, cf_zone_id)
                if all_dns_records is not None: break
            for dns_record in all_dns_records:
                if f"{cf_subdomain}.{domain_cheatsheet[str(droplet)]}" in dns_record['name']:
                    for i in range(5):
                        respond = cloudFlare.remove_dns_record_byID(cf_email, cf_api_key, cf_zone_id,
                                                                    dns_record['id'])
                        if respond is not None: break
                    for i in range(5):
                        respond = cloudFlare.add_dns_record(cf_email, cf_api_key, cf_zone_id, cf_domain,
                                                            f'{cf_subdomain}.{domain_cheatsheet[str(droplet)]}',
                                                            new_ip)
                        if respond is not None: break
            break
    return new_ip,f"{cf_subdomain}.{domain_cheatsheet[str(droplet)]}"

def main(droplets):
    global acceptable_connectivity
    start_time = time.time()
    tgtxt = ''
    for droplet in droplets:
        droplet_id = get_droplet_id_by_name(droplet)
        current_IP = get_reserved_floating_ip(droplet_id)
        if acceptable_connectivity <= 0:
            acceptable_connectivity = check_connectivity("8.8.8.8", 1, 10) + acceptable_connectivity
            print(f"[DEBUG]Acceptable Connectivity set to: {acceptable_connectivity}%")
        connectivity_percent = check_connectivity(current_IP,3, 15)
        print(f'[DEBUG]Connectivity percent of {droplet} ({current_IP}) is: {connectivity_percent}%')
        if connectivity_percent <= acceptable_connectivity:
            tgtxt += f'{droplet} IP REMOVED: {current_IP}\n'
            change_ip(droplet)
        else:
            tgtxt += f'{droplet} IP IS CLEAN!\n'
        # Beep(2000,500)

        print(f'[PASS]{droplet} Connectivity check Passed!\n-+-+-+-+-+-+-+-+-+-+-+-+-+-\n')
    tgtxt += f'DONE IN {round(time.time() - start_time)}s'
    tg(token, chat_ids, tgtxt)



if __name__=="__main__":
    main(droplets)
