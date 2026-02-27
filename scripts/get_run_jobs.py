import json
import sys
from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
run_id = '22471309644'
req = Request(f'https://api.github.com/repos/Baro222/x-news-bot-actions/actions/runs/{run_id}/jobs')
req.add_header('Authorization', 'Bearer ' + pat)
req.add_header('Accept','application/vnd.github+json')
with urlopen(req, timeout=30) as r:
    data = json.load(r)
    print('total_jobs', data.get('total_count'))
    for job in data.get('jobs',[]):
        print('JOB', job['id'], job['name'], job['status'], job.get('conclusion'))
        for step in job.get('steps',[]):
            print('  STEP', step.get('name'), step.get('status'), step.get('conclusion'))
            if step.get('name')=='Run newsbot (main.py)':
                # fetch logs_url?
                pass
