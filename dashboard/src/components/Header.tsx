/**
 * Command Center Header
 * 군사 정보 스타일 상단 네비게이션 바
 */

import { useState, useEffect } from 'react';
import { mockSystemStatus } from '@/lib/mockData';
import { getCountdown } from '@/lib/utils';
import type { SystemStatus } from '@/lib/types';

interface HeaderProps {
  systemStatus?: SystemStatus;
}

export default function Header({ systemStatus }: HeaderProps) {
  const status = systemStatus ?? mockSystemStatus;
  const [countdown, setCountdown] = useState(getCountdown(status.nextUpdate));
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(getCountdown(status.nextUpdate));
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, [status.nextUpdate]);

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
            value={status.systemHealth === 'operational' ? '정상' : '점검중'}
            color={status.systemHealth === 'operational' ? 'green' : 'amber'}
          />
          <StatusIndicator
            label="모니터링"
            value={`${status.activeAccounts}/${status.totalAccounts}`}
            color="green"
          />
          <StatusIndicator
            label="수집 트윗"
            value={`${status.tweetsCollected}건`}
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
            <span className="font-mono text-xs text-foreground font-semibold">
              {currentTime.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
            <span className="font-mono text-[10px] text-muted-foreground">
              {currentTime.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })} KST
            </span>
          </div>
          <a
            href="https://t.me/baroBTC"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-border/50 hover:border-primary/50 transition-colors"
            style={{ background: 'oklch(0.14 0.02 260)' }}
          >
            <span className="text-sm">✈</span>
            <span className="font-mono text-[11px] text-muted-foreground hover:text-primary transition-colors">텔레그램</span>
          </a>
        </div>
      </div>
    </header>
  );
}

function StatusIndicator({ label, value, color }: { label: string; value: string; color: 'green' | 'amber' | 'blue' }) {
  const colorMap = {
    green: 'oklch(0.85 0.25 155)',
    amber: 'oklch(0.82 0.18 80)',
    blue: 'oklch(0.65 0.18 220)',
  };

  return (
    <div className="flex flex-col items-center">
      <span className="font-mono text-[10px] text-muted-foreground tracking-wider">{label}</span>
      <span className="font-mono text-xs font-semibold" style={{ color: colorMap[color] }}>{value}</span>
    </div>
  );
}
