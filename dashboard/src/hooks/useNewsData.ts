/**
 * useNewsData - processed_news.json을 fetch하여 뉴스 데이터를 로드합니다.
 * JSON이 없거나 로드 실패 시 mockData로 폴백합니다.
 */

import { useState, useEffect } from 'react';
import type { NewsItem, SystemStatus } from '@/lib/types';
import { mockNews, mockSystemStatus } from '@/lib/mockData';

interface ProcessedNewsData {
  timestamp: string;
  news: NewsItem[];
  systemStatus: SystemStatus;
}

interface UseNewsDataResult {
  news: NewsItem[];
  systemStatus: SystemStatus;
  isLoading: boolean;
  isLiveData: boolean;
  lastFetched: string | null;
}

export function useNewsData(): UseNewsDataResult {
  const [news, setNews] = useState<NewsItem[]>(mockNews);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>(mockSystemStatus);
  const [isLoading, setIsLoading] = useState(true);
  const [isLiveData, setIsLiveData] = useState(false);
  const [lastFetched, setLastFetched] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        // 캐시 방지를 위해 타임스탬프 쿼리 추가
        const res = await fetch(`/processed_news.json?t=${Date.now()}`, {
          cache: 'no-store',
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data: ProcessedNewsData = await res.json();

        if (data.news && data.news.length > 0) {
          setNews(data.news);
          setSystemStatus(data.systemStatus || mockSystemStatus);
          setIsLiveData(true);
          setLastFetched(data.timestamp);
        } else {
          // JSON은 있지만 뉴스가 없는 경우 mockData 유지
          setIsLiveData(false);
        }
      } catch {
        // 파일 없음 또는 네트워크 오류 → mockData 유지
        setIsLiveData(false);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();

    // 5분마다 자동 갱신
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return { news, systemStatus, isLoading, isLiveData, lastFetched };
}
