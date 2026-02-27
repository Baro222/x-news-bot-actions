import zipfile
p='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs_22472006902.zip'
with zipfile.ZipFile(p) as z:
    for n in z.namelist():
        print(n)
    print('total', len(z.namelist()))
