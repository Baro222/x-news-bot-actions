/**
 * Command Center - Main Dashboard
 * Design: Military Intelligence Command Center
 * Layout: 3-column asymmetric grid (sidebar | news feed | analysis panel)
 * Theme: Dark navy/charcoal, cyber green/amber/red accents
 * Typography: Space Grotesk (headings) + IBM Plex Sans (body) + JetBrains Mono (data)
 */

import { useState, useMemo } from 'react';
import Header from '@/components/Header';
import NewsTicker from '@/components/NewsTicker';
import CategorySidebar from '@/components/CategorySidebar';
import NewsCard from '@/components/NewsCard';
import NewsDetailPanel from '@/components/NewsDetailPanel';
import AIAnalysisPanel from '@/components/AIAnalysisPanel';
import MarketSentimentGauge from '@/components/MarketSentimentGauge';
import CategoryDistribution from '@/components/CategoryDistribution';
import ActivityLog from '@/components/ActivityLog';
import SystemStatusBar from '@/components/SystemStatusBar';
import { mockNews } from '@/lib/mockData';
import type { Category, NewsItem } from '@/lib/types';

const HERO_BG_URL = 'https://private-us-east-1.manuscdn.com/sessionFile/L5zNvu3Ru4GOSPEkyfsTPD/sandbox/Z2UeFUYzYkK2Tbq1R0RgR5-img-1_1772135633000_na1fn_aGVyby1iZw.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTDV6TnZ1M1J1NEdPU1BFa3lmc1RQRC9zYW5kYm94L1oyVWVGVVl6WWtLMlRicTFSMFJnUjUtaW1nLTFfMTc3MjEzNTYzMzAwMF9uYTFmbl9hR1Z5YnkxaVp3LnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSx3XzE5MjAsaF8xOTIwL2Zvcm1hdCx3ZWJwL3F1YWxpdHkscV84MCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=FnzS~iQKTy47bZao3Sn~DFet4Cww260lKxJJUA-e9eGNWLhjLgMkVCbDLm6G-qhUDwbo0kJZCN9xrUPCwK~SEUxPjMLTZYQq18tUN~u98QqVontQ2OBuGQhJz7sR8jtOArtHNu~wG~hwsktuhBrpFTSbJUOJEawVh19nfdbEpT2Povdf2OdeUdp5MpyVGdpV6pUwVNXVyp-VMbDyTsPahSpdNrmLNM7ugTvCTyDqHz9hwBhrfphsxfnrIRn88K8icLFQtnyoi2sh6fny~HopwNd~qym0y14rnvMOpx88U~4HTkjvsKXWHUmRh8uWQgKHg8AD5fIovnJ6xc8Va6TRjg__';

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState<Category | 'all'>('all');
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [activeTab, setActiveTab] = useState<'feed' | 'analysis'>('feed');

  const filteredNews = useMemo(() => {
    if (selectedCategory === 'all') return mockNews;
    return mockNews.filter((item) => item.category === selectedCategory);
  }, [selectedCategory]);

  const criticalCount = mockNews.filter(n => n.priority === 'critical').length;

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Scanline overlay */}
      <div className="fixed inset-0 scanline-overlay z-[1] pointer-events-none" />

      {/* Header */}
      <div className="relative z-10">
        <Header />
      </div>

      {/* News Ticker */}
      <div className="relative z-10">
        <NewsTicker />
      </div>

      {/* Hero Banner */}
      <div className="relative z-10 border-b border-border/30">
        <div className="relative overflow-hidden" style={{ height: '130px' }}>
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${HERO_BG_URL})`, opacity: 0.2 }}
          />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, oklch(0.12 0.02 260 / 0.9), oklch(0.1 0.03 200 / 0.75))' }} />
          <div className="relative container h-full flex items-center">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <div className="px-2 py-0.5 rounded border border-primary/30 bg-primary/10">
                  <span className="font-mono text-[10px] text-primary font-semibold tracking-wider">LIVE</span>
                </div>
                {criticalCount > 0 && (
                  <div className="px-2 py-0.5 rounded border border-destructive/30 bg-destructive/10 animate-pulse">
                    <span className="font-mono text-[10px] text-destructive font-semibold tracking-wider">
                      긴급 {criticalCount}건
                    </span>
                  </div>
                )}
              </div>
              <h2 className="font-heading text-lg md:text-xl font-bold text-foreground tracking-tight mb-0.5">
                실시간 뉴스 인텔리전스
              </h2>
              <p className="font-sans text-[11px] text-muted-foreground max-w-lg leading-relaxed">
                60개 X(트위터) 계정에서 4시간 주기로 수집된 뉴스를 Gemini AI가 분석합니다.
              </p>
            </div>

            {/* Quick Stats */}
            <div className="hidden lg:flex items-center gap-3">
              <QuickStat label="총 뉴스" value={mockNews.length.toString()} suffix="건" />
              <QuickStat label="긴급" value={criticalCount.toString()} suffix="건" isAlert={criticalCount > 0} />
              <QuickStat label="모니터링" value="60" suffix="계정" />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Tab Switcher */}
      <div className="lg:hidden relative z-10 border-b border-border/30 px-4 py-2 flex gap-2" style={{ background: 'oklch(0.12 0.02 260)' }}>
        <button
          onClick={() => setActiveTab('feed')}
          className={`flex-1 py-2 rounded text-xs font-mono font-medium transition-colors ${
            activeTab === 'feed' ? 'bg-primary/10 text-primary border border-primary/30' : 'text-muted-foreground hover:text-foreground border border-transparent'
          }`}
        >
          뉴스 피드
        </button>
        <button
          onClick={() => setActiveTab('analysis')}
          className={`flex-1 py-2 rounded text-xs font-mono font-medium transition-colors ${
            activeTab === 'analysis' ? 'bg-primary/10 text-primary border border-primary/30' : 'text-muted-foreground hover:text-foreground border border-transparent'
          }`}
        >
          AI 분석
        </button>
        <button
          onClick={() => setShowMobileMenu(!showMobileMenu)}
          className="px-3 py-2 rounded text-xs font-mono text-muted-foreground hover:text-foreground border border-border/30"
        >
          필터
        </button>
      </div>

      {/* Mobile Category Filter */}
      {showMobileMenu && (
        <div className="lg:hidden relative z-10 border-b border-border/30 px-4 py-3" style={{ background: 'oklch(0.13 0.02 260)' }}>
          <CategorySidebar selectedCategory={selectedCategory} onSelectCategory={(cat) => { setSelectedCategory(cat); setShowMobileMenu(false); }} />
        </div>
      )}

      {/* Main Content - 3 Column Asymmetric Grid */}
      <main className="relative z-10 container py-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Left: Category Sidebar + Activity Log (hidden on mobile) */}
          <div className="hidden lg:block">
            <div className="sticky top-16 space-y-4">
              <CategorySidebar selectedCategory={selectedCategory} onSelectCategory={setSelectedCategory} />
              <ActivityLog />
            </div>
          </div>

          {/* Center: News Feed */}
          <div className={`flex-1 min-w-0 ${activeTab !== 'feed' ? 'hidden lg:block' : ''}`}>
            {/* Feed Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary pulse-indicator" />
                <span className="font-heading text-xs font-semibold tracking-wider text-foreground">
                  뉴스 피드
                </span>
                <span className="font-mono text-[10px] text-muted-foreground">
                  ({filteredNews.length}건)
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-muted-foreground">정렬:</span>
                <span className="font-mono text-[10px] text-primary">최신순</span>
              </div>
            </div>

            {/* News Cards */}
            <div className="space-y-3">
              {filteredNews.map((news) => (
                <NewsCard
                  key={news.id}
                  news={news}
                  onSelect={setSelectedNews}
                />
              ))}
            </div>

            {filteredNews.length === 0 && (
              <div className="border border-border/30 rounded-lg p-8 text-center" style={{ background: 'oklch(0.14 0.02 260)' }}>
                <span className="text-2xl opacity-30 block mb-2">📭</span>
                <p className="font-mono text-xs text-muted-foreground">선택한 카테고리에 해당하는 뉴스가 없습니다</p>
              </div>
            )}

            {/* System Status - Below News Feed */}
            <div className="mt-4">
              <SystemStatusBar />
            </div>
          </div>

          {/* Right: Detail Panel / AI Analysis */}
          <div className={`w-full lg:w-80 xl:w-96 shrink-0 ${activeTab !== 'analysis' ? 'hidden lg:block' : ''}`}>
            <div className="sticky top-16 space-y-4 max-h-[calc(100vh-5rem)] overflow-y-auto pr-1" style={{ scrollbarWidth: 'thin', scrollbarColor: 'oklch(0.3 0.02 260) transparent' }}>
              {/* News Detail Panel */}
              {selectedNews && (
                <NewsDetailPanel news={selectedNews} onClose={() => setSelectedNews(null)} />
              )}

              {/* Market Sentiment Gauge */}
              <MarketSentimentGauge />

              {/* Category Distribution */}
              <CategoryDistribution />

              {/* AI Analysis Panel */}
              <AIAnalysisPanel />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/30 mt-8">
        <div className="container py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="w-1 h-1 rounded-full bg-primary/50" />
            <span className="font-mono text-[10px] text-muted-foreground">
              X NEWS AI COMMAND CENTER v1.0 | Powered by Gemini AI
            </span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://t.me/baroBTC"
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-[10px] text-muted-foreground hover:text-primary transition-colors"
            >
              Telegram @baroBTC
            </a>
            <a
              href="https://github.com/Baro222/x-news-bot-actions"
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-[10px] text-muted-foreground hover:text-primary transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function QuickStat({ label, value, suffix, isAlert }: { label: string; value: string; suffix: string; isAlert?: boolean }) {
  return (
    <div className="text-center px-3 py-1.5 rounded-lg border border-border/30" style={{ background: 'oklch(0.12 0.02 260 / 0.8)' }}>
      <div className="font-mono text-[9px] text-muted-foreground tracking-wider mb-0.5">{label}</div>
      <div className="flex items-baseline justify-center gap-0.5">
        <span className={`font-mono text-base font-bold ${isAlert ? 'text-destructive' : 'text-primary'}`}>{value}</span>
        <span className="font-mono text-[9px] text-muted-foreground">{suffix}</span>
      </div>
    </div>
  );
}
