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

# ---------- 17 region pages (unique content per region) ----------
# Each region has independently written body, FAQ and related links so pages
# are not templated copies. Section headings, prose and FAQs deliberately
# differ per region to reflect actual local context.
REGIONS = [
{
  "slug": "seoul", "name": "서울", "full": "서울특별시",
  "title": "서울 방문 마사지 권역별 이용 안내 | 강남·마포·종로·여의도 | 바로GO",
  "description": "서울은 권역마다 이용 패턴이 다릅니다. 강남·서초의 호텔 야간 수요, 마포·용산의 직장인 가정 방문, 종로·중구의 단시간 호텔 코스 등 서울 6개 권역의 실제 이용 흐름을 정리했습니다.",
  "h1": "서울 권역별 방문 마사지 이용 안내",
  "lede": "서울은 25개 자치구가 각각 다른 생활 리듬을 가진 도시이며, 호텔·오피스·주거 분포가 권역마다 달라서 같은 도시 안에서도 예약 흐름이 크게 다릅니다. 이 안내는 권역별로 자주 문의되는 시간대와 진행 방식을 정리한 페이지입니다.",
  "body": """
<section class="block">
<h2>서울을 권역으로 나눠보면</h2>
<p>서울은 도심·강남·강북·서남·서북 다섯 권역으로 살피면 이해가 쉽습니다. 강남(강남·서초·송파)은 5성급 호텔과 비즈니스 호텔이 가장 밀집한 권역이라 호텔 방문 케어 비중이 높고, 도심(종로·중구)은 KTX 서울역·외국계 호텔이 모여 있어 단시간 코스 문의가 많습니다. 강북·서북(마포·용산·은평)은 직장인 단지 가정 방문 비중, 서남(영등포·여의도·강서)은 김포공항 인접 호텔과 여의도 야근 후 케어가 함께 안내됩니다.</p>
</section>

<section class="block">
<h2>강남·서초·송파 — 호텔 야간 비중이 가장 높은 권역</h2>
<p>강남 권역은 출장·관광 일정과 맞물려 5성·4성 체인 호텔의 객실 방문 문의가 가장 자주 들어오는 권역입니다. 자정 이후 시간대도 일부 가능하지만 객실 호수·체크인 일정 확인이 선행되어야 합니다. 압구정·청담 일대의 부티크 호텔도 안내되며, 송파(잠실) 권역은 컨벤션 일정에 맞춘 평일 저녁 예약이 함께 들어옵니다.</p>
</section>

<section class="block">
<h2>마포·용산·종로 — 평일 저녁 가정·호텔 혼합 권역</h2>
<p>마포·용산은 직장인 1인 가구 비중이 높아 평일 저녁 가정 방문 케어가 많은 권역입니다. 이태원·한남 호텔에서도 객실 방문이 가능하며, 종로·중구는 광화문·서울역·동대문 일대 비즈니스 호텔의 단시간 코스(60·90분) 비중이 큽니다.</p>
</section>

<section class="block">
<h2>여의도·강서 — 야근 후 케어와 공항 인접 호텔</h2>
<p>여의도 권역은 금융권 야근 일정과 맞물려 평일 밤 시간대 문의가 일정하게 발생하며, 강서·김포공항 인접 호텔은 환승 일정에 맞춘 단시간 케어가 자주 안내됩니다. 강서 일대는 강남·강북 대비 야간 가능 시간이 조금 빠르게 마감되는 편입니다.</p>
</section>

<section class="block">
<h2>서울에서 예약 시 자주 확인하는 사항</h2>
<ul class="check-list">
<li>호텔 방문은 객실 호수와 체크인 명의 확인이 함께 필요합니다.</li>
<li>강남·도심·여의도는 같은 시간대라도 가능 여부가 다릅니다.</li>
<li>심야 시간대는 일부 권역에서만 가능하며 사전 확인이 필요합니다.</li>
<li>광역시인 서울 안에서도 25개 구 간 이동 시간이 변수입니다.</li>
</ul>
</section>

<section class="block">
<h2>서울 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>강남에서 새벽 시간대도 받을 수 있나요?</summary><p>강남·서초·송파 일부 호텔에서는 자정 이후 시간대도 안내되는 경우가 있습니다. 권역과 객실 정보에 따라 가능 여부가 달라지므로 상담 단계에서 확인이 필요합니다.</p></details>
<details><summary>여의도 야근 후 회사로 받을 수 있나요?</summary><p>오피스 방문은 별도 보안 정책이 있는 빌딩이 많아 일반적으로 추천하지 않습니다. 인근 호텔 또는 자택을 안내드리는 경우가 일반적입니다.</p></details>
<details><summary>김포공항 인근 호텔에서도 가능한가요?</summary><p>강서 일대 공항 인접 호텔에서 단시간 코스 문의가 자주 안내됩니다. 환승·체류 일정 길이에 맞춘 60·90분 코스를 권해드리는 편입니다.</p></details>
<details><summary>강북(노원·도봉·강북구)도 안내되나요?</summary><p>가능합니다. 다만 강북 권역은 심야 시간대 마감이 강남 대비 이른 편이라 저녁 시간대 예약을 권해드립니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/reservation/late-night/">심야·새벽 예약 안내</a></li><li><a href="/guide/safe-reservation/">안전한 예약 확인 방법</a></li></ul></aside>',
},
{
  "slug": "gyeonggi", "name": "경기", "full": "경기도",
  "title": "경기도 방문 마사지 권역별 이용 안내 | 분당·수원·일산·평택 | 바로GO",
  "description": "경기도는 31개 시·군이 모두 다른 권역 특성을 가집니다. 분당·판교 IT 야근 후 케어, 수원·화성 산업 출장, 일산·파주 신도시 가정 방문 등 권역별 이용 흐름과 광역 이동 안내를 정리했습니다.",
  "h1": "경기도 권역별 방문 마사지 이용 안내",
  "lede": "경기도는 면적이 넓고 31개 시·군이 산업·신도시·전원 권역으로 나뉘어 있어, 같은 도(道) 안에서도 이용 패턴이 크게 다릅니다. 권역별로 자주 안내되는 시간과 이동 조건을 분리해 정리했습니다.",
  "body": """
<section class="block">
<h2>경기도를 4개 권역으로 나눠보면</h2>
<p>경기도는 흔히 동남(분당·판교·용인·성남), 서남(수원·화성·평택·오산), 서북(고양·파주·김포), 동북(남양주·구리·의정부·양주) 네 권역으로 나누어 안내합니다. 권역별로 산업·신도시·관광 비중이 달라서 가능 시간대와 호텔/가정 비중이 모두 다릅니다.</p>
</section>

<section class="block">
<h2>분당·판교·성남 — IT 야근 후 케어 비중이 높은 권역</h2>
<p>판교 테크노밸리와 분당 IT 단지가 밀집한 동남권은 평일 야근 후 시간대(밤 9시~새벽 1시) 가정 방문 비중이 높습니다. 분당·정자·서현·미금 일대 오피스텔 단지에서 자주 안내되며, 판교 일대 호텔은 비즈니스 출장 일정과 맞물린 객실 방문이 함께 들어옵니다.</p>
</section>

<section class="block">
<h2>수원·화성·평택 — 산업 출장 일정과 맞물린 호텔 권역</h2>
<p>서남권은 삼성전자(수원·화성)·기아(화성)·LG·평택 산업단지가 모여 있어 평일 저녁 호텔 방문 비중이 높습니다. 동탄 신도시·광교 일대는 가정 방문도 함께 안내되며, 평택은 미군기지 인접 호텔에서 단시간 코스 문의가 자주 안내됩니다.</p>
</section>

<section class="block">
<h2>고양·파주·김포 — 신도시 가정 방문이 중심</h2>
<p>일산·운정·삼송·김포한강 등 신도시가 모여 있는 서북권은 가정 방문 비중이 호텔보다 큽니다. 평일 저녁 시간대 문의가 가장 많으며, 파주 일부 외곽은 이동 거리에 따라 가능 시간이 제한되는 경우가 있습니다.</p>
</section>

<section class="block">
<h2>광역 이동 시 알아둘 점</h2>
<ul class="check-list">
<li>같은 경기도라도 평택→파주 이동은 2시간 이상 소요됩니다.</li>
<li>분당·판교·수원은 권역 내 이동, 일산·파주는 별도 권역으로 분리됩니다.</li>
<li>외곽 시군(가평·연천·여주 등)은 도착 가능 시간이 제한적입니다.</li>
<li>광역 이동 시 추가 이동료가 발생할 수 있습니다.</li>
</ul>
</section>

<section class="block">
<h2>경기도 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>분당과 일산 모두 같은 시간에 가능한가요?</summary><p>분당과 일산은 다른 권역으로 안내되며, 같은 시간대에 두 권역을 모두 진행하기는 어려운 경우가 일반적입니다. 권역별로 예약 가능 시간을 따로 확인해 주세요.</p></details>
<details><summary>외곽 시·군(가평·양평·여주 등)도 가능한가요?</summary><p>가능 여부는 시간대와 이동 거리에 따라 달라집니다. 외곽 권역은 사전에 가능 시간을 확인하는 것을 권장합니다.</p></details>
<details><summary>출장 일정으로 평택 호텔에서 받을 수 있나요?</summary><p>평택·오산 일대 비즈니스 호텔은 평일 저녁 시간대 객실 방문 비중이 높은 권역으로, 사전에 일정과 호실 정보를 함께 확인합니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/reservation/visit-area/">출장 가능 지역</a></li><li><a href="/reservation/price/">가격 및 코스 안내</a></li><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li></ul></aside>',
},
{
  "slug": "incheon", "name": "인천", "full": "인천광역시",
  "title": "인천 방문 마사지 이용 안내 | 인천공항·송도·부평 권역 | 바로GO",
  "description": "인천공항 환승 일정에 맞춘 단시간 코스, 송도 국제업무지구의 비즈니스 출장 케어, 부평·계양 주거 권역의 평일 저녁 가정 방문 등 인천 권역별 실제 이용 흐름을 정리했습니다.",
  "h1": "인천 권역별 방문 마사지 이용 안내",
  "lede": "인천은 인천국제공항과 송도 국제업무지구가 함께 있는 특수성으로, 환승·체류·출장 일정에 맞춘 단시간 호텔 케어 문의가 다른 광역시보다 두드러집니다.",
  "body": """
<section class="block">
<h2>인천 권역의 세 가지 흐름</h2>
<p>인천은 (1) 영종도·인천공항 인접 호텔, (2) 송도·연수 국제업무지구, (3) 부평·계양·서구 주거 권역의 세 흐름으로 안내됩니다. 권역별로 시간대와 코스 길이 선호가 다릅니다.</p>
</section>

<section class="block">
<h2>인천공항 인접 호텔 — 단시간 환승 케어</h2>
<p>영종도 일대 공항 인접 호텔(파라다이스·하얏트·그랜드 하얏트·네스트·베스트웨스턴 등)은 환승 대기 시간과 맞물린 60·90분 단시간 코스 문의가 자주 안내됩니다. 체크인 시간이 짧은 환승객 특성상 객실 호수·체크인 명의 사전 확인이 특히 중요합니다.</p>
</section>

<section class="block">
<h2>송도 국제업무지구 — 비즈니스 출장 권역</h2>
<p>송도 컨벤시아·G타워 일대는 국제 행사와 외국계 기업 출장 일정과 맞물려 평일 저녁 호텔 방문이 많습니다. 오크우드·쉐라톤·홀리데이인 송도 등에서 비즈니스 일정 종료 후 야간 케어로 자주 안내됩니다.</p>
</section>

<section class="block">
<h2>부평·계양·미추홀·서구 — 주거 권역 가정 방문</h2>
<p>인천 본토 권역(부평·계양·미추홀·남동·서구)은 직장인 가정 방문 비중이 높습니다. 평일 저녁 7~11시 시간대 문의가 가장 많으며, 검단·청라 신도시도 같은 흐름입니다. 강화·옹진 등 도서 권역은 이동 가능 여부가 시기에 따라 제한됩니다.</p>
</section>

<section class="block">
<h2>공항 환승 케어 시 안내사항</h2>
<ul class="check-list">
<li>체크인 후 객실 호수 안내가 가능한 상태에서 예약을 진행합니다.</li>
<li>환승 대기 시간이 짧으면 60분 코스를 권해드리는 편입니다.</li>
<li>공항 인근 모텔은 일부 운영 정책상 안내가 제한될 수 있습니다.</li>
</ul>
</section>

<section class="block">
<h2>인천 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>인천공항에서 환승 4시간 정도 가능합니다. 가능할까요?</summary><p>환승객 시간 기준 4시간이면 보안검색·체크인 시간을 제외하고 60분 코스 정도가 적절합니다. 공항 인접 호텔 체크인 일정에 맞춰 진행하시는 것을 권합니다.</p></details>
<details><summary>송도에서 외국어 안내가 되는지요?</summary><p>모든 케이스에 대해 보장되지는 않으며, 영어 안내가 가능한 일정으로 사전 조율이 필요합니다. 상담 단계에서 미리 알려 주시면 가능 여부를 확인해 드립니다.</p></details>
<details><summary>강화도에서도 이용 가능한가요?</summary><p>강화·옹진 등 도서 권역은 이동 시간 특성상 일반적으로 안내되지 않거나 사전 협의가 필요한 권역입니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li><li><a href="/reservation/how-to-book/">예약 방법</a></li></ul></aside>',
},
{
  "slug": "busan", "name": "부산", "full": "부산광역시",
  "title": "부산 방문 마사지 이용 안내 | 해운대·광안·서면·남포 권역 | 바로GO",
  "description": "부산은 전국에서 호텔 방문 케어 비중이 가장 높은 광역시입니다. 해운대·광안·서면 권역의 관광 호텔 일정, 성수기·비수기 가능 시간 차이, 부산 권역별 이용 흐름을 정리했습니다.",
  "h1": "부산 권역별 방문 마사지 이용 안내",
  "lede": "부산은 해운대·광안 일대 관광 호텔이 밀집해 있어 전국 광역시 중 호텔 방문 비중이 가장 두드러지는 도시입니다. 관광 성수기와 비수기에 따라 가능 시간대 흐름이 크게 달라집니다.",
  "body": """
<section class="block">
<h2>부산을 3개 권역으로 나눠보면</h2>
<p>부산은 (1) 해운대·수영·광안 관광 호텔 권역, (2) 서면·연제·동래 도심 직장인 권역, (3) 남포·중구·서구 구도심 권역으로 나누어 안내합니다. 권역별 호텔/가정 비중이 다르고 시즌 영향도 다릅니다.</p>
</section>

<section class="block">
<h2>해운대·광안 — 관광 호텔 야간 케어가 중심</h2>
<p>해운대(파라다이스·웨스틴조선·시그니엘·파크하얏트 등)와 광안(앰배서더·골든튤립 등) 권역은 평일 야간·주말 호텔 방문이 가장 많이 안내되는 권역입니다. 관광 일정 후 객실에서 받는 케어 비중이 압도적이며, 광안리 야경 시간대(밤 9~11시)에 문의가 집중되는 편입니다.</p>
</section>

<section class="block">
<h2>서면·연제·동래 — 도심 직장인 권역</h2>
<p>서면·전포·연산·온천 일대는 직장인 가정 방문과 비즈니스 호텔(롯데호텔 부산·노보텔 등) 객실 방문이 혼합된 권역입니다. 평일 저녁 시간대 문의가 가장 많고, 주말은 해운대 권역으로 흐름이 이동하는 편입니다.</p>
</section>

<section class="block">
<h2>남포·중구·서구 — 구도심·관광 혼합 권역</h2>
<p>남포동·자갈치·국제시장 일대는 관광 일정과 맞물려 호텔(코모도호텔·이비스 앰배서더 등) 방문이 자주 안내됩니다. 구도심 특성상 가정 방문 비중은 동부산보다 낮습니다.</p>
</section>

<section class="block">
<h2>부산 성수기 안내</h2>
<ul class="check-list">
<li>7~8월 해운대 성수기는 가능 시간이 빠르게 마감됩니다.</li>
<li>광안리 불꽃축제·부산국제영화제 시즌은 사전 예약이 권장됩니다.</li>
<li>비수기(11~2월)는 권역 전반에 걸쳐 시간 여유가 있는 편입니다.</li>
<li>기장·정관 신도시는 별도 권역으로 안내됩니다.</li>
</ul>
</section>

<section class="block">
<h2>부산 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>해운대 호텔에서 새벽 시간대도 가능한가요?</summary><p>해운대 권역은 새벽 시간대 가능 사례가 다른 권역보다 많은 편입니다. 객실 호수·체크인 정보 사전 확인을 거쳐 진행합니다.</p></details>
<details><summary>광안리 불꽃축제 당일 예약이 어려운가요?</summary><p>축제 당일은 호텔 가능 시간 자체가 빠르게 마감되므로 사전 예약을 권장드립니다. 당일 문의는 가능 권역이 제한될 수 있습니다.</p></details>
<details><summary>기장군(정관·일광)도 가능한가요?</summary><p>기장 권역은 안내 가능하나 본 시가지(해운대·서면)와 이동 시간이 다르므로 따로 권역을 두고 가능 시간을 확인합니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/reservation/late-night/">심야·새벽 예약 안내</a></li><li><a href="/reservation/price/">가격 및 코스 안내</a></li></ul></aside>',
},
{
  "slug": "daegu", "name": "대구", "full": "대구광역시",
  "title": "대구 방문 마사지 이용 안내 | 수성·동성로·달서 권역 | 바로GO",
  "description": "대구는 수성구 주거 권역 평일 저녁 가정 방문 비중이 높은 도시입니다. 동성로 도심 호텔 출장 케어, 폭염 시즌 시간대 조정, 권역별 이용 흐름을 정리했습니다.",
  "h1": "대구 권역별 방문 마사지 이용 안내",
  "lede": "대구는 수성구 주거 권역이 차지하는 비중이 크고, 동성로·교동 도심에 비즈니스 호텔이 모여 있어 가정 방문과 호텔 방문 흐름이 비교적 분리되어 있는 도시입니다.",
  "body": """
<section class="block">
<h2>대구 권역 구성</h2>
<p>대구는 (1) 수성구 주거 권역, (2) 중구 동성로·교동 도심 호텔 권역, (3) 달서·달성 서부 권역, (4) 동구·북구 동부 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>수성구 — 평일 저녁 가정 방문이 중심</h2>
<p>수성구는 학원가와 주거가 밀집된 권역으로, 평일 저녁 시간대 가정 방문 비중이 다른 권역보다 높습니다. 범어·만촌·황금 일대 아파트 단지에서 자주 안내되며, 주말 가족 일정과 겹치는 저녁 시간대는 사전 예약이 권장됩니다.</p>
</section>

<section class="block">
<h2>동성로·교동 — 비즈니스 호텔 권역</h2>
<p>동성로·교동·반월당 일대는 라온제나·노보텔 앰배서더·매리어트 등 비즈니스 호텔이 모여 있어, 출장 일정과 맞물린 객실 방문 문의가 안내됩니다. KTX 동대구역 일대(신천동) 호텔도 같은 흐름입니다.</p>
</section>

<section class="block">
<h2>달서·달성·동구 — 외곽 주거 권역</h2>
<p>달서구(상인·진천·월배)와 동구(동촌·신서) 권역은 도심 대비 가능 시간이 다소 빠르게 마감되는 편입니다. 평일 저녁 8~10시 시간대 가정 방문이 가장 많이 안내됩니다.</p>
</section>

<section class="block">
<h2>여름 폭염 시즌 안내</h2>
<ul class="check-list">
<li>대구는 7~8월 폭염 일수가 많아 낮 시간대 이동이 길어집니다.</li>
<li>한낮 진행보다 저녁 7시 이후 시간대를 권해드리는 편입니다.</li>
<li>차량 이동이 길어지는 시즌은 사전 시간 여유를 두고 예약해 주세요.</li>
</ul>
</section>

<section class="block">
<h2>대구 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>수성구 외 지역도 안내되나요?</summary><p>달서·달성·동구·북구 모두 안내됩니다. 권역별로 가능 시간이 다소 달라 사전 확인을 권장합니다.</p></details>
<details><summary>경산(경북)에서도 받을 수 있나요?</summary><p>경산은 행정구역상 경북이지만 대구 권역과 인접해 안내되는 경우가 있습니다. 자세한 내용은 <a href="/area/gyeongbuk/">경북 안내 페이지</a>를 참고해 주세요.</p></details>
<details><summary>여름철 낮 시간대도 가능한가요?</summary><p>가능합니다만 한여름 한낮은 이동 시간이 길어지므로 가능하면 저녁 시간대 예약을 권해드리는 편입니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/reservation/visit-area/">출장 가능 지역</a></li><li><a href="/service/swedish/">스웨디시 마사지</a></li><li><a href="/reservation/price/">가격 및 코스 안내</a></li></ul></aside>',
},
{
  "slug": "daejeon", "name": "대전", "full": "대전광역시",
  "title": "대전 방문 마사지 이용 안내 | 유성·둔산·대덕연구단지 권역 | 바로GO",
  "description": "대전은 대덕연구단지·정부청사 출장 일정과 맞물려 유성·둔산 권역의 평일 저녁 호텔 방문 비중이 높은 도시입니다. KTX 단시간 코스, 연구단지 출장 케어 흐름을 정리했습니다.",
  "h1": "대전 권역별 방문 마사지 이용 안내",
  "lede": "대전은 대덕연구단지와 정부청사가 자리한 특성으로, 평일 저녁 출장 연구원·공무원 대상 호텔 방문 케어가 다른 비수도권 광역시보다 두드러지게 안내됩니다.",
  "body": """
<section class="block">
<h2>대전 권역 구성</h2>
<p>대전은 (1) 유성구 호텔·연구단지 권역, (2) 둔산·서구 비즈니스·주거 혼합 권역, (3) 중구·동구 구도심 권역, (4) 대덕구 외곽 권역으로 안내됩니다.</p>
</section>

<section class="block">
<h2>유성구 — 출장 연구원·관광 호텔 권역</h2>
<p>유성구는 KAIST·대덕연구단지·정부 출연연이 인접해 있고, 호텔ICC·라온컨벤션·인터시티 등 비즈니스 호텔이 모여 있어 평일 저녁 출장 일정과 맞물린 객실 방문 비중이 가장 높습니다. 유성온천 일대 관광 호텔도 같은 권역으로 안내됩니다.</p>
</section>

<section class="block">
<h2>둔산·서구 — 정부청사 인근 평일 저녁 권역</h2>
<p>둔산동(정부대전청사)·갤러리아 일대는 직장인 가정 방문과 단기 출장 호텔이 혼합된 권역입니다. 평일 저녁 7~10시 시간대 문의가 가장 많고, 시청·법조타운 인근 주거 단지에서 가정 방문이 자주 안내됩니다.</p>
</section>

<section class="block">
<h2>KTX 대전역 일대 — 단시간 코스</h2>
<p>KTX 대전역 인근 호텔(롯데시티호텔 대전·인터시티 등)은 KTX 일정에 맞춘 60·90분 단시간 코스 문의가 자주 안내됩니다. 출장 일정이 짧은 경우 권장되는 패턴입니다.</p>
</section>

<section class="block">
<h2>대전에서 예약 시 알아둘 점</h2>
<ul class="check-list">
<li>유성·둔산·서구는 평일 저녁 시간대가 가장 가능 폭이 넓습니다.</li>
<li>대덕연구단지 출장 후 가능 시간은 보통 저녁 8시 이후입니다.</li>
<li>KTX 일정 단시간 코스는 60분을 권해드립니다.</li>
<li>세종·청주 권역은 별도 안내 페이지를 참고해 주세요.</li>
</ul>
</section>

<section class="block">
<h2>대전 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>유성 호텔에서 출장 일정 마치고 받을 수 있나요?</summary><p>가능합니다. 출장 종료 시간에 맞춰 객실 호수·체크인 정보를 함께 확인해 주시면 평일 저녁~밤 시간대 안내가 일반적입니다.</p></details>
<details><summary>세종에서 받을 수 있나요?</summary><p>세종은 별도 권역으로 안내됩니다. <a href="/area/sejong/">세종 안내 페이지</a>를 참고해 주세요.</p></details>
<details><summary>KTX 환승 1시간 30분 정도인데 가능한가요?</summary><p>이동·체크인 시간을 제외하면 60분 코스 진행이 빠듯하므로, 대전 체류 일정이 2시간 이상 확보된 경우를 권해드립니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/reservation/how-to-book/">예약 방법</a></li></ul></aside>',
},
{
  "slug": "gwangju", "name": "광주", "full": "광주광역시",
  "title": "광주 방문 마사지 이용 안내 | 상무지구·첨단·광산 권역 | 바로GO",
  "description": "광주는 상무지구 비즈니스 출장과 첨단·수완 신도시 가정 방문이 함께 안내되는 도시입니다. 평일 저녁·주말 가능 시간대와 권역별 이용 흐름을 정리했습니다.",
  "h1": "광주 권역별 방문 마사지 이용 안내",
  "lede": "광주는 호남권 중심 도시로, 상무지구 출장과 첨단·수완 신도시 가정 방문이 안정적으로 안내되는 도시입니다. 호텔 비중보다 가정 방문 비중이 다소 높은 권역입니다.",
  "body": """
<section class="block">
<h2>광주 권역 구성</h2>
<p>광주는 (1) 서구 상무지구 비즈니스 권역, (2) 광산구 첨단·수완 신도시 권역, (3) 동·남구 구도심 권역, (4) 북구 주거 권역으로 안내됩니다.</p>
</section>

<section class="block">
<h2>상무지구 — 출장·비즈니스 호텔 권역</h2>
<p>상무지구는 라마다플라자·홀리데이인 등 비즈니스 호텔이 모여 있고, 광주김대중컨벤션센터 행사 일정과 맞물려 평일 저녁 객실 방문이 안내됩니다. 행사 시즌에는 가능 시간이 빠르게 마감됩니다.</p>
</section>

<section class="block">
<h2>첨단·수완 — 신도시 가정 방문 비중</h2>
<p>광산구 첨단지구·수완지구는 주거 단지가 밀집된 신도시 권역으로, 평일 저녁·주말 가정 방문 비중이 광주에서 가장 높은 편입니다. 평일 저녁 8시 전후 문의가 집중됩니다.</p>
</section>

<section class="block">
<h2>동·남·북구 — 구도심·주거 혼합</h2>
<p>충장로·금남로 일대 도심 호텔과 봉선·운암 등 주거 권역이 함께 안내됩니다. 광주 전체적으로 호텔보다 가정 방문 비중이 높은 특성을 보입니다.</p>
</section>

<section class="block">
<h2>광주에서 예약 시 안내사항</h2>
<ul class="check-list">
<li>주말 가족 일정과 겹치는 시간대(토 저녁)는 예약이 빠르게 차는 편입니다.</li>
<li>상무지구는 컨벤션 일정과 맞물려 사전 예약이 권장됩니다.</li>
<li>전남 권역(나주·담양·화순)과 행정상 분리되어 있으니 별도 페이지를 확인해 주세요.</li>
</ul>
</section>

<section class="block">
<h2>광주 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>나주·담양도 광주에서 안내해 주시나요?</summary><p>나주·담양은 행정상 전남에 속해 별도 권역으로 안내됩니다. <a href="/area/jeonnam/">전남 안내 페이지</a>를 참고해 주세요.</p></details>
<details><summary>광주 외곽(광산구 송정·평동)도 가능한가요?</summary><p>가능합니다. 외곽 권역은 시간대에 따라 가능 시간이 다소 빠르게 마감되는 편입니다.</p></details>
<details><summary>비엔날레·시즌 행사 시기에 예약이 어렵나요?</summary><p>비엔날레·세계김치축제 등 대형 행사 시즌은 상무·동구 권역 호텔이 빠르게 마감되므로 사전 예약을 권장합니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/reservation/how-to-book/">예약 방법</a></li><li><a href="/reservation/price/">가격 및 코스 안내</a></li><li><a href="/service/hometai/">홈타이</a></li></ul></aside>',
},
{
  "slug": "ulsan", "name": "울산", "full": "울산광역시",
  "title": "울산 방문 마사지 이용 안내 | 남구·동구·울주 권역 | 바로GO",
  "description": "울산은 현대중공업·SK·미포 등 산업단지 출장 비중이 가장 높은 광역시입니다. 동구 조선소 인근, 남구 비즈니스 호텔, 장기 출장 재방문 패턴을 정리했습니다.",
  "h1": "울산 권역별 방문 마사지 이용 안내",
  "lede": "울산은 국내 산업단지 출장 비중이 압도적인 광역시로, 평일 야간 호텔 방문 케어가 다른 어떤 비수도권 도시보다 두드러지는 흐름을 보입니다.",
  "body": """
<section class="block">
<h2>울산 권역 구성</h2>
<p>울산은 (1) 남구 비즈니스 호텔 권역, (2) 동구 조선소·미포 권역, (3) 북구 산업단지 권역, (4) 중구 구도심 권역, (5) 울주군 외곽 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>남구 — 비즈니스 호텔 권역</h2>
<p>남구 삼산동·달동 일대는 롯데호텔 울산·신라스테이 울산·현대호텔 등이 모여 있는 권역으로, 평일 저녁 출장 일정과 맞물린 객실 방문 비중이 높습니다. KTX 울산역 일대(언양)는 단시간 코스 문의가 함께 안내됩니다.</p>
</section>

<section class="block">
<h2>동구·미포 — 조선소 출장 권역</h2>
<p>동구는 현대중공업·미포조선 등 조선소 인근 호텔과 게스트하우스가 모여 있는 권역으로, 장기 출장 일정에 맞춘 재방문 케어 비중이 다른 권역보다 높습니다. 출퇴근 시간(오전 7시·오후 5시) 차량 정체가 심해 시간대 조정이 필요합니다.</p>
</section>

<section class="block">
<h2>북구·온산 — 산업단지 권역</h2>
<p>북구(매곡·연암)와 온산공단 일대는 SK·S-OIL·LG화학 등 산업단지 출장객 대상 평일 저녁 호텔 방문이 안내됩니다. 시간대는 보통 저녁 8시 이후가 가장 안정적입니다.</p>
</section>

<section class="block">
<h2>장기 출장 재방문 패턴</h2>
<ul class="check-list">
<li>장기 출장객은 주 1~2회 정기 케어 문의가 자주 들어옵니다.</li>
<li>같은 호텔 재방문 시 객실 정보를 미리 알려 주시면 안내가 빠릅니다.</li>
<li>외국인 엔지니어 케이스는 영어 안내 가능 일정을 사전 협의합니다.</li>
</ul>
</section>

<section class="block">
<h2>울산 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>장기 출장 중 매주 같은 시간 예약 가능한가요?</summary><p>정기 일정 안내가 가능합니다. 다만 매번 가능 인력 일정이 변동될 수 있어 주차별 사전 확인이 필요합니다.</p></details>
<details><summary>조선소 게스트하우스에서도 가능한가요?</summary><p>일반적인 게스트하우스 객실 방문은 안내됩니다. 일부 사내 숙소(외부 출입 통제) 케이스는 사전 확인이 필요합니다.</p></details>
<details><summary>언양 KTX역 인근 호텔도 안내되나요?</summary><p>가능합니다. 단 언양 권역은 본 시가지(남구·동구)와 이동 시간이 있어 시간대 사전 확인을 권합니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li><li><a href="/service/sports-massage/">스포츠 마사지</a></li><li><a href="/reservation/late-night/">심야·새벽 예약 안내</a></li></ul></aside>',
},
{
  "slug": "sejong", "name": "세종", "full": "세종특별자치시",
  "title": "세종 방문 마사지 이용 안내 | 한솔·새롬·도담 권역 | 바로GO",
  "description": "세종은 호텔 인프라가 비교적 적어 가정 방문 비중이 높은 행정중심복합도시입니다. 평일 저녁 공무원 가정 방문 흐름, 인근 권역 확장 가능성을 정리했습니다.",
  "h1": "세종 권역별 방문 마사지 이용 안내",
  "lede": "세종은 행정중심복합도시 특성상 호텔 인프라가 광역시 대비 적은 편이며, 가정 방문 비중이 다른 도시보다 두드러집니다. 정부청사 출퇴근 흐름이 가능 시간대에 영향을 줍니다.",
  "body": """
<section class="block">
<h2>세종 권역 구성</h2>
<p>세종은 (1) 1생활권(한솔·도담), (2) 2생활권(새롬·다정·나성), (3) 3생활권(보람·소담·반곡), (4) 4생활권(아름·종촌·고운), (5) 조치원·연기 등 구 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>가정 방문 비중이 높은 도시</h2>
<p>세종은 정부세종청사 공무원·연구원 거주 비중이 높은 도시이며, 비즈니스 호텔이 광역시 대비 적은 편입니다. 그 결과 평일 저녁 가정 방문 케어가 전체 문의의 큰 비중을 차지합니다.</p>
</section>

<section class="block">
<h2>평일 저녁 — 가장 가능 폭이 넓은 시간대</h2>
<p>정부청사 퇴근 시간 이후 저녁 7~10시 시간대 문의가 가장 안정적으로 안내됩니다. 1·2생활권 아파트 단지에서 자주 진행되며, 4생활권(아름·종촌)도 비슷한 흐름입니다.</p>
</section>

<section class="block">
<h2>호텔 권역</h2>
<p>세종 권역 내 비즈니스 호텔(롯데시티호텔 대전 인근·세종 도담 호텔 등)에서도 객실 방문이 가능하나, 객실 수 자체가 광역시 대비 적어 사전 예약이 권장됩니다. KTX 오송역(행정상 충북)을 통한 출장객은 호텔보다 청사 인근 숙소를 자주 선택합니다.</p>
</section>

<section class="block">
<h2>인근 권역 확장 안내</h2>
<ul class="check-list">
<li>세종~대전 유성: 이동 가능하나 별도 권역으로 가능 시간 차이가 있습니다.</li>
<li>세종~청주(충북): 일부 시간대 안내, 사전 확인 필요.</li>
<li>세종~공주(충남): 시간대에 따라 안내 가능.</li>
<li>외곽 시간대는 마감이 비교적 이른 편입니다.</li>
</ul>
</section>

<section class="block">
<h2>세종 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>오송역 환승 일정에 받을 수 있나요?</summary><p>오송역은 행정상 충북 청주이지만 세종과 가까워 안내 사례가 있습니다. 환승 시간 길이에 맞춰 코스 길이를 조율합니다.</p></details>
<details><summary>정부청사 근처에서 평일 점심 시간대 가능한가요?</summary><p>일반적으로 저녁 시간대 비중이 훨씬 큽니다. 평일 점심 시간대는 가능 여부가 제한적이며 사전 확인이 필요합니다.</p></details>
<details><summary>세종에서 외곽(조치원·금남)도 가능한가요?</summary><p>가능합니다. 다만 본 신도시 권역(1~4생활권) 대비 가능 시간 폭이 좁은 편입니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/area/daejeon/">대전 안내</a></li><li><a href="/area/chungbuk/">충북 안내</a></li><li><a href="/reservation/how-to-book/">예약 방법</a></li></ul></aside>',
},
{
  "slug": "gangwon", "name": "강원", "full": "강원특별자치도",
  "title": "강원 방문 마사지 이용 안내 | 강릉·속초·춘천·평창 권역 | 바로GO",
  "description": "강원은 영동(강릉·속초)과 영서(춘천·원주)의 권역 성격이 매우 다른 지역입니다. 동계 스포츠·서핑 시즌의 회복 케어, 성수기·비수기 가능 시간 차이를 정리했습니다.",
  "h1": "강원 권역별 방문 마사지 이용 안내",
  "lede": "강원은 영동(동해안)과 영서(내륙)가 산맥으로 분리되어 권역이 사실상 두 곳으로 나뉘는 지역입니다. 시즌별 관광 흐름에 따라 가능 시간대 변동이 큽니다.",
  "body": """
<section class="block">
<h2>강원을 영동·영서로 나눠보면</h2>
<p>강원은 (1) 영서 — 춘천·원주·홍천 권역, (2) 영동 — 강릉·속초·동해·삼척 권역으로 나누어 안내합니다. 백두대간을 사이에 둔 두 권역은 이동 시간이 길어 같은 시간대에 양쪽을 모두 진행하기 어려운 경우가 많습니다.</p>
</section>

<section class="block">
<h2>강릉·속초·양양 — 관광 호텔·서핑 회복 케어</h2>
<p>강릉·속초·양양 일대는 7~9월 서핑·해수욕 시즌과 11~3월 동계 스포츠 시즌에 호텔·풀빌라 객실 방문 비중이 높습니다. 양양 서피비치 일대는 서핑 후 어깨·허리 회복 목적으로 안내되는 사례가 많습니다.</p>
</section>

<section class="block">
<h2>평창·정선 — 동계 스포츠 후 회복 케어</h2>
<p>평창 알펜시아·용평·휘닉스파크 일대는 동계 시즌 스키·스노보드 후 컨디션 회복 목적의 케어 문의가 자주 안내됩니다. 정선 하이원 일대도 동일한 흐름입니다.</p>
</section>

<section class="block">
<h2>춘천·원주·홍천 — 내륙 권역</h2>
<p>춘천(석사·온의), 원주(혁신도시), 홍천 일대는 가정 방문과 비즈니스 호텔 출장이 혼합된 권역입니다. 영동권 대비 시즌 영향이 적고 평일 저녁 시간대가 안정적으로 안내됩니다.</p>
</section>

<section class="block">
<h2>강원 성수기 안내</h2>
<ul class="check-list">
<li>여름(7~8월), 겨울(12~2월), 단풍철(10월) 모두 영동권 가능 시간이 빠르게 마감됩니다.</li>
<li>풀빌라·펜션 방문은 객실(객동) 정보 사전 확인이 필요합니다.</li>
<li>평창·정선 권역은 동계 시즌 가능 시간이 가장 빠르게 차는 편입니다.</li>
<li>영동~영서 동시 가능은 어렵습니다. 권역별로 예약을 분리해 주세요.</li>
</ul>
</section>

<section class="block">
<h2>강원 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>서핑 후 어깨 회복 목적인데 어떤 코스가 좋나요?</summary><p>서핑 후 어깨·등 회복은 <a href="/service/sports-massage/">스포츠 마사지</a> 또는 <a href="/service/hometai/">홈타이</a>가 자주 안내됩니다. 부위 집중 케어가 가능합니다.</p></details>
<details><summary>스키 시즌 평창 콘도에서 받을 수 있나요?</summary><p>평창 콘도·리조트 객실 방문은 가능하나, 동계 성수기는 가능 시간이 매우 빠르게 마감됩니다. 입실 일정 확정 후 사전 예약을 권합니다.</p></details>
<details><summary>춘천 펜션에서도 가능한가요?</summary><p>가능합니다. 단 외곽 펜션은 진입로·차량 진입 가능 여부 확인이 함께 필요한 경우가 있습니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/sports-massage/">스포츠 마사지</a></li><li><a href="/service/hometai/">홈타이</a></li><li><a href="/reservation/late-night/">심야·새벽 예약 안내</a></li></ul></aside>',
},
{
  "slug": "chungbuk", "name": "충북", "full": "충청북도",
  "title": "충북 방문 마사지 이용 안내 | 청주·오송·충주 권역 | 바로GO",
  "description": "충북은 청주공항·오송 바이오단지 출장 흐름이 두드러지는 지역입니다. KTX 오송 환승 단시간 코스, 청주·충주 권역별 이용 흐름을 정리했습니다.",
  "h1": "충북 권역별 방문 마사지 이용 안내",
  "lede": "충북은 청주공항과 오송역(KTX·SRT 분기)이 자리한 교통 결절 지역으로, 환승·출장 일정과 맞물린 단시간 호텔 케어 문의가 다른 도(道) 권역보다 많은 흐름을 보입니다.",
  "body": """
<section class="block">
<h2>충북 권역 구성</h2>
<p>충북은 (1) 청주(상당·서원·흥덕·청원), (2) 충주, (3) 제천, (4) 음성·진천 산업단지, (5) 단양·괴산 외곽 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>청주·오송 — 환승·출장 권역</h2>
<p>청주공항 인근 호텔과 오송역 일대(롯데시티호텔 대전 인근·일부 비즈니스 호텔)는 환승 일정에 맞춘 60·90분 단시간 코스 문의가 자주 안내됩니다. 오송 바이오단지 출장객 대상 평일 저녁 객실 방문도 함께 안내됩니다.</p>
</section>

<section class="block">
<h2>충주·제천 — 내륙 권역</h2>
<p>충주(연수·호암·중앙)와 제천(청전·하소) 권역은 가정 방문 비중이 호텔보다 높습니다. 평일 저녁 시간대가 가장 안정적이며, 외곽일수록 가능 시간 마감이 빠른 편입니다.</p>
</section>

<section class="block">
<h2>음성·진천 — 산업단지 권역</h2>
<p>음성(맹동)·진천(혁신도시) 일대는 LG에너지솔루션·하이닉스 출장 일정과 맞물려 평일 저녁 호텔 방문이 안내됩니다.</p>
</section>

<section class="block">
<h2>충북에서 예약 시 안내사항</h2>
<ul class="check-list">
<li>오송 KTX 환승객은 체류 일정이 짧으니 60분 코스를 권합니다.</li>
<li>청주공항 인근은 항공편 시간대에 영향을 받습니다.</li>
<li>단양·괴산 등 외곽은 사전 확인이 필요합니다.</li>
</ul>
</section>

<section class="block">
<h2>충북 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>오송역 환승 2시간 정도 가능할까요?</summary><p>2시간이면 이동·체크인 시간 제외 60분 코스가 빠듯할 수 있습니다. 환승 일정이 3시간 이상 확보된 경우를 권합니다.</p></details>
<details><summary>청주에서 세종 권역도 함께 가능한가요?</summary><p>같은 시간대 동시 진행은 어렵고, 권역을 분리해 예약을 잡는 형태로 안내됩니다.</p></details>
<details><summary>단양·괴산 외곽도 가능한가요?</summary><p>이동 시간이 길어 일반적으로 사전 협의가 필요한 권역입니다. 가능 일정이 제한될 수 있습니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/area/daejeon/">대전 안내</a></li><li><a href="/area/sejong/">세종 안내</a></li><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li></ul></aside>',
},
{
  "slug": "chungnam", "name": "충남", "full": "충청남도",
  "title": "충남 방문 마사지 이용 안내 | 천안·아산·서산·당진·보령 권역 | 바로GO",
  "description": "충남은 천안·아산 KTX 산업단지 출장과 서해안 보령·태안 휴양 두 패턴이 공존하는 지역입니다. 권역별 이용 흐름과 광역 이동 안내를 정리했습니다.",
  "h1": "충남 권역별 방문 마사지 이용 안내",
  "lede": "충남은 동부(천안·아산·공주)의 산업단지 출장과 서부(서산·당진·보령·태안)의 해안 휴양이 한 도(道) 안에 공존하는 지역입니다. 권역별로 가능 시간과 이용 패턴이 분리됩니다.",
  "body": """
<section class="block">
<h2>충남 권역 구성</h2>
<p>충남은 (1) 천안·아산 KTX·산업 권역, (2) 서산·당진 산업 권역, (3) 공주·논산 내륙 권역, (4) 보령·태안·서천 해안 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>천안·아산 — 산업·KTX 권역</h2>
<p>천안 신부동·두정동·불당동과 아산 배방·탕정(삼성디스플레이) 일대는 비즈니스 호텔(롯데시티호텔 천안·라마다 천안 등)과 KTX 천안아산역 일대 호텔의 출장 객실 방문이 가장 많이 안내되는 권역입니다.</p>
</section>

<section class="block">
<h2>서산·당진 — 산업단지 권역</h2>
<p>서산(대산석유화학)·당진(현대제철)은 산업단지 출장객 대상 평일 저녁 호텔 방문이 안내됩니다. 본 시가지와 산업단지 간 이동 시간이 있어 가능 시간 사전 확인이 필요합니다.</p>
</section>

<section class="block">
<h2>보령·태안·서천 — 해안 휴양 권역</h2>
<p>대천해수욕장·만리포·삼봉 일대 펜션과 호텔은 여름 성수기 가족 일정과 맞물린 객실 방문 문의가 안내됩니다. 머드축제 시즌(7월)은 가능 시간이 빠르게 마감됩니다.</p>
</section>

<section class="block">
<h2>광역 이동 시 알아둘 점</h2>
<ul class="check-list">
<li>천안~태안 이동은 2시간 이상 소요됩니다.</li>
<li>같은 충남이라도 권역별 예약 분리가 자연스럽습니다.</li>
<li>서해안 휴양 시즌(7~8월)은 사전 예약이 권장됩니다.</li>
</ul>
</section>

<section class="block">
<h2>충남 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>천안아산역 일정에 맞춰 단시간 가능한가요?</summary><p>천안아산역 인접 호텔에서 60·90분 코스 문의가 자주 안내됩니다. KTX 일정 시간을 함께 확인합니다.</p></details>
<details><summary>대천해수욕장 펜션에서도 가능한가요?</summary><p>가능합니다. 단 성수기에는 가능 시간이 빠르게 마감되므로 사전 예약을 권합니다.</p></details>
<details><summary>당진 산업단지 출장 일정에 가능한가요?</summary><p>현대제철·동부제철 등 산업단지 출장 일정과 맞물린 호텔 객실 방문이 가능합니다. 평일 저녁 시간대가 주로 안내됩니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/reservation/visit-area/">출장 가능 지역</a></li></ul></aside>',
},
{
  "slug": "jeonbuk", "name": "전북", "full": "전북특별자치도",
  "title": "전북 방문 마사지 이용 안내 | 전주·익산·군산 권역 | 바로GO",
  "description": "전북은 전주 한옥마을 관광·익산 KTX 환승·군산 새만금 산업 세 흐름이 함께 안내되는 지역입니다. 권역별 이용 패턴과 게스트하우스 안내 사항을 정리했습니다.",
  "h1": "전북 권역별 방문 마사지 이용 안내",
  "lede": "전북은 전주의 관광, 익산의 KTX 환승, 군산·새만금의 산업 세 권역이 동시에 안내되는 지역입니다. 권역마다 가능 시간 흐름이 분명히 다릅니다.",
  "body": """
<section class="block">
<h2>전북 권역 구성</h2>
<p>전북은 (1) 전주(완산·덕진) 관광·도심, (2) 익산 KTX·역세권, (3) 군산·새만금 산업·항만, (4) 정읍·남원 외곽으로 안내됩니다.</p>
</section>

<section class="block">
<h2>전주 — 한옥마을·관광 권역</h2>
<p>전주 한옥마을·객사·서신동 일대는 관광 일정과 맞물린 호텔·한옥 게스트하우스 객실 방문이 자주 안내됩니다. 한옥 게스트하우스는 객실(객동) 구조가 일반 호텔과 다르므로 사전 안내가 필요합니다.</p>
</section>

<section class="block">
<h2>익산 — KTX 환승 권역</h2>
<p>익산역(KTX·SRT 정차)은 호남선 환승 거점이라 평일 저녁·심야 시간대 단시간 코스 문의가 안내됩니다. 역세권 호텔(라마다·홀리데이 등) 객실 방문 비중이 높습니다.</p>
</section>

<section class="block">
<h2>군산·새만금 — 산업·항만 권역</h2>
<p>군산 산업단지·새만금 사업단지는 평일 저녁 출장 호텔 방문이 안내됩니다. 본 시가지(나운·수송·미장)와 산업단지 간 이동 시간이 있어 권역 분리가 필요합니다.</p>
</section>

<section class="block">
<h2>전북에서 예약 시 안내사항</h2>
<ul class="check-list">
<li>한옥마을 게스트하우스는 객실 구조와 출입 동선 확인이 필요합니다.</li>
<li>익산은 환승 일정 단시간 코스 비중이 큽니다.</li>
<li>군산~새만금 이동은 권역 내에서도 시간 여유가 필요합니다.</li>
</ul>
</section>

<section class="block">
<h2>전북 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>전주 한옥 게스트하우스에서 가능한가요?</summary><p>가능합니다. 단 한옥 객실 구조 특성상 베드 외 다른 방식(매트) 안내가 될 수 있어 사전 확인이 필요합니다.</p></details>
<details><summary>익산역 환승 일정 1시간 30분 가능한가요?</summary><p>익산역 인근 호텔 단시간 코스가 가능하나 1시간 30분은 빠듯할 수 있어 코스 길이와 동선 확인이 필요합니다.</p></details>
<details><summary>군산 새만금 출장 일정에 받을 수 있나요?</summary><p>가능합니다. 출장 종료 시간에 맞춘 평일 저녁 호텔 방문이 가장 자주 안내되는 시간대입니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/reservation/how-to-book/">예약 방법</a></li><li><a href="/area/jeonnam/">전남 안내</a></li></ul></aside>',
},
{
  "slug": "jeonnam", "name": "전남", "full": "전라남도",
  "title": "전남 방문 마사지 이용 안내 | 여수·순천·목포·광양 권역 | 바로GO",
  "description": "전남은 여수 밤바다 관광 호텔, 순천만 자연 관광, 광양제철 산업 출장, 목포 항만 권역 등 권역마다 성격이 다른 지역입니다. 권역별 이용 흐름을 정리했습니다.",
  "h1": "전남 권역별 방문 마사지 이용 안내",
  "lede": "전남은 여수 야경, 순천만 자연 관광, 광양제철 산업, 목포 항만으로 권역마다 성격이 분명히 갈리는 지역입니다. 같은 도(道)지만 권역별 가능 흐름이 다릅니다.",
  "body": """
<section class="block">
<h2>전남 권역 구성</h2>
<p>전남은 (1) 여수 — 관광 호텔, (2) 순천 — 자연 관광 도심, (3) 광양 — 제철 산업, (4) 목포 — 항만 도심, (5) 나주·담양·화순 — 광주 인접 권역으로 안내됩니다.</p>
</section>

<section class="block">
<h2>여수 — 야경 호텔 권역</h2>
<p>여수 종포·돌산·웅천 일대(MVL·디오션·베네치아 등)는 여수 밤바다 야경 일정과 맞물려 평일 저녁~밤 시간대 객실 방문 비중이 매우 높습니다. 여수세계박람회장·오동도 야간 관광 후 호텔 케어가 자주 안내됩니다.</p>
</section>

<section class="block">
<h2>순천 — 자연 관광 도심</h2>
<p>순천만국가정원·낙안읍성 관광 일정과 맞물린 평일 저녁 호텔 방문이 안내됩니다. 시즌(가을 단풍·봄 정원)에 가능 시간이 빠르게 마감되는 편입니다.</p>
</section>

<section class="block">
<h2>광양 — 제철·산업 권역</h2>
<p>광양제철 출장 일정과 맞물려 광양읍·중마동 일대 호텔에서 평일 저녁 객실 방문이 안내됩니다. 야간 출장 일정 비중이 다른 전남 권역보다 높은 편입니다.</p>
</section>

<section class="block">
<h2>목포·신안 — 항만·해양 권역</h2>
<p>목포 평화광장·하당 일대 호텔과 신안 휴양 일정 펜션 방문이 함께 안내됩니다. 신안은 도서 권역 특성상 사전 일정 협의가 필요합니다.</p>
</section>

<section class="block">
<h2>전남 성수기 안내</h2>
<ul class="check-list">
<li>여수: 거북선 축제(5월), 여름 휴가철, 연말 야경 시즌에 사전 예약 권장.</li>
<li>순천: 가을 단풍·정원박람회 시즌 가능 시간 빠르게 마감.</li>
<li>광양: 산업 출장 일정 따라 평일 저녁 비중 일정함.</li>
<li>목포: 항만 출장과 휴양이 혼합된 편.</li>
</ul>
</section>

<section class="block">
<h2>전남 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>여수 디오션리조트에서 가능한가요?</summary><p>여수 종포·웅천 일대 리조트 객실 방문이 자주 안내됩니다. 객동 정보와 체크인 일정을 함께 확인합니다.</p></details>
<details><summary>순천 정원박람회 시즌 예약이 어려운가요?</summary><p>박람회 시즌은 호텔 가능 시간이 빠르게 마감되므로 일정이 확정되면 빠른 예약을 권합니다.</p></details>
<details><summary>광양 산업단지 출장 일정에 받을 수 있나요?</summary><p>가능합니다. 광양읍·중마동 호텔에서 평일 저녁 객실 방문이 자주 안내됩니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/area/gwangju/">광주 안내</a></li><li><a href="/reservation/late-night/">심야·새벽 예약 안내</a></li></ul></aside>',
},
{
  "slug": "gyeongbuk", "name": "경북", "full": "경상북도",
  "title": "경북 방문 마사지 이용 안내 | 포항·경주·구미·안동 권역 | 바로GO",
  "description": "경북은 포항(포스코)·경주(관광)·구미(전자단지)·안동(전통 관광) 네 권역이 모두 성격이 다른 지역입니다. 권역별 이용 흐름과 가능 시간 안내를 정리했습니다.",
  "h1": "경북 권역별 방문 마사지 이용 안내",
  "lede": "경북은 포항 철강, 경주 관광, 구미 전자, 안동 전통으로 권역 색깔이 가장 다채로운 도(道)입니다. 권역별로 이용 흐름이 거의 다른 도시 수준으로 갈립니다.",
  "body": """
<section class="block">
<h2>경북 권역 구성</h2>
<p>경북은 (1) 포항 — 철강·항만, (2) 경주 — 역사 관광, (3) 구미 — 전자단지, (4) 안동 — 전통 관광, (5) 영주·문경·울진 외곽 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>포항 — 철강·항만 출장 권역</h2>
<p>포항제철소 출장 일정과 맞물려 포항 중앙(상도·죽도)·북구(양덕·장량) 호텔에서 평일 저녁 객실 방문이 자주 안내됩니다. 영일대 해수욕장 일대는 여름 휴가 시즌 가능 시간이 빠르게 마감됩니다.</p>
</section>

<section class="block">
<h2>경주 — 역사 관광 권역</h2>
<p>보문관광단지(힐튼·코오롱·켄싱턴리조트 등) 객실 방문이 가장 많이 안내되는 권역으로, 봄(벚꽃)·가을(단풍) 시즌에 가능 시간이 빠르게 마감됩니다. 한옥 게스트하우스 객실 방문은 객동 구조 사전 확인이 필요합니다.</p>
</section>

<section class="block">
<h2>구미 — 전자단지 권역</h2>
<p>구미 1·2·3·4국가산업단지 출장 일정과 맞물려 평일 저녁 호텔 객실 방문이 안내됩니다. 송정·인동 일대 비즈니스 호텔이 자주 이용됩니다.</p>
</section>

<section class="block">
<h2>안동·영주·문경 — 전통·자연 권역</h2>
<p>안동 하회마을·도산서원 관광 일정, 영주 부석사, 문경 새재 관광 일정과 맞물려 호텔 방문이 안내됩니다. 외곽 권역 특성상 가능 시간 마감이 빠른 편입니다.</p>
</section>

<section class="block">
<h2>경북에서 예약 시 안내사항</h2>
<ul class="check-list">
<li>경주 보문단지는 시즌별 가능 시간 차이가 큽니다.</li>
<li>포항·구미는 산업 출장 평일 저녁 비중이 큽니다.</li>
<li>안동·영주 등 외곽 권역은 사전 확인이 필요합니다.</li>
</ul>
</section>

<section class="block">
<h2>경북 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>경주 보문 켄싱턴리조트에서 받을 수 있나요?</summary><p>보문관광단지 내 호텔·리조트 객실 방문이 자주 안내됩니다. 시즌별 가능 시간 차이가 있으니 사전 확인이 좋습니다.</p></details>
<details><summary>포항제철 출장 일정에 가능한가요?</summary><p>가능합니다. 포항 중앙·북구 비즈니스 호텔에서 평일 저녁 객실 방문이 일반적인 패턴입니다.</p></details>
<details><summary>구미·대구 권역을 같은 시간대에 모두 진행할 수 있나요?</summary><p>같은 시간대 두 권역 동시 진행은 어려운 경우가 많습니다. 권역을 분리해 예약을 잡습니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/area/daegu/">대구 안내</a></li><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li></ul></aside>',
},
{
  "slug": "gyeongnam", "name": "경남", "full": "경상남도",
  "title": "경남 방문 마사지 이용 안내 | 창원·김해·진주·거제 권역 | 바로GO",
  "description": "경남은 창원 기계·김해공항·거제 조선소·진주 도심 등 권역마다 성격이 다른 지역입니다. 거제 장기 출장 케어, 김해공항 환승 케어 등 권역별 흐름을 정리했습니다.",
  "h1": "경남 권역별 방문 마사지 이용 안내",
  "lede": "경남은 창원의 기계 산업, 김해의 공항·물류, 거제의 조선소, 진주의 행정 도심으로 권역이 분명히 갈리는 지역입니다. 특히 거제는 장기 출장 외국인 케어 비중이 높습니다.",
  "body": """
<section class="block">
<h2>경남 권역 구성</h2>
<p>경남은 (1) 창원·진해 — 기계·해군, (2) 김해 — 공항·물류, (3) 거제·통영 — 조선·관광, (4) 진주 — 도심·행정, (5) 양산·밀양·함안 등 외곽 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>창원·진해 — 기계·해군 권역</h2>
<p>창원(상남·중앙·반송) 일대는 두산·LG·현대로템 등 기계 산업 출장 일정과 맞물려 평일 저녁 호텔 객실 방문이 자주 안내됩니다. 진해는 해군기지 일대 호텔에서 군 행사 시즌에 가능 시간이 빠르게 마감됩니다.</p>
</section>

<section class="block">
<h2>김해 — 공항·물류 권역</h2>
<p>김해공항 인접 호텔(롯데시티호텔 김해 등)은 환승·국내선 출장 일정과 맞물려 단시간 코스 문의가 안내됩니다. 김해 시내(외동·삼계)는 가정 방문 비중이 호텔보다 높습니다.</p>
</section>

<section class="block">
<h2>거제 — 조선소 출장 권역</h2>
<p>거제 옥포(한화오션)·고현(삼성중공업) 일대는 조선소 출장 일정과 맞물려 평일 저녁·야간 호텔 방문 비중이 가장 큰 권역 중 하나입니다. 장기 체류 외국인 엔지니어 케이스가 있어 영어 안내 가능 일정 사전 협의가 필요한 경우가 있습니다.</p>
</section>

<section class="block">
<h2>진주·양산 — 도심·외곽 권역</h2>
<p>진주(평거·신안) 일대는 가정 방문 비중이 높고, 양산은 부산 노포·물금 인접 권역으로 부산 권역과 함께 안내되는 사례가 있습니다.</p>
</section>

<section class="block">
<h2>경남에서 예약 시 안내사항</h2>
<ul class="check-list">
<li>거제 장기 출장 정기 예약은 주차별 사전 확인이 필요합니다.</li>
<li>김해공항 환승 단시간 코스는 60분을 권합니다.</li>
<li>창원~거제 이동은 1시간 이상 소요됩니다.</li>
<li>양산 일부는 부산 권역과 함께 안내됩니다.</li>
</ul>
</section>

<section class="block">
<h2>경남 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>거제 옥포 출장 중인데 영어 안내가 가능한가요?</summary><p>모든 케이스 보장되지 않으며, 영어 안내 가능 일정으로 사전 협의가 필요합니다. 상담 시 미리 알려 주시면 가능 여부를 안내합니다.</p></details>
<details><summary>김해공항에서 환승 시간 3시간 가능할까요?</summary><p>3시간이면 공항 인접 호텔 60분 코스 진행이 가능한 편입니다. 보안검색·체크인 시간을 함께 계산해 주세요.</p></details>
<details><summary>양산은 부산 권역으로 받을 수 있나요?</summary><p>양산 일부 권역(물금·동면)은 부산 인접으로 함께 안내되는 사례가 있습니다. 자세한 가능 여부는 상담 시 확인됩니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/area/busan/">부산 안내</a></li><li><a href="/service/business-trip-massage/">출장마사지 안내</a></li><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li></ul></aside>',
},
{
  "slug": "jeju", "name": "제주", "full": "제주특별자치도",
  "title": "제주 방문 마사지 이용 안내 | 제주시·서귀포·애월·표선 권역 | 바로GO",
  "description": "제주는 휴양 일정과 맞물린 리조트·풀빌라 객실 방문 비중이 가장 높은 지역입니다. 성수기·비수기 가능 시간 차이, 권역별 이용 흐름을 정리했습니다.",
  "h1": "제주 권역별 방문 마사지 이용 안내",
  "lede": "제주는 휴양 일정 중심으로 리조트·풀빌라 객실 방문이 압도적인 비중을 차지하는 지역입니다. 성수기·비수기, 동·서·남 권역에 따라 흐름이 분명히 달라집니다.",
  "body": """
<section class="block">
<h2>제주 권역 구성</h2>
<p>제주는 (1) 제주시 — 공항·시내 호텔, (2) 서귀포 — 리조트·관광, (3) 애월·한림 — 서부 펜션, (4) 함덕·세화·성산 — 동부 펜션, (5) 표선·남원 — 남부 휴양 권역으로 나뉩니다.</p>
</section>

<section class="block">
<h2>제주시 — 공항·시내 호텔</h2>
<p>제주시 연동·노형·이도(롯데시티호텔·메종글래드·라마다 등) 일대는 입·출도 일정과 맞물려 객실 방문이 자주 안내됩니다. 도착 당일·출도 전날 시간대 문의가 가장 많습니다.</p>
</section>

<section class="block">
<h2>서귀포 — 리조트·풀빌라 권역</h2>
<p>중문관광단지(롯데호텔 제주·신라호텔 제주·하얏트·해비치 등)는 휴양 일정 중심으로 평일 저녁·주말 객실 방문 비중이 가장 큰 권역입니다. 풀빌라 단지는 객동 구조와 진입로 확인이 필요한 사례가 있습니다.</p>
</section>

<section class="block">
<h2>애월·함덕·성산 — 펜션·게스트하우스 권역</h2>
<p>서부 애월·한림과 동부 함덕·세화·성산 일대는 펜션·풀빌라·게스트하우스 위주 권역입니다. 진입로가 좁거나 차량 진입이 제한되는 경우가 있어 사전 확인이 필요합니다.</p>
</section>

<section class="block">
<h2>제주 성수기 안내</h2>
<ul class="check-list">
<li>7~8월 여름 휴가철, 5월 황금연휴, 10월 단풍·축제 시즌은 사전 예약이 강력히 권장됩니다.</li>
<li>풀빌라는 객동 구조와 진입로(차량 진입) 정보를 함께 확인합니다.</li>
<li>외국인 휴양객 케이스는 사전 안내가 필요한 경우가 있습니다.</li>
<li>제주 동·서 이동(1시간 이상) 시 시간 여유가 필요합니다.</li>
</ul>
</section>

<section class="block">
<h2>제주 방문 마사지 FAQ</h2>
<div class="faq">
<details><summary>중문 신라호텔 풀빌라에서 받을 수 있나요?</summary><p>가능합니다. 풀빌라 객동 호수와 체크인 정보를 함께 확인하며 진입 동선 안내가 필요한 경우가 있습니다.</p></details>
<details><summary>애월 펜션 진입로가 좁은데 가능한가요?</summary><p>차량 진입 가능 여부를 사전에 확인합니다. 진입이 어려운 경우 도보 동선 안내가 필요할 수 있습니다.</p></details>
<details><summary>도착 당일 늦은 시간 가능한가요?</summary><p>제주공항 입도 일정 후 시내 호텔 객실 방문이 자주 안내됩니다. 성수기에는 가능 시간이 빠르게 마감되니 사전 예약을 권합니다.</p></details>
</div>
</section>
""",
  "related": '<aside class="related"><h2>함께 보면 좋은 안내</h2><ul><li><a href="/service/hotel-massage/">호텔 방문 마사지</a></li><li><a href="/service/aroma/">아로마 마사지</a></li><li><a href="/reservation/how-to-book/">예약 방법</a></li></ul></aside>',
},
]

