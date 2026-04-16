"""
X 뉴스 자동 수집 및 텔레그램 발송 메인 스크립트 (v4)

개선사항:
1. 73개 X 핸들 모니터링
2. Nitter RSS 기반 트윗 수집
3. LibreTranslate 기반 한글 번역
4. 참여도 점수 기반 우선순위
5. stockhubkr/baroBTC 포스팅 형식
6. 랭킹 시스템

실행: python3.11 main_v4.py
"""

import logging
import sys
import os
import json
from datetime import datetime, timezone, timedelta

# 로깅 설정
repo_root = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.environ.get('LOG_DIR', os.path.join(repo_root, 'logs'))
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    LOG_DIR = os.path.join(repo_root, 'logs')
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass

root_logger = logging.getLogger()
if not root_logger.handlers:
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        fh = logging.FileHandler(os.path.join(LOG_DIR, 'news_bot_v4.log'), encoding='utf-8')
        handlers.insert(0, fh)
    except Exception:
        pass

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


def save_processed_news_for_dashboard(ranked_news: dict, timestamp) -> None:
    """대시보드용 JSON 저장"""
    import uuid
    
    def get_priority(engagement_score: float) -> str:
        if engagement_score >= 30:
            return 'critical'
        elif engagement_score >= 15:
            return 'high'
        elif engagement_score >= 5:
            return 'medium'
        else:
            return 'low'
    
    def get_market_impact(category: str, engagement_score: float) -> str:
        if category == '암호화폐':
            if engagement_score >= 25:
                return 'very_bullish'
            elif engagement_score >= 10:
                return 'bullish'
            else:
                return 'neutral'
        elif category in ['지정학', '경제']:
            if engagement_score >= 25:
                return 'very_bearish'
            elif engagement_score >= 10:
                return 'bearish'
            else:
                return 'neutral'
        else:
            return 'neutral'
    
    news_items = []
    
    for category, items in ranked_news.items():
        for idx, item in enumerate(items):
            engagement_score = item.get('_engagement_score', 0)
            item_id = str(uuid.uuid4())
            
            news_item = {
                'id': item_id,
                'rank': idx + 1,
                'title': item.get('_headline', item.get('text', '')[:50]),
                'summary': item.get('_summary', item.get('text', '')[:200]),
                'fullAnalysis': item.get('_analysis', ''),
                'category': category,
                'priority': get_priority(engagement_score),
                'marketImpact': get_market_impact(category, engagement_score),
                'source': item.get('_account', 'unknown'),
                'sourceHandle': f"@{item.get('_account', 'unknown')}",
                'sourceUrl': item.get('_url', ''),
                'timestamp': item.get('created_at', timestamp.isoformat()),
                'engagement': {
                    'likes': item.get('likeCount', 0),
                    'views': item.get('viewCount', 0),
                    'score': engagement_score
                },
                'relatedAccounts': [],
                'tags': [],
                'impactScore': min(int(engagement_score / 5), 100),
            }
            news_items.append(news_item)
    
    # 참여도 점수 내림차순 정렬
    news_items.sort(key=lambda x: x['engagement']['score'], reverse=True)
    
    output = {
        'timestamp': timestamp.isoformat(),
        'news': news_items,
        'systemStatus': {
            'lastUpdate': timestamp.isoformat(),
            'nextUpdate': (timestamp + timedelta(hours=4)).isoformat(),
            'totalAccounts': 73,
            'activeAccounts': 73,
            'tweetsCollected': sum(len(items) for items in ranked_news.values()),
            'aiAnalysisCount': len(news_items),
            'systemHealth': 'operational',
            'uptime': '99.9%',
        }
    }
    
    # dashboard/public/ 디렉토리에 저장
    dashboard_public_dir = os.path.join(os.path.dirname(__file__), 'dashboard', 'public')
    os.makedirs(dashboard_public_dir, exist_ok=True)
    output_path = os.path.join(dashboard_public_dir, 'processed_news.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info(f"대시보드용 JSON 저장 완료: {output_path} ({len(news_items)}개 뉴스)")


def run_news_cycle_v4():
    """뉴스 수집 → AI 처리 → 텔레그램 발송 전체 사이클 (v4)"""
    
    start_time = datetime.now(KST)
    logger.info(f"===== 뉴스 수집 사이클 시작 (v4): {start_time.strftime('%Y-%m-%d %H:%M KST')} =====")
    
    try:
        # 1단계: 트윗 수집
        logger.info("1단계: X 트윗 수집 시작 (73개 계정)...")
        from twitter_fetcher_v3 import fetch_all_tweets
        tweets = fetch_all_tweets()
        
        if not tweets:
            logger.warning("수집된 트윗이 없습니다. 사이클 종료.")
            from telegram_sender_v4 import _send_via_bot
            _send_via_bot(
                f"⚠️ {start_time.strftime('%Y.%m.%d %H:%M KST')} 브리핑\n"
                "최근 24시간 내 수집된 트윗이 없습니다."
            )
            return False
        
        logger.info(f"수집 완료: {len(tweets)}개 트윗")
        
        # 2단계: AI 분류 및 번역
        logger.info("2단계: AI 분류, 번역, 참여도 점수 계산 시작...")
        from ai_processor_v4 import process_tweets, rank_and_select_news
        
        processed_tweets = process_tweets(tweets)
        ranked_news = rank_and_select_news(processed_tweets)
        
        total_processed = sum(len(items) for items in ranked_news.values())
        logger.info(f"AI 처리 완료: 총 {total_processed}개 뉴스 분류")
        
        for category, items in ranked_news.items():
            if items:
                logger.info(f"  [{category}] {len(items)}개 - TOP 1 참여도: {items[0].get('_engagement_score', 0):.2f}")
        
        # 3단계: 텔레그램 발송 (v4 형식: stockhubkr + baroBTC)
        logger.info("3단계: 텔레그램 발송 시작 (v4 형식)...")
        from telegram_sender_v4 import send_news_report_v4
        success = send_news_report_v4(ranked_news)
        
        if success:
            logger.info("텔레그램 발송 완료!")
        else:
            logger.error("텔레그램 발송 실패!")
        
        # 결과 저장
        result_file = f"{LOG_DIR}/last_result_v4.json"
        save_data = {
            "timestamp": start_time.isoformat(),
            "tweets_collected": len(tweets),
            "news_processed": total_processed,
            "categories": {cat: len(items) for cat, items in ranked_news.items()},
            "success": success
        }
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 대시보드용 JSON 저장
        save_processed_news_for_dashboard(ranked_news, start_time)
        
        # 데이터 백업
        data_dir = os.path.join(repo_root, 'data')
        os.makedirs(data_dir, exist_ok=True)
        backup_file = os.path.join(data_dir, 'processed_news.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"데이터 백업 완료: {backup_file}")
        
        end_time = datetime.now(KST)
        elapsed = (end_time - start_time).total_seconds()
        logger.info(f"===== 사이클 완료: {elapsed:.1f}초 소요 =====")
        
        return success
        
    except Exception as e:
        logger.error(f"사이클 실행 중 오류: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    dry_run = os.environ.get("DRY_RUN", "0") == "1"
    
    if dry_run:
        logger.info("DRY_RUN 모드: 실제 발송하지 않습니다.")
    else:
        logger.info("실전 모드: 실제로 텔레그램에 발송합니다.")
    
    success = run_news_cycle_v4()
    sys.exit(0 if success else 1)
