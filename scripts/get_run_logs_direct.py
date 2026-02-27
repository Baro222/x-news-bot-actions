from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
run_id='22471309644'
req=Request(f'https://api.github.com/repos/Baro222/x-news-bot-actions/actions/runs/{run_id}/logs')
req.add_header('Authorization','Bearer '+pat)
req.add_header('Accept','application/vnd.github+json')
with urlopen(req, timeout=60) as r:
    data=r.read()
    open('C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs.zip','wb').write(data)
    print('wrote', len(data))
