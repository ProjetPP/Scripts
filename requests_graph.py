#!/usr/bin/env python3

import sys
import time
import array
import argparse
import datetime
import requests
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Parse arguments
parser = argparse.ArgumentParser(
        description='Plots of graph of requests to the PPP')
parser.add_argument('outputfile')
parser.add_argument('-g', '--granulometry', type=int,
        default=1, help='Number of sections per hour.')
parser.add_argument('-n', '--nb-hours', type=int,
        default=48, help='Number of sections per hour.')
parser.add_argument('-t', '--ticks', type=int,
        default=6, help='Number of hours between two labels.')
args = parser.parse_args()
OUTPUT_FILE = args.outputfile
NB_HOURS = args.nb_hours
GRANULOMETRY = 60//args.granulometry
TICKS = args.ticks

# Initialize matplotlib
fig, ax = plt.subplots()

# Get data
data = requests.get('http://logger.frontend.askplatyp.us/', params={'limit': 10000}).json()

# Convert to datetime
data = [datetime.datetime(*time.strptime(x[1].split('.')[0], "%Y-%m-%d %H:%M:%S")[:6]) for x in data]

# Compute the difference
datemax = datetime.datetime.now()
data = [datemax - x for x in data]
delta = datetime.timedelta(hours=NB_HOURS)
datemin = datemax - delta
ax.set_xlim(datemin, datemax)

# Shrink and convert to minutes
data = [x.seconds//(60*GRANULOMETRY) for x in data if x <= delta]

# Compute the height of the bars
requests_per_minute = array.array('I', (0 for x in range(0, 60*NB_HOURS//GRANULOMETRY)))
for x in data:
    requests_per_minute[(60*NB_HOURS//GRANULOMETRY) - x - 1] += 1

# Units
hours    = mdates.HourLocator(interval=TICKS) # Show ticks every 6 hour
hoursFmt = mdates.DateFormatter('%H:00')
ax.xaxis.set_major_locator(hours)
ax.xaxis.set_major_formatter(hoursFmt)

# Final plot
x = list(map(lambda x:datemin + datetime.timedelta(minutes=x*GRANULOMETRY), range(0, 60*NB_HOURS//GRANULOMETRY)))
ax.plot(x, requests_per_minute, label=None)

# Titles
plt.title("Requests to the PPP in the last %d hours" % NB_HOURS)
plt.xlabel("Time (hours)")
plt.ylabel("Requests (per slice of %d minutes)" % GRANULOMETRY)
#plt.legend()
plt.savefig(OUTPUT_FILE)
