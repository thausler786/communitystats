from dateutil.relativedelta import *
import datetime

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
        opened_week_key = CommunityWeekFinder.get_sunday_before_day(issue_event.issue_opened)
        if opened_week_key:
            self.community_week_dict[opened_week_key].issues_opened += 1
        closed_week_key = CommunityWeekFinder.get_sunday_before_day(issue_event.issue_closed)
        if closed_week_key:
            self.community_week_dict[closed_week_key].issues_closed += 1
        self.add_latencies(issue_event)

    def add_latencies(self, issue_event):
        opened_week_key = CommunityWeekFinder.get_sunday_before_day(issue_event.issue_opened)
        closed_week_key = CommunityWeekFinder.get_sunday_before_day(issue_event.issue_closed) or datetime.date.max
        opened_week_index = self.community_week_dict[opened_week_key].week_index

        if opened_week_key:
            week_key = opened_week_key
            while (week_key in self.community_week_dict and week_key <= closed_week_key):
                current_week = self.community_week_dict[week_key]
                current_week.issues_open += 1
                current_week.total_weeks_open += current_week.week_index - opened_week_index
                week_key = week_key + datetime.timedelta(days=+7)

    @staticmethod
    def get_sunday_before_day(day):
        if day is None:
            return None
        return day + relativedelta(weekday=SU(-1))

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

    def average_issue_age(self):
        return float(self.total_weeks_open) / float(self.issues_open)

