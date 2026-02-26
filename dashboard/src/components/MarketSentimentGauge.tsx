/**
 * Command Center - Market Sentiment Gauge
 * 전체 시장 센티먼트를 시각적으로 표시하는 게이지
 */

import { mockNews } from '@/lib/mockData';
import { MARKET_IMPACT_CONFIG } from '@/lib/types';

export default function MarketSentimentGauge() {
  // Calculate overall sentiment
  const sentimentScores = mockNews.map(n => {
    switch (n.marketImpact) {
      case 'very_bullish': return 2;
      case 'bullish': return 1;
      case 'neutral': return 0;
      case 'bearish': return -1;
      case 'very_bearish': return -2;
    }
  });

  const avgScore = sentimentScores.reduce<number>((a, b) => a + b, 0) / sentimentScores.length;
  const sentimentPercent = ((avgScore + 2) / 4) * 100; // 0-100 scale

  // Count by sentiment
  const sentimentCounts = mockNews.reduce((acc, n) => {
    acc[n.marketImpact] = (acc[n.marketImpact] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const overallLabel = avgScore > 0.5 ? '긍정' : avgScore < -0.5 ? '부정' : '중립';
  const overallColor = avgScore > 0.5 ? '#00ff88' : avgScore < -0.5 ? '#ef4444' : '#94a3b8';

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden" style={{ background: 'oklch(0.14 0.02 260)' }}>
      <div className="px-4 py-2.5 border-b border-border/50 flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full pulse-indicator" style={{ background: overallColor }} />
        <span className="font-heading text-xs font-semibold tracking-wider text-foreground">시장 센티먼트</span>
      </div>

      <div className="p-4">
        {/* Gauge Bar */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="font-mono text-[10px] text-destructive">부정</span>
            <span className="font-mono text-xs font-bold" style={{ color: overallColor }}>{overallLabel}</span>
            <span className="font-mono text-[10px] text-primary">긍정</span>
          </div>
          <div className="relative h-2 rounded-full overflow-hidden" style={{ background: 'oklch(0.2 0.02 260)' }}>
            <div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'linear-gradient(90deg, #ef4444, #f59e0b, #94a3b8, #4ade80, #00ff88)',
                opacity: 0.3,
              }}
            />
            <div
              className="absolute top-0 h-full w-1 rounded-full transition-all duration-500"
              style={{
                left: `${sentimentPercent}%`,
                background: overallColor,
                boxShadow: `0 0 8px ${overallColor}`,
              }}
            />
          </div>
        </div>

        {/* Sentiment Distribution */}
        <div className="grid grid-cols-5 gap-1">
          {(Object.entries(MARKET_IMPACT_CONFIG) as [string, { label: string; color: string; icon: string }][]).map(([key, config]) => (
            <div key={key} className="text-center">
              <div className="font-mono text-xs font-bold" style={{ color: config.color }}>
                {sentimentCounts[key] || 0}
              </div>
              <div className="font-mono text-[9px] text-muted-foreground">{config.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
