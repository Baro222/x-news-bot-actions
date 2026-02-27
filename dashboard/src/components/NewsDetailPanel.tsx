/**
 * Command Center - News Detail Panel
 * 뉴스 선택 시 우측에 표시되는 상세 분석 패널
 */

import { CATEGORY_CONFIG, PRIORITY_CONFIG, MARKET_IMPACT_CONFIG, type NewsItem } from '@/lib/types';
import { formatDate, timeAgo } from '@/lib/utils';

interface NewsDetailPanelProps {
  news: NewsItem | null;
  onClose: () => void;
}

export default function NewsDetailPanel({ news, onClose }: NewsDetailPanelProps) {
  if (!news) {
    return (
      <div className="border border-border/50 rounded-lg overflow-hidden h-full flex flex-col" style={{ background: 'oklch(0.14 0.02 260)' }}>
        <div className="px-4 py-3 border-b border-border/50 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-chart-2 pulse-indicator" />
          <span className="font-heading text-xs font-semibold tracking-wider text-foreground">상세 분석</span>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center">
            <div className="w-16 h-16 rounded-lg border border-border/30 flex items-center justify-center mx-auto mb-3" style={{ background: 'oklch(0.18 0.02 260)' }}>
              <span className="text-2xl opacity-30">📋</span>
            </div>
            <p className="font-mono text-xs text-muted-foreground">뉴스를 선택하면<br />상세 분석이 표시됩니다</p>
          </div>
        </div>
      </div>
    );
  }

  const categoryConfig = CATEGORY_CONFIG[news.category];
  const priorityConfig = PRIORITY_CONFIG[news.priority];
  const impactConfig = MARKET_IMPACT_CONFIG[news.marketImpact];

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden h-full flex flex-col" style={{ background: 'oklch(0.14 0.02 260)' }}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-border/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full pulse-indicator" style={{ background: priorityConfig.color }} />
          <span className="font-heading text-xs font-semibold tracking-wider text-foreground">상세 분석</span>
        </div>
        <button
          onClick={onClose}
          className="w-6 h-6 rounded flex items-center justify-center hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M2 2l8 8M10 2l-8 8" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Category & Priority */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`${categoryConfig.badgeClass} px-2 py-0.5 rounded text-[10px] font-mono font-medium`}>
            {categoryConfig.icon} {news.category}
          </span>
          <span
            className="px-2 py-0.5 rounded text-[10px] font-mono font-medium border"
            style={{
              background: `${priorityConfig.color}15`,
              color: priorityConfig.color,
              borderColor: `${priorityConfig.color}40`,
            }}
          >
            우선순위: {priorityConfig.label}
          </span>
        </div>

        {/* Title */}
        <h2 className="font-heading text-base font-bold text-foreground leading-snug">
          {news.title}
        </h2>

        {/* Meta info */}
        <div className="flex items-center gap-4 text-[10px] font-mono text-muted-foreground">
          <span>{news.sourceHandle}</span>
          <span>{timeAgo(news.timestamp)}</span>
          <span>{formatDate(news.timestamp)}</span>
        </div>

        {/* Market Impact Panel */}
        <div className="rounded-lg border border-border/30 p-3" style={{ background: 'oklch(0.12 0.02 260)' }}>
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2">시장 영향 분석</div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg font-bold" style={{ color: impactConfig.color }}>
                {impactConfig.icon}
              </span>
              <span className="font-mono text-sm font-semibold" style={{ color: impactConfig.color }}>
                {impactConfig.label}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] text-muted-foreground">영향도</span>
              <div className="w-16 h-2 rounded-full overflow-hidden" style={{ background: 'oklch(0.2 0.02 260)' }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${news.impactScore}%`,
                    background: news.impactScore >= 90 ? '#ef4444' : news.impactScore >= 75 ? '#f59e0b' : '#3b82f6',
                  }}
                />
              </div>
              <span className="font-mono text-xs font-bold" style={{
                color: news.impactScore >= 90 ? '#ef4444' : news.impactScore >= 75 ? '#f59e0b' : '#3b82f6',
              }}>
                {news.impactScore}
              </span>
            </div>
          </div>
        </div>

        {/* Full Analysis */}
        <div>
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2 flex items-center gap-2">
            <div className="w-1 h-1 rounded-full bg-primary" />
            AI 분석 보고서
          </div>
          <div className="font-sans text-xs text-foreground/90 leading-relaxed whitespace-pre-line">
            {news.fullAnalysis}
          </div>
        </div>

        {/* Tags */}
        <div>
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2 flex items-center gap-2">
            <div className="w-1 h-1 rounded-full bg-chart-2" />
            관련 태그
          </div>
          <div className="flex flex-wrap gap-1.5">
            {news.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 rounded text-[10px] font-mono text-muted-foreground border border-border/30"
                style={{ background: 'oklch(0.18 0.02 260)' }}
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* Related Accounts */}
        <div>
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2 flex items-center gap-2">
            <div className="w-1 h-1 rounded-full bg-amber-alert" />
            관련 계정
          </div>
          <div className="flex flex-wrap gap-1.5">
            {news.relatedAccounts.map((account) => (
              <span
                key={account}
                className="px-2 py-1 rounded text-[10px] font-mono text-primary/80 border border-primary/20"
                style={{ background: 'oklch(0.85 0.25 155 / 0.05)' }}
              >
                {account}
              </span>
            ))}
          </div>
        </div>

        {/* Source Link */}
        <a
          href={news.sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-3 py-2 rounded border border-primary/20 text-primary text-xs font-mono hover:bg-primary/10 transition-colors"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3" />
          </svg>
          원문 보기 ({news.source})
        </a>
      </div>
    </div>
  );
}
