from dateutil.relativedelta import *
from dateutil.parser import *
import datetime
import requests
import sys
import json
import os
from community_week import CommunityWeekFinder, CommunityWeek
from issue_events import IssueEvents, IssueEventsFetcher

owner = sys.argv[1]
repo = sys.argv[2]
interval = 7

def get_date(community_week):
    return community_week.start_date

events = IssueEventsFetcher.fetch_issue_events(owner, repo, interval)

end_date = datetime.date.today() + relativedelta(weekday=SU(+1))

start_date = events[-1].issue_opened + relativedelta(weekday=SU(-1))

week_finder = CommunityWeekFinder(start_date, end_date)

map(week_finder.add_event, events)

#unaggregated statistics

velocities = open('point_velocities.csv', 'w')
velocities.truncate()
velocities.write('week,opened,closed\n')

still_open = open('still_open.csv', 'w')
still_open.truncate()
still_open.write('week,still_opened\n')

burnup = open('burnup.csv', 'w')
burnup.truncate()
burnup.write('week,opened,closed\n')


average_issue_latency = open('average_issue_latency.csv', 'w')
average_issue_latency.truncate()
average_issue_latency.write('week,average_issue_latency\n')

week_index = 0
total_opened = 0
total_closed = 0
difference = 0

for week in sorted(week_finder.community_week_dict.values(), key=get_date):
    total_opened += week.issues_opened
    total_closed += week.issues_closed
    difference = total_opened - total_closed

    velocities.write(str(week_index) + ',' + str(week.issues_opened) + ','+ str(week.issues_closed) + '\n')
    still_open.write(str(week_index) + ',' + str(difference) + '\n')
    burnup.write(str(week_index) + ',' + str(total_opened) + ',' + str(total_closed) + '\n')
    average_issue_latency.write(str(week_index) + ',' + str(week.average_issue_age()) + '\n')
    week_index += 1

#aggregated statistics

month_velocities = open('month_velocities.csv', 'w')
month_velocities.truncate()

month_index = 0
week_index = 0
opened_per_month = 0
closed_per_month = 0

month_velocities.write('month,opened,closed\n')

for week in sorted(week_finder.community_week_dict.values(), key=get_date):
    opened_per_month += week.issues_opened
    closed_per_month += week.issues_closed
    if week_index % 4 == 3:
        month_velocities.write(str(month_index) + ',' + str(opened_per_month) + ','+ str(closed_per_month) + '\n')
        month_index += 1
        opened_per_month = 0
        closed_per_month = 0
    week_index += 1

