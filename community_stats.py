import requests
import sys

owner = sys.argv[1]
repo = sys.argv[2]
interval = 7
range = 30

def fetch_events(owner, repo, interval, range):
    req = requests.get('https://api.github.com/search/issues/?q=', auth=requests.auth.HTTPBasicAuth('communitystats', ''))
    print req.text


fetch_events(owner, repo, interval, range)

