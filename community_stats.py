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
range = 30


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
        while week_start_date < end_date:
            self.community_week_dict[week_start_date] = CommunityWeek(week_start_date)
            week_start_date = week_start_date + relativedelta(weeks=+1)

    def get_week(date):
        return date

    def add_event(self, issue_event):
        print "adding" + str(issue_event.issue_opened) + " to " + str(issue_event.issue_closed)
        opened_week_key = get_sunday_before_day(issue_event.issue_opened)
        if opened_week_key:
            self.community_week_dict[opened_week_key].issues_opened += 1
        closed_week_key = get_sunday_before_day(issue_event.issue_closed)
        if closed_week_key:
            self.community_week_dict[closed_week_key].issues_opened += 1

class CommunityWeek:
    issues_opened = 0
    issues_closed = 0
    start_date = 0
    end_date = 0

    def __init__(self, start_date):
        print "making week " + str(start_date)
        self.start_date = start_date
        end_date = start_date + relativedelta(weeks=+1)
        issues_opened = 0
        issues_closed = 0

    def contains_date(date):
        return date >= start_date and date < end_date


def github_creds():
    requests.auth.HTTPBasicAuth(os.environ['COMM_USER'], os.environ['COMM_PASSWORD'])


def fetch_issue_events(owner, repo, interval, range):
    req = requests.get(('https://api.github.com/repos/%(owner)s/%(repo)s/issues?sort:created_at&order=asc&state=all' % locals()), auth=github_creds())
    print req.links
    issue_array = json.loads(req.text)
    while ('next' in req.links and 'url' in req.links['next']):
        print req.links['next']['url']
        req = requests.get(req.links['next']['url'], auth=github_creds())
        issue_array += json.loads(req.text)
        print req.links
        if not ('next' in req.links and 'url' in req.links['next']):
            break
    return map(get_events, issue_array)

def get_events(issue):
    events = IssueEvents(get_day_for_date(issue['created_at']), get_day_for_date(issue['closed_at']))
    print events.issue_opened
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


events = fetch_issue_events(owner, repo, interval, range)

end_date = get_day_for_date('2016-12-15T02:44:41Z') + relativedelta(weekday=SU(+2))

start_date = get_day_for_date('2015-08-27T20:45:56Z') + relativedelta(weekday=SU(-1))

week_finder = CommunityWeekFinder(start_date, end_date)

map(week_finder.add_event, events)

for week in week_finder.community_week_dict.values():
    print "Week " + str(week.start_date) + " had issues opened: " + str(week.issues_opened) + ", issues closed: " + str(week.issues_closed)

