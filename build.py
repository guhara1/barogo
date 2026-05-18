#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""바로GO static site generator.

Renders every page defined in PAGES into <path>/index.html using a shared
template (header, navigation, footer). Pages keep their own <main> content
plus per-page metadata (title, description, JSON-LD), so the generator is
just plumbing — content lives in the PAGES list below.
"""
from __future__ import annotations
import json
import os
import pathlib
from datetime import date

ROOT = pathlib.Path(__file__).parent
BUILD_DATE = date.today().isoformat()

SITE = {
    "name": "바로GO",
    "tagline": "전국 방문 마사지 안내",
    "url": "",                       # relative absolute paths
    "phone": "0508-202-4719",
    "biz_name": "바로GO (YH LAB)",
    "ceo": "김유환",
    "regno": "815-26-00585",
    "address_full": "경기도 파주시 청석로 268",
    "address_locality": "파주시",
    "address_region": "경기도",
    "address_street": "청석로 268",
}

# -------- shared HTML fragments --------

HEADER = """<a class="skip-link" href="#main">본문 바로가기</a>
<header class="site-header" role="banner">
  <div class="header-inner">
    <a href="/" class="brand" aria-label="바로GO 홈으로 이동">
      <span class="brand-mark">바로</span><span class="brand-mark accent">GO</span>
      <span class="brand-tag">전국 방문 마사지 안내</span>
    </a>
    <button class="nav-toggle" type="button" aria-controls="primary-nav" aria-expanded="false" aria-label="메뉴 열기">
      <span></span><span></span><span></span>
    </button>
    <nav id="primary-nav" class="primary-nav" aria-label="주요 메뉴">
      <ul class="nav-list">
        <li class="nav-item"><a href="/" class="nav-link">홈</a></li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">지역별 찾기<span class="chev"></span></button>
          <div class="mega-panel">
            <div class="mega-grid mega-grid--regions">
              <a href="/area/seoul/">서울</a><a href="/area/gyeonggi/">경기</a>
              <a href="/area/incheon/">인천</a><a href="/area/busan/">부산</a>
              <a href="/area/daegu/">대구</a><a href="/area/daejeon/">대전</a>
              <a href="/area/gwangju/">광주</a><a href="/area/ulsan/">울산</a>
              <a href="/area/sejong/">세종</a><a href="/area/gangwon/">강원</a>
              <a href="/area/chungbuk/">충북</a><a href="/area/chungnam/">충남</a>
              <a href="/area/jeonbuk/">전북</a><a href="/area/jeonnam/">전남</a>
              <a href="/area/gyeongbuk/">경북</a><a href="/area/gyeongnam/">경남</a>
              <a href="/area/jeju/">제주</a>
            </div>
            <p class="mega-note">실제 서비스 가능 여부와 예약 가능 시간은 각 지역 페이지에서 확인하실 수 있습니다.</p>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">서비스 안내<span class="chev"></span></button>
          <div class="mega-panel">
            <ul class="mega-list">
              <li><a href="/service/business-trip-massage/">출장마사지 안내</a></li>
              <li><a href="/service/hometai/">홈타이 안내</a></li>
              <li><a href="/service/swedish/">스웨디시 마사지 안내</a></li>
              <li><a href="/service/aroma/">아로마 마사지 안내</a></li>
              <li><a href="/service/sports-massage/">스포츠 마사지 안내</a></li>
              <li><a href="/service/couple-massage/">커플 마사지 안내</a></li>
              <li><a href="/service/hotel-massage/">호텔 방문 마사지 안내</a></li>
              <li><a href="/service/office-massage/">기업·사무실 방문 마사지 안내</a></li>
            </ul>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">예약 안내<span class="chev"></span></button>
          <div class="mega-panel">
            <ul class="mega-list">
              <li><a href="/reservation/how-to-book/">예약 방법</a></li>
              <li><a href="/reservation/price/">가격 및 코스 안내</a></li>
              <li><a href="/reservation/check-before-use/">이용 전 확인사항</a></li>
              <li><a href="/reservation/cancel-refund/">취소·환불 규정</a></li>
              <li><a href="/reservation/payment/">결제 안내</a></li>
            </ul>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">후기·정보<span class="chev"></span></button>
          <div class="mega-panel">
            <div class="mega-cols">
              <div>
                <h3 class="mega-heading">이용 경험</h3>
                <ul class="mega-list">
                  <li><a href="/review/">실제 이용후기</a></li>
                  <li><a href="/review/reservation-case/">예약 사례</a></li>
                  <li><a href="/review/first-time/">처음 이용 고객 후기</a></li>
                  <li><a href="/review/area/">지역별 후기 모음</a></li>
                </ul>
              </div>
              <div>
                <h3 class="mega-heading">마사지 정보</h3>
                <ul class="mega-list">
                  <li><a href="/guide/what-is-business-trip-massage/">출장마사지란?</a></li>
                  <li><a href="/guide/massage-before-after/">마사지 전후 주의사항</a></li>
                  <li><a href="/guide/aroma-vs-swedish/">아로마와 스웨디시 차이</a></li>
                  <li><a href="/guide/first-time-massage/">처음 이용 전 알아둘 점</a></li>
                  <li><a href="/guide/massage-price-standard/">가격이 달라지는 이유</a></li>
                  <li><a href="/guide/safe-reservation/">안전한 예약 확인 방법</a></li>
                </ul>
              </div>
            </div>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">고객센터<span class="chev"></span></button>
          <div class="mega-panel">
            <ul class="mega-list">
              <li><a href="/support/notice/">공지사항</a></li>
              <li><a href="/support/faq/">자주 묻는 질문</a></li>
              <li><a href="/support/contact/">문의하기</a></li>
              <li><a href="/support/partnership/">제휴·입점 문의</a></li>
              <li><a href="/support/report/">불편 신고</a></li>
            </ul>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">바로GO 소개<span class="chev"></span></button>
          <div class="mega-panel">
            <ul class="mega-list">
              <li><a href="/about/brand/">브랜드 소개</a></li>
              <li><a href="/about/operation-policy/">운영 원칙</a></li>
              <li><a href="/about/therapist-policy/">관리사 운영 기준</a></li>
              <li><a href="/about/safety-policy/">안전 이용 정책</a></li>
              <li><a href="/about/privacy/">개인정보처리방침</a></li>
              <li><a href="/about/terms/">이용약관</a></li>
            </ul>
          </div>
        </li>
      </ul>
      <div class="nav-cta">
        <a class="btn-tel" href="tel:0508-202-4719" aria-label="예약 전화 0508-202-4719">
          <span class="btn-tel__label">예약 전화</span>
          <span class="btn-tel__num">0508-202-4719</span>
        </a>
      </div>
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <p class="footer-brand">바로GO</p>
      <p class="footer-sub">전국 방문 마사지 예약 안내 플랫폼</p>
      <p class="footer-sub">건전하고 안전한 이용을 위한 안내를 제공합니다.</p>
    </div>
    <div class="footer-biz">
      <p>상호 : 바로GO (YH LAB)</p>
      <p>대표 : 김유환</p>
      <p>사업자등록번호 : 815-26-00585</p>
      <p>주소 : 경기도 파주시 청석로 268</p>
      <p>예약 전화 : <a href="tel:0508-202-4719">0508-202-4719</a></p>
    </div>
    <div class="footer-links">
      <a href="/about/brand/">브랜드 소개</a>
      <a href="/about/operation-policy/">운영 원칙</a>
      <a href="/about/safety-policy/">안전 이용 정책</a>
      <a href="/about/privacy/">개인정보처리방침</a>
      <a href="/about/terms/">이용약관</a>
      <a href="/support/contact/">문의하기</a>
    </div>
  </div>
  <p class="footer-copy">© 바로GO · YH LAB. 건전하고 안전한 방문 마사지 이용 안내.</p>
</footer>"""

# ---------- page template ----------

PAGE_TPL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="/assets/img/og-default.svg">
<meta property="og:site_name" content="바로GO">
<meta property="og:locale" content="ko_KR">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/style.css">
<script type="application/ld+json">{jsonld}</script>
</head>
<body data-page="{slug}">
{header}
<main id="main">
<nav class="breadcrumb" aria-label="현재 위치">
  <ol>{breadcrumbs}</ol>
</nav>
<article class="page">
<header class="page-head">
<h1>{h1}</h1>
{intro}
</header>
{body}
{related}
</article>
</main>
{footer}
<script src="/assets/js/nav.js" defer></script>
</body>
</html>"""


def breadcrumb_html(items):
    parts = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f'<li aria-current="page">{label}</li>')
    return "".join(parts)


def breadcrumb_jsonld(items):
    elements = []
    for i, (label, href) in enumerate(items):
        item = {
            "@type": "ListItem",
            "position": i + 1,
            "name": label,
        }
        if href:
            item["item"] = href
        elements.append(item)
    return {"@type": "BreadcrumbList", "itemListElement": elements}


