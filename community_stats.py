import requests
import sys
import json

owner = sys.argv[1]
repo = sys.argv[2]
interval = 7
range = 30

def fetch_issue_events(owner, repo, interval, range):
    req = requests.get('https://api.github.com/search/issues?q=the+type:pr+sort:created_at', auth=requests.auth.HTTPBasicAuth('communitystats', 'clone7adhere'))
    req = requests.get(('https://api.github.com/repos/%(owner)s/%(repo)s/issues?sort:created_at' % locals()), auth=requests.auth.HTTPBasicAuth('communitystats', 'clone7adhere'))
    while req.links['next']['url']
    print req.text
    issues = json.loads(req.text)
    map(get_events, issues)

def get_events(issue):
    print issue['created_at']



fetch_issue_events(owner, repo, interval, range)

