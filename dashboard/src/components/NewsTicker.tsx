/**
 * Command Center - News Ticker
 * 히어로 배너 하단의 실시간 뉴스 스크롤 틱커
 * 긴급 뉴스와 주요 이벤트를 스크롤하며 표시
 */

import { useEffect, useRef } from 'react';
import { mockNews } from '@/lib/mockData';
import { CATEGORY_CONFIG } from '@/lib/types';

export default function NewsTicker() {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;

    let animationId: number;
    let position = 0;

    const animate = () => {
      position -= 0.5;
      if (Math.abs(position) >= el.scrollWidth / 2) {
        position = 0;
      }
      el.style.transform = `translateX(${position}px)`;
      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, []);

  const tickerItems = mockNews.slice(0, 6);

  return (
    <div className="border-b border-border/30 overflow-hidden" style={{ background: 'oklch(0.11 0.02 260)' }}>
      <div className="container flex items-center h-8">
        <div className="shrink-0 flex items-center gap-1.5 pr-3 border-r border-border/30 mr-3">
          <div className="w-1.5 h-1.5 rounded-full bg-destructive pulse-indicator" />
          <span className="font-mono text-[10px] text-destructive font-bold tracking-wider whitespace-nowrap">BREAKING</span>
        </div>
        <div className="overflow-hidden flex-1">
          <div ref={scrollRef} className="flex items-center gap-8 whitespace-nowrap" style={{ width: 'max-content' }}>
            {[...tickerItems, ...tickerItems].map((news, i) => {
              const config = CATEGORY_CONFIG[news.category];
              return (
                <div key={`${news.id}-${i}`} className="flex items-center gap-2">
                  <span className="text-[10px]">{config.icon}</span>
                  <span className="font-mono text-[11px] text-foreground/80">{news.title}</span>
                  <span className="font-mono text-[10px] text-muted-foreground">|</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