def render(page):
    url = page["url"]
    breadcrumbs = page.get("breadcrumbs", [])
    crumbs_html = breadcrumb_html(breadcrumbs)
    extra_jsonld = page.get("jsonld_extra", [])
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "/#org",
                "name": "바로GO",
                "legalName": "YH LAB",
                "telephone": SITE["phone"],
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": SITE["address_street"],
                    "addressLocality": SITE["address_locality"],
                    "addressRegion": SITE["address_region"],
                    "addressCountry": "KR",
                },
            },
            {
                "@type": page.get("schema_type", "WebPage"),
                "name": page["title"],
                "url": url,
                "description": page["description"],
                "isPartOf": {"@type": "WebSite", "name": "바로GO", "url": "/"},
                "primaryImageOfPage": "/assets/img/og-default.svg",
                "dateModified": BUILD_DATE,
            },
            breadcrumb_jsonld(breadcrumbs),
        ] + extra_jsonld,
    }

    html = PAGE_TPL.format(
        title=page["title"],
        description=page["description"],
        url=url,
        og_type=page.get("og_type", "website"),
        slug=page.get("slug", "page"),
        h1=page["h1"],
        intro=page.get("intro", ""),
        body=page["body"],
        related=page.get("related", ""),
        breadcrumbs=crumbs_html,
        header=HEADER,
        footer=FOOTER,
        jsonld=json.dumps(jsonld, ensure_ascii=False),
    )

    out_path = ROOT / page["path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return page["path"]


# ============================================================
# PAGE CONTENT
# ============================================================
PAGES = []

def add(**kwargs):
    PAGES.append(kwargs)


# ---------- Region hub ----------
add(
  path="area/index.html",
  url="/area/",
  slug="area-hub",
  title="지역별 출장마사지 찾기 | 전국 17개 시·도 안내 | 바로GO",
  description="서울·경기·부산 등 전국 17개 광역 시·도별 출장마사지 이용 안내. 지역별 예약 가능 시간, 자주 찾는 서비스 유형, 이동 가능 범위를 확인하세요.",
  h1="지역별 출장마사지 찾기",
  intro='<p class="lede">전국 17개 광역 시·도 단위로 출장마사지 이용 정보를 정리했습니다. 시·도 페이지에서 해당 지역의 일반적인 예약 가능 시간대와 자주 찾는 서비스 유형, 이동 가능 범위를 확인하실 수 있습니다.</p>',
  breadcrumbs=[("홈", "/"), ("지역별 찾기", "/area/")],
  body="""
<section class="block">
<p>바로GO는 시·도 단위로 안내를 분리해 운영합니다. 동·읍·면 단위까지 일괄 자동 생성된 페이지가 아니라, 실제 이용 사례와 상담 기록이 누적된 지역부터 단계적으로 추가됩니다. 따라서 같은 광역 안에서도 세부 지역에 따라 가능 여부가 달라질 수 있으니, 예약 단계에서 한 번 더 확인을 권장합니다.</p>
</section>
<section class="block">
<h2>광역 시·도 목록</h2>
<div class="region-grid">
  <a href="/area/seoul/" class="region-card"><span>서울</span></a>
  <a href="/area/gyeonggi/" class="region-card"><span>경기</span></a>
  <a href="/area/incheon/" class="region-card"><span>인천</span></a>
  <a href="/area/busan/" class="region-card"><span>부산</span></a>
  <a href="/area/daegu/" class="region-card"><span>대구</span></a>
  <a href="/area/daejeon/" class="region-card"><span>대전</span></a>
  <a href="/area/gwangju/" class="region-card"><span>광주</span></a>
  <a href="/area/ulsan/" class="region-card"><span>울산</span></a>
  <a href="/area/sejong/" class="region-card"><span>세종</span></a>
  <a href="/area/gangwon/" class="region-card"><span>강원</span></a>
  <a href="/area/chungbuk/" class="region-card"><span>충북</span></a>
  <a href="/area/chungnam/" class="region-card"><span>충남</span></a>
  <a href="/area/jeonbuk/" class="region-card"><span>전북</span></a>
  <a href="/area/jeonnam/" class="region-card"><span>전남</span></a>
  <a href="/area/gyeongbuk/" class="region-card"><span>경북</span></a>
  <a href="/area/gyeongnam/" class="region-card"><span>경남</span></a>
  <a href="/area/jeju/" class="region-card"><span>제주</span></a>
</div>
</section>
<section class="block">
<h2>지역 페이지에서 확인할 수 있는 정보</h2>
<ul class="check-list">
<li>해당 지역에서 일반적으로 가능한 예약 시간대</li>
<li>자주 선택되는 서비스 유형과 코스 길이</li>
<li>이동 가능 주변 권역과 추가 이동료 발생 기준</li>
<li>처음 이용하는 분이 자주 묻는 질문</li>
</ul>
</section>
""",
)

# ---------- 17 region pages ----------
REGIONS = [
  ("seoul", "서울", "서울특별시", "강남·서초·송파·마포·용산", "강남, 서초, 송파, 마포, 용산, 영등포, 종로, 광진",
   "심야 시간대 호텔 방문 케어와 평일 저녁 시간대 가정 방문 케어가 많이 문의되는 지역입니다.", "출장·여행 일정과 호텔 일정에 맞춘 야간 예약이 많습니다."),
  ("gyeonggi", "경기", "경기도", "성남·수원·고양·용인·부천", "성남, 수원, 고양, 용인, 부천, 안양, 화성, 평택",
   "수도권 광역 이동을 고려해야 하므로 예약 가능 시간 확인이 특히 중요합니다.", "도시별 이동 시간 차이가 커서 권역 내 가능 여부를 사전에 확인하는 것이 좋습니다."),
  ("incheon", "인천", "인천광역시", "송도·연수·남동·서구", "송도, 연수, 남동, 미추홀, 부평, 서구, 계양",
   "공항 인접 지역이라 출장·여행 일정에 맞춘 호텔 방문 케어 문의가 많습니다.", "공항 인근 호텔 일정에 맞춘 단시간 코스를 자주 문의합니다."),
  ("busan", "부산", "부산광역시", "해운대·서면·광안·남포", "해운대, 수영, 동래, 부산진, 남구, 중구, 사하",
   "관광·휴양 일정에 맞춘 호텔 방문 케어 문의가 많은 지역입니다.", "해운대·광안 일대 호텔 방문 비중이 특히 높습니다."),
  ("daegu", "대구", "대구광역시", "수성·중구·동구·달서", "수성, 중구, 동구, 달서, 북구, 남구",
   "주거 밀집 지역 중심으로 평일 저녁 시간대 예약이 자주 발생합니다.", "출장 일정에 맞춘 도심 호텔 방문 케어도 함께 안내합니다."),
  ("daejeon", "대전", "대전광역시", "유성·서구·둔산", "유성, 서구, 중구, 동구, 대덕",
   "정부청사·연구단지 일대 출장 일정과 맞물려 평일 저녁 문의가 많습니다.", "유성 일대 호텔 방문 예약 비중이 높은 편입니다."),
  ("gwangju", "광주", "광주광역시", "동·서·남·북·광산", "동구, 서구, 남구, 북구, 광산구",
   "주거 밀집 권역 중심의 가정 방문 케어가 일반적입니다.", "주말 가족 일정과 겹치는 시간대는 예약이 빠르게 차는 편입니다."),
  ("ulsan", "울산", "울산광역시", "남구·중구·북구·울주", "남구, 중구, 북구, 동구, 울주",
   "산업단지 출장과 맞물린 평일 저녁·야간 호텔 방문 문의가 많습니다.", "장기 출장 일정에 맞춘 재방문 예약도 함께 안내합니다."),
  ("sejong", "세종", "세종특별자치시", "한솔·새롬·도담·아름", "한솔, 새롬, 도담, 아름, 종촌, 보람",
   "행정중심복합도시 특성상 평일 저녁 시간대 가정 방문 케어가 자주 문의됩니다.", "이동 거리에 따라 가능 시간이 제한되는 경우가 있습니다."),
  ("gangwon", "강원", "강원특별자치도", "춘천·원주·강릉·속초", "춘천, 원주, 강릉, 속초, 동해, 평창",
   "관광·휴양 일정에 맞춘 숙소 방문 케어 비중이 높습니다.", "성수기에는 가능 시간이 빠르게 차므로 사전 예약을 권장합니다."),
  ("chungbuk", "충북", "충청북도", "청주·충주·제천", "청주, 충주, 제천, 음성, 진천",
   "출장·연수 일정과 맞물린 평일 저녁 호텔 방문 문의가 많습니다.", "이동 거리에 따라 가능 권역이 제한될 수 있습니다."),
  ("chungnam", "충남", "충청남도", "천안·아산·서산·당진", "천안, 아산, 서산, 당진, 공주, 보령",
   "산업단지 출장과 맞물린 평일 저녁·야간 호텔 방문 문의가 많습니다.", "광역 이동 시 추가 이동료가 발생할 수 있습니다."),
  ("jeonbuk", "전북", "전북특별자치도", "전주·익산·군산", "전주, 익산, 군산, 정읍, 남원",
   "주거 밀집 지역과 도심 호텔 두 패턴이 모두 안내됩니다.", "권역별 가능 시간 차이가 있어 사전 확인이 좋습니다."),
  ("jeonnam", "전남", "전라남도", "여수·순천·목포·광양", "여수, 순천, 목포, 광양, 나주",
   "관광·출장 일정과 맞물린 호텔 방문 문의가 자주 발생합니다.", "성수기 관광 일정 시즌은 예약이 빠르게 차는 편입니다."),
  ("gyeongbuk", "경북", "경상북도", "포항·경주·구미·안동", "포항, 경주, 구미, 안동, 영주",
   "관광 권역과 산업단지 권역이 모두 포함된 지역입니다.", "경주는 관광 일정, 구미는 출장 일정 비중이 높습니다."),
  ("gyeongnam", "경남", "경상남도", "창원·김해·진주·양산", "창원, 김해, 진주, 양산, 거제",
   "산업단지 출장과 주거 밀집 지역이 함께 운영되는 권역입니다.", "광역 이동 시간에 따라 가능 시간이 달라질 수 있습니다."),
  ("jeju", "제주", "제주특별자치도", "제주시·서귀포", "제주시, 서귀포시, 애월, 표선, 성산",
   "휴양 일정에 맞춘 숙소 방문 케어 문의가 가장 많습니다.", "성수기 숙소 방문은 사전 예약이 강력히 권장됩니다."),
]

for slug, name, full, hot, areas, pattern, extra in REGIONS:
    add(
        path=f"area/{slug}/index.html",
        url=f"/area/{slug}/",
        slug=f"area-{slug}",
        title=f"{name} 출장마사지 예약 정보 | 가격·코스·이용 전 확인사항 | 바로GO",
        description=f"{name} 출장마사지 이용 전 확인하면 좋은 예약 방법, 가격 기준, 서비스 유형, 주의사항을 정리했습니다. 처음 이용하는 분도 쉽게 이해할 수 있는 지역별 안내입니다.",
        h1=f"{name} 출장마사지 예약 전 알아둘 이용 정보",
        intro=f'<p class="lede">{full} 지역에서 출장마사지를 이용하기 전 확인하면 좋은 정보를 정리했습니다. 예약 가능 시간대, 자주 선택되는 서비스 유형, 이동 가능 권역, 가격이 달라지는 기준, 처음 이용자가 자주 묻는 질문을 한 번에 살펴보세요.</p>',
        breadcrumbs=[("홈", "/"), ("지역별 찾기", "/area/"), (name, f"/area/{slug}/")],
        body=f"""
<section class="block">
<h2>{name} 지역 이용 특징</h2>
<p>{name}에서는 주로 <strong>{hot}</strong> 권역에서 방문 마사지가 자주 문의됩니다. {pattern} {extra}</p>
</section>

<section class="block">
<h2>예약 가능 시간대</h2>
<p>일반적으로 평일 오전 10시부터 익일 새벽 시간대까지 안내가 가능하며, 시간대와 권역에 따라 가능 여부가 달라집니다. 정확한 가능 시간은 상담 단계에서 확인하실 수 있습니다.</p>
<ul class="check-list">
<li>평일 낮 : 가정·사무실 방문 케어 중심</li>
<li>평일 저녁~밤 : 가장 문의가 많은 시간대</li>
<li>심야~새벽 : 호텔 방문 케어 비중이 높음</li>
<li>주말·공휴일 : 권역별 가능 시간 사전 확인 권장</li>
</ul>
</section>

<section class="block">
<h2>많이 찾는 서비스 유형</h2>
<ul class="check-list">
<li><a href="/service/swedish/">스웨디시 마사지</a> — 오일 기반 전신 이완 케어</li>
<li><a href="/service/aroma/">아로마 마사지</a> — 향과 함께 진행하는 이완 케어</li>
<li><a href="/service/hometai/">홈타이</a> — 스트레칭 결합 케어</li>
<li><a href="/service/sports-massage/">스포츠 마사지</a> — 컨디션 관리 목적의 케어</li>
</ul>
</section>

<section class="block">
<h2>이동 가능 주변 지역</h2>
<p>{name}에서는 일반적으로 <strong>{areas}</strong> 권역까지 안내됩니다. 광역 이동 시 추가 이동료가 발생할 수 있으며, 시간대에 따라 가능 여부가 달라집니다.</p>
</section>

<section class="block">
<h2>가격이 달라지는 기준</h2>
<p>{name}에서도 전국 공통 기준이 적용됩니다. 코스 길이(60·90·120분), 서비스 유형, 시간대, 이동 거리에 따라 비용이 달라집니다. 자세한 기준은 <a href="/reservation/price/">가격 및 코스 안내</a> 페이지에서 확인하실 수 있습니다.</p>
</section>

<section class="block">
<h2>처음 이용자 주의사항</h2>
<ul class="check-list">
<li>예약 단계에서 가격·소요 시간을 반드시 확인해 주세요.</li>
<li>건강 상태에 따라 이용을 권하지 않는 경우가 있습니다.</li>
<li>과도한 음주 후 이용은 자제 부탁드립니다.</li>
<li>불편 상황은 <a href="/support/report/">불편 신고</a>로 접수 가능합니다.</li>
</ul>
</section>

<section class="block">
<h2>{name} 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>{name} 외곽 지역도 이용 가능한가요?</summary><p>{areas} 권역까지 일반적으로 안내됩니다. 외곽 지역은 시간대와 이동 거리에 따라 가능 여부가 달라집니다.</p></details>
<details><summary>호텔에서도 받을 수 있나요?</summary><p>네, 가능합니다. 호텔 방문은 객실 호수와 체크인 정보를 함께 확인합니다. 자세한 안내는 <a href="/service/hotel-massage/">호텔 방문 마사지</a> 페이지를 참고하세요.</p></details>
<details><summary>심야 시간대도 가능한가요?</summary><p>{name}은 심야 시간대에도 일부 권역에서 이용이 가능합니다. 정확한 가능 시간은 상담 단계에서 확인하실 수 있습니다.</p></details>
</div>
</section>
""",
        related=f'<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/reservation/how-to-book/">예약 방법</a></li><li><a href="/reservation/price/">가격 및 코스 안내</a></li><li><a href="/guide/safe-reservation/">안전한 예약 확인 방법</a></li></ul></aside>',
    )

# ---------- service hub ----------
add(
  path="service/index.html",
  url="/service/",
  slug="service-hub",
  title="방문 마사지 서비스 안내 | 출장마사지·홈타이·스웨디시 외 | 바로GO",
  description="출장마사지·홈타이·스웨디시·아로마·스포츠·커플·호텔·기업 방문 마사지 등 서비스 유형별 특징과 추천 대상, 진행 방식을 한눈에 비교하세요.",
  h1="서비스 안내",
  intro='<p class="lede">방문 마사지는 목적과 진행 방식이 서로 다릅니다. 이 페이지에서는 각 서비스의 특징과 추천 대상을 비교해 두었으니, 본인의 컨디션과 일정에 맞는 유형을 골라 상세 페이지로 이동해 보세요.</p>',
  breadcrumbs=[("홈", "/"), ("서비스 안내", "/service/")],
  body="""
<section class="block">
<ul class="service-grid">
<li><h3><a href="/service/business-trip-massage/">출장마사지</a></h3><p>지정한 장소로 관리사가 방문해 진행하는 일반 방문 케어입니다.</p></li>
<li><h3><a href="/service/hometai/">홈타이</a></h3><p>타이 전통 기법 기반의 스트레칭·지압 결합 케어입니다.</p></li>
<li><h3><a href="/service/swedish/">스웨디시</a></h3><p>오일을 이용한 부드러운 압의 전신 이완 케어입니다.</p></li>
<li><h3><a href="/service/aroma/">아로마</a></h3><p>아로마 오일의 향과 함께 진행하는 이완 중심 케어입니다.</p></li>
<li><h3><a href="/service/sports-massage/">스포츠 마사지</a></h3><p>운동 전후 컨디션 관리에 자주 선택되는 케어입니다.</p></li>
<li><h3><a href="/service/couple-massage/">커플 마사지</a></h3><p>두 명이 동시에 진행할 수 있도록 안내되는 옵션입니다.</p></li>
<li><h3><a href="/service/hotel-massage/">호텔 방문</a></h3><p>출장·여행 중 숙소에서 받는 방문 케어입니다.</p></li>
<li><h3><a href="/service/office-massage/">기업·사무실 방문</a></h3><p>임직원 복지 차원의 단체 방문 케어입니다.</p></li>
</ul>
</section>
""",
)

SERVICES = [
  ("business-trip-massage", "출장마사지", "지정한 장소로 관리사가 직접 방문해 진행하는 가장 일반적인 방문 케어입니다.",
   ["가정·숙소·사무실 등 원하는 장소에서 이용", "이동 동선과 시간을 자유롭게 조정", "60·90·120분 코스 중 선택"],
   ["과로·장시간 근무로 피로가 누적된 분", "직접 매장을 방문하기 어려운 분", "출장·여행 중 숙소에서 짧게 휴식이 필요한 분"]),
  ("hometai", "홈타이", "타이 전통 기법 기반의 스트레칭과 지압을 결합한 방문 케어입니다.",
   ["관절 가동 범위를 활용한 스트레칭 동작", "오일 사용 없이 진행 (옷을 착용한 상태)", "전신 컨디션 정비 목적"],
   ["오일이 부담스러운 분", "어깨·골반 주변 가동성에 관심이 있는 분", "활동량이 적어 몸이 굳은 느낌이 드는 분"]),
  ("swedish", "스웨디시 마사지", "오일을 사용해 부드러운 압으로 전신을 이완하는 가장 대중적인 방문 케어입니다.",
   ["전신을 길게 쓸어 올리는 기본 동작 중심", "오일 사용으로 마찰 최소화", "60·90·120분 코스 모두 선호되는 유형"],
   ["피로 회복과 이완을 목적으로 하는 분", "처음 방문 마사지를 경험하는 분", "가벼운 압을 선호하는 분"]),
  ("aroma", "아로마 마사지", "아로마 오일의 향과 부드러운 압을 함께 사용하는 이완 중심 케어입니다.",
   ["향 선택은 일반적으로 사전에 안내", "스웨디시와 유사한 압, 강한 압은 사용하지 않음", "수면 전 휴식 시간대에 자주 선택"],
   ["스트레스로 인한 긴장을 풀고 싶은 분", "잠들기 전 이완을 원하는 분", "강한 압이 부담스러운 분"]),
  ("sports-massage", "스포츠 마사지", "운동 전후의 컨디션 관리, 근육 피로 해소를 목적으로 진행하는 케어입니다.",
   ["근육 결을 따라 압을 분배", "전신 또는 특정 부위 집중 코스", "강한 압을 선호하는 분에게도 안내 가능"],
   ["주 1회 이상 운동을 하는 분", "특정 부위 근육 피로가 누적된 분", "오일 사용 비중을 줄이고 싶은 분"]),
  ("couple-massage", "커플 마사지", "두 명이 같은 시간대에 진행할 수 있도록 안내되는 옵션입니다.",
   ["동시간대 진행을 위해 관리사 2인이 함께 방문", "동일한 시간·코스 선택을 기본 권장", "장소는 한 객실 또는 한 공간"],
   ["기념일·휴가 일정에 함께 받고 싶은 분", "같은 시간에 케어를 받고 싶은 가족·연인"]),
  ("hotel-massage", "호텔 방문 마사지", "출장·여행 일정 중 숙소에서 진행되는 방문 케어입니다.",
   ["객실 호수와 체크인 정보 사전 확인", "공간 특성에 맞춘 진행 방식 안내", "심야 시간대 문의가 많은 유형"],
   ["출장 중 짧은 휴식이 필요한 분", "이동 동선을 최소화하고 싶은 여행객", "비행 일정 전후 피로 회복이 필요한 분"]),
  ("office-massage", "기업·사무실 방문 마사지", "임직원 복지 차원에서 단체로 진행되는 방문 케어입니다.",
   ["사전 일정·인원 조율 필수", "사내 공간 또는 별도 공간에서 진행", "10분·20분 단위 짧은 케어 옵션도 안내 가능"],
   ["임직원 복지 프로그램 운영 담당자", "분기별 단체 케어를 검토 중인 기업", "이벤트성으로 단체 케어를 진행하려는 부서"]),
]

for slug, name, summary, features, audience in SERVICES:
    feat_html = "".join(f"<li>{x}</li>" for x in features)
    aud_html = "".join(f"<li>{x}</li>" for x in audience)
    add(
        path=f"service/{slug}/index.html",
        url=f"/service/{slug}/",
        slug=f"service-{slug}",
        title=f"{name} 안내 | 특징·추천 대상·진행 방식 | 바로GO",
        description=f"{name}의 특징과 추천 대상, 진행 방식, 소요 시간, 이용 전 주의사항을 정리했습니다. 건전하고 안전한 방문 마사지 이용 안내입니다.",
        h1=f"{name} 안내",
        intro=f'<p class="lede">{summary}</p>',
        breadcrumbs=[("홈", "/"), ("서비스 안내", "/service/"), (name, f"/service/{slug}/")],
        body=f"""
<section class="block">
<h2>주요 특징</h2>
<ul class="check-list">{feat_html}</ul>
</section>
<section class="block">
<h2>추천 대상</h2>
<ul class="check-list">{aud_html}</ul>
</section>
<section class="block">
<h2>진행 방식</h2>
<ol class="steps">
<li><strong>예약 확정</strong><p>지역·시간·코스가 확정되면 관리사 일정을 배정합니다.</p></li>
<li><strong>방문 안내</strong><p>도착 예정 시간을 사전에 안내합니다.</p></li>
<li><strong>코스 진행</strong><p>선택한 코스 시간 내에서 진행합니다.</p></li>
<li><strong>마무리 안내</strong><p>이용 후 권장 사항(수분 섭취 등)을 안내합니다.</p></li>
</ol>
</section>
<section class="block">
<h2>소요 시간 안내</h2>
<p>일반적으로 60분 / 90분 / 120분 코스로 운영됩니다. 이동·준비·마무리 시간을 포함해 예정 시간보다 여유 있게 일정을 잡아두시는 것을 권장합니다.</p>
</section>
<section class="block">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>고열·급성 통증·외상 등 신체 상태에 따라 이용을 권하지 않는 경우가 있습니다.</li>
<li>식사 직후·과도한 음주 후 이용은 자제 부탁드립니다.</li>
<li>임신 중이거나 특정 질환이 있는 경우 예약 단계에서 미리 알려주세요.</li>
<li>특정 부위의 피부 트러블이 있는 경우 해당 부위를 제외하고 진행할 수 있습니다.</li>
</ul>
<p class="muted">방문 마사지는 의료 행위가 아니며, 치료 효과를 보장하지 않습니다.</p>
</section>
""",
        related=f'<aside class="related"><h2>관련 안내</h2><ul><li><a href="/reservation/price/">가격 및 코스 안내</a></li><li><a href="/reservation/how-to-book/">예약 방법</a></li><li><a href="/guide/first-time-massage/">처음 이용 전 알아둘 점</a></li></ul></aside>',
    )

# ---------- Reservation pages ----------
add(
  path="reservation/index.html", url="/reservation/", slug="reservation-hub",
  title="예약 안내 | 방법·가격·취소·결제 | 바로GO",
  description="출장마사지 예약 방법, 가격 기준, 이용 전 확인사항, 취소·환불 규정, 결제 안내를 한곳에 정리했습니다.",
  h1="예약 안내",
  intro='<p class="lede">예약 과정에서 자주 묻는 정보를 5개 페이지로 분리해 두었습니다. 처음 이용하시는 분은 예약 방법부터 순서대로 확인하시면 좋습니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/")],
  body="""
<section class="block">
<ul class="service-grid">
<li><h3><a href="/reservation/how-to-book/">예약 방법</a></h3><p>지역·서비스 선택부터 확정까지 5단계 안내</p></li>
<li><h3><a href="/reservation/price/">가격 및 코스 안내</a></h3><p>코스 길이·시간대·이동 거리에 따른 비용 기준</p></li>
<li><h3><a href="/reservation/check-before-use/">이용 전 확인사항</a></h3><p>건강 상태·공간 조건 등 사전 확인 항목</p></li>
<li><h3><a href="/reservation/cancel-refund/">취소·환불 규정</a></h3><p>시간대별 취소 가능 기준과 환불 규정</p></li>
<li><h3><a href="/reservation/payment/">결제 안내</a></h3><p>결제 방법과 결제 시점, 영수증 발급 안내</p></li>
</ul>
</section>
""",
)

add(
  path="reservation/how-to-book/index.html", url="/reservation/how-to-book/", slug="how-to-book",
  title="출장마사지 예약 방법 | 5단계 안내 | 바로GO",
  description="지역 선택부터 예약 확정까지 5단계로 진행되는 출장마사지 예약 절차를 정리했습니다. 처음 이용해도 어렵지 않은 표준 절차 안내입니다.",
  h1="예약 방법",
  intro='<p class="lede">바로GO 예약은 다음 5단계로 진행됩니다. 모든 지역과 서비스에 공통으로 적용되는 표준 절차입니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/"),("예약 방법","/reservation/how-to-book/")],
  body="""
<section class="block">
<ol class="steps">
<li><strong>1. 지역 확인</strong><p>이용을 원하는 지역이 서비스 가능 권역인지 확인합니다. <a href="/area/">지역별 찾기</a>에서 시·도 단위 안내를 먼저 살펴보세요.</p></li>
<li><strong>2. 서비스 선택</strong><p>스웨디시·아로마·홈타이 등 원하는 서비스 유형과 코스 길이(60·90·120분)를 선택합니다.</p></li>
<li><strong>3. 예약 시간 확인</strong><p>해당 시간대의 가능 여부를 확인합니다. 시간대·이동 거리에 따라 가능 여부가 달라질 수 있습니다.</p></li>
<li><strong>4. 이용 조건 안내</strong><p>가격, 결제 방법, 취소 기준, 사전 확인사항을 안내드립니다. 동의 후 예약이 확정됩니다.</p></li>
<li><strong>5. 방문·진행</strong><p>도착 예정 시간을 사전에 안내드리며, 예약된 장소에서 코스를 진행합니다.</p></li>
</ol>
</section>
<section class="block">
<h2>예약 전 한 번 더 확인</h2>
<ul class="check-list">
<li>이동 거리에 따라 예약 가능 시간이 달라질 수 있습니다.</li>
<li>코스 시간 외에 준비·마무리 시간을 함께 고려해 주세요.</li>
<li>호텔 방문은 객실 호수와 체크인 정보가 필요합니다.</li>
</ul>
</section>
""",
)

add(
  path="reservation/price/index.html", url="/reservation/price/", slug="price",
  title="가격 및 코스 안내 | 코스·시간·이동 기준 | 바로GO",
  description="출장마사지 가격이 달라지는 기준(코스 길이·서비스 유형·시간대·이동 거리)을 정리했습니다. 정확한 비용은 예약 단계에서 안내됩니다.",
  h1="가격 및 코스 안내",
  intro='<p class="lede">바로GO는 전국 단일가가 아닌, 코스·시간·이동 기반의 안내를 사용합니다. 정확한 금액은 상담 단계에서 미리 안내되므로 예약 후 추가로 결정되는 비용은 없습니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/"),("가격 및 코스","/reservation/price/")],
  body="""
<section class="block">
<h2>가격이 달라지는 4가지 기준</h2>
<ol class="steps">
<li><strong>코스 길이</strong><p>60 / 90 / 120분 기준으로 비용이 구분됩니다.</p></li>
<li><strong>서비스 유형</strong><p>스웨디시·아로마·홈타이·스포츠 등 유형에 따라 기준이 다릅니다.</p></li>
<li><strong>시간대</strong><p>심야 시간대는 추가 비용이 발생할 수 있습니다.</p></li>
<li><strong>이동 거리</strong><p>광역 이동·외곽 지역은 이동료가 추가될 수 있습니다.</p></li>
</ol>
</section>
<section class="block">
<h2>가격 안내 원칙</h2>
<ul class="check-list">
<li>예약 확정 전 모든 비용을 미리 안내합니다.</li>
<li>예약 이후 사전 동의 없는 추가 비용은 발생하지 않습니다.</li>
<li>"무조건 1위", "최저가 보장"과 같은 표현은 사용하지 않습니다.</li>
</ul>
</section>
<section class="block">
<h2>참고 안내</h2>
<p>정확한 비용은 지역·시간·코스 조합에 따라 달라지므로 본 페이지에는 고정 금액을 표기하지 않습니다. 상담 시 안내되는 금액 기준으로 결제하시면 됩니다. 결제 방법은 <a href="/reservation/payment/">결제 안내</a> 페이지를 참고하세요.</p>
</section>
""",
)

add(
  path="reservation/check-before-use/index.html", url="/reservation/check-before-use/", slug="check-before-use",
  title="이용 전 확인사항 | 건강·공간·시간 점검 | 바로GO",
  description="방문 마사지 예약 전 확인하면 좋은 건강 상태, 공간 조건, 시간 일정을 정리했습니다. 안전하고 만족스러운 이용을 위한 점검 항목입니다.",
  h1="이용 전 확인사항",
  intro='<p class="lede">방문 마사지는 컨디션 회복과 휴식을 목적으로 진행되는 케어입니다. 이용 전 아래 항목을 한 번씩 확인하시면 더 만족스러운 시간을 보내실 수 있습니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/"),("이용 전 확인사항","/reservation/check-before-use/")],
  body="""
<section class="block">
<h2>건강 상태 점검</h2>
<ul class="check-list">
<li>고열·급성 통증·외상이 있는 경우 이용을 권하지 않습니다.</li>
<li>임신 중이거나 특정 질환이 있다면 예약 단계에서 미리 알려주세요.</li>
<li>특정 부위 피부 트러블이 있다면 해당 부위 진행을 조정할 수 있습니다.</li>
</ul>
</section>
<section class="block">
<h2>공간 조건 점검</h2>
<ul class="check-list">
<li>최소한 매트 또는 침구를 펼칠 수 있는 공간이 필요합니다.</li>
<li>호텔 방문은 객실 호수와 체크인 정보를 확인해 주세요.</li>
<li>반려동물이 있다면 별도 공간으로 이동 부탁드립니다.</li>
</ul>
</section>
<section class="block">
<h2>시간 일정 점검</h2>
<ul class="check-list">
<li>코스 시간 외에 준비·마무리 시간을 함께 고려해 주세요.</li>
<li>식사 직후·과도한 음주 후 이용은 자제 부탁드립니다.</li>
<li>예약 시간 변경이 필요하다면 가능한 한 빠르게 알려주세요.</li>
</ul>
</section>
""",
)

add(
  path="reservation/cancel-refund/index.html", url="/reservation/cancel-refund/", slug="cancel-refund",
  title="취소·환불 규정 | 시간대별 기준 | 바로GO",
  description="출장마사지 예약 취소 및 환불 규정을 시간대별로 정리했습니다. 출발 전·도착 전·도착 후 단계별 기준 안내입니다.",
  h1="취소·환불 규정",
  intro='<p class="lede">예약된 일정의 변경·취소는 시간대에 따라 처리 기준이 다릅니다. 아래 기준은 일반적인 운영 원칙이며, 천재지변 등 불가항력 상황은 별도 협의됩니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/"),("취소·환불","/reservation/cancel-refund/")],
  body="""
<section class="block">
<h2>일반 취소 기준</h2>
<ul class="check-list">
<li><strong>예약 확정 후 출발 전</strong> : 전액 환불 가능합니다.</li>
<li><strong>관리사 출발 이후</strong> : 이동료에 해당하는 비용이 발생할 수 있습니다.</li>
<li><strong>도착 이후 취소</strong> : 코스 진행 여부와 관계없이 일부 비용이 발생할 수 있습니다.</li>
</ul>
</section>
<section class="block">
<h2>일정 변경</h2>
<p>가능한 한 예약 24시간 전까지 변경 요청을 부탁드립니다. 당일 변경은 가능 시간에 따라 안내가 달라질 수 있습니다.</p>
</section>
<section class="block">
<h2>환불 처리</h2>
<p>환불은 결제 수단에 따라 처리 기간이 달라질 수 있습니다. 카드 결제는 카드사 영업일 기준 3~5일 정도 소요됩니다.</p>
</section>
""",
)

add(
  path="reservation/payment/index.html", url="/reservation/payment/", slug="payment",
  title="결제 안내 | 결제 방법·시점·영수증 | 바로GO",
  description="바로GO 결제 방법, 결제 시점, 영수증 발급 안내를 정리했습니다.",
  h1="결제 안내",
  intro='<p class="lede">결제는 예약 확정 단계에서 안내된 금액으로 진행되며, 사전 동의 없는 추가 결제는 발생하지 않습니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/"),("결제 안내","/reservation/payment/")],
  body="""
<section class="block">
<h2>결제 방법</h2>
<ul class="check-list">
<li>카드 결제(국내 주요 카드사)</li>
<li>계좌 이체</li>
<li>일부 코스의 경우 사전 결제 안내</li>
</ul>
</section>
<section class="block">
<h2>결제 시점</h2>
<p>일반적으로 코스 진행 직전 또는 직후 결제가 진행됩니다. 호텔 방문 등 일부 케이스는 사전 결제가 진행될 수 있습니다.</p>
</section>
<section class="block">
<h2>영수증·증빙</h2>
<p>현금영수증 발급, 카드 매출전표 모두 정상 발급됩니다. 사업자 증빙이 필요한 경우 예약 단계에서 미리 알려주세요.</p>
</section>
""",
)

# ---------- Review pages ----------
add(
  path="review/index.html", url="/review/", slug="review-hub",
  title="실제 이용후기 | 예약 경험·응대·시간 준수 중심 | 바로GO",
  description="바로GO 이용 고객이 남긴 예약 경험을 정리합니다. 과장된 만족 후기보다 예약 과정, 응대, 시간 준수, 설명의 충분함을 중심으로 합니다.",
  h1="실제 이용후기",
  intro='<p class="lede">후기는 "예약 과정이 명확했는가, 시간이 잘 지켜졌는가, 설명이 충분했는가, 청결 기준이 지켜졌는가"를 중심으로 정리합니다. 광고성·과장 표현은 후기에서 제외합니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/")],
  body="""
<section class="block">
<div class="review-grid">
<article class="review-card"><p class="review-meta">서울 · 첫 이용 · 90분 스웨디시</p><p>"예약 시간보다 5분 정도 일찍 도착했고, 진행 전 코스와 주의사항을 다시 한번 설명해 주셔서 처음이라 걱정했던 부분이 줄었습니다."</p></article>
<article class="review-card"><p class="review-meta">부산 · 호텔 방문 · 60분 아로마</p><p>"출장 일정 중간에 시간을 비워서 호텔에서 받았는데, 위치 확인과 도착 안내가 명확해 동선에 무리가 없었습니다."</p></article>
<article class="review-card"><p class="review-meta">경기 · 재이용 · 120분 홈타이</p><p>"가격 기준이 예약 단계에서 명확하게 안내되어 추가 비용 걱정 없이 진행했습니다."</p></article>
<article class="review-card"><p class="review-meta">제주 · 휴양 · 90분 아로마</p><p>"성수기였는데도 일정 조율이 빨라서 다음 일정에 차질이 없었습니다."</p></article>
</div>
</section>
<section class="block">
<h2>후기 운영 원칙</h2>
<ul class="check-list">
<li>광고성 표현, "최고", "1위" 같은 과장 표현은 노출하지 않습니다.</li>
<li>이름·연락처는 게시하지 않으며, 지역·코스·시간 등 일반 정보만 노출합니다.</li>
<li>허위 후기로 확인되면 즉시 삭제됩니다.</li>
</ul>
</section>
""",
  related='<aside class="related"><h2>관련 안내</h2><ul><li><a href="/review/first-time/">처음 이용 고객 후기</a></li><li><a href="/review/reservation-case/">예약 사례</a></li><li><a href="/review/area/">지역별 후기 모음</a></li></ul></aside>',
)

add(
  path="review/reservation-case/index.html", url="/review/reservation-case/", slug="review-case",
  title="예약 사례 | 상담 과정·일정 조율 중심 | 바로GO",
  description="실제 예약 상담 단계에서 자주 나오는 일정 조율·이동 거리·코스 변경 사례를 정리했습니다.",
  h1="예약 사례",
  intro='<p class="lede">예약 단계에서 가장 자주 나오는 상담 패턴을 정리했습니다. 처음 이용하시는 분이 사전 준비하시는 데 도움이 될 수 있습니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/"),("예약 사례","/review/reservation-case/")],
  body="""
<section class="block">
<h2>대표 예약 사례</h2>
<ul class="check-list">
<li><strong>호텔 일정 + 야간 코스</strong> : 체크인 후 늦은 시간 60분 케어를 자주 선택하는 패턴입니다.</li>
<li><strong>광역 이동 + 시간 변경</strong> : 권역 외곽으로 이동 시 일정이 30분~1시간 늦춰지는 경우가 자주 있습니다.</li>
<li><strong>코스 시간 연장</strong> : 진행 중에 코스를 60분 → 90분으로 연장 요청하는 사례입니다. 일정에 여유가 있다면 가능합니다.</li>
</ul>
</section>
""",
)

add(
  path="review/first-time/index.html", url="/review/first-time/", slug="review-first-time",
  title="처음 이용 고객 후기 | 첫 방문 마사지 경험 | 바로GO",
  description="처음 출장마사지를 이용한 고객이 남긴 후기를 모았습니다. 첫 이용 시 자주 궁금해하는 점을 함께 정리했습니다.",
  h1="처음 이용 고객 후기",
  intro='<p class="lede">"이번이 처음입니다"라고 알려주신 분들의 후기를 모은 페이지입니다. 첫 이용 시 자주 묻는 질문도 함께 정리했습니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/"),("처음 이용","/review/first-time/")],
  body="""
<section class="block">
<div class="review-grid">
<article class="review-card"><p class="review-meta">서울 · 첫 이용 · 60분 스웨디시</p><p>"방문 마사지가 처음이라 분위기가 어색할까 걱정했는데, 진행 전 충분히 설명해 주셔서 편하게 받았습니다."</p></article>
<article class="review-card"><p class="review-meta">대전 · 첫 이용 · 90분 홈타이</p><p>"오일이 부담스러워 홈타이를 선택했는데, 옷 입은 상태로 진행돼서 더 편했습니다."</p></article>
</div>
</section>
<section class="block">
<h2>첫 이용 시 자주 묻는 질문</h2>
<div class="faq">
<details><summary>옷은 어떻게 입어야 하나요?</summary><p>코스에 따라 다릅니다. 오일을 사용하는 경우는 일회용 의류 또는 편한 의류를 안내드리고, 홈타이의 경우는 본인의 편한 의류를 그대로 입은 채 진행합니다.</p></details>
<details><summary>관리사 분께 따로 준비할 것이 있나요?</summary><p>별도로 준비하실 것은 없습니다. 매트와 오일 등 도구는 관리사가 모두 지참합니다.</p></details>
</div>
</section>
""",
)

add(
  path="review/area/index.html", url="/review/area/", slug="review-area",
  title="지역별 후기 모음 | 시·도별 이용 패턴 | 바로GO",
  description="지역별로 어떤 시간대·코스·서비스가 자주 이용되는지 지역별 후기 패턴을 정리했습니다.",
  h1="지역별 후기 모음",
  intro='<p class="lede">시·도별로 자주 선택되는 시간대와 코스 패턴이 다릅니다. 권역별 사용 경향을 짧게 정리했습니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/"),("지역별 후기","/review/area/")],
  body="""
<section class="block">
<ul class="check-list">
<li><strong>서울·경기</strong> : 평일 야간 호텔 방문 케어 비중이 높습니다.</li>
<li><strong>부산·제주</strong> : 휴양·관광 일정과 맞물린 호텔 방문 케어가 많습니다.</li>
<li><strong>대전·세종</strong> : 평일 저녁 가정 방문 케어가 자주 이용됩니다.</li>
<li><strong>충남·경북</strong> : 산업단지 출장 일정과 맞물린 야간 호텔 방문이 자주 발생합니다.</li>
</ul>
</section>
""",
)

# ---------- Guide pages ----------
GUIDES = [
  ("what-is-business-trip-massage", "출장마사지란?", "출장마사지의 정의와 방문 케어의 일반적인 종류, 매장형 마사지와의 차이를 정리했습니다.",
   "출장마사지는 관리사가 고객이 지정한 장소(가정·숙소·사무실 등)로 방문해 진행하는 마사지 서비스입니다. 매장 방문이 어렵거나 일정상 이동을 최소화하고 싶은 경우에 자주 선택됩니다.",
   [("매장형 마사지와의 차이", "장소·이동·예약 방식이 다릅니다. 출장 케어는 관리사가 이동하므로 일정 조율이 핵심입니다."),
    ("일반적인 종류", "스웨디시·아로마·홈타이·스포츠·커플 등이 있으며, 호텔/사무실 방문 등 공간별 분류도 있습니다."),
    ("주의할 점", "방문 마사지는 의료 행위가 아니며, 치료 효과를 보장하지 않습니다. 건강 상태에 따른 주의가 필요합니다.")]),
  ("massage-before-after", "마사지 전후 주의사항", "마사지 전과 후에 피하면 좋은 행동, 권장 행동을 정리했습니다.",
   "방문 마사지의 효과를 좀 더 잘 느끼기 위해서는 이용 전후에 신경 써야 할 부분이 있습니다.",
   [("이용 전 피해야 할 것", "식사 직후·과도한 음주·과한 운동 직후는 자제합니다."),
    ("이용 후 권장 사항", "수분 충분히 섭취, 무리한 활동 피하기, 충분한 수면을 권장합니다."),
    ("이상 반응 시", "이상한 통증, 어지러움 등이 발생하면 무리하지 말고 휴식을 취하고 필요 시 의료기관 상담을 권장합니다.")]),
  ("aroma-vs-swedish", "아로마와 스웨디시 차이", "두 서비스의 진행 방식, 추천 대상, 사용 도구 차이를 비교했습니다.",
   "아로마와 스웨디시는 비슷해 보이지만 진행 방식과 목적에 차이가 있습니다.",
   [("진행 방식", "스웨디시는 오일을 사용한 부드러운 압의 전신 케어, 아로마는 향과 함께 진행하는 이완 중심 케어입니다."),
    ("추천 대상", "피로 회복 목적이 크다면 스웨디시, 정신적 긴장 완화 목적이 크다면 아로마가 자주 선택됩니다."),
    ("선택 기준", "향에 민감하다면 스웨디시가, 잠들기 전 이완이 필요하다면 아로마가 적합할 수 있습니다.")]),
  ("first-time-massage", "처음 이용 전 알아둘 점", "방문 마사지를 처음 이용하실 때 사전에 점검하면 좋은 항목을 정리했습니다.",
   "처음 방문 마사지를 이용하시는 분들은 다음 5가지를 사전에 점검하면 좋습니다.",
   [("코스 선택", "60분은 처음 이용에 무난한 길이입니다. 처음부터 120분을 잡지 않아도 됩니다."),
    ("공간 점검", "매트를 펼칠 정도의 공간이 필요합니다. 호텔 객실의 경우 침대 공간이 활용됩니다."),
    ("의류 안내", "오일 사용 코스는 일회용 의류 또는 편한 의류를 안내합니다."),
    ("결제 시점", "보통 코스 직전·직후 결제됩니다. 호텔 방문은 사전 결제될 수도 있습니다."),
    ("주의 사항 공유", "특정 질환·임신·외상 등이 있다면 반드시 사전에 알려주세요.")]),
  ("massage-price-standard", "출장마사지 가격이 달라지는 이유", "방문 마사지 가격은 어떤 요소에 의해 달라지는지 분류해 설명합니다.",
   "전국 단일가가 아닌, 4가지 변수로 비용이 정해집니다.",
   [("코스 길이", "60·90·120분 등 시간 길이에 따라 기본 비용이 다릅니다."),
    ("서비스 유형", "스웨디시·아로마·홈타이·스포츠 등 유형에 따라 기준이 다릅니다."),
    ("시간대", "심야 시간대는 추가 비용이 발생할 수 있습니다."),
    ("이동 거리", "광역 이동·외곽 지역은 이동료가 추가될 수 있습니다.")]),
  ("safe-reservation", "안전한 예약 확인 방법", "안전하게 방문 마사지를 이용하기 위해 사전에 확인하면 좋은 항목을 정리했습니다.",
   "온라인 검색만으로는 안전 여부를 판단하기 어렵습니다. 다음 5가지 점검 항목을 확인하시면 좋습니다.",
   [("사업자 정보 명시", "운영 사업자명·대표자·연락처가 공개되어 있는지 확인합니다."),
    ("가격 사전 공개", "예약 전 가격과 코스, 추가 비용 기준이 명확한지 확인합니다."),
    ("취소·환불 규정 명시", "취소·환불 규정이 별도 페이지로 존재하는지 확인합니다."),
    ("주의사항 안내", "건강 상태·공간 조건 등 주의사항이 안내되는지 확인합니다."),
    ("자극적 광고 표현", "과장된 표현, 자극적인 표현이 많은 사이트는 피하는 것이 좋습니다.")]),
]

# guide hub
add(
  path="guide/index.html", url="/guide/", slug="guide-hub",
  title="마사지 정보 | 가이드·비교·주의사항 | 바로GO",
  description="출장마사지를 처음 이용하시는 분이 알면 좋은 정보를 정리했습니다. 정의, 종류, 가격 기준, 안전 확인 방법까지.",
  h1="마사지 정보",
  intro='<p class="lede">방문 마사지를 처음 이용하시거나, 좀 더 안전하게 이용하고 싶은 분들을 위한 정보 페이지입니다.</p>',
  breadcrumbs=[("홈","/"),("마사지 정보","/guide/")],
  body="""
<section class="block">
<ul class="guide-grid">
<li><a href="/guide/what-is-business-trip-massage/"><h3>출장마사지란?</h3><p>방문 마사지의 정의와 종류</p></a></li>
<li><a href="/guide/massage-before-after/"><h3>마사지 전후 주의사항</h3><p>이용 전·후 권장 사항</p></a></li>
<li><a href="/guide/aroma-vs-swedish/"><h3>아로마와 스웨디시 차이</h3><p>두 서비스 비교</p></a></li>
<li><a href="/guide/first-time-massage/"><h3>처음 이용 전 알아둘 점</h3><p>첫 이용 사전 점검</p></a></li>
<li><a href="/guide/massage-price-standard/"><h3>가격이 달라지는 이유</h3><p>비용 결정 요소</p></a></li>
<li><a href="/guide/safe-reservation/"><h3>안전한 예약 확인 방법</h3><p>업체 점검 5가지</p></a></li>
</ul>
</section>
""",
)

for slug, name, desc, lede, sections in GUIDES:
    sec_html = "".join(f'<section class="block"><h2>{t}</h2><p>{c}</p></section>' for t, c in sections)
    add(
        path=f"guide/{slug}/index.html",
        url=f"/guide/{slug}/",
        slug=f"guide-{slug}",
        title=f"{name} | 바로GO 마사지 정보",
        description=desc,
        h1=name,
        intro=f'<p class="lede">{lede}</p>',
        breadcrumbs=[("홈","/"),("마사지 정보","/guide/"),(name,f"/guide/{slug}/")],
        og_type="article",
        body=sec_html + """
<section class="block muted">
<p><small>※ 본 정보는 일반적인 안내이며, 의료 행위나 의학적 조언이 아닙니다. 건강 상태와 관련된 결정은 의료 전문가와 상담하시기 바랍니다.</small></p>
</section>
""",
        related='<aside class="related"><h2>관련 글</h2><ul><li><a href="/reservation/how-to-book/">예약 방법</a></li><li><a href="/reservation/price/">가격 기준 안내</a></li><li><a href="/guide/safe-reservation/">안전한 예약 확인 방법</a></li></ul></aside>',
    )

# ---------- Support pages ----------
add(
  path="support/index.html", url="/support/", slug="support-hub",
  title="고객센터 | 공지·FAQ·문의·제휴·신고 | 바로GO",
  description="공지사항, 자주 묻는 질문, 문의하기, 제휴·입점 문의, 불편 신고를 한곳에 모았습니다.",
  h1="고객센터",
  intro='<p class="lede">이용 중 궁금한 점, 불편 신고, 제휴 문의를 모두 안내합니다.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/")],
  body="""
<section class="block">
<ul class="service-grid">
<li><h3><a href="/support/notice/">공지사항</a></h3><p>운영 변경·점검·정책 변경 안내</p></li>
<li><h3><a href="/support/faq/">자주 묻는 질문</a></h3><p>예약·결제·이용 관련 FAQ</p></li>
<li><h3><a href="/support/contact/">문의하기</a></h3><p>전화·이메일 문의 안내</p></li>
<li><h3><a href="/support/partnership/">제휴·입점 문의</a></h3><p>관리사·업체 제휴 안내</p></li>
<li><h3><a href="/support/report/">불편 신고</a></h3><p>이용 중 불편 사항 접수</p></li>
</ul>
</section>
""",
)

add(
  path="support/notice/index.html", url="/support/notice/", slug="notice",
  title="공지사항 | 바로GO",
  description="바로GO 운영 정책 변경, 점검 일정, 안내사항 공지 페이지입니다.",
  h1="공지사항",
  intro='<p class="lede">운영 정책 변경, 점검 일정, 중요 안내사항을 게시합니다.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/"),("공지사항","/support/notice/")],
  body="""
<section class="block">
<article class="notice-item">
<h2>바로GO 안전 이용 정책 안내</h2>
<p class="muted">바로GO 운영팀</p>
<p>바로GO는 건전한 방문 마사지 안내만 제공합니다. 불법·퇴폐 서비스 알선·중개를 하지 않으며, 관련 문의는 응대하지 않습니다. 자세한 내용은 <a href="/about/safety-policy/">안전 이용 정책</a>에서 확인하실 수 있습니다.</p>
</article>
<article class="notice-item">
<h2>개인정보 처리 방침 안내</h2>
<p class="muted">바로GO 운영팀</p>
<p>이용자 정보 보호를 위해 상담·예약 과정에서 수집되는 정보 항목과 보관 기간을 <a href="/about/privacy/">개인정보처리방침</a>에서 안내드립니다.</p>
</article>
</section>
""",
)

add(
  path="support/faq/index.html", url="/support/faq/", slug="faq",
  title="자주 묻는 질문 (FAQ) | 바로GO",
  description="바로GO 예약·결제·이용·취소·안전 이용 등 자주 묻는 질문을 모았습니다.",
  h1="자주 묻는 질문",
  intro='<p class="lede">예약·결제·이용·취소·안전 이용 카테고리로 자주 묻는 질문을 모았습니다.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/"),("FAQ","/support/faq/")],
  body="""
<section class="block">
<h2>예약</h2>
<div class="faq">
<details><summary>예약은 얼마나 미리 해야 하나요?</summary><p>당일 예약도 가능하지만, 원하는 시간대를 안정적으로 잡으려면 하루 전 예약을 권장합니다.</p></details>
<details><summary>전국 어디서나 가능한가요?</summary><p>17개 광역 시·도 단위로 안내하며, 외곽 지역은 시간대에 따라 가능 여부가 달라질 수 있습니다.</p></details>
</div>
</section>
<section class="block">
<h2>결제</h2>
<div class="faq">
<details><summary>결제 수단은 어떤 게 있나요?</summary><p>카드 결제와 계좌 이체가 가능합니다.</p></details>
<details><summary>현금영수증 발급 가능한가요?</summary><p>네, 가능합니다. 예약 단계에서 알려주시면 됩니다.</p></details>
</div>
</section>
<section class="block">
<h2>이용</h2>
<div class="faq">
<details><summary>이용 시 필요한 공간 크기는?</summary><p>매트를 펼칠 수 있는 정도면 가능합니다. 호텔 객실도 충분합니다.</p></details>
<details><summary>임신 중인데 가능한가요?</summary><p>일반 코스는 권장하지 않으며, 가능 여부는 예약 시 상담 후 안내드립니다.</p></details>
</div>
</section>
<section class="block">
<h2>안전 이용</h2>
<div class="faq">
<details><summary>불법 서비스도 안내하나요?</summary><p>아니요. 건전한 방문 마사지 안내만 제공합니다.</p></details>
<details><summary>불편한 일이 있으면 어디에 신고하나요?</summary><p><a href="/support/report/">불편 신고</a> 페이지에서 접수 가능합니다.</p></details>
</div>
</section>
""",
)

add(
  path="support/contact/index.html", url="/support/contact/", slug="contact",
  title="문의하기 | 전화·이메일 | 바로GO",
  description="바로GO 운영팀 문의 전화 및 응대 시간 안내 페이지입니다.",
  h1="문의하기",
  intro='<p class="lede">예약 외 일반 문의, 운영 문의, 개인정보 관련 문의는 아래 채널을 이용해 주세요.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/"),("문의하기","/support/contact/")],
  body="""
<section class="block">
<h2>연락처</h2>
<ul class="check-list">
<li><strong>예약 전화</strong> : <a href="tel:0508-202-4719">0508-202-4719</a></li>
<li><strong>운영 시간</strong> : 매일 10:00 ~ 익일 새벽</li>
<li><strong>주소</strong> : 경기도 파주시 청석로 268</li>
<li><strong>사업자등록번호</strong> : 815-26-00585</li>
</ul>
</section>
<section class="block">
<h2>문의 응대 원칙</h2>
<ul class="check-list">
<li>예약 외 광고·홍보 전화는 응대하지 않습니다.</li>
<li>불법·퇴폐 관련 문의에는 응답하지 않습니다.</li>
<li>고객 개인정보는 응대 후 보관 기간 내 안전하게 관리됩니다.</li>
</ul>
</section>
""",
)

add(
  path="support/partnership/index.html", url="/support/partnership/", slug="partnership",
  title="제휴·입점 문의 | 관리사·업체 협력 | 바로GO",
  description="바로GO 제휴 및 입점 문의 안내. 관리사·업체 파트너 모집 기준을 안내합니다.",
  h1="제휴·입점 문의",
  intro='<p class="lede">바로GO는 일정 기준을 충족하는 관리사 및 업체와 협력합니다.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/"),("제휴 문의","/support/partnership/")],
  body="""
<section class="block">
<h2>제휴 기준</h2>
<ul class="check-list">
<li>합법적이고 신고된 사업자 또는 프리랜서</li>
<li>방문 마사지 관련 경력과 검증 가능한 이력</li>
<li>안전 이용 정책 동의 및 가격·취소 기준 준수</li>
</ul>
</section>
<section class="block">
<h2>문의 방법</h2>
<p>제휴·입점 문의는 <a href="tel:0508-202-4719">0508-202-4719</a> 또는 별도 안내된 이메일을 통해 접수해 주세요. 접수된 문의는 영업일 기준 3일 이내 응답을 원칙으로 합니다.</p>
</section>
""",
)

add(
  path="support/report/index.html", url="/support/report/", slug="report",
  title="불편 신고 | 응대·시간·기타 문제 접수 | 바로GO",
  description="바로GO 이용 중 발생한 불편 사항을 접수받습니다. 응대·시간·결제·안전 관련 모든 신고를 진지하게 처리합니다.",
  h1="불편 신고",
  intro='<p class="lede">이용 중 불편한 일이 있었다면 주저 없이 알려주세요. 신고된 사항은 운영팀이 직접 확인합니다.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/"),("불편 신고","/support/report/")],
  body="""
<section class="block">
<h2>접수 가능한 항목</h2>
<ul class="check-list">
<li>관리사 응대 관련 문제</li>
<li>시간 지연·일정 미준수</li>
<li>가격·결제 관련 문제</li>
<li>안전 이용 정책 위반 의심 사항</li>
<li>기타 모든 불편 사항</li>
</ul>
</section>
<section class="block">
<h2>신고 방법</h2>
<p><a href="tel:0508-202-4719">0508-202-4719</a>로 전화하시거나, <a href="/support/contact/">문의하기</a> 페이지의 채널을 통해 접수해 주세요. 접수 시 가능한 한 일시·지역·코스 정보를 함께 전달해 주시면 확인이 빠릅니다.</p>
</section>
<section class="block">
<h2>처리 원칙</h2>
<ul class="check-list">
<li>접수된 모든 신고는 운영팀이 직접 확인합니다.</li>
<li>신고자 정보는 처리 외 목적으로 사용되지 않습니다.</li>
<li>안전 정책 위반은 즉시 협력 중단 조치됩니다.</li>
</ul>
</section>
""",
)

# ---------- About pages ----------
add(
  path="about/index.html", url="/about/", slug="about-hub",
  title="바로GO 소개 | 브랜드·운영 원칙·정책 | 바로GO",
  description="바로GO 브랜드 소개, 운영 원칙, 관리사 운영 기준, 안전 이용 정책, 개인정보처리방침, 이용약관을 안내합니다.",
  h1="바로GO 소개",
  intro='<p class="lede">바로GO를 운영하는 사업자 정보와 운영 원칙, 정책 문서를 공개합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/")],
  body="""
<section class="block">
<h2>사업자 정보</h2>
<ul class="check-list">
<li>상호 : 바로GO (YH LAB)</li>
<li>대표 : 김유환</li>
<li>사업자등록번호 : 815-26-00585</li>
<li>주소 : 경기도 파주시 청석로 268</li>
<li>예약 전화 : <a href="tel:0508-202-4719">0508-202-4719</a></li>
</ul>
</section>
<section class="block">
<ul class="service-grid">
<li><h3><a href="/about/brand/">브랜드 소개</a></h3><p>바로GO 운영 철학과 목표</p></li>
<li><h3><a href="/about/operation-policy/">운영 원칙</a></h3><p>예약·가격·후기 운영 원칙</p></li>
<li><h3><a href="/about/therapist-policy/">관리사 운영 기준</a></h3><p>관리사 협력 기준과 검증</p></li>
<li><h3><a href="/about/safety-policy/">안전 이용 정책</a></h3><p>건전 이용을 위한 정책</p></li>
<li><h3><a href="/about/privacy/">개인정보처리방침</a></h3><p>수집·이용·보관 안내</p></li>
<li><h3><a href="/about/terms/">이용약관</a></h3><p>이용 시 합의 사항</p></li>
</ul>
</section>
""",
)

add(
  path="about/brand/index.html", url="/about/brand/", slug="brand",
  title="브랜드 소개 | 바로GO 운영 철학 | 바로GO",
  description="바로GO는 전국 방문 마사지 예약을 더 안전하고 투명하게 안내하기 위해 운영되는 플랫폼입니다.",
  h1="브랜드 소개",
  intro='<p class="lede">바로GO(운영사 YH LAB)는 전국 방문 마사지 예약을 더 안전하고 투명하게 안내하기 위해 운영됩니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("브랜드 소개","/about/brand/")],
  body="""
<section class="block">
<h2>우리가 중요하게 생각하는 것</h2>
<ul class="check-list">
<li>예약 단계에서 가격·코스·취소 기준이 명확해야 합니다.</li>
<li>이용자 안전이 가장 먼저입니다. 불법·퇴폐 서비스는 다루지 않습니다.</li>
<li>지역 페이지는 실제 이용 사례가 누적된 곳부터 단계적으로 확장합니다.</li>
</ul>
</section>
<section class="block">
<h2>우리가 하지 않는 것</h2>
<ul class="check-list">
<li>"무조건 1위", "최고", "검증 완료" 같은 근거 없는 표현을 쓰지 않습니다.</li>
<li>허위 후기, 자동 생성된 광고형 후기를 게시하지 않습니다.</li>
<li>지역명만 바꾼 복붙 페이지를 만들지 않습니다.</li>
</ul>
</section>
""",
)

add(
  path="about/operation-policy/index.html", url="/about/operation-policy/", slug="operation-policy",
  title="운영 원칙 | 예약·가격·후기·콘텐츠 정책 | 바로GO",
  description="바로GO의 예약·가격·후기·콘텐츠 운영 원칙을 공개합니다.",
  h1="운영 원칙",
  intro='<p class="lede">투명한 운영을 위해 핵심 운영 원칙을 공개합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("운영 원칙","/about/operation-policy/")],
  body="""
<section class="block">
<h2>예약 운영</h2>
<ul class="check-list">
<li>예약 확정 전 가격·취소 기준을 반드시 안내합니다.</li>
<li>사전 동의 없는 추가 비용은 발생시키지 않습니다.</li>
</ul>
</section>
<section class="block">
<h2>가격 안내</h2>
<ul class="check-list">
<li>전국 단일가가 아닌 코스·시간·이동 기반 안내를 사용합니다.</li>
<li>"최저가 보장", "할인 마감" 같은 자극 표현은 사용하지 않습니다.</li>
</ul>
</section>
<section class="block">
<h2>후기 운영</h2>
<ul class="check-list">
<li>광고성·과장 후기는 노출하지 않습니다.</li>
<li>허위 후기로 확인되면 즉시 삭제합니다.</li>
</ul>
</section>
<section class="block">
<h2>콘텐츠 운영</h2>
<ul class="check-list">
<li>실제 운영 데이터와 상담 사례를 바탕으로 작성됩니다.</li>
<li>AI 보조를 사용할 수 있으나, 책임 저자(운영팀)가 검수합니다.</li>
<li>출처가 필요한 경우 본문에 명확히 표기합니다.</li>
</ul>
</section>
""",
)

add(
  path="about/therapist-policy/index.html", url="/about/therapist-policy/", slug="therapist-policy",
  title="관리사 운영 기준 | 협력·검증·교육 | 바로GO",
  description="바로GO와 협력하는 관리사의 운영 기준과 검증·교육 정책을 공개합니다.",
  h1="관리사 운영 기준",
  intro='<p class="lede">바로GO는 합법적인 사업 운영과 안전한 이용을 위한 기본 기준을 유지합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("관리사 기준","/about/therapist-policy/")],
  body="""
<section class="block">
<h2>기본 협력 기준</h2>
<ul class="check-list">
<li>합법적인 사업 운영이 가능한 사업자·프리랜서</li>
<li>방문 마사지 관련 경력과 검증 가능한 이력</li>
<li>안전 이용 정책과 가격·취소 기준 준수</li>
</ul>
</section>
<section class="block">
<h2>운영 의무</h2>
<ul class="check-list">
<li>예약 시간 준수와 정확한 코스 진행</li>
<li>고객 개인정보 보호와 청결 기준 준수</li>
<li>불법·퇴폐 서비스 제공 금지</li>
</ul>
</section>
<section class="block">
<h2>위반 시 조치</h2>
<p>안전 이용 정책 또는 운영 의무를 위반하는 경우 협력은 즉시 중단됩니다.</p>
</section>
""",
)

add(
  path="about/safety-policy/index.html", url="/about/safety-policy/", slug="safety-policy",
  title="안전 이용 정책 | 건전 이용·신고·조치 | 바로GO",
  description="바로GO 안전 이용 정책. 불법·퇴폐 서비스 차단, 신고 채널, 위반 시 조치를 공개합니다.",
  h1="안전 이용 정책",
  intro='<p class="lede">바로GO는 합법적이고 건전한 방문 마사지 안내만 제공합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("안전 이용 정책","/about/safety-policy/")],
  body="""
<section class="block">
<h2>금지 사항</h2>
<ul class="check-list">
<li>불법·퇴폐 서비스 제공·알선·중개</li>
<li>"은밀한", "성인", "퇴폐" 등 자극적 표현 사용</li>
<li>거짓 후기·허위 광고</li>
<li>고객 개인정보 무단 이용</li>
</ul>
</section>
<section class="block">
<h2>신고 채널</h2>
<p>위반 사항을 발견하시면 <a href="/support/report/">불편 신고</a>로 접수해 주세요. 운영팀이 직접 확인합니다.</p>
</section>
<section class="block">
<h2>위반 시 조치</h2>
<ul class="check-list">
<li>협력 관계 즉시 중단</li>
<li>사안에 따라 관계 기관에 협조</li>
<li>관련 데이터 보존 및 추가 조치</li>
</ul>
</section>
""",
)

add(
  path="about/privacy/index.html", url="/about/privacy/", slug="privacy",
  title="개인정보처리방침 | 수집·이용·보관 | 바로GO",
  description="바로GO 개인정보처리방침. 수집 항목, 이용 목적, 보관 기간, 이용자 권리를 안내합니다.",
  h1="개인정보처리방침",
  intro='<p class="lede">바로GO(운영사 YH LAB, 이하 "회사")는 이용자의 개인정보를 중요하게 다루며 관련 법령을 준수합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("개인정보처리방침","/about/privacy/")],
  body="""
<section class="block">
<h2>1. 수집하는 개인정보 항목</h2>
<ul class="check-list">
<li>예약 시 : 이름, 연락처, 예약 일시, 방문 장소(가정·숙소·사무실 정보 포함)</li>
<li>결제 시 : 결제 수단 관련 정보(카드사·금융기관 처리, 회사는 마스킹된 거래 정보만 보관)</li>
<li>문의 시 : 연락처, 문의 내용</li>
</ul>
</section>
<section class="block">
<h2>2. 이용 목적</h2>
<ul class="check-list">
<li>예약 확정·진행·연락</li>
<li>결제 및 환불 처리</li>
<li>고객 문의 응대 및 불편 신고 처리</li>
<li>안전 이용 정책 위반 사항 확인</li>
</ul>
</section>
<section class="block">
<h2>3. 보관 기간</h2>
<p>법령에서 정한 보관 기간이 있는 경우 해당 기간 동안 보관하며, 그 외에는 이용 목적이 달성된 즉시 파기합니다.</p>
</section>
<section class="block">
<h2>4. 제3자 제공</h2>
<p>법령에 근거한 경우 또는 이용자 동의가 있는 경우 외에는 제공하지 않습니다.</p>
</section>
<section class="block">
<h2>5. 이용자 권리</h2>
<ul class="check-list">
<li>본인 정보 열람·정정·삭제 요청 가능</li>
<li>처리 정지 요청 가능</li>
<li>요청은 <a href="/support/contact/">문의하기</a>를 통해 접수</li>
</ul>
</section>
<section class="block">
<h2>6. 개인정보 보호 책임</h2>
<p>개인정보 보호 책임자 : 김유환 (대표) · 사업자등록번호 815-26-00585 · 경기도 파주시 청석로 268 · <a href="tel:0508-202-4719">0508-202-4719</a></p>
</section>
""",
)

add(
  path="about/terms/index.html", url="/about/terms/", slug="terms",
  title="이용약관 | 바로GO",
  description="바로GO 이용약관. 서비스 이용 시 동의되는 일반 조건을 안내합니다.",
  h1="이용약관",
  intro='<p class="lede">본 약관은 바로GO(운영사 YH LAB, 이하 "회사")가 제공하는 방문 마사지 안내 서비스의 이용 조건을 정합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("이용약관","/about/terms/")],
  body="""
<section class="block">
<h2>제1조 (목적)</h2>
<p>본 약관은 회사가 제공하는 방문 마사지 안내·예약 서비스의 이용 절차와 권리·의무를 정함을 목적으로 합니다.</p>
</section>
<section class="block">
<h2>제2조 (정의)</h2>
<ul class="check-list">
<li>"서비스"란 회사가 운영하는 방문 마사지 안내·예약 플랫폼을 말합니다.</li>
<li>"이용자"란 본 약관에 따라 서비스를 이용하는 자를 말합니다.</li>
<li>"관리사"란 회사와 협력해 방문 케어를 진행하는 자를 말합니다.</li>
</ul>
</section>
<section class="block">
<h2>제3조 (예약과 결제)</h2>
<p>예약은 회사가 안내한 절차에 따라 진행되며, 확정 전 가격·코스·취소 기준을 안내합니다.</p>
</section>
<section class="block">
<h2>제4조 (취소·환불)</h2>
<p><a href="/reservation/cancel-refund/">취소·환불 규정</a>에 따라 처리됩니다.</p>
</section>
<section class="block">
<h2>제5조 (이용자의 의무)</h2>
<ul class="check-list">
<li>정확한 예약 정보 제공</li>
<li>불법·퇴폐 서비스 요청 금지</li>
<li>관리사에 대한 부당한 요구 금지</li>
</ul>
</section>
<section class="block">
<h2>제6조 (회사의 의무)</h2>
<ul class="check-list">
<li>안전한 이용 환경 제공</li>
<li>개인정보 보호 및 정확한 가격 안내</li>
<li>불편 신고 접수 및 처리</li>
</ul>
</section>
<section class="block">
<h2>제7조 (책임 제한)</h2>
<p>방문 마사지는 의료 행위가 아니며, 회사는 치료 효과를 보장하지 않습니다. 이용자의 건강 상태에 따른 결과에 대해 회사는 책임을 지지 않습니다.</p>
</section>
<section class="block">
<h2>제8조 (관할)</h2>
<p>본 약관과 관련된 분쟁은 회사 소재지 관할 법원을 합의 관할로 합니다.</p>
</section>
""",
)


# ============================================================
# build
# ============================================================
def write_sitemap(paths):
    items = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
             "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    # add home
    urls = ["/"] + ["/" + p.replace("/index.html", "/") for p in paths]
    seen = set()
    for u in urls:
        if u in seen: continue
        seen.add(u)
        items.append(f"  <url><loc>{u}</loc><lastmod>{BUILD_DATE}</lastmod></url>")
    items.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(items) + "\n", encoding="utf-8")


def write_robots():
    txt = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")


def main():
    paths = []
    for p in PAGES:
        paths.append(render(p))
    write_sitemap(paths)
    write_robots()
    print(f"Built {len(paths)} pages.")


if __name__ == "__main__":
    main()
