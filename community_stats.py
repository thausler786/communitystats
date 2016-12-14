import requests
import sys
import json
import os

owner = sys.argv[1]
repo = sys.argv[2]
interval = 7
range = 30

def github_creds():
    requests.auth.HTTPBasicAuth(os.environ['COMM_USER'], os.environ['COMM_PASSWORD'])


def fetch_issue_events(owner, repo, interval, range):
    req = requests.get('https://api.github.com/search/issues?q=the+type:pr+sort:created_at', auth=github_creds())
    req = requests.get(('https://api.github.com/repos/%(owner)s/%(repo)s/issues?sort:created_at' % locals()), auth=github_creds())
    print req.links
    issue_array = json.loads(req.text)
    while ('next' in req.links and 'url' in req.links['next']):
        print req.links['next']['url']
        #print req.text
        req = requests.get(req.links['next']['url'], auth=github_creds())
        issue_array += json.loads(req.text)
        print req.links
        if not ('next' in req.links and 'url' in req.links['next']):
            break
    map(get_events, issue_array)

def get_events(issue):
    print issue['created_at']



fetch_issue_events(owner, repo, interval, range)

