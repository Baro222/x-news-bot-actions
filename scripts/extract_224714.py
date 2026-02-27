import zipfile
p='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs_22471462697.zip'
with zipfile.ZipFile(p) as z:
    names=z.namelist()
    for n in names:
        if '5_Run News Bot' in n or 'Run News Bot' in n:
            print('FOUND',n)
    target=[n for n in names if '5_Run News Bot' in n][0]
    txt=z.read(target).decode('utf-8',errors='replace')
    out='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_newsbot_log_22471462697.txt'
    open(out,'w',encoding='utf-8').write(txt)
    print('wrote',out)
