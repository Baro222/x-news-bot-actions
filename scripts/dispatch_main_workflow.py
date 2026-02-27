import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
pat_path = r"C:\openclaw_data\.openclaw\workspace\secure\gh_pat.txt"
workflow = "main.yml"
repo = "Baro222/x-news-bot-actions"
ref = "main"
try:
    with open(pat_path, 'r', encoding='utf-8') as f:
        pat = f.read().strip()
except Exception as e:
    print('ERROR: could not read PAT file:', e)
    sys.exit(2)
url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
body = json.dumps({"ref": ref}).encode('utf-8')
req = Request(url, data=body, method='POST')
req.add_header('Accept', 'application/vnd.github+json')
req.add_header('Authorization', f'Bearer {pat}')
req.add_header('Content-Type', 'application/json')
try:
    with urlopen(req, timeout=30) as resp:
        print('DISPATCH_STATUS', resp.status)
        print('DISPATCH_REASON', resp.reason)
        print('Workflow dispatched (likely 204 Accepted).')
except HTTPError as e:
    print('HTTP_ERROR', e.code)
    try:
        print(e.read().decode())
    except Exception:
        pass
    sys.exit(3)
except Exception as e:
    print('ERROR', e)
    sys.exit(4)
