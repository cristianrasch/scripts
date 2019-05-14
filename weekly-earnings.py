#!/usr/bin/env python3

from argparse import ArgumentParser
from decimal import Decimal
from datetime import date, timedelta
import os
import re

DEF_HR_RATE = Decimal(70)
TIME_FORMAT = "%d:%02d"
DATE_FORMAT = "%m/%d"
CURRENCY_FORMAT = "$%6.2f"
ENTRY_SEP = ","
ENTRY_RE = re.compile(r'(\d{1,})(?::(\d{2}))?')
MINS_IN_HR = Decimal(60)

def format_time(time_in_mins):
    return TIME_FORMAT % (time_in_mins / 60, time_in_mins % 60)

def format_currency(amount):
  return CURRENCY_FORMAT % amount

parser = ArgumentParser(description="Weekly earnings calculator")
parser.add_argument("-d", "--date", metavar="IS08601_DATE",
                    help="First day of the billing cycle")
parser.add_argument("-e", "--entry", metavar="H1:M1,M2", dest="entries",
                    help="hour1:min1,min2", action="append")
parser.add_argument("-r", "--rate", type=Decimal,
                    help="Hourly rate (overrides the RATE env var)")
args = parser.parse_args()

weekly_earnings = Decimal(0)
total_time_tracked_in_mins = 0

dt = args.date
one_day = timedelta(days=1)
if dt:
    dt = date.fromisoformat(dt)
else:
    dt = date.today()
    while dt.weekday(): # 0=Monday
        dt -= one_day

hr_rate = args.rate or Decimal(os.environ.get('RATE', DEF_HR_RATE))

for day_entries in args.entries:
  day_mins = 0
  for entry in day_entries.split(ENTRY_SEP):
    for match in ENTRY_RE.finditer(entry):
        h_or_m, m = match.group(1, 2)
        if m:
            day_mins += int(h_or_m)*60 + int(m)
        else:
            day_mins += int(h_or_m)

  total_time_tracked_in_mins += day_mins

  day_earnings = (day_mins * hr_rate) / MINS_IN_HR
  d = dt.strftime(DATE_FORMAT)
  t = format_time(day_mins)
  amount = format_currency(day_earnings)
  print(f"[{d}] {t} hours tracked - {amount}")

  weekly_earnings += day_earnings
  dt += one_day

total_hours_tracked = format_time(total_time_tracked_in_mins)
total_earnings = format_currency(weekly_earnings)
print(f"\n{total_hours_tracked} hours tracked in total - {total_earnings}")
