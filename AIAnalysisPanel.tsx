/**
 * Command Center - AI Analysis Panel
 * 우측 AI 종합 분석 패널
 * Gemini AI 분석 결과 표시
 */

import { MARKET_IMPACT_CONFIG, PRIORITY_CONFIG, type AIAnalysis } from '@/lib/types';
import { mockAIAnalyses } from '@/lib/mockData';
import { timeAgo } from '@/lib/utils';

const AI_BG_URL = 'https://private-us-east-1.manuscdn.com/sessionFile/L5zNvu3Ru4GOSPEkyfsTPD/sandbox/Z2UeFUYzYkK2Tbq1R0RgR5-img-5_1772135637000_na1fn_YWktYW5hbHlzaXMtYmc.png?x-oss-process=image/resize,w_1920,h_1920/format,webp/quality,q_80&Expires=1798761600&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvTDV6TnZ1M1J1NEdPU1BFa3lmc1RQRC9zYW5kYm94L1oyVWVGVVl6WWtLMlRicTFSMFJnUjUtaW1nLTVfMTc3MjEzNTYzNzAwMF9uYTFmbl9ZV2t0WVc1aGJIbHphWE10WW1jLnBuZz94LW9zcy1wcm9jZXNzPWltYWdlL3Jlc2l6ZSx3XzE5MjAsaF8xOTIwL2Zvcm1hdCx3ZWJwL3F1YWxpdHkscV84MCIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=GKBuxz1HkcXqrusJg~a4fc36taRF4Ym5DYKmm-aX2ZI7y0jHQcUNUXLwGw0XnOYa6U5eG9Iyg-LfTyhO3Mm1tS7CO6YfUy4GVMgpu~BLSZ3xAdhoLmTt8LB6TO4LMOjlgKivt8dgKRaNks03BXFVz23X~02iggisMQs9G4FwKOqnfnc4oP8TgliWQwJdhXg3BU0mW5Cc~tFMfWyz~AK8lYpDbjo5b7j5EsvB5Kii5AArtL78kJ8AKAd5jZJ4kZNn4iTSGK7v-qZpIVSTbvlYy76GpPLXhmWZT2usgRahhwT9A33msUTtiTJGmtn396TnKLR1QV10l3RPRRFS0RPwYQ__';

export default function AIAnalysisPanel() {
  return (
    <div className="space-y-4">
      {/* AI Brain Banner */}
      <div className="relative rounded-lg overflow-hidden border border-primary/20" style={{ minHeight: '120px' }}>
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{ backgroundImage: `url(${AI_BG_URL})` }}
        />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, oklch(0.12 0.02 260 / 0.8), oklch(0.14 0.04 180 / 0.6))' }} />
        <div className="relative p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-6 h-6 rounded border border-primary/40 flex items-center justify-center" style={{ background: 'oklch(0.85 0.25 155 / 0.15)' }}>
              <span className="text-xs">🧠</span>
            </div>
            <div>
              <span className="font-heading text-xs font-bold text-foreground tracking-wider">GEMINI AI 분석</span>
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 rounded-full bg-primary pulse-indicator" />
                <span className="font-mono text-[9px] text-primary">실시간 분석 활성</span>
              </div>
            </div>
          </div>
          <p className="font-mono text-[10px] text-muted-foreground leading-relaxed">
            60개 계정에서 수집된 트윗을 Gemini AI가 분석하여 시장 영향도와 핵심 인사이트를 제공합니다.
          </p>
        </div>
      </div>

      {/* Analysis Cards */}
      {mockAIAnalyses.map((analysis) => (
        <AnalysisCard key={analysis.id} analysis={analysis} />
      ))}
    </div>
  );
}

function AnalysisCard({ analysis }: { analysis: AIAnalysis }) {
  const sentimentConfig = MARKET_IMPACT_CONFIG[analysis.sentiment];
  const riskConfig = PRIORITY_CONFIG[analysis.riskLevel];

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden" style={{ background: 'oklch(0.14 0.02 260)' }}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-border/30 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full pulse-indicator" style={{ background: sentimentConfig.color }} />
          <span className="font-heading text-xs font-semibold text-foreground">{analysis.title}</span>
        </div>
        <span className="font-mono text-[10px] text-muted-foreground">{timeAgo(analysis.timestamp)}</span>
      </div>

      <div className="p-4 space-y-3">
        {/* Sentiment & Risk */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded border" style={{
            background: `${sentimentConfig.color}10`,
            borderColor: `${sentimentConfig.color}30`,
          }}>
            <span className="font-mono text-xs font-bold" style={{ color: sentimentConfig.color }}>
              {sentimentConfig.icon}
            </span>
            <span className="font-mono text-[10px]" style={{ color: sentimentConfig.color }}>
              {sentimentConfig.label}
            </span>
          </div>
          <div className="flex items-center gap-1.5 px-2 py-1 rounded border" style={{
            background: `${riskConfig.color}10`,
            borderColor: `${riskConfig.color}30`,
          }}>
            <span className="font-mono text-[10px]" style={{ color: riskConfig.color }}>
              리스크: {riskConfig.label}
            </span>
          </div>
        </div>

        {/* Content Preview */}
        <p className="font-sans text-xs text-foreground/80 leading-relaxed line-clamp-4">
          {analysis.content}
        </p>

        {/* Key Insights */}
        <div>
          <div className="font-mono text-[10px] text-muted-foreground tracking-wider mb-2">핵심 인사이트</div>
          <div className="space-y-1.5">
            {analysis.keyInsights.map((insight, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-1 h-1 rounded-full bg-primary mt-1.5 shrink-0" />
                <span className="font-sans text-[11px] text-foreground/80 leading-snug">{insight}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
