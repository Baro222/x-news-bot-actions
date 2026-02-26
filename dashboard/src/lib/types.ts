/**
 * Command Center - Data Types
 * 군사 정보 스타일 뉴스 대시보드 데이터 구조
 */

export type Category = '지정학' | '경제' | '암호화폐' | '트럼프' | '규제';

export type Priority = 'critical' | 'high' | 'medium' | 'low';

export type MarketImpact = 'very_bullish' | 'bullish' | 'neutral' | 'bearish' | 'very_bearish';

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  fullAnalysis: string;
  category: Category;
  priority: Priority;
  marketImpact: MarketImpact;
  source: string;
  sourceHandle: string;
  sourceUrl: string;
  timestamp: string;
  relatedAccounts: string[];
  tags: string[];
  impactScore: number; // 1-100
}

export interface AIAnalysis {
  id: string;
  title: string;
  content: string;
  timestamp: string;
  category: Category;
  sentiment: MarketImpact;
  keyInsights: string[];
  riskLevel: Priority;
}

export interface SystemStatus {
  lastUpdate: string;
  nextUpdate: string;
  totalAccounts: number;
  activeAccounts: number;
  tweetsCollected: number;
  aiAnalysisCount: number;
  systemHealth: 'operational' | 'degraded' | 'down';
  uptime: string;
}

export interface AccountInfo {
  handle: string;
  name: string;
  category: Category;
  isPriority: boolean;
  lastTweet: string;
  tweetCount: number;
}

export const CATEGORY_CONFIG: Record<Category, { color: string; badgeClass: string; icon: string }> = {
  '지정학': { color: '#ef4444', badgeClass: 'badge-geopolitics', icon: '🌍' },
  '경제': { color: '#3b82f6', badgeClass: 'badge-economy', icon: '📊' },
  '암호화폐': { color: '#00ff88', badgeClass: 'badge-crypto', icon: '₿' },
  '트럼프': { color: '#f59e0b', badgeClass: 'badge-trump', icon: '🏛️' },
  '규제': { color: '#a855f7', badgeClass: 'badge-regulation', icon: '⚖️' },
};

export const PRIORITY_CONFIG: Record<Priority, { label: string; color: string }> = {
  critical: { label: '긴급', color: '#ef4444' },
  high: { label: '높음', color: '#f59e0b' },
  medium: { label: '보통', color: '#3b82f6' },
  low: { label: '낮음', color: '#6b7280' },
};

export const MARKET_IMPACT_CONFIG: Record<MarketImpact, { label: string; color: string; icon: string }> = {
  very_bullish: { label: '매우 긍정', color: '#00ff88', icon: '▲▲' },
  bullish: { label: '긍정', color: '#4ade80', icon: '▲' },
  neutral: { label: '중립', color: '#94a3b8', icon: '━' },
  bearish: { label: '부정', color: '#f97316', icon: '▼' },
  very_bearish: { label: '매우 부정', color: '#ef4444', icon: '▼▼' },
};
