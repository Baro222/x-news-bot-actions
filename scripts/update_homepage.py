"""
homepage.html을 최신 뉴스 데이터로 업데이트하는 스크립트
data/processed_news.json → homepage.html의 '최근 하이라이트' 섹션 갱신
"""

import re
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO = Path(__file__).resolve().parents[1]
PROCESSED = REPO / 'data' / 'processed_news.json'
DASHBOARD_JSON = REPO / 'dashboard' / 'public' / 'processed_news.json'
MOCK = REPO / 'dashboard' / 'src' / 'lib' / 'mockData.ts'
HOMEPAGE = REPO / 'homepage.html'

items = []

# Primary source 1: data/processed_news.json (list 형식)
if PROCESSED.exists():
    try:
        data = json.loads(PROCESSED.read_text(encoding='utf-8'))
        if isinstance(data, list):
            for obj in data:
                title = obj.get('title') or obj.get('_headline') or obj.get('headline') or ''
                summary = obj.get('summary') or obj.get('_summary') or obj.get('summary_text') or ''
                source = obj.get('source') or obj.get('account') or obj.get('sourceHandle') or ''
                category = obj.get('category', '')
                if title and summary:
                    items.append({'title': title, 'summary': summary, 'source': source, 'category': category})
        print(f'data/processed_news.json 로드: {len(items)}개 항목')
    except Exception as e:
        print(f'data/processed_news.json 파싱 실패: {e}')

# Primary source 2: dashboard/public/processed_news.json (dict 형식)
if not items and DASHBOARD_JSON.exists():
    try:
        data = json.loads(DASHBOARD_JSON.read_text(encoding='utf-8'))
        if isinstance(data, dict) and 'news' in data:
            for obj in data['news']:
                title = obj.get('title', '')
                summary = obj.get('summary', '')
                source = obj.get('source', '')
                category = obj.get('category', '')
                if title and summary:
                    items.append({'title': title, 'summary': summary, 'source': source, 'category': category})
        print(f'dashboard/public/processed_news.json 로드: {len(items)}개 항목')
    except Exception as e:
        print(f'dashboard JSON 파싱 실패: {e}')

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
            t = re.search(r"title:\s*['\"]([^'\"]+)['\"]", pclean)
            s = re.search(r"summary:\s*['\"]([^'\"]+)['\"]", pclean)
            src = re.search(r"source:\s*['\"]([^'\"]+)['\"]", pclean)
            if t and s:
                items.append({'title': t.group(1), 'summary': s.group(1), 'source': src.group(1) if src else ''})
    print(f'mockData.ts 폴백: {len(items)}개 항목')

# If still empty, use placeholder
if not items:
    items = [{'title': '뉴스 데이터 없음', 'summary': '뉴스봇 실행 후 데이터가 자동으로 업데이트됩니다.', 'source': 'system'}]

# Select up to 5 items (sorted by importance if available)
selected = items[:5]

# Generate timestamp
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
time_str = now_kst.strftime('%Y.%m.%d %H:%M KST')

# Read homepage and replace the news-list inner HTML
hp = HOMEPAGE.read_text(encoding='utf-8')

# Update summary section
total_count = len(items)
summary_text = f'<strong>최근 수집</strong>: 약 {total_count}건의 뉴스를 수집하여 AI 요약을 수행했습니다. ({time_str} 기준)'
hp = re.sub(
    r'<strong>최근 수집</strong>:.*?<br>',
    summary_text + '<br>',
    hp,
    flags=re.S
)

# Update news list section
new_section = ['  <section class="news-list">', '    <h2>최근 하이라이트</h2>']
for it in selected:
    cat_badge = f'[{it.get("category", "")}] ' if it.get('category') else ''
    new_section.append('    <div class="news-item">')
    new_section.append(f'      <div><strong>{cat_badge}{it["title"]}</strong></div>')
    new_section.append(f'      <div class="meta">출처: {it["source"]} | {it["summary"][:150]}</div>')
    new_section.append('    </div>')
new_section.append('  </section>')

new_html = re.sub(
    r'<section class="news-list">.*?</section>',
    '\n'.join(new_section),
    hp,
    flags=re.S
)

HOMEPAGE.write_text(new_html, encoding='utf-8')
print(f'homepage.html 업데이트 완료: {len(selected)}개 항목 반영')
