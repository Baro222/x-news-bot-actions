# X News AI Dashboard

**Command Center** 군사 정보 스타일의 실시간 뉴스 인텔리전스 대시보드입니다.

## 개요

60개 X(트위터) 계정에서 4시간 주기로 수집된 뉴스를 Gemini AI가 분석하여 시장 영향도와 핵심 인사이트를 시각적으로 제공하는 웹 대시보드입니다.

## 기술 스택

| 항목 | 기술 |
|------|------|
| **프레임워크** | React 19 + TypeScript |
| **스타일링** | Tailwind CSS 4 |
| **UI 컴포넌트** | shadcn/ui |
| **라우팅** | Wouter |
| **폰트** | Space Grotesk, IBM Plex Sans, JetBrains Mono, Noto Sans KR |

## 주요 기능

- **3컬럼 비대칭 레이아웃**: 카테고리 사이드바 | 뉴스 피드 | AI 분석 패널
- **실시간 뉴스 틱커**: 긴급 뉴스 스크롤 배너
- **카테고리 필터**: 지정학, 경제, 암호화폐, 트럼프, 규제
- **시장 센티먼트 게이지**: 전체 시장 심리 시각화
- **카테고리 분포 차트**: 카테고리별 뉴스 분포
- **Gemini AI 분석 패널**: AI 기반 시장 분석 및 인사이트
- **시스템 모니터**: 수집 시스템 상태 표시
- **활동 로그**: 실시간 시스템 활동 스트림
- **모바일 반응형**: 모바일/태블릿 지원

## 디자인 테마

- **스타일**: Military Intelligence Command Center
- **색상**: 다크 네이비 배경, 사이버 그린/앰버/레드 액센트
- **타이포그래피**: Space Grotesk (헤딩) + IBM Plex Sans (본문) + JetBrains Mono (데이터)
- **효과**: 스캔라인 오버레이, 그리드 패턴, 펄스 인디케이터

## 파일 구조

```
dashboard/
├── index.html              # HTML 엔트리포인트
├── src/
│   ├── App.tsx             # 라우트 및 테마 설정
│   ├── main.tsx            # React 엔트리포인트
│   ├── index.css           # 글로벌 스타일 및 CSS 변수
│   ├── components/
│   │   ├── Header.tsx              # 상단 헤더 바
│   │   ├── NewsTicker.tsx          # 실시간 뉴스 틱커
│   │   ├── CategorySidebar.tsx     # 카테고리 필터 사이드바
│   │   ├── NewsCard.tsx            # 뉴스 카드 컴포넌트
│   │   ├── NewsDetailPanel.tsx     # 뉴스 상세 패널
│   │   ├── AIAnalysisPanel.tsx     # AI 분석 패널
│   │   ├── MarketSentimentGauge.tsx # 시장 센티먼트 게이지
│   │   ├── CategoryDistribution.tsx # 카테고리 분포 차트
│   │   ├── ActivityLog.tsx         # 활동 로그
│   │   └── SystemStatusBar.tsx     # 시스템 상태 바
│   ├── lib/
│   │   ├── types.ts        # 타입 정의
│   │   ├── mockData.ts     # 데모 데이터
│   │   └── utils.ts        # 유틸리티 함수
│   └── pages/
│       └── Home.tsx        # 메인 대시보드 페이지
└── README.md               # 이 파일
```

## 향후 개선

- [ ] GitHub Actions 워크플로우에서 생성된 실제 뉴스 데이터 연동
- [ ] 실시간 BTC/ETH 가격 위젯 추가
- [ ] 뉴스 검색 기능
- [ ] 다크/라이트 테마 전환
