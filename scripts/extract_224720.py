import zipfile
p='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs_22472006902.zip'
with zipfile.ZipFile(p) as z:
    for n in z.namelist():
        if 'Run News Bot' in n or 'update-news' in n:
            print('FOUND',n)
    target=[n for n in z.namelist() if 'update-news/5_Run News Bot.txt' in n][0]
    txt=z.read(target).decode('utf-8',errors='replace')
    out='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_newsbot_log_22472006902.txt'
    open(out,'w',encoding='utf-8').write(txt)
    print('wrote',out)
