import os
os.environ['DRY_RUN']='1'
import logging
logging.basicConfig(level=logging.INFO)
# Ensure repo root on path
import sys
repo_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, repo_root)
# Monkeypatch telegram_sender to prevent any network sends
try:
    import telegram_sender
    def _noop_send_news_report(ranked_news):
        logging.info('DRY_RUN: send_news_report suppressed; would have sent %d messages', sum(len(v) for v in ranked_news.values()))
        return True
    def _noop_send_telegram_message(text):
        logging.info('DRY_RUN: send_telegram_message suppressed')
        return True
    telegram_sender.send_news_report = _noop_send_news_report
    telegram_sender.send_telegram_message = _noop_send_telegram_message
except Exception as e:
    logging.warning('telegram_sender import failed or cannot monkeypatch: %s', e)

from main import run_news_cycle
success = run_news_cycle()
print('DRY_RUN success=', success)
