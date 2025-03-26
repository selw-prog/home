from doctest import script_from_examples
import socket
import time
import os
from dns import resolver

def get_dns_query(provider:str, query:str):
    resolve = resolver.Resolver()
    resolve.nameservers = [provider]
    start_time = time.time()
    try:
        resolve.resolve(query)
        end_time = time.time()
        return end_time - start_time
    except resolver.NXDOMAIN :
        print ('Domain name does not exist.')
        return None
    except resolver.Timeout :
        print ('Request timed out.')
        return None


script_directory = os.path.join(os.path.dirname(__file__), 'query.py')

dns_providers = []
with open('dns_servers.txt', 'r') as file:
    for line in file:
        dns_providers.append(line.strip())

query = 'google.com'
for provider in dns_providers:
    response_time = get_dns_query(provider, query)
    if response_time:
        print(f"{provider} : {response_time*1000}")
    else:
        print(f"{provider} : Failed")

