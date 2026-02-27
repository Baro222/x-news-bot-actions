import re
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROCESSED = REPO / 'data' / 'processed_news.json'
MOCK = REPO / 'mockData.ts'
HOMEPAGE = REPO / 'homepage.html'

items = []

# Primary source: processed_news.json (produced by ai_processor)
if PROCESSED.exists():
    try:
        data = json.loads(PROCESSED.read_text(encoding='utf-8'))
        # Expecting a list of objects with keys: title, summary, source
        for obj in data:
            title = obj.get('title') or obj.get('_headline') or obj.get('headline')
            summary = obj.get('summary') or obj.get('_summary') or obj.get('summary_text')
            source = obj.get('source') or obj.get('account') or obj.get('sourceHandle') or ''
            if title and summary:
                items.append({'title': title, 'summary': summary, 'source': source})
    except Exception as e:
        print('Failed to parse processed_news.json:', e)

# Fallback: parse mockData.ts
if not items and MOCK.exists():
    text = MOCK.read_text(encoding='utf-8')
    m = re.search(r"export const mockNews:\s*NewsItem\[\] = \[(.*?)\];", text, re.S)
    if m:
        arr = m.group(1)
        parts = re.split(r"\},\s*\{", arr)
        for p in parts:
            pclean = p.strip()
            if not pclean.startswith('{'):
                pclean = '{' + pclean
            if not pclean.endswith('}'):
                pclean = pclean + '}'
            t = re.search(r"title:\s*'([^']+)'", pclean)
            s = re.search(r"summary:\s*'([^']+)'", pclean)
            src = re.search(r"source:\s*'([^']+)'", pclean)
            if t and s:
                items.append({'title': t.group(1), 'summary': s.group(1), 'source': src.group(1) if src else ''})

# If still empty, use placeholder
if not items:
    items = [{'title': '샘플 뉴스 없음', 'summary': '데이터를 불러올 수 없습니다.', 'source': 'local'}]

# Select up to 5 items according to repo rules (use first 5 by priority)
selected = items[:5]

# Read homepage and replace the news-list inner HTML
hp = HOMEPAGE.read_text(encoding='utf-8')
new_section = ['  <section class="news-list">', '    <h2>최근 하이라이트</h2>']
for it in selected:
    new_section.append('    <div class="news-item">')
    new_section.append(f'      <div><strong>{it["title"]}</strong></div>')
    new_section.append(f'      <div class="meta">출처: {it["source"]} • 요약: {it["summary"]}</div>')
    new_section.append('    </div>')
new_section.append('  </section>')
new_html = re.sub(r"<section class=\"news-list\">.*?</section>", '\\n'.join(new_section), hp, flags=re.S)
HOMEPAGE.write_text(new_html, encoding='utf-8')
print('homepage updated with', len(selected), 'items (source:', 'processed_news.json' if PROCESSED.exists() and items else 'mockData.ts', ')')
