# X News AI Dashboard

**Command Center** 군사 정보 스타일의 실시간 뉴스 인텔리전스 대시보드입니다.

## 빠른 시작 (로컬 실행)

```bash
cd dashboard
npm install    # 또는 pnpm install
npm run dev    # http://localhost:3000 에서 실행
```

## 빌드 및 배포

```bash
npm run build     # dist/ 디렉토리에 정적 파일 생성
npm run preview   # 빌드 결과 미리보기
```

빌드된 `dist/` 폴더를 Vercel, Netlify, GitHub Pages 등 어디든 배포할 수 있습니다.

## 기술 스택

| 항목 | 기술 |
|------|------|
| **프레임워크** | React 19 + TypeScript |
| **빌드 도구** | Vite 6 |
| **스타일링** | Tailwind CSS 4 |
| **UI 컴포넌트** | shadcn/ui (button, card, tooltip, sonner) |
| **라우팅** | Wouter |
| **폰트** | Space Grotesk, IBM Plex Sans, JetBrains Mono, Noto Sans KR |

## 주요 기능

- 3컬럼 비대칭 레이아웃: 카테고리 사이드바 | 뉴스 피드 | AI 분석 패널
- 실시간 뉴스 틱커: 긴급 뉴스 스크롤 배너
- 카테고리 필터: 지정학, 경제, 암호화폐, 트럼프, 규제
- 시장 센티먼트 게이지: 전체 시장 심리 시각화
- 카테고리 분포 차트: 카테고리별 뉴스 분포
- Gemini AI 분석 패널: AI 기반 시장 분석 및 인사이트
- 시스템 모니터: 수집 시스템 상태 표시
- 활동 로그: 실시간 시스템 활동 스트림
- 모바일 반응형: 모바일/태블릿 지원

## 디자인 테마

- 스타일: Military Intelligence Command Center
- 색상: 다크 네이비 배경, 사이버 그린/앰버/레드 액센트
- 타이포그래피: Space Grotesk + IBM Plex Sans + JetBrains Mono
- 효과: 스캔라인 오버레이, 그리드 패턴, 펄스 인디케이터

## 실제 데이터 연동

현재는 mockData.ts의 데모 데이터를 사용합니다. 실제 뉴스 데이터를 연동하려면:

1. 뉴스봇(main.py)이 생성하는 logs/last_result.json을 참조
2. mockData.ts를 수정하거나, API 엔드포인트에서 데이터를 fetch하도록 변경
3. GitHub Actions 워크플로우에서 자동으로 processed_news.json을 생성하여 연동 가능
