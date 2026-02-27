/**
 * Command Center - Category Sidebar
 * 좌측 카테고리 네비게이션 패널
 * 군사 정보 스타일 - 카테고리별 필터링 및 통계
 */

import { CATEGORY_CONFIG, type Category } from '@/lib/types';
import { mockNews } from '@/lib/mockData';
import { cn } from '@/lib/utils';

interface CategorySidebarProps {
  selectedCategory: Category | 'all';
  onSelectCategory: (category: Category | 'all') => void;
}

export default function CategorySidebar({ selectedCategory, onSelectCategory }: CategorySidebarProps) {
  const categoryCounts = mockNews.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalCount = mockNews.length;

  return (
    <aside className="w-full lg:w-56 shrink-0">
      <div className="border border-border/50 rounded-lg overflow-hidden" style={{ background: 'oklch(0.14 0.02 260)' }}>
        {/* Header */}
        <div className="px-4 py-3 border-b border-border/50 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary pulse-indicator" />
          <span className="font-heading text-xs font-semibold tracking-wider text-foreground">카테고리 필터</span>
        </div>

        {/* All category */}
        <div className="p-2">
          <button
            onClick={() => onSelectCategory('all')}
            className={cn(
              'w-full flex items-center justify-between px-3 py-2.5 rounded text-left transition-all duration-200',
              selectedCategory === 'all'
                ? 'bg-primary/10 border border-primary/30'
                : 'hover:bg-accent border border-transparent'
            )}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">📡</span>
              <span className="font-mono text-xs font-medium text-foreground">전체 인텔</span>
            </div>
            <span className="font-mono text-xs text-muted-foreground">{totalCount}</span>
          </button>

          {/* Category items */}
          <div className="mt-1 space-y-1">
            {(Object.entries(CATEGORY_CONFIG) as [Category, typeof CATEGORY_CONFIG[Category]][]).map(([category, config]) => {
              const count = categoryCounts[category] || 0;
              const isSelected = selectedCategory === category;

              return (
                <button
                  key={category}
                  onClick={() => onSelectCategory(category)}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2.5 rounded text-left transition-all duration-200',
                    isSelected
                      ? 'border'
                      : 'hover:bg-accent border border-transparent'
                  )}
                  style={isSelected ? {
                    background: `${config.color}15`,
                    borderColor: `${config.color}40`,
                  } : undefined}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{config.icon}</span>
                    <span className="font-mono text-xs font-medium text-foreground">{category}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-muted-foreground">{count}</span>
                    {count > 0 && (
                      <div
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ background: config.color }}
                      />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Priority Accounts Section */}
        <div className="border-t border-border/50 px-4 py-3">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-alert pulse-indicator" />
            <span className="font-heading text-xs font-semibold tracking-wider text-foreground">우선 계정</span>
          </div>
          <div className="space-y-1.5">
            {['@dons_korea', '@bloomingbit_io', '@WuBlockchain', '@zoomerfied', '@MarioNawfal', '@martypartymusic'].map((handle) => (
              <div key={handle} className="flex items-center gap-2 px-2 py-1">
                <div className="w-1 h-1 rounded-full bg-primary/60" />
                <span className="font-mono text-[11px] text-muted-foreground hover:text-primary transition-colors cursor-default">
                  {handle}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* System Info */}
        <div className="border-t border-border/50 px-4 py-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1.5 h-1.5 rounded-full bg-chart-2 pulse-indicator" />
            <span className="font-heading text-xs font-semibold tracking-wider text-foreground">시스템 정보</span>
          </div>
          <div className="space-y-1">
            <InfoRow label="업데이트 주기" value="4시간" />
            <InfoRow label="AI 엔진" value="Gemini" />
            <InfoRow label="언어" value="한국어" />
            <InfoRow label="가동률" value="99.7%" />
          </div>
        </div>
      </div>
    </aside>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between px-2 py-0.5">
      <span className="font-mono text-[10px] text-muted-foreground">{label}</span>
      <span className="font-mono text-[10px] text-foreground">{value}</span>
    </div>
  );
}
