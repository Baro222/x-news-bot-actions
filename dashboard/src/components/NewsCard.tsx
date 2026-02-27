/**
 * Command Center - News Card
 * 군사 정보 스타일 뉴스 카드
 * 우선순위 표시, 카테고리 뱃지, 시장 영향도 인디케이터
 */

import { CATEGORY_CONFIG, PRIORITY_CONFIG, MARKET_IMPACT_CONFIG, type NewsItem } from '@/lib/types';
import { timeAgo } from '@/lib/utils';

interface NewsCardProps {
  news: NewsItem;
  onSelect: (news: NewsItem) => void;
}

export default function NewsCard({ news, onSelect }: NewsCardProps) {
  const categoryConfig = CATEGORY_CONFIG[news.category];
  const priorityConfig = PRIORITY_CONFIG[news.priority];
  const impactConfig = MARKET_IMPACT_CONFIG[news.marketImpact];

  return (
    <article
      className="news-card rounded-lg overflow-hidden cursor-pointer group"
      style={{ background: 'oklch(0.14 0.02 260)' }}
      onClick={() => onSelect(news)}
    >
      {/* Priority bar */}
      <div
        className="h-0.5 w-full"
        style={{ background: priorityConfig.color }}
      />

      <div className="p-4">
        {/* Top row: Category + Priority + Time */}
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center gap-2">
            <span className={`${categoryConfig.badgeClass} px-2 py-0.5 rounded text-[10px] font-mono font-medium`}>
              {categoryConfig.icon} {news.category}
            </span>
            {news.priority === 'critical' && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-destructive/20 text-destructive border border-destructive/30 animate-pulse">
                긴급
              </span>
            )}
            {news.priority === 'high' && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-alert/15 text-amber-alert border border-amber-alert/30">
                높음
              </span>
            )}
          </div>
          <span className="font-mono text-[10px] text-muted-foreground">
            {timeAgo(news.timestamp)}
          </span>
        </div>

        {/* Title */}
        <h3 className="font-heading text-sm font-semibold text-foreground leading-snug mb-2 group-hover:text-primary transition-colors line-clamp-2">
          {news.title}
        </h3>

        {/* Summary */}
        <p className="font-sans text-xs text-muted-foreground leading-relaxed mb-3 line-clamp-2">
          {news.summary}
        </p>

        {/* Bottom row: Source + Impact + Score */}
        <div className="flex items-center justify-between pt-2 border-t border-border/30">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] text-muted-foreground">
              {news.sourceHandle}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Market Impact */}
            <div className="flex items-center gap-1">
              <span className="font-mono text-[10px] font-bold" style={{ color: impactConfig.color }}>
                {impactConfig.icon}
              </span>
              <span className="font-mono text-[10px]" style={{ color: impactConfig.color }}>
                {impactConfig.label}
              </span>
            </div>

            {/* Impact Score */}
            <div className="flex items-center gap-1">
              <div className="w-8 h-1.5 rounded-full overflow-hidden" style={{ background: 'oklch(0.2 0.02 260)' }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${news.impactScore}%`,
                    background: news.impactScore >= 90 ? '#ef4444' : news.impactScore >= 75 ? '#f59e0b' : news.impactScore >= 50 ? '#3b82f6' : '#6b7280',
                  }}
                />
              </div>
              <span className="font-mono text-[10px] text-muted-foreground">{news.impactScore}</span>
            </div>
          </div>
        </div>

        {/* Tags */}
        {news.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {news.tags.slice(0, 4).map((tag) => (
              <span
                key={tag}
                className="px-1.5 py-0.5 rounded text-[9px] font-mono text-muted-foreground border border-border/30"
                style={{ background: 'oklch(0.18 0.02 260)' }}
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
