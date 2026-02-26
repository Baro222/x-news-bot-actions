/**
 * Command Center - Category Distribution
 * 카테고리별 뉴스 분포를 시각적 바 차트로 표시
 */

import { mockNews } from '@/lib/mockData';
import { CATEGORY_CONFIG, type Category } from '@/lib/types';

export default function CategoryDistribution() {
  const categoryCounts = mockNews.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const maxCount = Math.max(...Object.values(categoryCounts), 1);

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden" style={{ background: 'oklch(0.14 0.02 260)' }}>
      <div className="px-4 py-2.5 border-b border-border/50 flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-chart-2 pulse-indicator" />
        <span className="font-heading text-xs font-semibold tracking-wider text-foreground">카테고리 분포</span>
      </div>

      <div className="p-4 space-y-2.5">
        {(Object.entries(CATEGORY_CONFIG) as [Category, typeof CATEGORY_CONFIG[Category]][]).map(([category, config]) => {
          const count = categoryCounts[category] || 0;
          const percent = (count / maxCount) * 100;

          return (
            <div key={category} className="flex items-center gap-3">
              <div className="w-16 flex items-center gap-1.5 shrink-0">
                <span className="text-xs">{config.icon}</span>
                <span className="font-mono text-[10px] text-foreground">{category}</span>
              </div>
              <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: 'oklch(0.2 0.02 260)' }}>
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${percent}%`,
                    background: config.color,
                    boxShadow: `0 0 6px ${config.color}40`,
                  }}
                />
              </div>
              <span className="font-mono text-[10px] text-muted-foreground w-6 text-right">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
