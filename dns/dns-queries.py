from tkinter import filedialog
import re
import csv
import matplotlib.pyplot as plt

# Apr  5 20:53:06 dnsmasq[4317]: query[A] checkappexec.microsoft.com from 192.168.4.40
# Probably ought to build out this class a little more
# queries(requestor_ip, query, record_type, date, time)
class Query:
    requestor = ''
    query = ''
    record_type = ''
    date = ''
    time = ''

def toBarGraph(data:dict) -> None:
    graph_dates = list(data.keys())
    graph_values = list(data.values())
    plt.bar(range(len(data)), graph_values, tick_label = graph_dates)
    plt.show()

IP_REGEX = re.compile('(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})$')
DNS_QUERY_EXISTS = re.compile('(query)')
DNS_QUERY_REGEX = re.compile('(query.+)')
MONTH_DAY_REGEX = re.compile(r'^\w{3} \d{1,2}')
TIME_REGEX = re.compile(r'\d{2}:\d{2}:\d{2}')
queries_list = []
with filedialog.askopenfile(title = 'Select DNS Query Log', filetypes=[('Log Files', '.log'),('Text Files', '.txt')]) as f:
    for line in f:
        if DNS_QUERY_EXISTS.search(line):
            dns_query = Query()
            dns_query.date = MONTH_DAY_REGEX.search(line).group()
            dns_query.time = TIME_REGEX.search(line).group()
            dns_query.requestor = IP_REGEX.search(line).group()
            dns_query.record_type = (line.split(sep = 'query['))[1].split(']')[0]
            dns_query.query = (line.split(sep = '] '))[1].split(' from')[0]
            queries_list.append(dns_query)
requestors = {}
queries = {}
record_types = {}
dates = {}
for query in queries_list:
    if query.requestor in requestors:
        requestors[query.requestor] += 1 
    else:
        requestors[query.requestor] = 1 
    if query.query in queries:
        queries[query.query] += 1 
    else:
        queries[query.query] = 1 
    if query.record_type in record_types:
        record_types[query.record_type] += 1 
    else:
        record_types[query.record_type] = 1
    if query.date in dates:
        dates[query.date] += 1 
    else:
        dates[query.date] = 1

#sorted_queries = sorted(queries.items(), key = lambda x:x[1], reverse = True)
#sorted_dates = sorted(dates.items())
csv_file = 'queries.csv'
fieldnames = ['query','amount']
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    for k, v in queries.items():
        writer.writerow((k,v))
#toBarGraph(queries)