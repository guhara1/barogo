# 바로GO — 전국 방문 마사지 예약 안내 (정적 사이트)

전국 출장마사지 예약 안내 플랫폼 바로GO의 정적 웹사이트입니다. 명세서 기준 상단 7개 메뉴 그룹의 모든 페이지(허브 + 리프)와 메인 페이지가 포함되어 있습니다.

## 빌드

```bash
python3 build.py     # PAGES 정의로부터 57개 페이지 + sitemap.xml + robots.txt 생성
python3 -m http.server 8000
# http://localhost:8000
```

페이지 데이터(`PAGES`)는 `build.py` 안에 인라인되어 있습니다. 새 페이지를 추가하려면 `add(...)` 호출을 한 줄 더 추가하고 다시 빌드하면 됩니다.

## 생성된 페이지 (57개)

| 그룹 | 개수 | 경로 |
| --- | --- | --- |
| 홈 | 1 | `/` |
| 지역별 찾기 | 1 + 17 | `/area/`, `/area/seoul/` … `/area/jeju/` |
| 서비스 안내 | 1 + 8 | `/service/`, `/service/business-trip-massage/` 외 |
| 예약 안내 | 1 + 5 | `/reservation/`, `/reservation/how-to-book/` 외 |
| 후기 | 1 + 3 | `/review/`, `/review/reservation-case/` 외 |
| 마사지 정보 | 1 + 6 | `/guide/`, `/guide/what-is-business-trip-massage/` 외 |
| 고객센터 | 1 + 5 | `/support/`, `/support/notice/` 외 |
| 바로GO 소개 | 1 + 6 | `/about/`, `/about/privacy/`, `/about/terms/` 외 |

## 적용한 SEO·신뢰 요소

- **E-E-A-T** : 운영 사업자 정보(상호·대표·등록번호·주소·전화)를 모든 페이지 푸터에 노출, About 그룹에 운영 원칙·관리사 기준·안전 정책 분리. JSON-LD `Organization`을 모든 페이지에 포함.
- **구조화 데이터** : 모든 페이지에 `WebPage` + `BreadcrumbList` JSON-LD. 가이드 페이지는 `og:type=article`.
- **선호 이미지 지정** : `og:image` 및 schema.org `primaryImageOfPage`를 명시(2026-03 가이드 반영).
- **도어웨이 방지** : 시·도 17개 페이지는 동일 템플릿이 아니라 권역 특성·이용 패턴·이동 가능 범위 문구를 지역별로 다르게 작성.
- **Core Web Vitals 친화** : 이미지 자리표시는 SVG, 외부 JS·폰트 없음. CSS·JS는 각각 1파일 + `defer`.
- **접근성** : skip link, breadcrumb `aria-current`, `aria-haspopup`/`aria-expanded`, ESC 닫기, 키보드 포커스 스타일.
- **안전·정책 톤** : "최고", "1위", "은밀한", "퇴폐" 등 표현 배제. 안전 이용 정책·불편 신고 페이지 분리. 본문 곳곳에 "의료 행위가 아님" 명시.
- **sitemap.xml / robots.txt** : 빌드 시 자동 생성.

## 파일 구조

```
.
├── index.html
├── area/{seoul,…,jeju}/index.html        (17 + 허브)
├── service/{8 services}/index.html
├── reservation/{5 pages}/index.html
├── review/{4 pages}/index.html
├── guide/{6 pages}/index.html
├── support/{5 pages}/index.html
├── about/{6 pages}/index.html
├── sitemap.xml
├── robots.txt
├── build.py                              # 정적 사이트 제너레이터
├── assets/
│   ├── css/style.css
│   ├── js/nav.js
│   └── img/{og-default.svg, favicon.svg}
└── README.md
```

## 사업자 정보

- 상호 : 바로GO (YH LAB)
- 대표 : 김유환
- 사업자등록번호 : 815-26-00585
- 주소 : 경기도 파주시 청석로 268
- 예약 전화 : 0508-202-4719

## 다음 단계로 권장하는 작업

1. 실제 도메인이 정해지면 `build.py` 상단의 `SITE.url` 및 sitemap 절대 URL을 도메인으로 교체.
2. 후기 페이지의 카드를 실제 상담 사례 기반 콘텐츠로 단계적으로 교체(허위·복붙 금지).
3. 시·군·구 페이지는 메뉴에서 자동 노출하지 말고, 실제 운영 데이터가 충분히 누적된 지역부터 `area/<sido>/<sigungu>/`로 단계 확장.
4. 메인 og 이미지는 실제 디자인 시안으로 교체.
5. Search Console 등록 후 sitemap 제출.