# Per-region "quick facts" strip — 4 short, scannable stats shown directly
# under the hero. Values are written, not derived, so each region has its own
# voice on the strip (e.g. 부산=관광 호텔↑, 울산=장기 출장 재방문, 세종=가정 비중↑).
REGION_FACTS = {
  "seoul":     [("권역", "6개 권역"), ("주요 시간대", "평일 저녁~심야"), ("호텔/가정", "강남·도심 호텔↑"), ("특이점", "심야 가능 권역 존재")],
  "gyeonggi":  [("권역", "4개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "신도시 가정·산업 호텔"), ("특이점", "광역 이동료 발생")],
  "incheon":   [("권역", "3개 권역"), ("주요 시간대", "환승·평일 저녁"), ("호텔/가정", "공항·송도 호텔↑"), ("특이점", "단시간 코스 비중")],
  "busan":     [("권역", "3개 권역"), ("주요 시간대", "야간·주말"), ("호텔/가정", "관광 호텔 압도적"), ("성수기", "여름·연말 사전 예약")],
  "daegu":     [("권역", "4개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "수성 가정·도심 호텔"), ("시즌", "여름 폭염 야간 권장")],
  "daejeon":   [("권역", "4개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "유성·둔산 호텔↑"), ("특이점", "연구단지 출장")],
  "gwangju":   [("권역", "4개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "가정 방문 비중↑"), ("특이점", "상무지구 컨벤션")],
  "ulsan":     [("권역", "5개 권역"), ("주요 시간대", "평일 야간"), ("호텔/가정", "산업단지 호텔 압도적"), ("특이점", "장기 출장 재방문")],
  "sejong":    [("권역", "5개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "가정 비중↑(호텔 적음)"), ("특이점", "정부청사 인접")],
  "gangwon":   [("권역", "영동·영서 2축"), ("주요 시간대", "시즌별 변동"), ("호텔/가정", "관광 객실 비중↑"), ("성수기", "여름·겨울 사전 예약")],
  "chungbuk":  [("권역", "5개 권역"), ("주요 시간대", "환승·평일 저녁"), ("호텔/가정", "오송·청주 호텔↑"), ("특이점", "KTX 단시간 코스")],
  "chungnam":  [("권역", "4개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "산업 호텔·해안 펜션"), ("특이점", "권역별 이동 분리")],
  "jeonbuk":   [("권역", "4개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "한옥·역세권 혼합"), ("특이점", "익산 KTX 환승")],
  "jeonnam":   [("권역", "5개 권역"), ("주요 시간대", "야간"), ("호텔/가정", "여수 야경 호텔↑"), ("성수기", "축제 시즌 사전 예약")],
  "gyeongbuk": [("권역", "5개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "산업·관광 양분"), ("성수기", "경주 봄·가을 마감 빠름")],
  "gyeongnam": [("권역", "5개 권역"), ("주요 시간대", "평일 저녁"), ("호텔/가정", "거제 산업·김해 환승"), ("특이점", "장기 외국인 케이스")],
  "jeju":      [("권역", "5개 권역"), ("주요 시간대", "휴양 일정 기반"), ("호텔/가정", "리조트·풀빌라 압도적"), ("성수기", "휴가철 사전 예약 필수")],
}


def _region_facts_html(slug):
    facts = REGION_FACTS.get(slug, [])
    if not facts:
        return ""
    items = "".join(
        f'<div class="region-fact"><span class="region-fact-label">{label}</span>'
        f'<span class="region-fact-value">{value}</span></div>'
        for label, value in facts
    )
    return f'<div class="region-facts" role="list" aria-label="권역 요약">{items}</div>'


def _region_cta_html(name):
    return (
        '<aside class="region-cta">'
        f'<div class="region-cta-text"><h3>{name} 권역 바로 상담</h3>'
        '<p>예약 가능 시간·코스·이동 가능 권역은 전화 상담에서 안내드립니다.</p></div>'
        '<a class="region-cta-btn" href="tel:0508-202-4719">'
        '<span class="region-cta-btn-label">예약 전화</span>'
        '<span class="region-cta-btn-num">0508-202-4719</span></a>'
        '</aside>'
    )


# Per-region hero CTA copy — short, region-specific headline shown inside the
# hero card right above the phone button. Each line names actual districts so
# the CTA reads as a designer-written tagline, not generic boilerplate.
REGION_HERO_CTA = {
  "seoul":     "권역 6곳 가능 시간이 모두 다른 서울, 바로 상담",
  "gyeonggi":  "31개 시·군의 경기, 권역 분리해 정확히 안내",
  "incheon":   "공항 환승부터 송도 출장까지, 단시간 코스도 가능",
  "busan":     "해운대·광안 관광 호텔 야간 케어, 사전 예약 권장",
  "daegu":     "수성 가정·동성로 호텔, 권역별 가능 시간 안내",
  "daejeon":   "유성 연구단지·둔산 출장, 일정에 맞춰 상담",
  "gwangju":   "상무·첨단·수완 평일 저녁, 가정·호텔 모두 안내",
  "ulsan":     "산업단지 야간·장기 출장 재방문, 정기 예약 가능",
  "sejong":    "정부청사 인근 평일 저녁, 가정 방문 중심 안내",
  "gangwon":   "강릉·속초·평창 시즌 객실 케어, 사전 예약 권장",
  "chungbuk":  "오송 KTX·청주공항 환승, 단시간 코스부터 가능",
  "chungnam":  "천안 KTX 산업·태안 펜션, 권역 분리해 안내",
  "jeonbuk":   "전주 한옥·익산 KTX·새만금, 권역별 일정 안내",
  "jeonnam":   "여수 야경·순천·광양, 권역마다 다른 가능 시간",
  "gyeongbuk": "포항·경주·구미·안동 네 권역 모두 가능",
  "gyeongnam": "거제 조선소·김해공항, 출장 일정에 맞춰 상담",
  "jeju":      "제주시·서귀포·애월·함덕 휴양 객실 케어 안내",
}


def _region_hero_cta_html(slug):
    headline = REGION_HERO_CTA.get(
        slug, "전화로 권역·가능 시간을 바로 안내드립니다"
    )
    return (
        '<div class="region-hero-cta">'
        '<div class="region-hero-cta-text">'
        f'<strong class="region-hero-cta-headline">{headline}</strong>'
        '<span class="region-hero-cta-sub">'
        '<span class="dot-live"></span>'
        '전화로 권역·가능 시간·코스를 바로 안내드립니다 · 24시간 상담'
        '</span>'
        '</div>'
        '<a class="region-hero-tel" '
        'href="tel:0508-202-4719" '
        'aria-label="예약 전화 0508-202-4719">'
        '<span class="region-hero-tel-icon" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round">'
        '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 '
        '19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3'
        'a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 '
        '9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 '
        '2.81.7A2 2 0 0 1 22 16.92z"/>'
        '</svg>'
        '</span>'
        '<span class="region-hero-tel-text">'
        '<span class="region-hero-tel-label">예약 전화 · 24시간</span>'
        '<span class="region-hero-tel-num">0508-202-4719</span>'
        '</span>'
        '</a>'
        '</div>'
    )


for r in REGIONS:
    add(
        path=f"area/{r['slug']}/index.html",
        url=f"/area/{r['slug']}/",
        slug=f"area-{r['slug']}",
        title=r["title"],
        description=r["description"],
        h1=r["h1"],
        intro=f'<p class="lede">{r["lede"]}</p>' + _region_hero_cta_html(r["slug"]),
        breadcrumbs=[("홈", "/"), ("지역별 찾기", "/area/"), (r["name"], f"/area/{r['slug']}/")],
        body=_region_facts_html(r["slug"]) + r["body"] + _region_cta_html(r["name"]),
        related=r["related"],
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
