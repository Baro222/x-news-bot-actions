#!/usr/bin/env python3
"""
X(Twitter) 트윗 스크래핑 및 텔레그램 자동 발송
- 로그인 없이 공개 프로필에서 트윗 추출
- Selenium + BeautifulSoup 사용
- 텔레그램 Bot API로 자동 발송
"""

import time
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from collections import defaultdict

# 설정
ACCOUNTS = {
    "visegrad24": "지정학",
    "TrumpTruthOnX": "트럼프",
    "zerohedge": "경제",
    "Cointelegraph": "암호화폐",
    "nytimes": "뉴스",
}

TELEGRAM_BOT_TOKEN = "8605573358:AAGb_oalPLqiimVpq-hX4IqTVKGCp80nddc"
TELEGRAM_CHANNEL_ID = "-1003683270211"

def setup_driver():
    """Selenium 드라이버 설정"""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_tweets(driver, account):
    """X 프로필에서 트윗 스크래핑"""
    url = f"https://x.com/{account}"
    tweets = []
    
    try:
        print(f"🔍 {account} 프로필 접속 중...")
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 트윗 요소 찾기
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
        
        # 페이지 소스 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 트윗 추출
        articles = soup.find_all('article', limit=5)  # 최대 5개
        
        for article in articles:
            try:
                # 트윗 텍스트 추출
                text_elem = article.find('div', {'data-testid': 'tweetText'})
                if not text_elem:
                    # 다른 방식으로 텍스트 찾기
                    text_elem = article.find('div', {'lang': True})
                
                if text_elem:
                    tweet_text = text_elem.get_text(strip=True)
                    if tweet_text and len(tweet_text) > 10:
                        tweets.append({
                            "account": account,
                            "text": tweet_text[:300],  # 300자 제한
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"⚠️ 트윗 파싱 오류: {e}")
                continue
        
        print(f"✅ {account}에서 {len(tweets)} 개 트윗 추출")
        return tweets
        
    except Exception as e:
        print(f"❌ {account} 스크래핑 실패: {e}")
        return []

def send_to_telegram(category, headline):
    """텔레그램 채널에 메시지 발송"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        message = f"""📰 **{category}**

{headline[:200]}

---"""
        
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ 메시지 발송 성공")
            return True
        else:
            print(f"❌ 메시지 발송 실패: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ 텔레그램 발송 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    print(f"\n🚀 X 뉴스 스크래핑 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    driver = None
    try:
        driver = setup_driver()
        
        all_tweets = defaultdict(list)
        
        # 각 계정에서 트윗 수집
        for account, category in ACCOUNTS.items():
            tweets = scrape_tweets(driver, account)
            if tweets:
                all_tweets[category].extend(tweets)
            time.sleep(2)  # 요청 간격
        
        # 텔레그램 발송
        print(f"\n📤 텔레그램 발송 중...")
        count = 0
        for category, tweets in all_tweets.items():
            for tweet in tweets[:2]:  # 카테고리당 2개
                if send_to_telegram(category, tweet["text"]):
                    count += 1
                time.sleep(1)
        
        print(f"\n✅ 완료! {count}개 뉴스 발송")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
