/**
 * Command Center - Activity Log
 * 시스템 활동 로그 스트림
 * 군사 정보 스타일 - 실시간 활동 모니터링
 */

import { useState, useEffect } from 'react';

interface LogEntry {
  id: string;
  timestamp: string;
  type: 'collect' | 'analyze' | 'alert' | 'system';
  message: string;
}

const initialLogs: LogEntry[] = [
  { id: '1', timestamp: new Date(Date.now() - 2 * 60000).toISOString(), type: 'system', message: '시스템 정상 가동 중' },
  { id: '2', timestamp: new Date(Date.now() - 5 * 60000).toISOString(), type: 'analyze', message: 'Gemini AI 분석 완료 - 8건 처리' },
  { id: '3', timestamp: new Date(Date.now() - 8 * 60000).toISOString(), type: 'collect', message: '@bloomingbit_io 트윗 3건 수집' },
  { id: '4', timestamp: new Date(Date.now() - 12 * 60000).toISOString(), type: 'alert', message: '긴급 뉴스 감지: 트럼프 관세 정책' },
  { id: '5', timestamp: new Date(Date.now() - 15 * 60000).toISOString(), type: 'collect', message: '@MarioNawfal 트윗 5건 수집' },
  { id: '6', timestamp: new Date(Date.now() - 18 * 60000).toISOString(), type: 'analyze', message: '한국어 번역 검증 완료' },
  { id: '7', timestamp: new Date(Date.now() - 22 * 60000).toISOString(), type: 'collect', message: '@WuBlockchain 트윗 4건 수집' },
  { id: '8', timestamp: new Date(Date.now() - 25 * 60000).toISOString(), type: 'system', message: 'GitHub Actions 워크플로우 실행' },
];

const typeConfig = {
  collect: { color: 'oklch(0.85 0.25 155)', label: 'COLLECT', icon: '📥' },
  analyze: { color: 'oklch(0.65 0.18 220)', label: 'ANALYZE', icon: '🧠' },
  alert: { color: 'oklch(0.65 0.25 25)', label: 'ALERT', icon: '⚠️' },
  system: { color: 'oklch(0.6 0.02 260)', label: 'SYSTEM', icon: '⚙️' },
};

export default function ActivityLog() {
  const [logs] = useState(initialLogs);
  const [visibleCount, setVisibleCount] = useState(5);

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden" style={{ background: 'oklch(0.14 0.02 260)' }}>
      <div className="px-4 py-2.5 border-b border-border/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary pulse-indicator" />
          <span className="font-heading text-xs font-semibold tracking-wider text-foreground">활동 로그</span>
        </div>
        <span className="font-mono text-[10px] text-muted-foreground">{logs.length}건</span>
      </div>

      <div className="p-3 space-y-1">
        {logs.slice(0, visibleCount).map((log) => {
          const config = typeConfig[log.type];
          const time = new Date(log.timestamp);
          const timeStr = time.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

          return (
            <div key={log.id} className="flex items-start gap-2 px-2 py-1.5 rounded hover:bg-accent/50 transition-colors">
              <span className="font-mono text-[10px] text-muted-foreground shrink-0 mt-0.5 w-10">{timeStr}</span>
              <span
                className="font-mono text-[9px] font-bold px-1 py-0.5 rounded shrink-0"
                style={{ color: config.color, background: `${config.color}15`, border: `1px solid ${config.color}30` }}
              >
                {config.label}
              </span>
              <span className="font-mono text-[11px] text-foreground/80 leading-snug">{log.message}</span>
            </div>
          );
        })}
      </div>

      {visibleCount < logs.length && (
        <div className="px-4 py-2 border-t border-border/30">
          <button
            onClick={() => setVisibleCount(logs.length)}
            className="w-full text-center font-mono text-[10px] text-primary hover:text-primary/80 transition-colors"
          >
            더 보기 ({logs.length - visibleCount}건)
          </button>
        </div>
      )}
    </div>
  );
}
