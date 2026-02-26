/**
 * Command Center - System Status Bar
 * 하단 시스템 상태 모니터링 바
 * 실시간 시스템 상태, 업데이트 주기, 계정 상태 표시
 */

import { useState, useEffect } from 'react';
import { mockSystemStatus, mockAccounts } from '@/lib/mockData';
import { getCountdown, formatDate } from '@/lib/utils';

export default function SystemStatusBar() {
  const [countdown, setCountdown] = useState(getCountdown(mockSystemStatus.nextUpdate));

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(getCountdown(mockSystemStatus.nextUpdate));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const priorityAccounts = mockAccounts.filter(a => a.isPriority);

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden" style={{ background: 'oklch(0.14 0.02 260)' }}>
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-border/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary pulse-indicator" />
          <span className="font-heading text-xs font-semibold tracking-wider text-foreground">시스템 모니터</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="font-mono text-[10px] text-muted-foreground">UPTIME</span>
          <span className="font-mono text-[10px] text-primary font-semibold">{mockSystemStatus.uptime}</span>
        </div>
      </div>

      <div className="p-4">
        {/* Status Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
          <StatusCard
            label="시스템 상태"
            value={mockSystemStatus.systemHealth === 'operational' ? '정상 운영' : '점검중'}
            color="green"
            icon="●"
          />
          <StatusCard
            label="다음 업데이트"
            value={countdown}
            color="cyan"
            icon="⏱"
          />
          <StatusCard
            label="수집 트윗"
            value={`${mockSystemStatus.tweetsCollected}건`}
            color="blue"
            icon="📥"
          />
          <StatusCard
            label="AI 분석"
            value={`${mockSystemStatus.aiAnalysisCount}건`}
            color="amber"
            icon="🧠"
          />
        </div>

        {/* Timeline */}
        <div className="rounded-lg border border-border/30 p-3" style={{ background: 'oklch(0.12 0.02 260)' }}>
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2">업데이트 타임라인</div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-primary" />
              <span className="font-mono text-[10px] text-foreground">마지막: {formatDate(mockSystemStatus.lastUpdate)}</span>
            </div>
            <div className="flex-1 h-px bg-border/30 relative">
              <div className="absolute left-1/3 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-primary/50 pulse-indicator" />
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full border border-primary/50" />
              <span className="font-mono text-[10px] text-muted-foreground">다음: {formatDate(mockSystemStatus.nextUpdate)}</span>
            </div>
          </div>
        </div>

        {/* Priority Account Status */}
        <div className="mt-4">
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2">우선 계정 활동 현황</div>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
            {priorityAccounts.map((account) => (
              <div
                key={account.handle}
                className="flex items-center gap-2 px-2.5 py-2 rounded border border-border/30"
                style={{ background: 'oklch(0.12 0.02 260)' }}
              >
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 pulse-indicator" />
                <div className="flex-1 min-w-0">
                  <div className="font-mono text-[10px] text-foreground truncate">{account.handle}</div>
                  <div className="font-mono text-[9px] text-muted-foreground">{account.tweetCount}건 수집</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusCard({ label, value, color, icon }: { label: string; value: string; color: string; icon: string }) {
  const colorMap: Record<string, string> = {
    green: 'oklch(0.85 0.25 155)',
    cyan: 'oklch(0.8 0.15 200)',
    blue: 'oklch(0.65 0.18 220)',
    amber: 'oklch(0.82 0.18 80)',
    red: 'oklch(0.65 0.25 25)',
  };

  return (
    <div className="rounded-lg border border-border/30 p-3" style={{ background: 'oklch(0.12 0.02 260)' }}>
      <div className="flex items-center gap-1.5 mb-1">
        <span className="text-xs">{icon}</span>
        <span className="font-mono text-[10px] text-muted-foreground">{label}</span>
      </div>
      <span className="font-mono text-sm font-bold" style={{ color: colorMap[color] || colorMap.green }}>
        {value}
      </span>
    </div>
  );
}
