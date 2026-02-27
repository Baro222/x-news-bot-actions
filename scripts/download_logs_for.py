from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
run_id = '22493057531'
url = f'https://api.github.com/repos/Baro222/x-news-bot-actions/actions/runs/{run_id}/logs'
req = Request(url)
req.add_header('Authorization', 'Bearer '+pat)
req.add_header('Accept', 'application/vnd.github+json')
with urlopen(req, timeout=120) as r:
    data = r.read()
open(f'C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs_{run_id}.zip','wb').write(data)
print('wrote', len(data))
