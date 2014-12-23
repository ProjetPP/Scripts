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

# From https://github.com/ProgVal/Limnoria/blob/master/plugins/Time/plugin.py
def human_to_seconds(string):
    seconds = 0
    for arg in string.split(' '):
        if not arg or arg[-1] not in 'ywdhms':
            raise ValueError(arg)
        (s, kind) = arg[:-1], arg[-1]
        i = int(s)
        if kind == 'y':
            seconds += i*31536000
        elif kind == 'w':
            seconds += i*604800
        elif kind == 'd':
            seconds += i*86400
        elif kind == 'h':
            seconds += i*3600
        elif kind == 'm':
            seconds += i*60
        elif kind == 's':
            seconds += i
    return seconds

# Parse arguments
parser = argparse.ArgumentParser(
        description='Plots of graph of requests to the PPP')
parser.add_argument('outputfile')
parser.add_argument('-g', '--granulometry', type=str,
        default='1h', help='Number of sections per hour.')
parser.add_argument('-i', '--interval', type=str,
        default='48h', help='Number of sections per hour.')
parser.add_argument('-t', '--ticks', type=int,
        default=6, help='Number of hours between two labels.')
parser.add_argument('-l', '--logger-url', type=str,
        default='http://logger.frontend.askplatyp.us/',
        help='The URL to the logger.')
args = parser.parse_args()
OUTPUT_FILE = args.outputfile
INTERVAL = human_to_seconds(args.interval)
GRANULOMETRY = human_to_seconds(args.granulometry)
TICKS = args.ticks
LOGGER_URL = args.logger_url

# Initialize matplotlib
fig, ax = plt.subplots()

# Get data
data = requests.get(LOGGER_URL, params={'limit': 10000}).json()

# Convert to datetime
data = [datetime.datetime(*time.strptime(x[1].split('.')[0], "%Y-%m-%d %H:%M:%S")[:6]) for x in data]

# Compute the difference
datemax = datetime.datetime.now()
data = [datemax - x for x in data]
delta = datetime.timedelta(seconds=INTERVAL)
datemin = datemax - delta
ax.set_xlim(datemin, datemax)

# Shrink and convert to seconds
data = [x.seconds//GRANULOMETRY for x in data if x <= delta]

# Compute the height of the bars
requests_per_slice = array.array('I', (0 for x in range(0, INTERVAL//GRANULOMETRY)))
for x in data:
    requests_per_slice[(INTERVAL//GRANULOMETRY) - x - 1] += 1

# Units
if INTERVAL < human_to_seconds('6h'):
    locator = mdates.MinuteLocator(interval=TICKS)
    fmt = mdates.DateFormatter('%H:%M')
elif INTERVAL < human_to_seconds('3d'):
    locator = mdates.HourLocator(interval=TICKS)
    fmt = mdates.DateFormatter('%H:00')
elif INTERVAL < human_to_seconds('8w'):
    locator = mdates.DayLocator(interval=TICKS)
    fmt = mdates.DateFormatter('%d-%m')
else:
    raise ValueError('Too large.')
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(fmt)

# Final plot
x = list(map(lambda x:datemin + datetime.timedelta(seconds=x*GRANULOMETRY), range(0, INTERVAL//GRANULOMETRY)))
ax.plot(x, requests_per_slice, label=None)

# Titles
plt.title("Requests to the PPP in the last %d seconds" % INTERVAL) # TODO: readability
plt.xlabel("Time (hours)")
plt.ylabel("Requests (per slice of %d seconds)" % GRANULOMETRY) # TODO: readability
#plt.legend()
plt.savefig(OUTPUT_FILE)
