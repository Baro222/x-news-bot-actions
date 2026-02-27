import sys, json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
pat_path = r"C:\openclaw_data\.openclaw\workspace\secure\gh_pat.txt"
try:
    with open(pat_path,'r',encoding='utf-8') as f:
        pat = f.read().strip()
except Exception as e:
    print('ERROR reading PAT', e); sys.exit(2)
req = Request('https://api.github.com/user')
req.add_header('Authorization', f'Bearer {pat}')
req.add_header('Accept','application/vnd.github+json')
try:
    with urlopen(req, timeout=30) as r:
        data = r.read().decode()
        print('OK', data)
except HTTPError as e:
    print('HTTP_ERROR', e.code)
    try:
        print(e.read().decode())
    except:
        pass
    sys.exit(3)
except Exception as e:
    print('ERROR', e); sys.exit(4)
