import json
from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
run_id = '22471309644'
req = Request(f'https://api.github.com/repos/Baro222/x-news-bot-actions/actions/runs/{run_id}/jobs')
req.add_header('Authorization', 'Bearer ' + pat)
req.add_header('Accept','application/vnd.github+json')
with urlopen(req, timeout=30) as r:
    data = json.load(r)
    job = data['jobs'][0]
    print('job html_url', job.get('html_url'))
    print('logs_url', job.get('logs_url'))
    # fetch logs_url
    req2 = Request(job.get('logs_url'))
    req2.add_header('Authorization', 'Bearer ' + pat)
    req2.add_header('Accept','application/vnd.github+json')
    with urlopen(req2, timeout=30) as r2:
        # logs endpoint returns a redirect to a URL; we'll print status
        print('logs status', r2.status)
        data2 = r2.read()
        print('logs bytes', len(data2))
        # save to file
        open('C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/latest_run_logs.zip','wb').write(data2)
        print('saved logs to latest_run_logs.zip')
