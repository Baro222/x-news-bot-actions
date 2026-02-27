import zipfile, os
p='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs_22493057531.zip'
if not os.path.exists(p):
    print('missing',p)
else:
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            print(n)
        target=None
        for n in z.namelist():
            if 'Run newsbot' in n or 'Run newsbot (main.py)' in n or 'Run News Bot' in n or 'Run newsbot (main.py).txt' in n:
                target=n
                break
        if not target:
            txts=[n for n in z.namelist() if n.endswith('.txt')]
            if txts:
                target=txts[-1]
        print('target=',target)
        if target:
            txt=z.read(target).decode('utf-8',errors='replace')
            out='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/extracted_runlog_22493057531.txt'
            open(out,'w',encoding='utf-8').write(txt)
            print('wrote',out)
