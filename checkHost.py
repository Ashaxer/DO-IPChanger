import time
import requests

# Check connectivity percent
def check_ip_connectivity(ip_address, sleep_time):
    check_host_api_url = 'https://check-host.net/check-ping'
    print(f'[INFO]Checking connectivity of {ip_address}')

    # List of Iran locations from which to test connectivity
    nodes_url = "https://check-host.net/nodes/hosts"
    nodes_response = requests.get(nodes_url, headers={"Accept": "application/json"}).json()
    
    all_nodes = nodes_response.get("nodes", {})
    nodes = [node for node, info in all_nodes.items() if info["location"][0].lower() == "ir"]
    
    print(f"[INFO] Found {len(nodes)} nodes:")
    print("\n".join(f"[INFO] {node}" for node in nodes))
        
    headers = {'Accept': 'application/json'}
    success_count = 0
    total_tests = 4*len(nodes)

    response = requests.get(f'{check_host_api_url}?host={ip_address}&{"&".join(f"node={node}" for node in nodes)}', headers=headers)


    if response.status_code == 200:
        result = response.json()
        try:
            if result['ok'] == 1:
                request_id = result['request_id']
                print(f'[INFO]Connectivity of {ip_address} checked. Link:')
                print(f"https://check-host.net/check-result/{request_id}")
                print('[INFO]Waiting 15 seconds for next request')
                time.sleep(int(sleep_time))
                response2 = requests.get(f"https://check-host.net/check-result/{request_id}").json()
                for node in nodes:
                    try:
                        for res in response2[node][0]:
                            if res[0] == 'OK': success_count += 1
                    except: pass
        except: pass
    else:
        print(f'[ERROR]Ping test failed.')

    success_ratio = (success_count / total_tests) * 100
    return success_ratio

