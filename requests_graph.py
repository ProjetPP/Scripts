#!/usr/bin/env python3

import sys
import time
import array
import datetime
import requests
import matplotlib.pyplot as plt

NB_HOURS = 2

if len(sys.argv) != 2:
    print('Syntax: %s file.png' % sys.argv[0])
    exit(1)

# Get data
data = requests.get('http://gunicorn9005.ppp.pony.ovh/', params={'limit': 10000}).json()

# Convert to datetime
data = [datetime.datetime(*time.strptime(x[1].split('.')[0], "%Y-%m-%d %H:%M:%S")[:6]) for x in data]

# Compute the difference
now = datetime.datetime.now()
data = [now - x for x in data]
max_ = datetime.timedelta(hours=NB_HOURS)

# Shrink and convert to minutes
data = [x.seconds//60 for x in data if x <= max_]

# Compute the height of the bars
requests_per_minute = array.array('I', (0 for x in range(0, 60*NB_HOURS)))
for x in data:
    requests_per_minute[(60*NB_HOURS) - x - 1] += 1

x = range(0, 60*NB_HOURS)


plt.plot(x, requests_per_minute, label=None)
#plt.hist(requests_per_minute, bins=20, histtype='stepfilled', normed=True, color='b', label='Gaussian')
plt.title("Requests per minute")
plt.xlabel("Time (seconds)")
plt.ylabel("Requests")
plt.legend()
plt.savefig(sys.argv[1])
