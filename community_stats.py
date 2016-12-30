from dateutil.relativedelta import *
from dateutil.parser import *
import datetime
import requests
import sys
import json
import os

owner = sys.argv[1]
repo = sys.argv[2]
interval = 7

class IssueEvents:
    issue_opened = 0
    issue_closed = 0

    def __init__(self, issue_opened, issue_closed):
        self.issue_opened = issue_opened
        self.issue_closed = issue_closed

class CommunityWeekFinder:
    start_date = 0
    end_date = 0
    community_week_dict = {}

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        week_start_date = start_date
        week_index = 0
        while week_start_date < end_date:
            self.community_week_dict[week_start_date] = CommunityWeek(week_start_date, week_index)
            week_start_date = week_start_date + relativedelta(weeks=+1)
            week_index += 1

    def get_week(date):
        return date

    def add_event(self, issue_event):
        #print "adding" + str(issue_event.issue_opened) + " to " + str(issue_event.issue_closed)
        opened_week_key = get_sunday_before_day(issue_event.issue_opened)
        if opened_week_key:
            self.community_week_dict[opened_week_key].issues_opened += 1
        closed_week_key = get_sunday_before_day(issue_event.issue_closed)
        if closed_week_key:
            self.community_week_dict[closed_week_key].issues_closed += 1
        self.add_latencies(issue_event)

    def add_latencies(self, issue_event):
        opened_week_key = get_sunday_before_day(issue_event.issue_opened)
        closed_week_key = get_sunday_before_day(issue_event.issue_closed) or datetime.datetime.max
        opened_week_index = self.community_week_dict[opened_week_key].week_index


        if opened_week_key:
            week_key = opened_week_key
            while (self.community_week_dict[week_key] and week_key <= closed_week_key):
                current_week = self.community_week_dict[week_key]
                current_week.issues_open += 1
                current_week.total_weeks_open += current_week.week_index - opened_week_index

                week_key = week_key + datetime.timedelta(days=+7)

class CommunityWeek:
    issues_opened = 0
    issues_closed = 0
    start_date = 0
    end_date = 0

    issues_open = 0
    total_weeks_open = 0

    week_index = 0

    def __init__(self, start_date, week_index):
        self.start_date = start_date
        end_date = start_date + relativedelta(weeks=+1)
        issues_opened = 0
        issues_closed = 0
        issues_open = 0
        total_weeks_open = 0
        self.week_index = week_index

    def contains_date(date):
        return date >= start_date and date < end_date

    def average_issue_age():
        return issues_open / total_weeks_open

def github_creds():
    return requests.auth.HTTPBasicAuth(os.environ['COMM_USER'], os.environ['COMM_PASSWORD'])


def fetch_issue_events(owner, repo, interval):
    req = requests.get(('https://api.github.com/repos/%(owner)s/%(repo)s/issues?sort:created_at&order=asc&state=all' % locals()), auth=github_creds())
    issue_array = json.loads(req.text)
    while ('next' in req.links and 'url' in req.links['next']):
        print req.links['next']['url']
        req = requests.get(req.links['next']['url'], auth=github_creds())
        issue_array += json.loads(req.text)
        if not ('next' in req.links and 'url' in req.links['next']):
            break
    return map(get_events, issue_array)

def get_events(issue):
    events = IssueEvents(get_day_for_date(issue['created_at']), get_day_for_date(issue['closed_at']))
    return events

def get_sunday_before_day(day):
    if day is None:
        return None
    return day + relativedelta(weekday=SU(-1))

def get_day_for_date(date_string):
    if date_string is None:
        return None
    raw_date = parse(date_string)
    day = datetime.date(year=raw_date.year,
                        month=raw_date.month,
                        day=raw_date.day)
    return day

def get_date(community_week):
    return community_week.start_date

events = fetch_issue_events(owner, repo, interval)

end_date = get_day_for_date('2016-12-31T02:44:41Z') + relativedelta(weekday=SU(+2))

start_date = events[-1].issue_opened + relativedelta(weekday=SU(-1))

week_finder = CommunityWeekFinder(start_date, end_date)

map(week_finder.add_event, events)

#unaggregated statistics

velocities = open('point_velocities.csv', 'w')
velocities.truncate()

still_open = open('still_open.csv', 'w')
still_open.truncate()

burnup = open('burnup.csv', 'w')
burnup.truncate()

week_index = 0
total_opened = 0
total_closed = 0
difference = 0

velocities.write('week,opened,closed\n')
still_open.write('week,still_opened\n')
burnup.write('week,opened,closed\n')

for week in sorted(week_finder.community_week_dict.values(), key=get_date):
    total_opened += week.issues_opened
    total_closed += week.issues_closed
    difference = total_opened - total_closed

    velocities.write(str(week_index) + ',' + str(week.issues_opened) + ','+ str(week.issues_closed) + '\n')
    still_open.write(str(week_index) + ',' + str(difference) + '\n')
    burnup.write(str(week_index) + ',' + str(total_opened) + ',' + str(total_closed) + '\n')
    week_index += 1

#aggregated statistics

month_velocities = open('month_velocities.csv', 'w')
month_velocities.truncate()

month_index = 0
week_index = 0
opened_per_month = 0
closed_per_month = 0


burnup.write('month,opened,closed\n')

for week in sorted(week_finder.community_week_dict.values(), key=get_date):
    opened_per_month += week.issues_opened
    closed_per_month += week.issues_closed
    if week_index % 4 == 3:
        month_velocities.write(str(month_index) + ',' + str(opened_per_month) + ','+ str(closed_per_month) + '\n')
        month_index += 1
        opened_per_month = 0
        closed_per_month = 0
    week_index += 1

