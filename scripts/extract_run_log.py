import zipfile
p='C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_logs.zip'
with zipfile.ZipFile(p) as z:
    names=z.namelist()
    target=[n for n in names if '5_Run News Bot' in n][0]
    data=z.read(target)
    txt=data.decode('utf-8',errors='replace')
    open('C:/openclaw_data/.openclaw/workspace/repos/x-news-bot-actions/scripts/run_newsbot_log.txt','w',encoding='utf-8').write(txt)
    # wrote file
