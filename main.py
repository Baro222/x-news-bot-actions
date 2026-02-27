"""
X 뉴스 자동 수집 및 텔레그램 발송 메인 스크립트
실행: python3.11 main.py
"""

import logging
import sys
import os
import json
from datetime import datetime, timezone, timedelta

# 로깅 설정
LOG_DIR = "/home/ubuntu/x_news_bot/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 루트 로거에 핸들러가 없을 때만 추가 (중복 방지)
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{LOG_DIR}/news_bot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))


def save_processed_news_for_dashboard(ranked_news: dict, timestamp) -> None:
    """
    AI 처리된 뉴스를 대시보드가 읽을 수 있는 JSON 형식으로 저장합니다.
    저장 위치: dashboard/public/processed_news.json
    """
    import uuid
    
    # 중요도 -> priority 매핑
    def get_priority(importance: int) -> str:
        if importance >= 9:
            return 'critical'
        elif importance >= 7:
            return 'high'
        elif importance >= 4:
            return 'medium'
        else:
            return 'low'
    
    # 중요도 -> marketImpact 매핑 (주제별 휴리스틱)
    def get_market_impact(category: str, importance: int) -> str:
        if category == '암호화폐':
            if importance >= 8:
                return 'very_bullish'
            elif importance >= 6:
                return 'bullish'
            else:
                return 'neutral'
        elif category in ['지정학', '트럼프']:
            if importance >= 8:
                return 'very_bearish'
            elif importance >= 6:
                return 'bearish'
            else:
                return 'neutral'
        elif category == '경제':
            if importance >= 8:
                return 'bearish'
            elif importance >= 6:
                return 'neutral'
            else:
                return 'bullish'
        return 'neutral'
    
    news_items = []
    for category, items in ranked_news.items():
        for item in items:
            # 고유 ID 생성 (트윗 URL 기반)
            url = item.get('_url', '')
            item_id = url.split('/')[-1] if url else str(uuid.uuid4())[:8]
            
            importance = item.get('_importance', 5)
            
            news_item = {
                'id': item_id,
                'title': item.get('_headline', item.get('text', '')[:50]),
                'summary': item.get('_summary', item.get('text', '')[:200]),
                'fullAnalysis': item.get('_analysis', ''),
                'category': category,
                'priority': get_priority(importance),
                'marketImpact': get_market_impact(category, importance),
                'source': item.get('_account', 'unknown'),
                'sourceHandle': f"@{item.get('_account', 'unknown')}",
                'sourceUrl': item.get('_url', ''),
                'timestamp': item.get('created_at', timestamp.isoformat()),
                'relatedAccounts': [],
                'tags': [],
                'impactScore': min(importance * 10, 100),
            }
            news_items.append(news_item)
    
    # 중요도 내림차순 정렬
    news_items.sort(key=lambda x: x['impactScore'], reverse=True)
    
    output = {
        'timestamp': timestamp.isoformat(),
        'news': news_items,
        'systemStatus': {
            'lastUpdate': timestamp.isoformat(),
            'nextUpdate': (timestamp + timedelta(hours=4)).isoformat(),
            'totalAccounts': 60,
            'activeAccounts': 60,
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


def run_news_cycle():
    """뉴스 수집 -> AI 처리 -> 텔레그램 발송 전체 사이클 실행"""
    
    start_time = datetime.now(KST)
    logger.info(f"===== 뉴스 수집 사이클 시작: {start_time.strftime('%Y-%m-%d %H:%M KST')} =====")
    
    try:
        # 1단계: 트윗 수집
        logger.info("1단계: X 트윗 수집 시작...")
        from twitter_fetcher import fetch_all_tweets
        tweets = fetch_all_tweets()
        
        if not tweets:
            logger.warning("수집된 트윗이 없습니다. 사이클 종료.")
            from telegram_sender import send_telegram_message
            send_telegram_message(
                f"⚠️ {start_time.strftime('%Y.%m.%d %H:%M KST')} 브리핑\n"
                "최근 4시간 내 수집된 트윗이 없습니다."
            )
            return False
        
        logger.info(f"수집 완료: {len(tweets)}개 트윗")
        
        # 2단계: AI 분류 및 요약
        logger.info("2단계: AI 분류 및 요약 처리 시작...")
        from ai_processor import process_tweets
        ranked_news = process_tweets(tweets)
        
        total_processed = sum(len(items) for items in ranked_news.values())
        logger.info(f"AI 처리 완료: 총 {total_processed}개 뉴스 분류")
        
        # 3단계: 텔레그램 발송
        logger.info("3단계: 텔레그램 발송 시작...")
        from telegram_sender import send_news_report
        success = send_news_report(ranked_news)
        
        if success:
            logger.info("텔레그램 발송 완료!")
        else:
            logger.error("텔레그램 발송 실패!")
        
        # 결과 저장 (디버깅용)
        result_file = f"{LOG_DIR}/last_result.json"
        save_data = {
            "timestamp": start_time.isoformat(),
            "tweets_collected": len(tweets),
            "news_processed": total_processed,
            "categories": {cat: len(items) for cat, items in ranked_news.items()},
            "success": success
        }
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        # 홈페이지 연동용: processed_news.json 생성 (repo/data/processed_news.json)
        try:
            repo_root = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(repo_root, 'data')
            os.makedirs(data_dir, exist_ok=True)
            processed_path = os.path.join(data_dir, 'processed_news.json')

            # Flatten ranked_news into a list
            out_list = []
            for category, items in ranked_news.items():
                for it in items:
                    out_item = {
                        'title': it.get('_headline') or it.get('headline') or '' ,
                        'summary': it.get('_summary') or it.get('summary') or '',
                        'source': it.get('_account') or it.get('source') or '',
                        'url': it.get('_url') or it.get('url') or '',
                        'category': category,
                        'timestamp': it.get('_timestamp') or it.get('timestamp') or start_time.isoformat()
                    }
                    out_list.append(out_item)

            # atomic write
            tmp_path = processed_path + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(out_list, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, processed_path)
            logger.info(f"processed_news.json 생성: {processed_path} ({len(out_list)} 항목)")
        except Exception as e:
            logger.error(f"processed_news.json 생성 실패: {e}", exc_info=True)
        
        # 대시보드용 processed_news.json 저장
        save_processed_news_for_dashboard(ranked_news, start_time)
        
        end_time = datetime.now(KST)
        elapsed = (end_time - start_time).total_seconds()
        logger.info(f"===== 사이클 완료: {elapsed:.1f}초 소요 =====")
        
        return success
        
    except Exception as e:
        logger.error(f"사이클 실행 중 오류 발생: {e}", exc_info=True)
        
        # 오류 알림 발송
        try:
            from telegram_sender import send_telegram_message
            send_telegram_message(
                f"❌ 뉴스봇 오류 발생\n"
                f"시간: {start_time.strftime('%Y.%m.%d %H:%M KST')}\n"
                f"오류: {str(e)[:200]}"
            )
        except Exception:
            pass
        
        return False


if __name__ == "__main__":
    logger.info("X 뉴스 자동 수집 봇 시작")
    success = run_news_cycle()
    sys.exit(0 if success else 1)
