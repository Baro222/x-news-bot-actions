import json
from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
url = 'https://api.github.com/repos/Baro222/x-news-bot-actions/actions/workflows/run-newsbot.yml/dispatches'
req = Request(url, data=b'{"ref":"main"}', method='POST')
req.add_header('Authorization', 'Bearer '+pat)
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('Content-Type', 'application/json')
with urlopen(req, timeout=30) as r:
    print('STATUS', r.status)
    print(r.read().decode())
