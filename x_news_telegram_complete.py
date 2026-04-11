#!/usr/bin/env python3
"""
X 뉴스 완전 자동화 시스템
- X에서 실시간 트윗 수집
- 카테고리별 정리
- 브레이킹 뉴스 이미지 생성
- 텔레그램에 이미지 + 텍스트 발송
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
from PIL import Image, ImageDraw, ImageFont
import io
import os

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

CATEGORY_COLORS = {
    "지정학": "#FF6B6B",
    "트럼프": "#4ECDC4",
    "경제": "#45B7D1",
    "암호화폐": "#FFA502",
    "뉴스": "#95E1D3",
}

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
        time.sleep(3)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', limit=5)
        
        for article in articles:
            try:
                text_elem = article.find('div', {'data-testid': 'tweetText'})
                if not text_elem:
                    text_elem = article.find('div', {'lang': True})
                
                if text_elem:
                    tweet_text = text_elem.get_text(strip=True)
                    if tweet_text and len(tweet_text) > 10:
                        tweets.append(tweet_text[:300])
            except Exception as e:
                continue
        
        print(f"✅ {account}에서 {len(tweets)} 개 트윗 추출")
        return tweets
        
    except Exception as e:
        print(f"❌ {account} 스크래핑 실패: {e}")
        return []

def create_breaking_news_image(category, headline):
    """브레이킹 뉴스 이미지 생성"""
    try:
        # 이미지 생성
        width, height = 1200, 630
        color = CATEGORY_COLORS.get(category, "#FF6B6B")
        
        # RGB 색상 변환
        color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        img = Image.new('RGB', (width, height), color_rgb)
        draw = ImageDraw.Draw(img)
        
        # 텍스트 추가
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_category = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font_title = ImageFont.load_default()
            font_category = ImageFont.load_default()
        
        # 카테고리 텍스트
        draw.text((50, 50), f"🔴 BREAKING NEWS - {category}", fill=(255, 255, 255), font=font_category)
        
        # 헤드라인 텍스트 (줄바꿈 처리)
        headline_short = headline[:80] + "..." if len(headline) > 80 else headline
        draw.text((50, 200), headline_short, fill=(255, 255, 255), font=font_title)
        
        # 시간 텍스트
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((50, 550), timestamp, fill=(200, 200, 200), font=font_category)
        
        # 이미지를 바이트로 변환
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
        
    except Exception as e:
        print(f"⚠️ 이미지 생성 오류: {e}")
        return None

def send_to_telegram_with_image(category, headline, content, image_data):
    """이미지와 함께 텔레그램에 메시지 발송"""
    try:
        if image_data:
            # 이미지 발송
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            
            files = {
                'photo': ('breaking_news.png', image_data, 'image/png')
            }
            
            data = {
                'chat_id': TELEGRAM_CHANNEL_ID,
                'caption': f"**{category}**\n\n{headline}\n\n{content[:200]}",
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()
            
            if result.get("ok"):
                print(f"✅ 이미지 메시지 발송 성공")
                return True
            else:
                print(f"❌ 이미지 메시지 발송 실패: {result.get('description')}")
        
        # 이미지 없이 텍스트만 발송
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        message = f"""📰 **{category}**

**{headline}**

{content[:200]}

---"""
        
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ 텍스트 메시지 발송 성공")
            return True
        else:
            print(f"❌ 메시지 발송 실패")
            return False
            
    except Exception as e:
        print(f"❌ 텔레그램 발송 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    print(f"\n🚀 X 뉴스 완전 자동화 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    driver = None
    try:
        driver = setup_driver()
        
        all_tweets = defaultdict(list)
        
        # 각 계정에서 트윗 수집
        for account, category in ACCOUNTS.items():
            tweets = scrape_tweets(driver, account)
            if tweets:
                all_tweets[category].extend(tweets)
            time.sleep(2)
        
        # 텔레그램 발송
        print(f"\n📤 텔레그램 발송 중...")
        count = 0
        
        for category in sorted(all_tweets.keys()):
            tweets = all_tweets[category]
            
            # 카테고리별 최대 3개 뉴스
            for i, tweet in enumerate(tweets[:3]):
                headline = tweet[:80]
                content = tweet
                
                # 주요 뉴스는 이미지 포함
                if i == 0:  # 첫 번째 뉴스만 이미지 포함
                    image_data = create_breaking_news_image(category, headline)
                    if send_to_telegram_with_image(category, headline, content, image_data):
                        count += 1
                else:
                    # 나머지는 텍스트만
                    if send_to_telegram_with_image(category, headline, content, None):
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
