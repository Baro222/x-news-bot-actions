import json
from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
req = Request('https://api.github.com/repos/Baro222/x-news-bot-actions/actions/runs')
req.add_header('Authorization', 'Bearer ' + pat)
req.add_header('Accept','application/vnd.github+json')
with urlopen(req, timeout=30) as r:
    data = json.load(r)
    print('total_count', data.get('total_count'))
    for run in data.get('workflow_runs', [])[:5]:
        print(run['id'], run['name'], run['status'], run.get('conclusion'), run['html_url'])
