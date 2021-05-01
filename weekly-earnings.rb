#!/usr/bin/env ruby

require "bigdecimal"
require "date"
require "optparse"

DEF_HR_RATE = BigDecimal(70)
TIME_FORMAT = "%d:%02d".freeze
DATE_FORMAT = "%m/%d".freeze
CURRENCY_FORMAT = "$%6.2f".freeze
ENTRY_SEP = ",".freeze

def format_time(time_in_mins)
  TIME_FORMAT % [time_in_mins / 60, time_in_mins % 60]
end

def format_currency(amount)
  CURRENCY_FORMAT % amount
end

arguments = { entries: [] }
OptionParser.new do |args|
  args.banner = "Usage: #{__FILE__} [options]"

  args.on("-d", "--start-date DATE", "First day of the billing cycle") do |date|
    arguments[:start_date] = Date.parse(date)
  end

  args.on("-e", "--entry ENTRY", "hour1:min1,min2", "e.g. 49,2:04") do |entry|
    arguments[:entries] << entry
  end

  args.on("-r", "--rate RATE", "Hourly rate (overrides the RATE env var)") do |rate|
    arguments[:rate] = BigDecimal(rate)
  end

  args.on("-q", "--discreet", "Don't output any monetary amount") do |rate|
    arguments[:discreet] = true
  end
end.parse!

weekly_earnings = BigDecimal(0)
total_time_tracked_in_mins = 0

date = arguments[:start_date]
date ||= begin
           today = Date.today

           if today.monday?
             today -= 7
           else
             today -= 1 until today.monday?
           end

           today
         end

hr_rate = arguments[:rate] || BigDecimal(ENV.fetch("RATE", DEF_HR_RATE))

arguments[:entries].each do |day_entries|
  entries = day_entries.split(ENTRY_SEP)

  minutes = entries.map do |e|
    h_or_m, m = e.match(/\A(\d{1,})(?::(\d{2}))?\z/).captures

    if m.nil?
      h_or_m.to_i
    else
      h_or_m.to_i * 60 + m.to_i
    end
  end
  day_mins = minutes.inject(&:+)

  total_time_tracked_in_mins += day_mins

  day_earnings = (day_mins * hr_rate) / 60.0
  d = date.strftime(DATE_FORMAT)
  t = format_time(day_mins)
  row = "[#{d}] #{t} hours tracked"
  unless arguments[:discreet]
    amount = format_currency(day_earnings)
    row << " - #{amount}"
  end
  puts row

  weekly_earnings += day_earnings
  date += 1
end

total_hours_tracked = format_time(total_time_tracked_in_mins)
last_row = "\n#{total_hours_tracked} hours tracked in total"
unless arguments[:discreet]
  total_earnings = format_currency(weekly_earnings)
  last_row << " - #{total_earnings}"
end
puts last_row
