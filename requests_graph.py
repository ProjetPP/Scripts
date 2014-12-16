#!/usr/bin/env python3

import sys
import time
import array
import datetime
import requests
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

NB_HOURS = 24
GRANULOMETRY = 15 # must be a divisor of 60

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
data = [x.seconds//(60*GRANULOMETRY) for x in data if x <= max_]

# Compute the height of the bars
requests_per_minute = array.array('I', (0 for x in range(0, 60*NB_HOURS//GRANULOMETRY)))
for x in data:
    requests_per_minute[(60*NB_HOURS//GRANULOMETRY) - x - 1] += 1


# Final plot
x = range(0, 60*NB_HOURS//GRANULOMETRY)
plt.plot(x, requests_per_minute, label=None)
plt.title("Requests to the PPP")
plt.xlabel("Time (minutes)")
plt.ylabel("Requests")
plt.legend()
plt.savefig(sys.argv[1])
