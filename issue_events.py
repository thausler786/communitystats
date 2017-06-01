
from dateutil.relativedelta import *
from dateutil.parser import *
import datetime
import requests
import sys
import json
import os
from community_week import CommunityWeekFinder, CommunityWeek

class IssueEvents:
    issue_opened = 0
    issue_closed = 0

    def __init__(self, issue_opened, issue_closed):
        self.issue_opened = issue_opened
        self.issue_closed = issue_closed

class IssueEventsFetcher:
    @staticmethod
    def github_creds():
        return requests.auth.HTTPBasicAuth(os.environ['COMM_USER'], os.environ['COMM_PASSWORD'])

    @staticmethod
    def fetch_issue_events(owner, repo, interval):
        req = requests.get(('https://api.github.com/repos/%(owner)s/%(repo)s/issues?sort:created_at&order=asc&state=all' % locals()), auth=IssueEventsFetcher.github_creds())
        issue_array = json.loads(req.text)
        while ('next' in req.links and 'url' in req.links['next']):
            req = requests.get(req.links['next']['url'], auth=IssueEventsFetcher.github_creds())
            issue_array += json.loads(req.text)
            if not ('next' in req.links and 'url' in req.links['next']):
                break
        return map(IssueEventsFetcher.get_events, issue_array)

    @staticmethod
    def get_events(issue):
        events = IssueEvents(IssueEventsFetcher.get_day_for_date(issue['created_at']),
                             IssueEventsFetcher.get_day_for_date(issue['closed_at']))
        return events

    @staticmethod
    def get_day_for_date(date_string):
        if date_string is None:
            return None
        raw_date = parse(date_string)
        day = datetime.date(year=raw_date.year,
                            month=raw_date.month,
                            day=raw_date.day)
        return day
