from doctest import script_from_examples
import socket
import time
import os
from tracemalloc import start
from dns import resolver

def resolve_name(provider:str, query:str) -> dict:
    timestamps = {}
    resolve = resolver.Resolver()
    resolve.nameservers = [provider]
    start_time = time.time()
    timestamps['start_time'] = start_time
    try:
        resolve.resolve(query)
        end_time = time.time()
        timestamps['elapsed_time'] = (end_time - start_time)
        return timestamps
    except resolver.NXDOMAIN :
        print ('Domain name does not exist.')
        return None
    except resolver.Timeout :
        print ('Request timed out.')
        return None


script_directory = os.path.join(os.path.dirname(__file__), 'query.py')

dns_providers = []
with open('C:\\Users\\seanr\\OneDrive\\Documents\\Home-Lab\\code\\dns_monitor\\dns_servers.txt', 'r') as file:
    for line in file:
        dns_providers.append(line.strip())

query = 'google.com'
for provider in dns_providers:
    insert_data = resolve_name(provider, query)
    if insert_data:
        #print(f"{provider} : Success")
        insert_data['provider_ip'] = provider
        insert_data['status'] = 'Success'
    else:
        #print(f"{provider} : Failed")
        insert_data['provider_ip'] = provider
        insert_data['status'] = 'Failure'
    print(insert_data)