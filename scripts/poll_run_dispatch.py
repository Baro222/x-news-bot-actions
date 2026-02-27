import time, json
from urllib.request import Request, urlopen
pat = open('C:/openclaw_data/.openclaw/workspace/secure/gh_pat.txt').read().strip()
for i in range(60):
    req = Request('https://api.github.com/repos/Baro222/x-news-bot-actions/actions/runs?event=workflow_dispatch')
    req.add_header('Authorization','Bearer '+pat)
    req.add_header('Accept','application/vnd.github+json')
    with urlopen(req, timeout=30) as r:
        data=json.load(r)
    runs = data.get('workflow_runs',[])
    if runs:
        run = runs[0]
        print(i, 'found run', run['id'], run['status'], run.get('conclusion'))
        if run['status']=='completed':
            print(json.dumps(run, indent=2))
            break
    else:
        print(i, 'no runs yet')
    time.sleep(5)
