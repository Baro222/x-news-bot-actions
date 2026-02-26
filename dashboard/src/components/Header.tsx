/**
 * Command Center Header
 * 군사 정보 스타일 상단 네비게이션 바
 * Dark navy background, cyber green accents, scan line overlay
 */

import { useState, useEffect } from 'react';
import { mockSystemStatus } from '@/lib/mockData';
import { getCountdown } from '@/lib/utils';

export default function Header() {
  const [countdown, setCountdown] = useState(getCountdown(mockSystemStatus.nextUpdate));
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(getCountdown(mockSystemStatus.nextUpdate));
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-border/50" style={{ background: 'oklch(0.1 0.02 260 / 0.95)', backdropFilter: 'blur(12px)' }}>
      <div className="container flex items-center justify-between h-14">
        {/* Left: Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-8 h-8 rounded border border-primary/50 flex items-center justify-center" style={{ background: 'oklch(0.85 0.25 155 / 0.1)' }}>
              <span className="font-mono text-primary text-sm font-bold">X</span>
            </div>
            <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-primary pulse-indicator" />
          </div>
          <div className="flex flex-col">
            <h1 className="font-heading text-sm font-bold tracking-wider text-foreground leading-none">
              COMMAND CENTER
            </h1>
            <span className="font-mono text-[10px] text-muted-foreground tracking-widest">
              X NEWS AI INTELLIGENCE
            </span>
          </div>
        </div>

        {/* Center: System Status */}
        <div className="hidden md:flex items-center gap-6">
          <StatusIndicator
            label="시스템"
            value={mockSystemStatus.systemHealth === 'operational' ? '정상' : '점검중'}
            color={mockSystemStatus.systemHealth === 'operational' ? 'green' : 'amber'}
          />
          <StatusIndicator
            label="모니터링"
            value={`${mockSystemStatus.activeAccounts}/${mockSystemStatus.totalAccounts}`}
            color="green"
          />
          <StatusIndicator
            label="수집 트윗"
            value={`${mockSystemStatus.tweetsCollected}건`}
            color="blue"
          />
          <div className="h-6 w-px bg-border/50" />
          <div className="flex flex-col items-center">
            <span className="font-mono text-[10px] text-muted-foreground tracking-wider">다음 업데이트</span>
            <span className="font-mono text-sm text-primary font-semibold tracking-wider glow-green-text">{countdown}</span>
          </div>
        </div>

        {/* Right: Time & Telegram */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex flex-col items-end">
            <span className="font-mono text-[10px] text-muted-foreground tracking-wider">KST</span>
            <span className="font-mono text-xs text-foreground">
              {currentTime.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          </div>
          <a
            href="https://t.me/baroBTC"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-primary/30 text-primary text-xs font-mono hover:bg-primary/10 transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
            @baroBTC
          </a>
        </div>
      </div>
    </header>
  );
}

function StatusIndicator({ label, value, color }: { label: string; value: string; color: 'green' | 'amber' | 'blue' | 'red' }) {
  const colorMap = {
    green: { dot: 'bg-primary', text: 'text-primary' },
    amber: { dot: 'bg-amber-alert', text: 'text-amber-alert' },
    blue: { dot: 'bg-chart-2', text: 'text-chart-2' },
    red: { dot: 'bg-destructive', text: 'text-destructive' },
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`w-1.5 h-1.5 rounded-full ${colorMap[color].dot} pulse-indicator`} />
      <div className="flex flex-col">
        <span className="font-mono text-[10px] text-muted-foreground tracking-wider">{label}</span>
        <span className={`font-mono text-xs font-medium ${colorMap[color].text}`}>{value}</span>
      </div>
    </div>
  );
}
