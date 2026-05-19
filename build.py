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
import re
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


# Per-region full administrative-district list. Shown right after the
# quick-facts strip so users can immediately see every 시·군·구 that the
# region page covers. Grouped (시/군 or 신도시/구도심 or 제주시/서귀포시)
# where the distinction is meaningful; otherwise a single flat list.
REGION_DISTRICTS = {
  "seoul": {
    "headline": "서울 25개 자치구",
    "note": "서울 전체 자치구에서 안내가 가능합니다. 시간대·이동 가능 여부는 권역별로 달라집니다.",
    "groups": [
      {"label": None, "items": [
        "강남구","강동구","강북구","강서구","관악구",
        "광진구","구로구","금천구","노원구","도봉구",
        "동대문구","동작구","마포구","서대문구","서초구",
        "성동구","성북구","송파구","양천구","영등포구",
        "용산구","은평구","종로구","중구","중랑구",
      ]},
    ],
  },
  "gyeonggi": {
    "headline": "경기 31개 시·군",
    "note": "31개 시·군 전체에서 안내됩니다. 권역(동남·서남·서북·동북) 간 이동 시 시간·요금 차이가 있어 권역별 확인이 필요합니다.",
    "groups": [
      {"label": "시 · 28", "items": [
        "수원시","성남시","의정부시","안양시","부천시","광명시","평택시","동두천시",
        "안산시","고양시","과천시","구리시","남양주시","오산시","시흥시","군포시",
        "의왕시","하남시","용인시","파주시","이천시","안성시","김포시","화성시",
        "광주시","양주시","포천시","여주시",
      ]},
      {"label": "군 · 3", "items": ["연천군","가평군","양평군"]},
    ],
  },
  "incheon": {
    "headline": "인천 10개 구·군",
    "note": "인천 전체 구·군에서 안내됩니다. 강화·옹진 등 도서 권역은 사전 협의가 필요한 경우가 있습니다.",
    "groups": [
      {"label": "구 · 8", "items": ["중구","동구","미추홀구","연수구","남동구","부평구","계양구","서구"]},
      {"label": "군 · 2", "items": ["강화군","옹진군"]},
    ],
  },
  "busan": {
    "headline": "부산 16개 구·군",
    "note": "부산 전체 구·군에서 안내됩니다. 관광 성수기는 해운대·광안 권역의 가능 시간이 빠르게 마감됩니다.",
    "groups": [
      {"label": "구 · 15", "items": [
        "중구","서구","동구","영도구","부산진구","동래구","남구","북구",
        "해운대구","사하구","금정구","강서구","연제구","수영구","사상구",
      ]},
      {"label": "군 · 1", "items": ["기장군"]},
    ],
  },
  "daegu": {
    "headline": "대구 9개 구·군",
    "note": "대구 전체 구·군에서 안내됩니다. 2023년 7월부터 군위군이 대구에 편입되어 함께 운영됩니다.",
    "groups": [
      {"label": "구 · 7", "items": ["중구","동구","서구","남구","북구","수성구","달서구"]},
      {"label": "군 · 2", "items": ["달성군","군위군"]},
    ],
  },
  "daejeon": {
    "headline": "대전 5개 구",
    "note": "대전 전체 구에서 안내됩니다. 유성·둔산 권역은 호텔·연구단지 출장 비중이 높은 편입니다.",
    "groups": [
      {"label": None, "items": ["동구","중구","서구","유성구","대덕구"]},
    ],
  },
  "gwangju": {
    "headline": "광주 5개 구",
    "note": "광주 전체 구에서 안내됩니다. 상무·첨단·수완 권역의 평일 저녁 시간대 문의가 가장 많습니다.",
    "groups": [
      {"label": None, "items": ["동구","서구","남구","북구","광산구"]},
    ],
  },
  "ulsan": {
    "headline": "울산 5개 구·군",
    "note": "울산 전체 구·군에서 안내됩니다. 산업단지가 위치한 동구·북구·울주 권역이 출장 케어 중심을 이룹니다.",
    "groups": [
      {"label": "구 · 4", "items": ["중구","남구","동구","북구"]},
      {"label": "군 · 1", "items": ["울주군"]},
    ],
  },
  "sejong": {
    "headline": "세종 행정 권역",
    "note": "세종 신도시 행정동과 구도심 읍·면 전체에서 안내됩니다. 본 신도시 권역의 평일 저녁 시간대 비중이 높습니다.",
    "groups": [
      {"label": "신도시 행정동 · 17", "items": [
        "한솔동","새롬동","다정동","도담동","어진동","종촌동","아름동","고운동",
        "보람동","대평동","소담동","반곡동","해밀동","산울동","합강동","나성동","가람동",
      ]},
      {"label": "구도심 읍·면 · 10", "items": [
        "조치원읍","연기면","연동면","부강면","금남면","장군면","연서면","전의면","전동면","소정면",
      ]},
    ],
  },
  "gangwon": {
    "headline": "강원 18개 시·군",
    "note": "강원 전체 시·군에서 안내됩니다. 백두대간을 사이에 둔 영동·영서 권역은 이동 시간 차이가 큽니다.",
    "groups": [
      {"label": "시 · 7", "items": ["춘천시","원주시","강릉시","동해시","태백시","속초시","삼척시"]},
      {"label": "군 · 11", "items": [
        "홍천군","횡성군","영월군","평창군","정선군","철원군","화천군","양구군","인제군","고성군","양양군",
      ]},
    ],
  },
  "chungbuk": {
    "headline": "충북 11개 시·군",
    "note": "충북 전체 시·군에서 안내됩니다. 청주·오송 등 교통 결절 권역에서 환승 단시간 코스 문의가 많습니다.",
    "groups": [
      {"label": "시 · 3", "items": ["청주시","충주시","제천시"]},
      {"label": "군 · 8", "items": ["보은군","옥천군","영동군","증평군","진천군","괴산군","음성군","단양군"]},
    ],
  },
  "chungnam": {
    "headline": "충남 15개 시·군",
    "note": "충남 전체 시·군에서 안내됩니다. 동부(천안·아산) 산업 권역과 서부(서산·당진·태안) 해안 권역은 권역을 분리해 확인합니다.",
    "groups": [
      {"label": "시 · 8", "items": ["천안시","공주시","보령시","아산시","서산시","논산시","계룡시","당진시"]},
      {"label": "군 · 7", "items": ["금산군","부여군","서천군","청양군","홍성군","예산군","태안군"]},
    ],
  },
  "jeonbuk": {
    "headline": "전북 14개 시·군",
    "note": "전북 전체 시·군에서 안내됩니다. 전주·익산·군산 도심 권역과 군 단위 외곽 권역은 가능 시간 흐름이 다릅니다.",
    "groups": [
      {"label": "시 · 6", "items": ["전주시","군산시","익산시","정읍시","남원시","김제시"]},
      {"label": "군 · 8", "items": ["완주군","진안군","무주군","장수군","임실군","순창군","고창군","부안군"]},
    ],
  },
  "jeonnam": {
    "headline": "전남 22개 시·군",
    "note": "전남 전체 시·군에서 안내됩니다. 여수·순천·광양·목포 도심 권역과 도서·외곽 군 단위는 권역 분리가 자연스럽습니다.",
    "groups": [
      {"label": "시 · 5", "items": ["목포시","여수시","순천시","나주시","광양시"]},
      {"label": "군 · 17", "items": [
        "담양군","곡성군","구례군","고흥군","보성군","화순군","장흥군","강진군","해남군",
        "영암군","무안군","함평군","영광군","장성군","완도군","진도군","신안군",
      ]},
    ],
  },
  "gyeongbuk": {
    "headline": "경북 22개 시·군",
    "note": "경북 전체 시·군에서 안내됩니다. 포항·구미(산업)와 경주·안동(관광) 등 권역 성격이 분명히 갈립니다.",
    "groups": [
      {"label": "시 · 10", "items": [
        "포항시","경주시","김천시","안동시","구미시","영주시","영천시","상주시","문경시","경산시",
      ]},
      {"label": "군 · 12", "items": [
        "의성군","청송군","영양군","영덕군","청도군","고령군","성주군","칠곡군",
        "예천군","봉화군","울진군","울릉군",
      ]},
    ],
  },
  "gyeongnam": {
    "headline": "경남 18개 시·군",
    "note": "경남 전체 시·군에서 안내됩니다. 창원·김해·거제·진주 4개 도심 권역은 성격이 모두 다릅니다.",
    "groups": [
      {"label": "시 · 8", "items": ["창원시","진주시","통영시","사천시","김해시","밀양시","거제시","양산시"]},
      {"label": "군 · 10", "items": [
        "의령군","함안군","창녕군","고성군","남해군","하동군","산청군","함양군","거창군","합천군",
      ]},
    ],
  },
  "jeju": {
    "headline": "제주 2개 시 · 전 권역",
    "note": "제주시·서귀포시 전 권역에서 안내됩니다. 휴양 일정 중심의 리조트·풀빌라 객실 방문이 가장 많은 패턴입니다.",
    "groups": [
      {"label": "제주시 권역", "items": [
        "노형동","연동","이도동","일도동","삼도동","용담동","화북동","삼양동",
        "봉개동","아라동","오라동","외도동","이호동","도두동",
        "한림읍","애월읍","구좌읍","조천읍","한경면","추자면","우도면",
      ]},
      {"label": "서귀포시 권역", "items": [
        "송산동","정방동","중앙동","천지동","효돈동","영천동","동홍동","서홍동",
        "대륜동","대천동","중문동","예래동",
        "대정읍","남원읍","성산읍","안덕면","표선면",
      ]},
    ],
  },
}


def _district_chip_href(parent_slug, name):
    """If a 2차 leaf page exists for this district, return its href; else None."""
    return DISTRICT_PAGE_INDEX.get((parent_slug, name)) if "DISTRICT_PAGE_INDEX" in globals() else None


def _region_districts_html(slug):
    data = REGION_DISTRICTS.get(slug)
    if not data:
        return ""
    groups_html = ""
    for g in data["groups"]:
        chips = []
        for name in g["items"]:
            href = _district_chip_href(slug, name)
            if href:
                chips.append(
                    f'<li class="has-link">'
                    f'<a href="{href}">{name}'
                    '<span class="region-districts-grid-arrow" aria-hidden="true">→</span>'
                    '</a></li>'
                )
            else:
                chips.append(f"<li>{name}</li>")
        items_html = "".join(chips)
        label_html = (
            f'<h3 class="region-districts-group-label">'
            f'<span>{g["label"]}</span></h3>'
            if g.get("label") else ""
        )
        groups_html += (
            '<div class="region-districts-group">'
            f'{label_html}'
            f'<ul class="region-districts-grid">{items_html}</ul>'
            '</div>'
        )
    return (
        '<section class="region-districts" aria-label="행정구역 전체">'
        '<header class="region-districts-head">'
        '<span class="region-districts-eyebrow">'
        '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
        '행정구역 전체'
        '</span>'
        f'<h2 class="region-districts-headline">{data["headline"]}</h2>'
        f'<p class="region-districts-note">{data["note"]}</p>'
        '</header>'
        f'<div class="region-districts-body">{groups_html}</div>'
        '</section>'
    )


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
        '<span class="region-hero-tel-label">24시간 예약 전화</span>'
        '<span class="region-hero-tel-num">0508-202-4719</span>'
        '</span>'
        '</a>'
        '</div>'
    )


# Pre-declared chip-link index for 2차 leaf pages. Each tuple is
# (parent_region_slug, district_name_korean) → district page URL.
# Populated here so _region_districts_html() can attach hrefs during the
# REGIONS loop body assembly (which runs before _build_seoul_districts).
DISTRICT_PAGE_INDEX = {
    ("seoul", "강남구"):    "/area/seoul/gangnam/",
    ("seoul", "강동구"):    "/area/seoul/gangdong/",
    ("seoul", "강북구"):    "/area/seoul/gangbuk/",
    ("seoul", "강서구"):    "/area/seoul/gangseo/",
    ("seoul", "관악구"):    "/area/seoul/gwanak/",
    ("seoul", "광진구"):    "/area/seoul/gwangjin/",
    ("seoul", "구로구"):    "/area/seoul/guro/",
    ("seoul", "금천구"):    "/area/seoul/geumcheon/",
    ("seoul", "노원구"):    "/area/seoul/nowon/",
    ("seoul", "도봉구"):    "/area/seoul/dobong/",
    ("seoul", "동대문구"):  "/area/seoul/dongdaemun/",
    ("seoul", "동작구"):    "/area/seoul/dongjak/",
    ("seoul", "마포구"):    "/area/seoul/mapo/",
    ("seoul", "서대문구"):  "/area/seoul/seodaemun/",
    ("seoul", "서초구"):    "/area/seoul/seocho/",
    ("seoul", "성동구"):    "/area/seoul/seongdong/",
    ("seoul", "성북구"):    "/area/seoul/seongbuk/",
    ("seoul", "송파구"):    "/area/seoul/songpa/",
    ("seoul", "양천구"):    "/area/seoul/yangcheon/",
    ("seoul", "영등포구"):  "/area/seoul/yeongdeungpo/",
    ("seoul", "용산구"):    "/area/seoul/yongsan/",
    ("seoul", "은평구"):    "/area/seoul/eunpyeong/",
    ("seoul", "종로구"):    "/area/seoul/jongno/",
    ("seoul", "중구"):      "/area/seoul/junggu/",
    ("seoul", "중랑구"):    "/area/seoul/jungnang/",

    ("gyeonggi", "수원시"):    "/area/gyeonggi/suwon/",
    ("gyeonggi", "성남시"):    "/area/gyeonggi/seongnam/",
    ("gyeonggi", "의정부시"):  "/area/gyeonggi/uijeongbu/",
    ("gyeonggi", "안양시"):    "/area/gyeonggi/anyang/",
    ("gyeonggi", "부천시"):    "/area/gyeonggi/bucheon/",
    ("gyeonggi", "광명시"):    "/area/gyeonggi/gwangmyeong/",
    ("gyeonggi", "평택시"):    "/area/gyeonggi/pyeongtaek/",
    ("gyeonggi", "동두천시"):  "/area/gyeonggi/dongducheon/",
    ("gyeonggi", "안산시"):    "/area/gyeonggi/ansan/",
    ("gyeonggi", "고양시"):    "/area/gyeonggi/goyang/",
    ("gyeonggi", "과천시"):    "/area/gyeonggi/gwacheon/",
    ("gyeonggi", "구리시"):    "/area/gyeonggi/guri/",
    ("gyeonggi", "남양주시"):  "/area/gyeonggi/namyangju/",
    ("gyeonggi", "오산시"):    "/area/gyeonggi/osan/",
    ("gyeonggi", "시흥시"):    "/area/gyeonggi/siheung/",
    ("gyeonggi", "군포시"):    "/area/gyeonggi/gunpo/",
    ("gyeonggi", "의왕시"):    "/area/gyeonggi/uiwang/",
    ("gyeonggi", "하남시"):    "/area/gyeonggi/hanam/",
    ("gyeonggi", "용인시"):    "/area/gyeonggi/yongin/",
    ("gyeonggi", "파주시"):    "/area/gyeonggi/paju/",
    ("gyeonggi", "이천시"):    "/area/gyeonggi/icheon/",
    ("gyeonggi", "안성시"):    "/area/gyeonggi/anseong/",
    ("gyeonggi", "김포시"):    "/area/gyeonggi/gimpo/",
    ("gyeonggi", "화성시"):    "/area/gyeonggi/hwaseong/",
    ("gyeonggi", "광주시"):    "/area/gyeonggi/gwangju-si/",
    ("gyeonggi", "양주시"):    "/area/gyeonggi/yangju/",
    ("gyeonggi", "포천시"):    "/area/gyeonggi/pocheon/",
    ("gyeonggi", "여주시"):    "/area/gyeonggi/yeoju/",
    ("gyeonggi", "연천군"):    "/area/gyeonggi/yeoncheon/",
    ("gyeonggi", "가평군"):    "/area/gyeonggi/gapyeong/",
    ("gyeonggi", "양평군"):    "/area/gyeonggi/yangpyeong/",

    ("busan","중구"):"/area/busan/jung/", ("busan","서구"):"/area/busan/seo/", ("busan","동구"):"/area/busan/dong/",
    ("busan","영도구"):"/area/busan/yeongdo/", ("busan","부산진구"):"/area/busan/busanjin/", ("busan","동래구"):"/area/busan/dongnae/",
    ("busan","남구"):"/area/busan/nam/", ("busan","북구"):"/area/busan/buk/", ("busan","해운대구"):"/area/busan/haeundae/",
    ("busan","사하구"):"/area/busan/saha/", ("busan","금정구"):"/area/busan/geumjeong/", ("busan","강서구"):"/area/busan/gangseo/",
    ("busan","연제구"):"/area/busan/yeonje/", ("busan","수영구"):"/area/busan/suyeong/", ("busan","사상구"):"/area/busan/sasang/",
    ("busan","기장군"):"/area/busan/gijang/",

    ("incheon","중구"):"/area/incheon/jung/", ("incheon","동구"):"/area/incheon/dong/", ("incheon","미추홀구"):"/area/incheon/michuhol/",
    ("incheon","연수구"):"/area/incheon/yeonsu/", ("incheon","남동구"):"/area/incheon/nam-dong/", ("incheon","부평구"):"/area/incheon/bupyeong/",
    ("incheon","계양구"):"/area/incheon/gyeyang/", ("incheon","서구"):"/area/incheon/seo/",
    ("incheon","강화군"):"/area/incheon/ganghwa/", ("incheon","옹진군"):"/area/incheon/ongjin/",

    ("daegu","중구"):"/area/daegu/jung/", ("daegu","동구"):"/area/daegu/dong/", ("daegu","서구"):"/area/daegu/seo/",
    ("daegu","남구"):"/area/daegu/nam/", ("daegu","북구"):"/area/daegu/buk/", ("daegu","수성구"):"/area/daegu/suseong/",
    ("daegu","달서구"):"/area/daegu/dalseo/", ("daegu","달성군"):"/area/daegu/dalseong/", ("daegu","군위군"):"/area/daegu/gunwi/",

    ("daejeon","동구"):"/area/daejeon/dong/", ("daejeon","중구"):"/area/daejeon/jung/", ("daejeon","서구"):"/area/daejeon/seo/",
    ("daejeon","유성구"):"/area/daejeon/yuseong/", ("daejeon","대덕구"):"/area/daejeon/daedeok/",

    ("gwangju","동구"):"/area/gwangju/dong/", ("gwangju","서구"):"/area/gwangju/seo/", ("gwangju","남구"):"/area/gwangju/nam/",
    ("gwangju","북구"):"/area/gwangju/buk/", ("gwangju","광산구"):"/area/gwangju/gwangsan/",

    ("ulsan","중구"):"/area/ulsan/jung/", ("ulsan","남구"):"/area/ulsan/nam/", ("ulsan","동구"):"/area/ulsan/dong/",
    ("ulsan","북구"):"/area/ulsan/buk/", ("ulsan","울주군"):"/area/ulsan/ulju/",

    ("gangwon","춘천시"):"/area/gangwon/chuncheon/", ("gangwon","원주시"):"/area/gangwon/wonju/",
    ("gangwon","강릉시"):"/area/gangwon/gangneung/", ("gangwon","동해시"):"/area/gangwon/donghae/",
    ("gangwon","태백시"):"/area/gangwon/taebaek/", ("gangwon","속초시"):"/area/gangwon/sokcho/",
    ("gangwon","삼척시"):"/area/gangwon/samcheok/", ("gangwon","홍천군"):"/area/gangwon/hongcheon/",
    ("gangwon","횡성군"):"/area/gangwon/hoengseong/", ("gangwon","영월군"):"/area/gangwon/yeongwol/",
    ("gangwon","평창군"):"/area/gangwon/pyeongchang/", ("gangwon","정선군"):"/area/gangwon/jeongseon/",
    ("gangwon","철원군"):"/area/gangwon/cheorwon/", ("gangwon","화천군"):"/area/gangwon/hwacheon/",
    ("gangwon","양구군"):"/area/gangwon/yanggu/", ("gangwon","인제군"):"/area/gangwon/inje/",
    ("gangwon","고성군"):"/area/gangwon/goseong/", ("gangwon","양양군"):"/area/gangwon/yangyang/",

    ("chungbuk","청주시"):"/area/chungbuk/cheongju/", ("chungbuk","충주시"):"/area/chungbuk/chungju/",
    ("chungbuk","제천시"):"/area/chungbuk/jecheon/", ("chungbuk","보은군"):"/area/chungbuk/boeun/",
    ("chungbuk","옥천군"):"/area/chungbuk/okcheon/", ("chungbuk","영동군"):"/area/chungbuk/yeongdong/",
    ("chungbuk","증평군"):"/area/chungbuk/jeungpyeong/", ("chungbuk","진천군"):"/area/chungbuk/jincheon/",
    ("chungbuk","괴산군"):"/area/chungbuk/goesan/", ("chungbuk","음성군"):"/area/chungbuk/eumseong/",
    ("chungbuk","단양군"):"/area/chungbuk/danyang/",

    ("chungnam","천안시"):"/area/chungnam/cheonan/", ("chungnam","공주시"):"/area/chungnam/gongju/",
    ("chungnam","보령시"):"/area/chungnam/boryeong/", ("chungnam","아산시"):"/area/chungnam/asan/",
    ("chungnam","서산시"):"/area/chungnam/seosan/", ("chungnam","논산시"):"/area/chungnam/nonsan/",
    ("chungnam","계룡시"):"/area/chungnam/gyeryong/", ("chungnam","당진시"):"/area/chungnam/dangjin/",
    ("chungnam","금산군"):"/area/chungnam/geumsan/", ("chungnam","부여군"):"/area/chungnam/buyeo/",
    ("chungnam","서천군"):"/area/chungnam/seocheon/", ("chungnam","청양군"):"/area/chungnam/cheongyang/",
    ("chungnam","홍성군"):"/area/chungnam/hongseong/", ("chungnam","예산군"):"/area/chungnam/yesan/",
    ("chungnam","태안군"):"/area/chungnam/taean/",

    ("jeonbuk","전주시"):"/area/jeonbuk/jeonju/", ("jeonbuk","군산시"):"/area/jeonbuk/gunsan/",
    ("jeonbuk","익산시"):"/area/jeonbuk/iksan/", ("jeonbuk","정읍시"):"/area/jeonbuk/jeongeup/",
    ("jeonbuk","남원시"):"/area/jeonbuk/namwon/", ("jeonbuk","김제시"):"/area/jeonbuk/gimje/",
    ("jeonbuk","완주군"):"/area/jeonbuk/wanju/", ("jeonbuk","진안군"):"/area/jeonbuk/jinan/",
    ("jeonbuk","무주군"):"/area/jeonbuk/muju/", ("jeonbuk","장수군"):"/area/jeonbuk/jangsu/",
    ("jeonbuk","임실군"):"/area/jeonbuk/imsil/", ("jeonbuk","순창군"):"/area/jeonbuk/sunchang/",
    ("jeonbuk","고창군"):"/area/jeonbuk/gochang/", ("jeonbuk","부안군"):"/area/jeonbuk/buan/",

    ("jeonnam","목포시"):"/area/jeonnam/mokpo/", ("jeonnam","여수시"):"/area/jeonnam/yeosu/",
    ("jeonnam","순천시"):"/area/jeonnam/suncheon/", ("jeonnam","나주시"):"/area/jeonnam/naju/",
    ("jeonnam","광양시"):"/area/jeonnam/gwangyang/", ("jeonnam","담양군"):"/area/jeonnam/damyang/",
    ("jeonnam","곡성군"):"/area/jeonnam/gokseong/", ("jeonnam","구례군"):"/area/jeonnam/gurye/",
    ("jeonnam","고흥군"):"/area/jeonnam/goheung/", ("jeonnam","보성군"):"/area/jeonnam/boseong/",
    ("jeonnam","화순군"):"/area/jeonnam/hwasun/", ("jeonnam","장흥군"):"/area/jeonnam/jangheung/",
    ("jeonnam","강진군"):"/area/jeonnam/gangjin/", ("jeonnam","해남군"):"/area/jeonnam/haenam/",
    ("jeonnam","영암군"):"/area/jeonnam/yeongam/", ("jeonnam","무안군"):"/area/jeonnam/muan/",
    ("jeonnam","함평군"):"/area/jeonnam/hampyeong/", ("jeonnam","영광군"):"/area/jeonnam/yeonggwang/",
    ("jeonnam","장성군"):"/area/jeonnam/jangseong/", ("jeonnam","완도군"):"/area/jeonnam/wando/",
    ("jeonnam","진도군"):"/area/jeonnam/jindo/", ("jeonnam","신안군"):"/area/jeonnam/sinan/",

    ("gyeongbuk","포항시"):"/area/gyeongbuk/pohang/", ("gyeongbuk","경주시"):"/area/gyeongbuk/gyeongju/",
    ("gyeongbuk","김천시"):"/area/gyeongbuk/gimcheon/", ("gyeongbuk","안동시"):"/area/gyeongbuk/andong/",
    ("gyeongbuk","구미시"):"/area/gyeongbuk/gumi/", ("gyeongbuk","영주시"):"/area/gyeongbuk/yeongju/",
    ("gyeongbuk","영천시"):"/area/gyeongbuk/yeongcheon/", ("gyeongbuk","상주시"):"/area/gyeongbuk/sangju/",
    ("gyeongbuk","문경시"):"/area/gyeongbuk/mungyeong/", ("gyeongbuk","경산시"):"/area/gyeongbuk/gyeongsan/",
    ("gyeongbuk","의성군"):"/area/gyeongbuk/uiseong/", ("gyeongbuk","청송군"):"/area/gyeongbuk/cheongsong/",
    ("gyeongbuk","영양군"):"/area/gyeongbuk/yeongyang/", ("gyeongbuk","영덕군"):"/area/gyeongbuk/yeongdeok/",
    ("gyeongbuk","청도군"):"/area/gyeongbuk/cheongdo/", ("gyeongbuk","고령군"):"/area/gyeongbuk/goryeong/",
    ("gyeongbuk","성주군"):"/area/gyeongbuk/seongju/", ("gyeongbuk","칠곡군"):"/area/gyeongbuk/chilgok/",
    ("gyeongbuk","예천군"):"/area/gyeongbuk/yecheon/", ("gyeongbuk","봉화군"):"/area/gyeongbuk/bonghwa/",
    ("gyeongbuk","울진군"):"/area/gyeongbuk/uljin/", ("gyeongbuk","울릉군"):"/area/gyeongbuk/ulleung/",

    ("gyeongnam","창원시"):"/area/gyeongnam/changwon/", ("gyeongnam","진주시"):"/area/gyeongnam/jinju/",
    ("gyeongnam","통영시"):"/area/gyeongnam/tongyeong/", ("gyeongnam","사천시"):"/area/gyeongnam/sacheon/",
    ("gyeongnam","김해시"):"/area/gyeongnam/gimhae/", ("gyeongnam","밀양시"):"/area/gyeongnam/miryang/",
    ("gyeongnam","거제시"):"/area/gyeongnam/geoje/", ("gyeongnam","양산시"):"/area/gyeongnam/yangsan/",
    ("gyeongnam","의령군"):"/area/gyeongnam/uiryeong/", ("gyeongnam","함안군"):"/area/gyeongnam/haman/",
    ("gyeongnam","창녕군"):"/area/gyeongnam/changnyeong/", ("gyeongnam","고성군"):"/area/gyeongnam/goseong-nam/",
    ("gyeongnam","남해군"):"/area/gyeongnam/namhae/", ("gyeongnam","하동군"):"/area/gyeongnam/hadong/",
    ("gyeongnam","산청군"):"/area/gyeongnam/sancheong/", ("gyeongnam","함양군"):"/area/gyeongnam/hamyang/",
    ("gyeongnam","거창군"):"/area/gyeongnam/geochang/", ("gyeongnam","합천군"):"/area/gyeongnam/hapcheon/",

    ("jeju","제주시"):"/area/jeju/jeju-si/", ("jeju","서귀포시"):"/area/jeju/seogwipo/",
}


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
        body=(
            _region_facts_html(r["slug"])
            + _region_districts_html(r["slug"])
            + r["body"]
            + _region_cta_html(r["name"])
        ),
        related=r["related"],
    )


# ============================================================
# 3차 영역 — 2차 시·군·구 페이지 (자치구 → 행정동 / 시 → 구·동)
# ============================================================
# 각 페이지는 다음 구조를 따릅니다.
#   - Hero (지역명 H1 + 지역 고유 lede)
#   - Hero CTA (지역명 들어간 카피 + 0508-202-4719 버튼)
#   - 4개 quick-facts
#   - 행정동/구 전체 카드
#   - 권역 특성 (지역 고유 prose, 실제 랜드마크 언급)
#   - 이용 시간·예약 패턴 (지역 고유 prose)
#   - 3개 지역 고유 FAQ
#   - 하단 CTA + 관련 자치구 링크
# 모든 prose는 지역 고유 사실(주요 호텔/단지/산업/관광지)을 인용해
# 도어웨이 패턴을 피합니다.

SEOUL_DISTRICTS = [
  {"slug":"gangnam","name":"강남구",
   "lede":"강남구는 강남대로·테헤란로의 비즈니스 호텔과 압구정·청담 부티크 호텔이 함께 모인 자치구입니다. 평일 야간·심야 시간대 객실 방문 비중이 서울에서 가장 두드러지는 권역입니다.",
   "facts":[("행정동","22개"),("주요 시간대","야간·심야"),("호텔/가정","호텔 비중↑↑"),("심야","일부 권역 가능")],
   "dongs":["신사동","논현1동","논현2동","압구정동","청담동","삼성1동","삼성2동","대치1동","대치2동","대치4동","역삼1동","역삼2동","도곡1동","도곡2동","개포1동","개포2동","개포4동","세곡동","일원본동","일원1동","수서동","율현동"],
   "character":"테헤란로(역삼·삼성)에는 그랜드 인터컨티넨탈·인터컨티넨탈 코엑스·파크 하얏트 서울·르 메르디앙 서울·라마다 강남 등 대형 체인이 밀집해 평일 비즈니스 출장 종료 후 객실 방문이 가장 자주 안내됩니다. 압구정·청담은 글래드 강남·임피리얼 팰리스·라까사 등 부티크 호텔에서 관광·휴양 일정 후 야간 케어 문의가 많고, 도곡·대치 일대는 주거 권역이라 가정 방문이 함께 들어옵니다.",
   "pattern":"강남구는 다른 자치구 대비 자정 이후 가능 사례가 많은 권역입니다. 호텔 방문은 객실 호수·체크인 명의 사전 확인이 함께 진행되며, 토요일 밤~일요일 새벽 시간대는 가능 시간이 빠르게 마감되는 편입니다.",
   "faqs":[
     ("강남역 호텔에서 자정 이후 가능한가요?","강남구는 자정 이후 시간대 가능 사례가 다른 권역보다 많습니다. 객실 정보와 체크인 일정 사전 확인을 거쳐 진행합니다."),
     ("압구정·청담 부티크 호텔도 안내되나요?","네, 압구정·청담 일대 부티크 호텔 객실 방문이 자주 안내됩니다. 일부 호텔은 외부 방문객 동선 정책이 있어 사전 확인이 필요합니다."),
     ("같은 시간에 강남·서초 모두 가능한가요?","권역 간 이동 시간이 있어 같은 시간대 동시 진행은 어려운 경우가 많습니다. 권역별로 예약 시간을 분리하는 것을 권합니다."),
   ],
   "neighbors":["서초구","송파구","용산구"]},

  {"slug":"gangdong","name":"강동구",
   "lede":"강동구는 천호·둔촌·고덕·상일 일대 대단지 아파트가 밀집한 주거 중심 자치구입니다. 평일 저녁 가정 방문 비중이 호텔 객실 방문보다 큰 권역입니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","대단지 재건축")],
   "dongs":["강일동","상일제1동","상일제2동","명일제1동","명일제2동","고덕제1동","고덕제2동","암사제1동","암사제2동","암사제3동","천호제1동","천호제2동","천호제3동","성내제1동","성내제2동","성내제3동","길동","둔촌제1동"],
   "character":"올림픽파크포레온(둔촌주공 재건축)과 고덕 그라시움·아르테온·롯데캐슬, 강일 미사강변 등 대단지가 밀집한 강동구는 평일 저녁~밤 가정 방문 비중이 가장 큰 자치구 중 하나입니다. 천호역 일대는 직장인·1인 가구 비중이 함께 있어 평일 저녁 7~10시 시간대 문의가 가장 안정적이며, 호텔 객실 방문은 천호·고덕 일부 비즈니스 호텔에서 안내됩니다.",
   "pattern":"강동구는 평일 저녁(7~10시) 시간대 가능 폭이 가장 넓습니다. 주말은 가족 일정과 겹치는 저녁 6~8시 시간대를 피해 늦은 저녁(밤 9시 이후)으로 안내드리는 편입니다.",
   "faqs":[
     ("둔촌 올림픽파크포레온 입주 단지 가능한가요?","대단지 가정 방문이 자주 안내됩니다. 입주 단지마다 외부 방문객 출입·차량 등록 정책이 다르므로 사전 확인이 필요합니다."),
     ("강동구 내 호텔 방문 가능한 곳이 있나요?","강동은 호텔 자체가 적은 권역이라 천호·고덕 일대 일부 비즈니스 호텔에서 객실 방문이 안내됩니다."),
     ("하남 미사 권역과 동시 가능한가요?","강동~하남 미사는 행정상 다른 권역으로, 같은 시간대 두 권역 동시 진행은 어렵습니다. 각각 사전 예약이 필요합니다."),
   ],
   "neighbors":["송파구","광진구","중랑구"]},

  {"slug":"gangbuk","name":"강북구",
   "lede":"강북구는 미아·수유·번동 일대의 주거 권역으로, 강북 본연의 생활권 색이 짙은 자치구입니다. 호텔 객실 방문보다 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","북한산 인접")],
   "dongs":["삼양동","미아동","송중동","송천동","삼각산동","번1동","번2동","번3동","수유1동","수유2동","수유3동","인수동","우이동"],
   "character":"강북구는 미아사거리·수유역·우이동 일대의 주거 단지 가정 방문이 중심을 이룹니다. 우이동·인수동은 북한산 인접 권역이라 가족 일정·여가 일정 후 가정 케어 문의가 들어오고, 미아·수유는 평일 저녁 직장인 가정 방문 비중이 큽니다. 강북구는 비즈니스 호텔이 적어 객실 방문 비중은 낮은 편입니다.",
   "pattern":"강북구는 평일 저녁 7~10시 시간대 비중이 가장 큽니다. 외곽 권역(우이·인수) 일부는 시간대에 따라 가능 시간이 빠르게 마감되는 편이어서 사전 예약을 권장합니다.",
   "faqs":[
     ("강북구 외곽(우이·인수)도 안내되나요?","우이·인수동 일대 가정 방문이 안내됩니다. 외곽 권역은 평일 늦은 저녁 시간대 마감이 빠른 편이라 사전 예약을 권합니다."),
     ("강북구 내 호텔 방문이 가능한가요?","강북은 호텔 인프라가 적은 권역이라 객실 방문 사례는 제한적입니다. 가정 방문이 일반적입니다."),
     ("도봉·노원과 같은 권역으로 묶이나요?","강북·도봉·노원은 인접 권역으로 분류되지만 행정상 별도이며, 가능 시간은 각 자치구별로 사전 확인이 필요합니다."),
   ],
   "neighbors":["도봉구","노원구","성북구"]},

  {"slug":"gangseo","name":"강서구",
   "lede":"강서구는 김포공항과 마곡지구가 함께 있는 자치구로, 공항 인접 호텔 단시간 코스와 마곡 비즈니스 출장 케어가 함께 안내되는 권역입니다.",
   "facts":[("행정동","20개"),("주요 시간대","평일 저녁·환승"),("호텔/가정","공항권 호텔↑"),("특이점","김포공항·마곡지구")],
   "dongs":["염창동","등촌1동","등촌2동","등촌3동","화곡본동","화곡1동","화곡2동","화곡3동","화곡4동","화곡6동","화곡8동","가양1동","가양2동","가양3동","발산1동","우장산동","공항동","방화1동","방화2동","방화3동"],
   "character":"김포공항 인근 호텔(롯데시티호텔 김포공항·메이필드 호텔·코트야드 메리어트 서울 보타닉파크)은 환승·국내선 일정과 맞물려 단시간 코스 문의가 자주 들어옵니다. 마곡지구(LG사이언스파크·코오롱·이마트·홈앤쇼핑) 일대 비즈니스 호텔에서 평일 저녁 객실 방문이 안내되며, 화곡·발산·우장산 일대는 가정 방문 비중이 함께 큽니다.",
   "pattern":"공항 인접 호텔은 환승 일정에 맞춘 60·90분 단시간 코스 문의가 많고, 마곡은 평일 저녁 7~10시 시간대 비중이 큽니다. 김포공항~인천공항 환승 일정은 이동 시간 사전 확인이 필요합니다.",
   "faqs":[
     ("김포공항 환승 2시간 가능한가요?","환승 2시간이면 이동·체크인 시간 제외 60분 코스가 빠듯할 수 있습니다. 공항 인접 호텔 체크인 일정이 확정된 경우를 권합니다."),
     ("마곡지구 비즈니스 호텔에서 가능한가요?","마곡 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다. 평일 저녁 출장 종료 후가 일반적입니다."),
     ("화곡·발산 권역도 평일 저녁 가능한가요?","가능합니다. 화곡·발산·우장산 일대 가정 방문이 평일 저녁 시간대 가장 자주 안내됩니다."),
   ],
   "neighbors":["양천구","영등포구","마포구"]},

  {"slug":"gwanak","name":"관악구",
   "lede":"관악구는 신림·봉천·서울대 일대의 1인 가구·대학생 권역과 사당·낙성대 도심 인접 권역이 함께 있는 자치구입니다. 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","1인 가구 많음")],
   "dongs":["보라매동","청림동","성현동","행운동","낙성대동","청룡동","은천동","중앙동","인헌동","남현동","신림동","신사동","조원동","미성동","난곡동","난향동","서원동","신원동","서림동","삼성동","대학동"],
   "character":"신림역·봉천역·서울대입구역 일대는 대학생·청년 1인 가구가 밀집한 권역으로 평일 저녁 가정 방문 비중이 큽니다. 사당·낙성대 일대는 직장인 주거가 함께 있어 야간 시간대 안내도 안정적이며, 관악구 자체는 호텔 인프라가 적어 객실 방문 비중은 낮습니다.",
   "pattern":"관악구는 평일 저녁 7~11시 시간대가 가장 안정적입니다. 신림·봉천 일대 원룸·오피스텔이 많아 진입 동선·엘리베이터 호수 등 사전 확인이 도움이 됩니다.",
   "faqs":[
     ("신림역 원룸·오피스텔에서 가능한가요?","신림·봉천 일대 원룸·오피스텔 가정 방문이 자주 안내됩니다. 진입 동선과 호수 사전 확인이 필요합니다."),
     ("관악구 내 호텔 방문이 가능한가요?","관악은 호텔 자체가 적어 객실 방문 사례는 제한적입니다. 인근 동작·서초 권역 호텔을 함께 살펴보시는 것을 권합니다."),
     ("서울대 인근(대학동) 가능한가요?","대학동·낙성대 일대 가정 방문이 안내됩니다. 단 외곽 시간대 마감이 빠른 편이어서 사전 예약이 좋습니다."),
   ],
   "neighbors":["동작구","서초구","구로구"]},

  {"slug":"gwangjin","name":"광진구",
   "lede":"광진구는 광장동·자양동 한강변 호텔과 건대입구·구의 직장인 권역이 함께 있는 자치구입니다. 평일 저녁 가정·호텔 방문이 균형 있게 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","워커힐·건대 권역")],
   "dongs":["화양동","군자동","중곡1동","중곡2동","중곡3동","중곡4동","능동","구의1동","구의2동","구의3동","광장동","자양1동","자양2동","자양3동","자양4동"],
   "character":"광장동 워커힐(그랜드 워커힐 서울·비스타 워커힐 서울)은 한강변 5성 호텔로 휴양·출장 일정 후 야간 객실 방문이 자주 안내됩니다. 건대입구역·자양·구의 일대는 직장인·1인 가구 권역으로 평일 저녁 가정 방문이 활발하며, 화양·군자·중곡은 가정 방문 중심입니다.",
   "pattern":"워커힐 객실 방문은 사전 객실 호수 확인이 필수이며, 건대·자양 권역은 평일 저녁 7~10시 시간대가 가장 안정적입니다. 광장동~강남 권역은 별도 동선이라 권역 분리가 자연스럽습니다.",
   "faqs":[
     ("워커힐 호텔에서 가능한가요?","그랜드 워커힐 서울·비스타 워커힐 서울 객실 방문이 안내됩니다. 객실 호수와 체크인 정보를 사전 확인합니다."),
     ("건대입구 오피스텔에서 가능한가요?","건대·자양 일대 오피스텔·원룸 가정 방문이 자주 안내됩니다. 평일 저녁 시간대 비중이 큽니다."),
     ("광진~강남 동시에 가능한가요?","권역 간 이동 시간이 있어 같은 시간대 동시 진행은 어려운 경우가 일반적입니다. 권역별 예약을 분리하는 것을 권합니다."),
   ],
   "neighbors":["성동구","강동구","중랑구"]},

  {"slug":"guro","name":"구로구",
   "lede":"구로구는 구로디지털단지·신도림 권역의 IT·업무지구와 고척·개봉 주거 권역이 함께 있는 자치구입니다. 평일 저녁 야근 후 가정·호텔 방문이 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","IT 단지·신도림")],
   "dongs":["신도림동","구로1동","구로2동","구로3동","구로4동","구로5동","가리봉동","고척1동","고척2동","개봉1동","개봉2동","개봉3동","오류1동","오류2동","수궁동"],
   "character":"구로디지털단지(G밸리)는 IT 기업 야근 일정과 맞물려 평일 저녁~밤 시간대 가정 방문 비중이 큽니다. 신도림역 일대는 비즈니스 호텔(쉐라톤 서울 디큐브시티)에서 객실 방문이 안내되며, 고척·개봉·오류 일대는 주거 권역으로 가정 방문이 자주 들어옵니다.",
   "pattern":"구로구는 평일 저녁 8~11시 시간대(야근 후) 비중이 큽니다. 신도림역 호텔은 KTX·지하철 환승 동선과 가까워 단시간 코스 문의도 자주 안내됩니다.",
   "faqs":[
     ("구로디지털단지 야근 후 가능한가요?","평일 야근 후 가정 방문이 자주 안내됩니다. 단지 내 오피스 방문은 보안 정책상 일반적으로 권하지 않으며, 인근 자택이나 호텔로 안내드리는 편입니다."),
     ("신도림 쉐라톤 디큐브시티 가능한가요?","신도림역 쉐라톤 객실 방문이 안내됩니다. 객실 호수·체크인 정보 사전 확인이 필요합니다."),
     ("가산디지털단지(금천)와 같은 권역인가요?","구로·금천 디지털단지는 인접하지만 행정상 별도 자치구입니다. 가산은 <a href=\"/area/seoul/geumcheon/\">금천구 안내</a>를 참고해 주세요."),
   ],
   "neighbors":["금천구","영등포구","양천구"]},

  {"slug":"geumcheon","name":"금천구",
   "lede":"금천구는 가산디지털단지를 중심으로 한 IT·산업 권역과 시흥동 주거 권역이 함께 있는 자치구입니다. 평일 야간 IT 종사자 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 야간"),("호텔/가정","혼합"),("특이점","가산디지털단지")],
   "dongs":["가산동","독산1동","독산2동","독산3동","독산4동","시흥1동","시흥2동","시흥3동","시흥4동","시흥5동"],
   "character":"가산디지털단지는 G밸리 핵심 권역으로 IT·게임·바이오 기업이 밀집해 평일 야근 후 가정 방문 비중이 큽니다. 가산역 일대 비즈니스 호텔(롯데시티호텔 가산디지털·머큐어 앰배서더 서울 가산)에서 객실 방문이 자주 안내되며, 독산·시흥 일대는 주거 권역으로 가정 방문이 들어옵니다.",
   "pattern":"금천구는 평일 야간(9~11시) 시간대 비중이 큽니다. 가산 호텔 객실 방문은 사전 객실 정보 확인이 필요하며, 출장객 단기 체류 일정과 자주 맞물립니다.",
   "faqs":[
     ("가산 롯데시티호텔에서 가능한가요?","가산 롯데시티호텔·머큐어 가산 객실 방문이 안내됩니다. 출장 일정에 맞춘 평일 저녁 시간대 비중이 큽니다."),
     ("독산·시흥 주거 권역도 안내되나요?","독산·시흥 일대 아파트·오피스텔 가정 방문이 평일 저녁 시간대 자주 안내됩니다."),
     ("구로 디지털단지(G밸리)와 같은 권역인가요?","가산·구로 디지털단지는 인접하지만 자치구가 다릅니다. 구로는 <a href=\"/area/seoul/guro/\">구로구 안내</a>를 참고해 주세요."),
   ],
   "neighbors":["구로구","영등포구","관악구"]},

  {"slug":"nowon","name":"노원구",
   "lede":"노원구는 상계·중계·하계·공릉 일대의 대단지 아파트와 학원가가 밀집한 주거 중심 자치구입니다. 평일 저녁·주말 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","대단지·학원가")],
   "dongs":["월계1동","월계2동","월계3동","공릉1동","공릉2동","하계1동","하계2동","중계본동","중계1동","중계4동","중계2·3동","상계1동","상계2동","상계3·4동","상계5동","상계6·7동","상계8동","상계9동","상계10동"],
   "character":"노원구는 상계 주공·중계동 은행사거리 학원가·공릉 한국과학기술원 일대를 중심으로 대단지 아파트가 밀집한 자치구입니다. 평일 저녁 가정 방문 비중이 가장 크고, 주말 가족 일정과 겹치는 시간대는 사전 예약이 권장됩니다. 호텔 인프라가 적어 객실 방문 비중은 낮습니다.",
   "pattern":"노원구는 평일 저녁 7~10시 시간대가 가장 안정적입니다. 학원가 주거 권역 특성상 주말 오전·오후는 가족 일정 비중이 커서 늦은 저녁 시간대를 권합니다.",
   "faqs":[
     ("중계 은행사거리 학원가 인근 가정 방문 가능한가요?","중계·하계 일대 가정 방문이 자주 안내됩니다. 평일 저녁 시간대 비중이 가장 큽니다."),
     ("노원구 내 호텔 방문 가능한 곳이 있나요?","노원은 호텔 인프라가 적어 객실 방문 비중은 낮습니다. 가정 방문이 일반적입니다."),
     ("의정부·구리 권역과 함께 가능한가요?","노원~의정부·구리는 인접하지만 행정상 다른 권역입니다. 각각 사전 예약이 필요합니다."),
   ],
   "neighbors":["도봉구","강북구","중랑구"]},

  {"slug":"dobong","name":"도봉구",
   "lede":"도봉구는 창동·방학·쌍문 일대의 대단지 아파트와 도봉산 인접 주거 권역으로 이루어진 자치구입니다. 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","도봉산 인접")],
   "dongs":["쌍문1동","쌍문2동","쌍문3동","쌍문4동","방학1동","방학2동","방학3동","창1동","창2동","창3동","창4동","창5동","도봉1동","도봉2동"],
   "character":"도봉구는 창동 주공·방학·쌍문 주거 단지 가정 방문이 중심을 이룹니다. 도봉산·북한산 인접 권역(도봉동)은 주말 등산·자연 일정 후 컨디션 회복 케어 문의도 들어옵니다. 호텔 인프라가 적어 객실 방문 비중은 낮은 편입니다.",
   "pattern":"도봉구는 평일 저녁 7~10시 시간대가 가장 안정적입니다. 외곽(도봉동·우이동 인근) 시간대는 마감이 빠른 편이라 사전 예약을 권합니다.",
   "faqs":[
     ("창동 주공 단지에서 가능한가요?","창1~5동 일대 대단지 가정 방문이 자주 안내됩니다. 입주 단지마다 외부 방문객 출입 정책이 다르니 사전 확인이 좋습니다."),
     ("도봉산 등산 후 회복 케어 가능한가요?","도봉동 권역에서 등산·자연 일정 후 회복 목적의 케어 안내가 들어옵니다. <a href=\"/service/sports-massage/\">스포츠 마사지</a>가 자주 권해집니다."),
     ("강북·노원과 같은 권역인가요?","도봉·강북·노원은 인접 권역이지만 행정상 별도이며, 가능 시간은 각각 사전 확인이 필요합니다."),
   ],
   "neighbors":["강북구","노원구","은평구"]},

  {"slug":"dongdaemun","name":"동대문구",
   "lede":"동대문구는 청량리역·회기·답십리 일대의 도심 인접 권역과 외대·시립대 등 대학가가 함께 있는 자치구입니다. 평일 저녁 가정 방문과 도심 호텔 객실 방문이 혼합됩니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","청량리·대학가")],
   "dongs":["용신동","제기동","전농1동","전농2동","답십리1동","답십리2동","장안1동","장안2동","청량리동","회기동","휘경1동","휘경2동","이문1동","이문2동"],
   "character":"청량리역 일대는 KTX 강릉선·중앙선 환승 거점으로 비즈니스 호텔(롯데캐슬·청량리역 GS자이) 인근 객실 방문이 안내됩니다. 회기·이문은 외대·경희대·시립대 학생·연구원 권역으로 평일 저녁 가정 방문 비중이 크고, 답십리·장안은 일반 주거 권역입니다.",
   "pattern":"청량리역 KTX 환승 일정과 맞물린 단시간 코스 문의가 있으며, 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("청량리역 환승 일정에 가능한가요?","청량리역 KTX 일정과 맞물린 단시간 코스 안내가 가능합니다. 환승 시간이 2시간 이상 확보된 경우를 권합니다."),
     ("외대·경희대 인근 가능한가요?","회기·이문 일대 가정 방문이 자주 안내됩니다."),
     ("동대문역사문화공원(중구) 권역과 다른가요?","DDP 권역은 행정상 중구입니다. 동대문구와 별도 권역이니 중구 안내를 참고해 주세요."),
   ],
   "neighbors":["중랑구","성북구","성동구"]},

  {"slug":"dongjak","name":"동작구",
   "lede":"동작구는 노량진 학원가·사당역·흑석 주거가 함께 있는 자치구입니다. 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","노량진 학원가")],
   "dongs":["노량진1동","노량진2동","상도1동","상도2동","상도3동","상도4동","흑석동","사당1동","사당2동","사당3동","사당4동","사당5동","대방동","신대방1동","신대방2동"],
   "character":"노량진은 공무원·고시 학원가가 밀집해 1인 가구 비중이 크고, 흑석동은 중앙대 인근 주거 권역입니다. 사당역 일대는 직장인 주거가 많아 평일 저녁 가정 방문이 가장 자주 안내됩니다. 동작구는 호텔 인프라가 적어 객실 방문 비중은 낮습니다.",
   "pattern":"동작구는 평일 저녁 7~10시 시간대 가능 폭이 가장 넓고, 사당역·노량진 일대 원룸·오피스텔 가정 방문이 자주 들어옵니다.",
   "faqs":[
     ("노량진 고시원·원룸 가능한가요?","노량진 원룸·오피스텔 가정 방문이 안내됩니다. 일부 고시원은 외부 방문객 출입 정책상 제한이 있을 수 있어 사전 확인이 좋습니다."),
     ("사당역에서 평일 저녁 가능한가요?","사당역 일대 가정 방문이 평일 저녁 시간대 가장 안정적으로 안내됩니다."),
     ("동작~서초 권역 동시에 가능한가요?","동작·서초는 인접 권역이나 같은 시간대 두 권역 진행은 어려운 경우가 많습니다. 권역별 예약 분리가 자연스럽습니다."),
   ],
   "neighbors":["관악구","서초구","영등포구"]},

  {"slug":"mapo","name":"마포구",
   "lede":"마포구는 홍대·합정·망원·상암 권역의 직장인·미디어 종사자 주거가 밀집한 자치구입니다. 평일 저녁 가정 방문 비중이 크고, 상암 DMC 출장 호텔 방문도 함께 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","DMC·홍대 권역")],
   "dongs":["공덕동","아현동","도화동","용강동","대흥동","염리동","신수동","서강동","서교동","합정동","망원1동","망원2동","연남동","성산1동","성산2동","상암동"],
   "character":"홍대·합정·연남·망원은 직장인·1인 가구·프리랜서 비중이 큰 주거 권역으로 평일 저녁 가정 방문이 가장 자주 안내됩니다. 상암 DMC(MBC·SBS·YTN·CJ ENM)는 미디어 종사자 출장과 야근 일정이 많아 인근 비즈니스 호텔(스탠포드 호텔·글래드 마포)에서 객실 방문이 함께 안내됩니다. 공덕·아현은 도심 직장인 권역입니다.",
   "pattern":"마포구는 평일 야간(9~12시) 시간대 비중이 다른 자치구보다 큽니다. 상암 DMC 출장 케어는 평일 야근 종료 후 호텔 객실 방문이 일반적입니다.",
   "faqs":[
     ("DMC 일정 야근 후 가능한가요?","상암 DMC 인근 호텔 객실 방문이 자주 안내됩니다. 평일 야근 종료 후 시간대가 가장 안정적입니다."),
     ("연남·망원 1인 가구 가능한가요?","연남·망원 일대 원룸·오피스텔 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("홍대 인근 호텔에서도 가능한가요?","홍대·합정 일대 비즈니스 호텔 객실 방문이 안내됩니다. 객실 호수·체크인 정보 사전 확인이 필요합니다."),
   ],
   "neighbors":["서대문구","용산구","영등포구"]},

  {"slug":"seodaemun","name":"서대문구",
   "lede":"서대문구는 신촌·연희·홍제 일대 대학가와 주거 권역이 함께 있는 자치구입니다. 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","연세·이화 대학가")],
   "dongs":["천연동","북아현동","충현동","신촌동","연희동","홍제1동","홍제2동","홍제3동","홍은1동","홍은2동","남가좌1동","남가좌2동","북가좌1동","북가좌2동"],
   "character":"신촌·연희는 연세대·이화여대 인근 권역으로 대학생·연구원·직장인 가정 방문 비중이 큽니다. 홍제·홍은은 일반 주거 권역이며 가정 방문 중심이고, 신촌역 일대는 비즈니스 호텔(스카이파크 센트럴·BW 프리미어 서울 가든)에서 객실 방문이 함께 안내됩니다.",
   "pattern":"서대문구는 평일 저녁 7~10시 시간대가 가장 안정적입니다. 신촌·연희 대학가는 학기 중·방학 시기에 따라 흐름이 약간 다릅니다.",
   "faqs":[
     ("신촌역 비즈니스 호텔 가능한가요?","신촌역 일대 비즈니스 호텔 객실 방문이 안내됩니다. 객실 정보 사전 확인이 필요합니다."),
     ("연희동·이대 인근 1인 가구 가능한가요?","연희·신촌 일대 원룸·오피스텔 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("홍제·홍은 외곽도 가능한가요?","홍제·홍은 일대 주거 권역 가정 방문이 평일 저녁 시간대 안내됩니다."),
   ],
   "neighbors":["마포구","종로구","은평구"]},

  {"slug":"seocho","name":"서초구",
   "lede":"서초구는 강남역 남쪽 비즈니스 권역과 반포·잠원·방배 주거 권역이 함께 있는 자치구입니다. 평일 야간 호텔 객실 방문과 가정 방문이 모두 활발한 권역입니다.",
   "facts":[("행정동","18개"),("주요 시간대","야간"),("호텔/가정","혼합 비중↑"),("특이점","법조타운·반포")],
   "dongs":["서초1동","서초2동","서초3동","서초4동","잠원동","반포본동","반포1동","반포2동","반포3동","반포4동","방배본동","방배1동","방배2동","방배3동","방배4동","양재1동","양재2동","내곡동"],
   "character":"서초구는 강남대로 남쪽(서초·양재)의 비즈니스 호텔(JW 메리어트 서울·반포 메리어트 등), 반포·잠원 일대의 한강변 주거 단지(아크로리버파크·반포자이), 방배의 고급 주거 권역이 함께 있는 자치구입니다. 법조타운(법원·검찰청) 인근은 평일 저녁 직장인 가정 방문 비중이 크고, 호텔 객실 방문은 야간 비중이 강남구 다음으로 높습니다.",
   "pattern":"서초구는 야간·심야 시간대 가능 사례가 강남구와 함께 많은 권역입니다. 호텔 방문은 객실 호수·체크인 정보 사전 확인이 필요합니다.",
   "faqs":[
     ("반포 JW 메리어트 가능한가요?","반포 JW 메리어트·메리어트 호텔 객실 방문이 안내됩니다. 객실 정보 사전 확인이 필요합니다."),
     ("아크로리버파크·반포자이 가능한가요?","반포·잠원 일대 대단지 가정 방문이 자주 안내됩니다. 단지 내 외부 방문객 출입 정책 사전 확인이 좋습니다."),
     ("강남구·서초구 동시에 가능한가요?","두 자치구는 인접하지만 같은 시간대 동시 진행은 어려운 경우가 많습니다. 권역별 예약 분리를 권합니다."),
   ],
   "neighbors":["강남구","동작구","용산구"]},

  {"slug":"seongdong","name":"성동구",
   "lede":"성동구는 성수·왕십리·옥수 일대의 신흥 도심 권역과 한강변 주거가 함께 있는 자치구입니다. 평일 저녁 가정 방문과 트렌드 권역 호텔 방문이 함께 안내됩니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","성수·왕십리 트렌드")],
   "dongs":["왕십리도선동","왕십리2동","마장동","사근동","행당1동","행당2동","응봉동","금호1가동","금호2·3가동","금호4가동","옥수동","성수1가1동","성수1가2동","성수2가1동","성수2가3동","송정동","용답동"],
   "character":"성수동(성수1가·2가)은 카페·라이프스타일 트렌드 권역으로 떠오르며 1인 가구·직장인·프리랜서 비중이 큽니다. 왕십리는 한양대·왕십리역 일대 직장인 주거가 밀집하고, 옥수·금호는 한강변 고급 주거 권역(트리마제·아크로서울포레스트)입니다. 평일 저녁 가정 방문이 중심을 이룹니다.",
   "pattern":"성동구는 평일 저녁 7~11시 시간대가 가장 안정적입니다. 성수동 일대는 트렌드 권역 특성상 야간 시간대 문의도 함께 들어옵니다.",
   "faqs":[
     ("성수동 오피스텔에서 가능한가요?","성수1가·2가 일대 오피스텔·원룸 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("옥수동 트리마제·아크로서울포레스트 가능한가요?","옥수·금호 일대 대단지 가정 방문이 안내됩니다. 단지 내 외부 방문객 출입 정책 사전 확인이 좋습니다."),
     ("왕십리역 환승 일정에 가능한가요?","왕십리역 KTX 환승 일정에 맞춘 단시간 코스 안내가 가능합니다."),
   ],
   "neighbors":["광진구","중구","동대문구"]},

  {"slug":"seongbuk","name":"성북구",
   "lede":"성북구는 정릉·길음·안암 일대의 주거와 대학가가 함께 있는 자치구입니다. 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","20개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","고대·돈암 대학가")],
   "dongs":["성북동","삼선동","동선동","돈암1동","돈암2동","안암동","보문동","정릉1동","정릉2동","정릉3동","정릉4동","길음1동","길음2동","종암동","월곡1동","월곡2동","장위1동","장위2동","장위3동","석관동"],
   "character":"성북구는 고려대(안암·종암)·국민대·서경대 등 대학가가 자리한 권역이며 길음·정릉 일대 대단지 아파트가 밀집해 평일 저녁 가정 방문 비중이 큽니다. 성북동 일부는 외국 공관 거주지로 외부 방문객 동선 정책이 있는 단지가 있어 사전 확인이 필요합니다.",
   "pattern":"성북구는 평일 저녁 7~10시 시간대가 가장 안정적이며, 길음·돈암 일대 대단지 가정 방문 비중이 큽니다.",
   "faqs":[
     ("고려대·안암 인근 가능한가요?","안암·종암 일대 원룸·오피스텔 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("길음 뉴타운 가능한가요?","길음 뉴타운 대단지 가정 방문이 자주 안내됩니다. 단지 내 정책 사전 확인이 좋습니다."),
     ("성북동 일부 단지는 출입 제한이 있나요?","성북동 일부 단지·공관 인근은 외부 방문객 동선 정책이 있어 사전 확인이 필요할 수 있습니다."),
   ],
   "neighbors":["강북구","종로구","동대문구"]},

  {"slug":"songpa","name":"송파구",
   "lede":"송파구는 잠실 일대의 대형 호텔·롯데월드 권역과 가락·문정·잠실 주거 권역이 함께 있는 자치구입니다. 호텔 야간 방문과 가정 방문이 모두 활발한 권역입니다.",
   "facts":[("행정동","27개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑"),("특이점","잠실·롯데월드")],
   "dongs":["풍납1동","풍납2동","거여1동","거여2동","마천1동","마천2동","방이1동","방이2동","오륜동","오금동","송파1동","송파2동","석촌동","삼전동","가락본동","가락1동","가락2동","문정1동","문정2동","장지동","위례동","잠실본동","잠실2동","잠실3동","잠실4동","잠실6동","잠실7동"],
   "character":"잠실 시그니엘 서울(롯데월드타워)·롯데호텔 월드·소피텔 앰배서더 서울 등 대형 5성·4성 호텔이 모인 잠실은 관광·휴양·출장 일정과 맞물려 야간 객실 방문 비중이 가장 큰 권역 중 하나입니다. 가락·문정·장지 일대는 주거 권역으로 가정 방문이 함께 안내되며, 위례신도시(위례동)도 같은 흐름입니다.",
   "pattern":"송파구는 잠실 호텔 야간 시간대(밤 9시~새벽 1시) 비중이 큽니다. 가락·문정 일대 가정 방문은 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("시그니엘 서울 가능한가요?","롯데월드타워 시그니엘 서울 객실 방문이 안내됩니다. 객실 호수·체크인 정보 사전 확인이 필요합니다."),
     ("롯데월드 일정 후 가능한가요?","잠실 일대 호텔에서 관광 일정 종료 후 야간 객실 방문이 자주 안내됩니다."),
     ("위례신도시(위례동) 가능한가요?","위례 일대 가정 방문이 자주 안내됩니다. 위례신도시는 송파·성남·하남 경계에 걸쳐 있으니 행정 동 확인이 좋습니다."),
   ],
   "neighbors":["강남구","강동구","광진구"]},

  {"slug":"yangcheon","name":"양천구",
   "lede":"양천구는 목동·신정 일대의 대단지 아파트와 학원가가 밀집한 주거 중심 자치구입니다. 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","목동 학원가")],
   "dongs":["목1동","목2동","목3동","목4동","목5동","신월1동","신월2동","신월3동","신월4동","신월5동","신월6동","신월7동","신정1동","신정2동","신정3동","신정4동","신정6동","신정7동"],
   "character":"목동(목1~5동) 신시가지 단지와 신정 일대 학원가는 서울 서남권에서 학원가 비중이 가장 큰 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다. 호텔 인프라가 적어 객실 방문 비중은 낮은 편입니다. 신월·신정 외곽 일부는 김포공항 인근 권역과 흐름이 닿아 있습니다.",
   "pattern":"양천구는 평일 저녁 7~10시 시간대가 가장 안정적이며, 학원가 권역 특성상 주말 가족 일정 시간대를 피해 늦은 저녁을 권합니다.",
   "faqs":[
     ("목동 신시가지 가능한가요?","목1~5동 신시가지 단지 가정 방문이 자주 안내됩니다. 단지 내 정책 사전 확인이 좋습니다."),
     ("양천구 내 호텔 방문 가능한 곳이 있나요?","양천은 호텔 인프라가 적은 권역이라 객실 방문 사례는 제한적입니다."),
     ("강서구(김포공항)와 같은 권역인가요?","양천·강서는 인접하지만 행정상 별도 자치구입니다."),
   ],
   "neighbors":["강서구","구로구","영등포구"]},

  {"slug":"yeongdeungpo","name":"영등포구",
   "lede":"영등포구는 여의도 금융 권역과 영등포역·당산 도심이 함께 있는 자치구입니다. 평일 야근 후 야간 시간대 가정·호텔 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","18개"),("주요 시간대","야간"),("호텔/가정","혼합"),("특이점","여의도 금융")],
   "dongs":["영등포본동","영등포동","여의동","당산1동","당산2동","도림동","문래동","양평1동","양평2동","신길1동","신길3동","신길4동","신길5동","신길6동","신길7동","대림1동","대림2동","대림3동"],
   "character":"여의도(여의동)는 금융권·증권사·국회 인근 권역으로 평일 야근 일정과 맞물려 야간 시간대 케어 문의가 일정하게 들어옵니다. 콘래드 서울·페어몬트 앰배서더 서울 등 여의도 5성 호텔에서 객실 방문이 안내되며, 영등포역·당산 일대는 직장인 가정 방문 비중이 큽니다.",
   "pattern":"영등포구는 평일 야간(9시~자정) 시간대 비중이 큽니다. 여의도 금융권 야근 일정에 맞춘 호텔 객실 방문은 사전 객실 정보 확인이 필요합니다.",
   "faqs":[
     ("콘래드 서울에서 가능한가요?","여의도 콘래드 서울·페어몬트 앰배서더 서울 객실 방문이 자주 안내됩니다."),
     ("여의도 오피스 방문도 가능한가요?","오피스 빌딩은 보안 정책상 외부 케어 진행이 일반적으로 어려운 경우가 많아 인근 호텔·자택으로 안내드립니다."),
     ("영등포역 인근에서 가능한가요?","영등포역·당산 일대 비즈니스 호텔 객실 방문과 주거 권역 가정 방문이 모두 안내됩니다."),
   ],
   "neighbors":["마포구","구로구","동작구"]},

  {"slug":"yongsan","name":"용산구",
   "lede":"용산구는 한남·이태원·용산역 일대의 외국인 비중이 높은 호텔·주거 권역으로 이루어진 자치구입니다. 야간 호텔 객실 방문 비중이 강남·송파와 함께 가장 큰 권역입니다.",
   "facts":[("행정동","16개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑↑"),("특이점","한남·이태원")],
   "dongs":["후암동","용산2가동","남영동","청파동","원효로1동","원효로2동","효창동","용문동","한강로동","이촌1동","이촌2동","이태원1동","이태원2동","한남동","서빙고동","보광동"],
   "character":"한남·이태원은 외국인·연예인·고소득 주거 권역으로 그랜드 하얏트 서울·해밀톤 호텔 등 호텔과 더 한남·나인원한남 같은 고급 주거 단지가 모여 있습니다. 용산역(드래곤시티)은 비즈니스·관광 호텔이 밀집해 평일 저녁·주말 객실 방문이 자주 안내되며, 이촌 일대는 한강변 주거 권역입니다.",
   "pattern":"용산구는 야간 시간대 가능 사례가 강남구와 함께 많은 권역입니다. 한남·이태원 호텔은 외국인 케이스가 있어 영어 안내 가능 일정 사전 협의가 필요할 수 있습니다.",
   "faqs":[
     ("그랜드 하얏트 서울에서 가능한가요?","한남 그랜드 하얏트 서울 객실 방문이 안내됩니다. 객실 정보 사전 확인이 필요합니다."),
     ("용산역 드래곤시티 가능한가요?","용산역 드래곤시티 일대 호텔(노보텔 앰배서더·이비스 스타일·그랜드 머큐어) 객실 방문이 자주 안내됩니다."),
     ("이태원에서 영어 안내가 되나요?","외국인 케이스는 영어 안내 가능 일정 사전 협의가 필요합니다. 상담 시 미리 알려 주시면 확인해 드립니다."),
   ],
   "neighbors":["중구","마포구","서초구"]},

  {"slug":"eunpyeong","name":"은평구",
   "lede":"은평구는 은평뉴타운·응암·갈현·진관 일대의 주거 중심 자치구입니다. 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","은평뉴타운")],
   "dongs":["녹번동","불광1동","불광2동","갈현1동","갈현2동","구산동","대조동","응암1동","응암2동","응암3동","역촌동","신사1동","신사2동","증산동","수색동","진관동"],
   "character":"은평뉴타운(진관동)을 중심으로 응암·갈현·불광 일대 대단지가 밀집한 주거 권역으로, 평일 저녁 가정 방문이 가장 자주 안내됩니다. 디지털미디어시티(DMC)와 인접한 수색·증산은 마포 상암 흐름과 닿아 있어 미디어 종사자 케이스도 들어옵니다.",
   "pattern":"은평구는 평일 저녁 7~10시 시간대가 가장 안정적입니다. 진관·갈현 외곽 일부는 시간대에 따라 가능 시간이 빠르게 마감되는 편입니다.",
   "faqs":[
     ("은평뉴타운 진관동 가능한가요?","진관동 일대 대단지 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("DMC(상암) 일정과 묶을 수 있나요?","DMC는 행정상 마포구 상암동이며, 은평 수색·증산과 인접하지만 별도 권역입니다."),
     ("응암·갈현 외곽 가능한가요?","응암·갈현 일대 가정 방문이 평일 저녁 시간대 안내됩니다. 외곽 마감 시간이 빠른 편이라 사전 예약을 권합니다."),
   ],
   "neighbors":["서대문구","마포구","종로구"]},

  {"slug":"jongno","name":"종로구",
   "lede":"종로구는 광화문·종각·인사동 일대의 도심 5성 호텔과 평창·부암 등 한적한 주거 권역이 함께 있는 자치구입니다. 도심 호텔 객실 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","17개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑"),("특이점","도심 5성 호텔")],
   "dongs":["청운효자동","사직동","삼청동","부암동","평창동","무악동","교남동","가회동","종로1·2·3·4가동","종로5·6가동","이화동","혜화동","명륜3가동","창신1동","창신2동","창신3동","숭인1동"],
   "character":"광화문·종각·청계 일대(포시즌스 서울·코트야드 메리어트 서울·노보텔 앰배서더 서울 동대문·JW 메리어트 동대문 인근)는 도심 5성·4성 호텔이 모여 출장·관광 일정 후 객실 방문이 자주 안내됩니다. 가회·삼청·부암·평창은 한옥·고급 주거 권역으로 가정 방문 사례도 있으나 비중은 호텔 대비 낮습니다.",
   "pattern":"종로구는 도심 호텔 야간 시간대(밤 9시~새벽 1시) 비중이 큽니다. 일부 호텔은 외부 방문객 동선 정책이 있어 사전 확인이 필요합니다.",
   "faqs":[
     ("포시즌스 호텔 서울 가능한가요?","광화문 포시즌스 호텔 서울 객실 방문이 안내됩니다. 객실 호수·체크인 정보 사전 확인이 필요합니다."),
     ("관광 일정 후 야간 가능한가요?","경복궁·인사동·북촌 관광 일정 후 도심 호텔 객실 방문이 자주 안내됩니다."),
     ("부암·평창 한옥에서 가능한가요?","부암·평창 일대 일부 한옥·고급 주거 가정 방문이 안내됩니다. 출입 정책 사전 확인이 필요할 수 있습니다."),
   ],
   "neighbors":["중구","서대문구","성북구"]},

  {"slug":"junggu","name":"중구",
   "lede":"중구는 명동·을지로·동대문 일대의 도심 호텔이 가장 밀집한 자치구입니다. 관광·출장 일정과 맞물린 호텔 객실 방문 비중이 종로와 함께 가장 큰 권역입니다.",
   "facts":[("행정동","15개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑↑"),("특이점","명동·DDP")],
   "dongs":["소공동","회현동","명동","필동","장충동","광희동","을지로동","신당동","다산동","약수동","청구동","신당5동","동화동","황학동","중림동"],
   "character":"명동·을지로·소공·회현 일대는 롯데호텔 서울·신라호텔·플라자호텔·웨스틴 조선 서울 등 도심 5성 호텔이 가장 많이 모인 권역입니다. 동대문(DDP·동대문역사문화공원)은 JW 메리어트 동대문·노보텔 앰배서더 동대문에서 관광·출장 일정 후 객실 방문이 자주 안내되며, 신당·황학·청구는 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"중구는 종로와 함께 도심 호텔 야간 시간대 비중이 가장 큰 권역입니다. 호텔 방문은 객실 호수·체크인 명의 사전 확인이 필수입니다.",
   "faqs":[
     ("신라호텔·롯데호텔 서울 가능한가요?","장충 신라호텔, 소공 롯데호텔 서울 객실 방문이 안내됩니다. 객실 정보 사전 확인이 필요합니다."),
     ("DDP·동대문 호텔 가능한가요?","JW 메리어트 동대문·노보텔 앰배서더 동대문 객실 방문이 자주 안내됩니다."),
     ("명동 관광 일정 후 가능한가요?","명동·을지로 일대 호텔에서 관광 일정 후 야간 객실 방문이 자주 안내됩니다."),
   ],
   "neighbors":["종로구","용산구","성동구"]},

  {"slug":"jungnang","name":"중랑구",
   "lede":"중랑구는 면목·중화·묵·망우 일대의 주거 권역으로 이루어진 자치구입니다. 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","주거 밀집")],
   "dongs":["면목본동","면목2동","면목3·8동","면목4동","면목5동","면목7동","상봉1동","상봉2동","중화1동","중화2동","묵1동","묵2동","망우본동","망우3동","신내1동","신내2동"],
   "character":"중랑구는 면목·상봉·중화·묵·망우·신내 일대 주거 단지 가정 방문이 중심입니다. 상봉역·망우역 일대는 KTX 강릉선·중앙선 환승 인접 권역이라 단시간 코스 문의가 일부 들어옵니다. 호텔 인프라는 적어 객실 방문 비중은 낮은 편입니다.",
   "pattern":"중랑구는 평일 저녁 7~10시 시간대가 가장 안정적입니다. 신내·상봉 외곽은 시간대에 따라 마감이 빠른 편이라 사전 예약이 좋습니다.",
   "faqs":[
     ("상봉역 환승 일정에 가능한가요?","상봉역 KTX 강릉선 환승 일정에 맞춘 단시간 코스 문의가 안내됩니다. 환승 시간 2시간 이상 확보된 경우를 권합니다."),
     ("면목·중화 가정 방문 가능한가요?","면목·중화·묵 일대 주거 권역 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("동대문·광진과 같은 권역인가요?","중랑·동대문·광진은 인접하지만 행정상 별도이며, 가능 시간은 각각 사전 확인이 필요합니다."),
   ],
   "neighbors":["동대문구","광진구","노원구"]},
]


# Sanity check: the pre-declared DISTRICT_PAGE_INDEX must agree with the
# actual SEOUL_DISTRICTS data — fail loudly if a slug was renamed.
_expected = {("seoul", d["name"]): f"/area/seoul/{d['slug']}/" for d in SEOUL_DISTRICTS}
_seoul_only_index = {k: v for k, v in DISTRICT_PAGE_INDEX.items() if k[0] == "seoul"}
assert _expected == _seoul_only_index, (
    "DISTRICT_PAGE_INDEX (pre-declared) disagrees with SEOUL_DISTRICTS data. "
    f"missing: {set(_expected) - set(_seoul_only_index)} "
    f"extra: {set(_seoul_only_index) - set(_expected)}"
)


_DONG_DIGIT_RE   = re.compile(r'(?:[0-9·.]|본)+(?=동$)')
_DONG_GA_RE      = re.compile(r'[0-9·.]+(?=가동$)')


def _district_title(name, parent_name, facts):
    """Unique title per district by appending the 4th fact ("특이점"/landmark)."""
    highlight = facts[3][1] if len(facts) >= 4 else None
    if highlight:
        return f"{name} 방문 마사지 안내 · {highlight} | {parent_name} | 바로GO"
    return f"{name} 방문 마사지 이용 안내 | {parent_name} | 바로GO"


def _district_description(lede, name, parent_name, max_len=160):
    """Unique meta description using the district lede; falls back to a
    short opener if lede is empty."""
    if not lede:
        return f"{parent_name} {name} 방문 마사지 이용 정보를 정리한 안내 페이지입니다."
    if len(lede) <= max_len:
        return lede
    cut = lede[:max_len].rsplit('.', 1)[0]
    return cut + ('.' if not cut.endswith('.') else '')

def _consolidate_dongs(dongs):
    """행정동 리스트에서 숫자/본 접미를 단순화하고 중복 제거.

    예: ['논현1동','논현2동','삼성1동','삼성2동','일원본동','일원1동']
        → ['논현동','삼성동','일원동']

    번호 없는 동(압구정동·세곡동 등)·읍·면·구는 그대로 유지.
    """
    seen = set()
    result = []
    for d in dongs:
        new = d
        # repeatedly strip until stable so that '성수1가1동' → '성수가동'
        for _ in range(5):
            old = new
            new = _DONG_DIGIT_RE.sub('', new)
            new = _DONG_GA_RE.sub('', new)
            if new == old:
                break
        if new not in seen:
            seen.add(new)
            result.append(new)
    return result


def _district_facts_html(facts):
    items = "".join(
        f'<div class="region-fact"><span class="region-fact-label">{lbl}</span>'
        f'<span class="region-fact-value">{val}</span></div>'
        for lbl, val in facts
    )
    return f'<div class="region-facts" role="list" aria-label="권역 요약">{items}</div>'


def _district_dong_card_html(name, dongs):
    dongs = _consolidate_dongs(dongs)
    chips = "".join(f"<li>{n}</li>" for n in dongs)
    return (
        '<section class="region-districts" aria-label="행정동 전체">'
        '<header class="region-districts-head">'
        '<span class="region-districts-eyebrow">'
        '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
        '행정동 전체'
        '</span>'
        f'<h2 class="region-districts-headline">{name} {len(dongs)}개 행정동</h2>'
        f'<p class="region-districts-note">{name} 전체 행정동에서 안내가 가능합니다. 시간대·이동 가능 여부는 동별로 다르며, 정확한 가능 시간은 전화 상담에서 확인됩니다.</p>'
        '</header>'
        '<div class="region-districts-body">'
        '<div class="region-districts-group">'
        f'<ul class="region-districts-grid">{chips}</ul>'
        '</div>'
        '</div>'
        '</section>'
    )


def _district_faqs_html(name, faqs):
    rows = "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>"
        for q, a in faqs
    )
    return (
        '<section class="block">'
        f'<h2>{name} 자주 묻는 질문</h2>'
        f'<div class="faq">{rows}</div>'
        '</section>'
    )


def _district_hero_cta_html(name):
    headline = f"{name} 권역 가능 시간 · 전화로 바로 안내드립니다"
    return (
        '<div class="region-hero-cta">'
        '<div class="region-hero-cta-text">'
        f'<strong class="region-hero-cta-headline">{headline}</strong>'
        '<span class="region-hero-cta-sub">'
        '<span class="dot-live"></span>'
        '전화로 행정동·가능 시간·코스를 바로 안내드립니다 · 24시간 상담'
        '</span>'
        '</div>'
        '<a class="region-hero-tel" href="tel:0508-202-4719" '
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
        '<span class="region-hero-tel-label">24시간 예약 전화</span>'
        '<span class="region-hero-tel-num">0508-202-4719</span>'
        '</span>'
        '</a>'
        '</div>'
    )


def _district_neighbor_related_html(parent_slug, parent_name, neighbors):
    items = "".join(
        f'<li><a href="/area/{parent_slug}/{n_slug}/">{n_name}</a></li>'
        for n_name, n_slug in neighbors
    )
    return (
        '<aside class="related">'
        f'<h2>인접 자치구</h2>'
        f'<ul><li><a href="/area/{parent_slug}/">{parent_name} 전체</a></li>{items}</ul>'
        '</aside>'
    )


def _build_seoul_districts():
    name_to_slug = {d["name"]: d["slug"] for d in SEOUL_DISTRICTS}
    for d in SEOUL_DISTRICTS:
        body_parts = [
            _district_facts_html(d["facts"]),
            _district_dong_card_html(d["name"], d["dongs"]),
            '<section class="block">'
            f'<h2>{d["name"]} 권역 특성</h2>'
            f'<p>{d["character"]}</p>'
            '</section>',
            '<section class="block">'
            f'<h2>{d["name"]} 이용 시간 패턴</h2>'
            f'<p>{d["pattern"]}</p>'
            '</section>',
            _district_faqs_html(d["name"], d["faqs"]),
            _region_cta_html(d["name"]),
        ]
        neighbors = [(n, name_to_slug[n]) for n in d["neighbors"] if n in name_to_slug]
        add(
            path=f"area/seoul/{d['slug']}/index.html",
            url=f"/area/seoul/{d['slug']}/",
            slug=f"area-seoul-{d['slug']}",
            title=_district_title(d['name'], "서울", d['facts']),
            description=_district_description(d['lede'], d['name'], "서울"),
            h1=f"{d['name']} 방문 마사지 이용 안내",
            intro=f'<p class="lede">{d["lede"]}</p>' + _district_hero_cta_html(d["name"]),
            breadcrumbs=[
                ("홈", "/"),
                ("지역별 찾기", "/area/"),
                ("서울", "/area/seoul/"),
                (d["name"], f"/area/seoul/{d['slug']}/"),
            ],
            body="".join(body_parts),
            related=_district_neighbor_related_html("seoul", "서울", neighbors),
        )


_build_seoul_districts()


# ------------------------------------------------------------
# 경기도 31 시·군 (수원·성남·고양·용인 등 시 with 구는 sub_label="구")
# ------------------------------------------------------------
GYEONGGI_DISTRICTS = [
  # ---- 시 with 구 (6) — clicking shows 구 list ----
  {"slug":"suwon","name":"수원시","sub_label":"4개 구",
   "lede":"수원시는 삼성전자 본사가 자리한 산업·행정 중심 도시로, 영통·광교·인계 일대의 비즈니스 호텔과 주거 단지에서 평일 저녁 케어 비중이 큽니다.",
   "facts":[("구","4개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","삼성전자 본사")],
   "subs":["장안구","권선구","팔달구","영통구"],
   "character":"영통구(광교·매탄·이의)는 삼성전자 사업장 출장 일정과 맞물려 평일 저녁 호텔 객실 방문 비중이 가장 큰 권역입니다. 팔달구는 수원 화성·행궁동 관광 일정과 라마다 플라자 수원·이비스 앰배서더 등 호텔이 모여 있고, 장안·권선은 주거 권역으로 가정 방문이 자주 안내됩니다.",
   "pattern":"수원시는 평일 저녁 7~10시 시간대 비중이 큽니다. 광교·영통 일대는 야간 시간대도 일부 가능합니다.",
   "faqs":[
     ("광교 호텔에서 가능한가요?","광교 코트야드 메리어트·신라스테이 광교 등 객실 방문이 안내됩니다."),
     ("삼성전자 출장 일정에 가능한가요?","영통구 일대 비즈니스 호텔 객실 방문이 평일 저녁 자주 안내됩니다."),
     ("화성 동탄과 함께 가능한가요?","화성은 별도 권역으로, <a href=\"/area/gyeonggi/hwaseong/\">화성시 안내</a>를 참고해 주세요."),
   ],"neighbors":["seongnam","yongin","hwaseong"]},

  {"slug":"seongnam","name":"성남시","sub_label":"3개 구",
   "lede":"성남시는 판교 테크노밸리·분당 IT 거점과 위례·중원 주거 권역이 함께 있는 시로, 평일 야근 후 가정·호텔 케어 비중이 경기에서 가장 큰 도시 중 하나입니다.",
   "facts":[("구","3개"),("주요 시간대","평일 야간"),("호텔/가정","혼합 비중↑"),("특이점","판교 테크노밸리")],
   "subs":["수정구","중원구","분당구"],
   "character":"분당구(판교·정자·서현·미금)는 카카오·네이버·엔씨소프트 등 IT 기업이 밀집한 테크노밸리 인근으로 평일 야근(밤 9시~새벽) 시간대 가정 방문 비중이 매우 큽니다. 판교 일대 호텔(코트야드 메리어트 판교·아만티 등)에서 비즈니스 출장 객실 방문도 자주 안내됩니다. 수정·중원은 위례신도시와 일반 주거 권역으로 가정 방문이 중심입니다.",
   "pattern":"성남시는 평일 야간(밤 9시~자정) 시간대가 다른 경기 권역보다 두드러집니다. 판교 IT 야근 후 케어가 일정한 흐름입니다.",
   "faqs":[
     ("판교에서 야근 후 가능한가요?","판교 테크노밸리 인근 가정·오피스텔·호텔 방문이 평일 야간 시간대 자주 안내됩니다."),
     ("분당 아파트 단지에서 가능한가요?","분당 정자·서현·미금 일대 가정 방문이 평일 저녁·야간 안내됩니다."),
     ("위례신도시(수정구) 가능한가요?","위례 일대 가정 방문이 안내됩니다. 위례는 송파·하남·성남 경계라 행정 동 확인이 좋습니다."),
   ],"neighbors":["yongin","hanam","gwangju-si"]},

  {"slug":"anyang","name":"안양시","sub_label":"2개 구",
   "lede":"안양시는 평촌신도시(동안구)와 만안 일대 주거 권역으로 이루어진 시로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("구","2개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","평촌 학원가")],
   "subs":["만안구","동안구"],
   "character":"동안구 평촌(범계·평촌·호계)은 학원가와 대단지 아파트가 밀집해 평일 저녁 가정 방문 비중이 큽니다. 만안구(안양·박달·석수)는 일반 주거 권역으로 동일한 흐름이며, 인덕원역(동안구) 일대는 직장인 권역 가정 방문이 함께 들어옵니다.",
   "pattern":"안양시는 평일 저녁 7~10시 시간대가 가장 안정적입니다. 평촌 학원가 권역은 주말 가족 일정 시간대를 피해 늦은 저녁 권장.",
   "faqs":[
     ("평촌 아파트 단지에서 가능한가요?","평촌·범계 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("인덕원·관양 가능한가요?","인덕원·관양 일대 직장인 가정 방문이 평일 저녁 안내됩니다."),
     ("의왕·과천과 같은 권역인가요?","의왕·과천은 별도 시이며, 인접하지만 각각 권역 확인이 필요합니다."),
   ],"neighbors":["uiwang","gunpo","gwacheon"]},

  {"slug":"ansan","name":"안산시","sub_label":"2개 구",
   "lede":"안산시는 반월·시화 산업단지와 상록·고잔 주거 권역이 함께 있는 시로, 평일 저녁 출장·산업 종사자 케어 비중이 큰 권역입니다.",
   "facts":[("구","2개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","반월·시화 산단")],
   "subs":["상록구","단원구"],
   "character":"단원구(고잔·원곡·선부)는 반월·시화 산업단지 출장 일정과 맞물려 평일 저녁 비즈니스 호텔 객실 방문이 자주 안내됩니다. 상록구(사동·본오·이동·일동·반월)는 한양대 ERICA 캠퍼스와 주거 단지가 함께 있어 평일 저녁 가정 방문 비중이 큽니다.",
   "pattern":"안산시는 평일 저녁 7~10시 시간대 비중이 큽니다. 산업단지 출장은 평일 야간(9시 이후) 비중도 높은 편입니다.",
   "faqs":[
     ("산업단지 출장 일정에 가능한가요?","단원구 고잔·원곡 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("상록구 한대 인근 가능한가요?","한양대 ERICA 인근 사동·본오 가정 방문이 평일 저녁 안내됩니다."),
     ("시흥·화성과 함께 가능한가요?","시흥·화성은 별도 시로, 권역별 사전 확인이 필요합니다."),
   ],"neighbors":["siheung","gunpo","hwaseong"]},

  {"slug":"goyang","name":"고양시","sub_label":"3개 구",
   "lede":"고양시는 일산신도시와 덕양구 주거 권역이 함께 있는 대규모 신도시로, 평일 저녁 가정 방문 비중이 경기 서북부에서 가장 큰 권역입니다.",
   "facts":[("구","3개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","일산신도시")],
   "subs":["덕양구","일산동구","일산서구"],
   "character":"일산동구(장항·마두·백석·풍동)와 일산서구(주엽·일산·탄현·송포)는 일산신도시 대단지 가정 방문이 중심이며, 킨텍스·고양종합운동장 인근 호텔(소노캄·메이필드 호텔)에서 행사 일정 후 객실 방문도 안내됩니다. 덕양구(화정·행신·원흥·삼송)는 신도시·신축 단지 권역으로 평일 저녁 가정 방문이 활발합니다.",
   "pattern":"고양시는 평일 저녁 7~11시 시간대가 가장 안정적이며, 킨텍스 행사 시즌은 인근 호텔 가능 시간이 빠르게 마감됩니다.",
   "faqs":[
     ("일산 호수공원·라페스타 가능한가요?","일산동·서구 주엽·장항 일대 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("킨텍스 행사 일정과 묶을 수 있나요?","킨텍스 인근 호텔(소노캄·메이필드) 객실 방문이 안내됩니다. 행사 시즌은 사전 예약 권장."),
     ("파주·김포와 같은 권역인가요?","파주·김포는 별도 시로, 권역별 확인이 필요합니다."),
   ],"neighbors":["paju","gimpo","yangju"]},

  {"slug":"yongin","name":"용인시","sub_label":"3개 구",
   "lede":"용인시는 수지·기흥의 신도시 권역과 처인의 산업·주거가 함께 있는 시로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("구","3개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","에버랜드·삼성")],
   "subs":["처인구","기흥구","수지구"],
   "character":"수지구(풍덕천·죽전·동천)와 기흥구(보정·신갈·구갈·상갈·서농)는 분당과 인접한 신도시 권역으로 평일 저녁 가정 방문 비중이 큽니다. 처인구(역북·삼가·포곡·모현)는 에버랜드·삼성반도체 화성·기흥 사업장 인접이라 출장 호텔 방문이 일부 들어옵니다.",
   "pattern":"용인시는 평일 저녁 7~10시 시간대가 가장 안정적이며, 수지·기흥은 분당 권역 흐름과 닿아 있어 야간 시간대 비중도 큽니다.",
   "faqs":[
     ("수지·기흥 신도시 가능한가요?","수지·기흥 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("에버랜드 일정 후 가능한가요?","처인구 에버랜드 인접 호텔·펜션 방문이 일부 안내됩니다."),
     ("분당·성남과 함께 가능한가요?","분당은 별도 권역(성남시 분당구)으로 권역별 확인이 필요합니다."),
   ],"neighbors":["seongnam","suwon","gwangju-si"]},

  # ---- 시 (without 구) (22) ----
  {"slug":"uijeongbu","name":"의정부시",
   "lede":"의정부시는 경기 북부의 중심 도시로 의정부역·신곡·민락 일대 주거 권역의 평일 저녁 가정 방문이 중심을 이룹니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","경기 북부 거점")],
   "subs":["의정부동","호원동","장암동","신곡1동","신곡2동","송산1동","송산2동","송산3동","민락동","낙양동","녹양동","가능동","흥선동","의정부1동","의정부2동","의정부3동","자금동"],
   "character":"의정부역 일대는 경기 북부 KTX·1호선 환승 거점이며 민락·낙양 일대 신도시 단지에서 평일 저녁 가정 방문 비중이 큽니다. 호텔 인프라는 제한적이라 객실 방문 사례는 적은 편입니다.",
   "pattern":"의정부시는 평일 저녁 7~10시 시간대가 가장 안정적이며, 외곽 자금·신곡 일부는 마감이 빠른 편입니다.",
   "faqs":[
     ("민락신도시 가능한가요?","민락·낙양 일대 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("의정부역 인근 호텔에서 가능한가요?","의정부 일부 비즈니스 호텔에서 객실 방문이 안내됩니다."),
     ("양주·동두천과 권역이 같나요?","경기 북부 인접 시이지만 각각 별도 권역입니다."),
   ],"neighbors":["yangju","dongducheon","pocheon"]},

  {"slug":"bucheon","name":"부천시",
   "lede":"부천시는 중동·상동 신도시 권역과 원미·소사 일반 주거가 함께 있는 시로, 평일 저녁 가정 방문 비중이 매우 큽니다.",
   "facts":[("행정동","36개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","중동·상동 신도시")],
   "subs":["원미동","심곡동","춘의동","도당동","약대동","중1동","중2동","중3동","중4동","상1동","상2동","상3동","역곡1동","역곡2동","소사본동","범박동","괴안동","송내1동","송내2동","오정동","원종1동","원종2동","고강본동","고강1동","성곡동","대산동","계남동"],
   "character":"중동(중1~4동)·상동(상1~3동) 신도시는 대단지 아파트 가정 방문이 매우 활발한 권역으로 평일 저녁 7~10시 시간대 비중이 큽니다. 부천역·역곡역·송내역 일대 직장인 권역과 원미·소사 일반 주거 권역 모두 가정 방문 중심입니다.",
   "pattern":"부천시는 평일 저녁 7~10시 시간대가 가장 안정적이며, 신도시 권역 특성상 가족 일정 외 시간대를 권합니다.",
   "faqs":[
     ("중동·상동 신도시 가능한가요?","중동·상동 일대 대단지 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("부천 호텔 방문 가능한가요?","부천 일부 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("인천 부평과 같은 권역인가요?","부평은 인천이므로 <a href=\"/area/incheon/\">인천 안내</a> 참고."),
   ],"neighbors":["siheung","gwangmyeong","gimpo"]},

  {"slug":"gwangmyeong","name":"광명시",
   "lede":"광명시는 광명역세권 신도시와 철산·하안 주거 권역이 함께 있는 시로, KTX 광명역 인접 호텔 단시간 코스와 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","KTX 광명역")],
   "subs":["광명1동","광명2동","광명3동","광명4동","광명5동","광명6동","광명7동","철산1동","철산2동","철산3동","철산4동","하안1동","하안2동","하안3동","하안4동","소하1동","소하2동","학온동"],
   "character":"광명역 KTX 환승 일정과 맞물린 단시간 코스 문의가 자주 들어오며, 철산·하안 일대 대단지 가정 방문이 평일 저녁 활발합니다. 광명역세권(소하·일직) 신도시 단지에서도 가정 방문이 안내됩니다.",
   "pattern":"광명시는 평일 저녁 7~10시 시간대 비중이 큽니다. KTX 광명역 환승 단시간 코스는 60분 권장.",
   "faqs":[
     ("KTX 광명역 환승 가능한가요?","광명역 인근 호텔 60·90분 단시간 코스 문의가 안내됩니다."),
     ("철산·하안 단지 가능한가요?","철산·하안 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("서울 구로·금천과 함께 가능한가요?","행정상 별도이며 권역별 사전 확인이 필요합니다."),
   ],"neighbors":["siheung","bucheon","anyang"]},

  {"slug":"pyeongtaek","name":"평택시",
   "lede":"평택시는 미군기지(캠프 험프리스)·삼성전자 평택 캠퍼스·평택항이 모인 산업·물류 거점 도시로, 평일 저녁 출장 호텔 객실 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁"),("호텔/가정","호텔 비중↑"),("특이점","미군·삼성·항만")],
   "subs":["평택동","서정동","송탄동","지산동","송북동","신장1동","신장2동","중앙동","서탄면","고덕면","오성면","청북읍","포승읍","현덕면","안중읍","팽성읍","비전1동","비전2동","원평동","통복동","세교동","독곡동","이충동"],
   "character":"송탄(서정·신장) 일대 미군 캠프 험프리스 인접 호텔에서 외국인 케이스 객실 방문이 자주 안내됩니다. 고덕(삼성전자 평택 캠퍼스) 인접 호텔과 비전·중앙 도심 호텔에서 출장 일정 객실 방문이 함께 들어오며, 안중·포승은 평택항·산업단지 권역입니다.",
   "pattern":"평택시는 평일 저녁 7~11시 시간대 비중이 큽니다. 외국인 케이스는 영어 안내 가능 일정 사전 협의 필요.",
   "faqs":[
     ("캠프 험프리스 미군 가족 가능한가요?","송탄 일대 외국인 케이스 안내가 자주 있으며 영어 일정 사전 협의가 필요합니다."),
     ("삼성 평택 캠퍼스 출장 가능한가요?","고덕 인근 호텔 객실 방문이 자주 안내됩니다."),
     ("오산·안성과 같은 권역인가요?","오산·안성은 별도 시로 각각 권역 확인이 필요합니다."),
   ],"neighbors":["osan","anseong","hwaseong"]},

  {"slug":"dongducheon","name":"동두천시",
   "lede":"동두천시는 미군기지(캠프 케이시)·생연동 주거가 함께 있는 경기 북부 도시로, 평일 저녁 가정·호텔 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","미군기지")],
   "subs":["생연1동","생연2동","불현동","보산동","송내동","상패동","소요동","상봉암동"],
   "character":"보산동 캠프 케이시 인근 호텔에서 외국인 케이스 객실 방문이 안내되며, 생연·송내 일대는 일반 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"동두천시는 평일 저녁 7~10시 시간대가 안정적이며, 외곽 시간대 마감이 빠른 편입니다.",
   "faqs":[
     ("캠프 케이시 인근 가능한가요?","보산동 일대 호텔 외국인 케이스가 안내됩니다."),
     ("생연동 주거 권역 가능한가요?","생연·송내 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("의정부·양주와 함께 가능한가요?","행정상 별도이며 각각 권역 확인이 필요합니다."),
   ],"neighbors":["yangju","uijeongbu","yeoncheon"]},

  {"slug":"gwacheon","name":"과천시",
   "lede":"과천시는 정부과천청사·과천 주공 재건축 단지가 있는 소규모 도시로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","6개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","정부과천청사")],
   "subs":["중앙동","갈현동","별양동","부림동","과천동","문원동"],
   "character":"과천 주공 재건축(별양·중앙·부림) 단지와 신축 아파트가 밀집한 권역으로 평일 저녁 가정 방문이 자주 안내됩니다. 정부과천청사·서울대공원 인접 권역이라 야간 외곽 시간대 마감이 다소 빠른 편입니다.",
   "pattern":"과천시는 평일 저녁 7~10시 시간대가 안정적입니다.",
   "faqs":[
     ("과천 주공 재건축 단지 가능한가요?","별양·중앙 일대 신축 아파트 가정 방문이 안내됩니다."),
     ("정부과천청사 출장에 가능한가요?","청사 인근 호텔이 적어 인근 시(안양·서울 서초)로 안내드리는 경우가 있습니다."),
     ("안양·서울 서초와 같은 권역인가요?","행정상 별도이며 각각 사전 확인이 필요합니다."),
   ],"neighbors":["anyang","uiwang","seoul"]},

  {"slug":"guri","name":"구리시",
   "lede":"구리시는 한강 인접 주거 권역과 인창·교문 일대 신축 단지가 함께 있는 시로, 평일 저녁 가정 방문 중심입니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","서울 강동 인접")],
   "subs":["갈매동","동구동","인창동","교문1동","교문2동","수택1동","수택2동","수택3동"],
   "character":"구리시는 서울 강동·송파와 인접해 평일 저녁 가정 방문 비중이 큽니다. 갈매·인창 일대 신도시 단지에서 자주 안내되며, 호텔 인프라는 제한적입니다.",
   "pattern":"구리시는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("갈매신도시 가능한가요?","갈매·인창 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("서울 강동과 같은 권역인가요?","행정상 별도이며 인접하지만 각각 권역 확인이 필요합니다."),
     ("남양주와 함께 가능한가요?","남양주는 별도 시이며 권역별 확인이 필요합니다."),
   ],"neighbors":["namyangju","hanam","yangju"]},

  {"slug":"namyangju","name":"남양주시",
   "lede":"남양주시는 다산·별내 신도시와 평내·호평·진접 일대 신축 단지가 밀집한 시로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","다산·별내·진접")],
   "subs":["호평동","평내동","금곡동","양정동","다산1동","다산2동","별내동","와부읍","진접읍","오남읍","화도읍","수동면","조안면","퇴계원읍","진건읍","별내면"],
   "character":"다산신도시·별내신도시·평내호평·진접지구 등 대규모 택지 단지가 밀집해 평일 저녁 가정 방문 비중이 매우 큰 시입니다. 호텔 인프라는 제한적이며 가정 방문이 압도적입니다.",
   "pattern":"남양주시는 평일 저녁 7~11시 시간대 비중이 큽니다. 외곽 읍·면(수동·조안)은 마감이 빠른 편입니다.",
   "faqs":[
     ("다산신도시 가능한가요?","다산 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("별내·진접 가능한가요?","별내·진접 신도시 가정 방문이 평일 저녁 안내됩니다."),
     ("구리·하남과 같은 권역인가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["guri","hanam","yangju"]},

  {"slug":"osan","name":"오산시",
   "lede":"오산시는 평택과 인접한 산업·주거 도시로, 세교·운암 신도시 가정 방문과 출장 호텔 객실 방문이 함께 안내됩니다.",
   "facts":[("행정동","6개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","세교신도시")],
   "subs":["중앙동","대원동","남촌동","신장동","세마동","초평동"],
   "character":"세교신도시(세교1·2) 일대 대단지와 운암지구에서 평일 저녁 가정 방문이 자주 안내됩니다. 평택과 인접해 산업 출장 호텔 객실 방문도 일부 들어옵니다.",
   "pattern":"오산시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("세교신도시 가능한가요?","세교 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("평택과 함께 가능한가요?","평택은 별도 시로 권역별 확인이 필요합니다."),
     ("화성 동탄과 같은 권역인가요?","동탄은 화성시 권역으로 별도 안내됩니다."),
   ],"neighbors":["pyeongtaek","hwaseong","suwon"]},

  {"slug":"siheung","name":"시흥시",
   "lede":"시흥시는 시화산업단지와 배곧신도시·정왕동이 함께 있는 시로, 평일 저녁 가정·산업 출장 호텔 케어가 안내됩니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","시화 산단·배곧")],
   "subs":["대야동","신천동","신현동","은행동","매화동","목감동","과림동","연성동","능곡동","장곡동","월곶동","정왕본동","정왕1동","정왕2동","정왕3동","정왕4동","배곧동","군자동"],
   "character":"정왕(시화산단)은 산업 출장 호텔 객실 방문이 평일 저녁 자주 안내되며, 배곧신도시는 신축 단지 가정 방문 비중이 큽니다. 대야·신천 일대는 일반 주거 권역입니다.",
   "pattern":"시흥시는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("시화 산단 출장에 가능한가요?","정왕 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("배곧신도시 가능한가요?","배곧 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("안산과 함께 가능한가요?","안산은 별도 시이며 권역별 확인이 필요합니다."),
   ],"neighbors":["ansan","gwangmyeong","bucheon"]},

  {"slug":"gunpo","name":"군포시",
   "lede":"군포시는 산본신도시 대단지와 당정·금정 일대 주거 권역으로 이루어진 시로, 평일 저녁 가정 방문 중심입니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","산본신도시")],
   "subs":["군포1동","군포2동","산본1동","산본2동","금정동","당동","오금동","수리동","대야미동","둔대동","속달동"],
   "character":"산본신도시 대단지(산본1·2동)와 금정역 일대 가정 방문이 평일 저녁 자주 안내됩니다. 호텔 인프라는 제한적입니다.",
   "pattern":"군포시는 평일 저녁 7~10시 시간대가 안정적입니다.",
   "faqs":[
     ("산본신도시 가능한가요?","산본 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("의왕·안양과 같은 권역인가요?","각각 별도 시이며 인접 권역 확인이 필요합니다."),
     ("수원과 함께 가능한가요?","수원은 별도 권역으로 권역별 확인이 필요합니다."),
   ],"neighbors":["anyang","uiwang","ansan"]},

  {"slug":"uiwang","name":"의왕시",
   "lede":"의왕시는 내손·고천 일대 주거 권역과 백운호수 인접 단지로 이루어진 시로, 평일 저녁 가정 방문 중심입니다.",
   "facts":[("행정동","6개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","백운호수")],
   "subs":["고천동","부곡동","오전동","청계동","내손1동","내손2동"],
   "character":"의왕시는 내손·고천·오전 일대 신축 단지와 일반 주거 권역에서 평일 저녁 가정 방문이 자주 안내됩니다. 백운호수 인접 단지에서도 가정 방문이 들어옵니다.",
   "pattern":"의왕시는 평일 저녁 7~10시 시간대가 안정적입니다.",
   "faqs":[
     ("내손지구 가능한가요?","내손 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("안양·과천과 같은 권역인가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("백운호수 인근 펜션 가능한가요?","청계동 일대 일부 펜션·단지 방문이 안내됩니다."),
   ],"neighbors":["anyang","gunpo","gwacheon"]},

  {"slug":"hanam","name":"하남시",
   "lede":"하남시는 미사강변도시·위례신도시 일부와 감일·교산 신축 단지가 함께 있는 시로, 평일 저녁 가정 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","미사·위례·감일")],
   "subs":["천현동","신장1동","신장2동","덕풍1동","덕풍2동","덕풍3동","풍산동","미사1동","미사2동","미사3동","감북동","감일동","위례동"],
   "character":"미사강변도시(미사1~3)와 위례(위례동)·감일지구 등 대규모 신축 단지가 밀집해 평일 저녁 가정 방문 비중이 가장 큰 시 중 하나입니다. 스타필드 하남 인근 호텔(스타필드 인근 비즈니스 호텔)에서도 객실 방문이 일부 안내됩니다.",
   "pattern":"하남시는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("미사강변도시 가능한가요?","미사1~3동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("위례신도시(위례동) 가능한가요?","하남 위례동·송파·성남 위례 경계 권역에서 가정 방문이 안내됩니다. 행정 동 확인이 필요합니다."),
     ("스타필드 하남 인근 호텔 가능한가요?","스타필드 인근 비즈니스 호텔 객실 방문이 안내됩니다."),
   ],"neighbors":["guri","namyangju","seongnam"]},

  {"slug":"paju","name":"파주시",
   "lede":"파주시는 운정신도시·교하·금촌 일대 신축 단지와 LG디스플레이 사업장이 있는 시로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","운정신도시·LG")],
   "subs":["문산읍","파주읍","법원읍","조리읍","월롱면","탄현면","광탄면","파평면","적성면","군내면","장단면","진동면","진서면","교하동","운정1동","운정2동","운정3동","운정4동","운정5동","운정6동","금촌1동","금촌2동","금촌3동"],
   "character":"운정신도시(운정1~6동) 대단지와 교하·금촌 일대 가정 방문이 평일 저녁 자주 안내됩니다. LG디스플레이 파주 사업장 출장과 맞물려 비즈니스 호텔 객실 방문도 함께 들어옵니다.",
   "pattern":"파주시는 평일 저녁 7~10시 시간대 비중이 큽니다. 외곽 읍·면은 마감이 빠른 편입니다.",
   "faqs":[
     ("운정신도시 가능한가요?","운정1~6동 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("LG디스플레이 출장 가능한가요?","파주 LG 사업장 인근 호텔 객실 방문이 안내됩니다."),
     ("일산·고양과 함께 가능한가요?","고양은 별도 시이며 권역별 확인이 필요합니다."),
   ],"neighbors":["goyang","gimpo","yangju"]},

  {"slug":"icheon","name":"이천시",
   "lede":"이천시는 SK하이닉스 본사가 자리한 산업 도시로, 부발·중리·창전 일대 출장 호텔 객실 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","호텔 비중↑"),("특이점","SK하이닉스")],
   "subs":["창전동","중리동","증일동","갈산동","증포동","관고동","장호원읍","부발읍","신둔면","백사면","호법면","마장면","대월면","모가면"],
   "character":"부발읍·중리·창전 일대 SK하이닉스 본사 출장 일정과 맞물려 평일 저녁 호텔 객실 방문 비중이 큽니다. 외국인 엔지니어 케이스가 있어 영어 안내 가능 일정 사전 협의가 필요할 수 있습니다.",
   "pattern":"이천시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("SK하이닉스 출장 일정 가능한가요?","부발·중리 일대 호텔 객실 방문이 평일 저녁 자주 안내됩니다."),
     ("외국인 엔지니어 영어 안내 가능한가요?","사전 협의 일정에서 가능 여부를 확인해 드립니다."),
     ("여주·광주와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeoju","gwangju-si","anseong"]},

  {"slug":"anseong","name":"안성시",
   "lede":"안성시는 안성맞춤랜드·미양 등 산업·관광이 함께 있는 시로, 평일 저녁 가정·호텔 방문이 안내되는 권역입니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","평택 인접")],
   "subs":["안성1동","안성2동","안성3동","공도읍","보개면","금광면","서운면","미양면","대덕면","양성면","원곡면","일죽면","죽산면","삼죽면","고삼면"],
   "character":"안성시는 공도읍 신축 단지와 안성1~3동 도심 권역 가정 방문이 평일 저녁 안내됩니다. 평택과 인접한 공도읍 일대는 산업 권역 호텔 객실 방문도 일부 들어옵니다.",
   "pattern":"안성시는 평일 저녁 7~10시 시간대가 안정적입니다.",
   "faqs":[
     ("공도읍 신축 단지 가능한가요?","공도 일대 가정 방문이 자주 안내됩니다."),
     ("평택과 함께 가능한가요?","평택은 별도 시이며 권역별 확인이 필요합니다."),
     ("이천·용인과 같은 권역인가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["pyeongtaek","yongin","icheon"]},

  {"slug":"gimpo","name":"김포시",
   "lede":"김포시는 김포한강신도시·풍무·구래 일대 신축 단지가 밀집한 시로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","한강신도시")],
   "subs":["통진읍","월곶면","대곶면","양촌읍","하성면","고촌읍","김포본동","장기본동","장기동","구래동","마산동","운양동","풍무동","사우동"],
   "character":"김포한강신도시(장기·구래·마산·운양)와 풍무·고촌 일대 대단지 가정 방문이 평일 저녁 자주 안내됩니다. 김포공항(서울 강서)과 인접해 일부 환승 호텔 케이스도 함께 들어옵니다.",
   "pattern":"김포시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("한강신도시 가능한가요?","장기·구래·마산·운양 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("김포공항과 함께 가능한가요?","김포공항은 행정상 서울 강서구이며 별도 권역입니다."),
     ("인천 검단과 같은 권역인가요?","검단은 인천 서구이며 별도 권역입니다."),
   ],"neighbors":["goyang","bucheon","paju"]},

  {"slug":"hwaseong","name":"화성시",
   "lede":"화성시는 동탄신도시와 삼성전자 화성·기흥 사업장이 함께 있는 시로, 평일 저녁 가정·산업 출장 호텔 케어 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","29개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","동탄·삼성")],
   "subs":["봉담읍","우정읍","향남읍","남양읍","매송면","비봉면","마도면","송산면","서신면","팔탄면","장안면","양감면","정남면","화산동","반월동","기배동","화성동","새솔동","동탄1동","동탄2동","동탄3동","동탄4동","동탄5동","동탄6동","동탄7동","동탄8동","동탄9동","진안동","병점1동","병점2동"],
   "character":"동탄신도시(동탄1~9동)는 경기 남부 최대 신도시 중 하나로 평일 저녁 가정 방문 비중이 가장 큰 권역입니다. 삼성전자 화성·기흥 사업장 출장과 맞물려 동탄·반월·기배 일대 비즈니스 호텔 객실 방문도 많이 안내됩니다. 향남·봉담은 일반 주거 권역입니다.",
   "pattern":"화성시는 평일 저녁 7~11시 시간대 비중이 큽니다. 동탄 호텔 객실 방문은 야간 시간대 비중도 높은 편입니다.",
   "faqs":[
     ("동탄신도시 가능한가요?","동탄1~9동 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("삼성전자 화성 출장 가능한가요?","동탄·반월 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("수원·오산과 같은 권역인가요?","각각 별도 시이며 권역별 확인이 필요합니다."),
   ],"neighbors":["suwon","osan","pyeongtaek"]},

  {"slug":"gwangju-si","name":"광주시",
   "lede":"광주시(경기)는 오포·태전·송정 일대 신축 단지가 밀집한 시로, 평일 저녁 가정 방문 비중이 큰 권역입니다. (전라남도 광주광역시와 다릅니다.)",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","오포·태전 신도시")],
   "subs":["경안동","송정동","광남1동","광남2동","오포1동","오포2동","오포3동","초월읍","곤지암읍","도척면","퇴촌면","남종면","남한산성면"],
   "character":"오포(오포1~3) 신도시와 태전·송정 일대 신축 단지에서 평일 저녁 가정 방문이 자주 안내됩니다. 곤지암·초월은 외곽 권역으로 시간대 마감이 빠른 편입니다.",
   "pattern":"광주시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("오포·태전 신도시 가능한가요?","오포1~3 일대 가정 방문이 자주 안내됩니다."),
     ("성남(분당)과 같은 권역인가요?","성남은 별도 시이며 권역별 확인이 필요합니다."),
     ("전라남도 광주와 헷갈리지 않나요?","행정구역상 별도이며, <a href=\"/area/gwangju/\">광주광역시 안내</a>는 별도 페이지를 참고해 주세요."),
   ],"neighbors":["seongnam","yongin","icheon"]},

  {"slug":"yangju","name":"양주시",
   "lede":"양주시는 옥정·회천 신도시 단지가 자리한 경기 북부 도시로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","옥정·회천")],
   "subs":["백석읍","은현면","남면","광적면","장흥면","양주1동","양주2동","회천1동","회천2동","회천3동","회천4동","옥정1동","옥정2동"],
   "character":"옥정신도시(옥정1·2동)와 회천 일대 대단지 가정 방문이 평일 저녁 자주 안내됩니다. 의정부·동두천과 인접한 경기 북부 거점입니다.",
   "pattern":"양주시는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("옥정신도시 가능한가요?","옥정1·2동 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("의정부·동두천과 같은 권역인가요?","각각 별도 시이며 권역별 확인이 필요합니다."),
     ("회천지구 가능한가요?","회천 1~4 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["uijeongbu","dongducheon","pocheon"]},

  {"slug":"pocheon","name":"포천시",
   "lede":"포천시는 송우·소흘 일대 주거 권역과 산정호수 인접 관광 권역이 함께 있는 시로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","산정호수 관광")],
   "subs":["포천동","선단동","소흘읍","군내면","내촌면","가산면","신북면","창수면","영중면","일동면","이동면","영북면","관인면","화현면"],
   "character":"소흘읍·송우 일대 주거 권역 가정 방문이 평일 저녁 안내됩니다. 산정호수·이동갈비촌 등 관광 권역은 주말 방문 일정과 맞물린 펜션 방문 사례가 일부 들어옵니다.",
   "pattern":"포천시는 평일 저녁 7~10시 시간대가 안정적이며, 외곽 읍·면은 마감이 빠른 편입니다.",
   "faqs":[
     ("소흘 송우 가능한가요?","소흘읍 송우리 일대 가정 방문이 자주 안내됩니다."),
     ("산정호수 펜션 가능한가요?","영북면 산정호수 인근 펜션 일부 방문이 안내됩니다."),
     ("의정부·양주와 같은 권역인가요?","각각 별도 시·군이며 권역별 확인이 필요합니다."),
   ],"neighbors":["yangju","uijeongbu","yeoncheon"]},

  {"slug":"yeoju","name":"여주시",
   "lede":"여주시는 여주역 KTX·여주프리미엄아울렛이 있는 시로, 평일 저녁 가정 방문과 주말 관광 일정 케어가 함께 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","KTX·아울렛")],
   "subs":["여흥동","중앙동","오학동","능서면","흥천면","금사면","산북면","대신면","북내면","강천면","점동면","가남읍"],
   "character":"여주시는 여주역 KTX 환승 거점이며 여흥·중앙 도심과 가남읍 일대 가정 방문이 평일 저녁 안내됩니다. 여주프리미엄아울렛 인접 일부 호텔 객실 방문 사례가 있습니다.",
   "pattern":"여주시는 평일 저녁 7~10시 시간대가 안정적입니다.",
   "faqs":[
     ("여주역 KTX 환승 가능한가요?","여주역 인근 60·90분 단시간 코스 안내가 일부 가능합니다."),
     ("여주아울렛 인근 호텔 가능한가요?","아울렛 인근 일부 호텔에서 객실 방문이 안내됩니다."),
     ("이천·광주(경기)와 같은 권역인가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["icheon","gwangju-si","yangpyeong"]},

  # ---- 군 (3) ----
  {"slug":"yeoncheon","name":"연천군",
   "lede":"연천군은 경기 최북단의 농촌·DMZ 인접 군으로, 전곡·연천읍 일대 가정 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","DMZ 인접")],
   "subs":["연천읍","전곡읍","청산면","백학면","미산면","왕징면","신서면","중면","장남면","군남면"],
   "character":"전곡읍·연천읍 도심 권역 가정 방문이 안내되며, 외곽 면 단위는 이동 시간 특성상 일정 협의가 필요한 권역입니다.",
   "pattern":"연천군은 평일 저녁 7~9시 시간대가 안정적이며, 외곽 면은 마감이 빠릅니다.",
   "faqs":[
     ("전곡 도심 가능한가요?","전곡읍 일대 가정 방문이 안내됩니다."),
     ("외곽 면 단위 가능한가요?","면 단위 외곽은 이동 시간이 길어 사전 협의가 필요합니다."),
     ("동두천·포천과 함께 가능한가요?","각각 별도 권역으로 사전 확인이 필요합니다."),
   ],"neighbors":["dongducheon","pocheon","yangju"]},

  {"slug":"gapyeong","name":"가평군",
   "lede":"가평군은 자라섬·아침고요수목원 등 관광 권역으로 유명한 군으로, 펜션·리조트 객실 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","6개"),("주요 시간대","주말·시즌"),("호텔/가정","펜션 비중↑"),("특이점","휴양 관광지")],
   "subs":["가평읍","청평면","상면","조종면","북면","설악면"],
   "character":"청평·설악·조종 일대 펜션·리조트(샹그리아 리조트·캠프통톤 등)에서 휴양 일정 후 객실 방문이 안내됩니다. 관광 성수기(여름·가을 단풍철)는 가능 시간이 빠르게 마감됩니다.",
   "pattern":"가평군은 주말·시즌 시간대 비중이 큽니다. 펜션 객실 방문은 객동 정보·진입로 사전 확인이 필요합니다.",
   "faqs":[
     ("청평 펜션 가능한가요?","청평·설악 일대 펜션·리조트 객실 방문이 안내됩니다."),
     ("성수기 사전 예약 필요한가요?","여름·단풍철 성수기는 사전 예약이 강력 권장됩니다."),
     ("아침고요수목원 인근 가능한가요?","상면·조종 일대 일부 펜션·숙소 방문이 안내됩니다."),
   ],"neighbors":["namyangju","yangpyeong","pocheon"]},

  {"slug":"yangpyeong","name":"양평군",
   "lede":"양평군은 양평읍·용문 도심과 두물머리·세미원 관광 권역이 함께 있는 군으로, 평일 저녁 가정 방문과 주말 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","두물머리 관광")],
   "subs":["양평읍","강상면","강하면","양서면","옥천면","서종면","단월면","청운면","양동면","지평면","용문면","개군면"],
   "character":"양평읍·용문 도심 가정 방문이 평일 저녁 안내되며, 강상·강하·양서 일대 한강변 펜션·전원주택에서 주말 객실 방문이 자주 들어옵니다.",
   "pattern":"양평군은 평일 저녁 7~10시 시간대와 주말 시즌이 가장 안정적입니다.",
   "faqs":[
     ("양평 한강변 펜션 가능한가요?","강상·강하·양서 일대 펜션 객실 방문이 안내됩니다."),
     ("두물머리 인근 가능한가요?","양수리 일대 일부 단지·펜션 방문이 안내됩니다."),
     ("여주·가평과 같은 권역인가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gapyeong","yeoju","namyangju"]},
]


def _build_gyeonggi_districts():
    name_to_slug = {d["name"]: d["slug"] for d in GYEONGGI_DISTRICTS}
    for d in GYEONGGI_DISTRICTS:
        sub_label = d.get("sub_label")
        if sub_label:
            displayed = d["subs"]
            headline = f'{d["name"]} {sub_label}'
            note = f'{d["name"]}는 행정상 {sub_label}로 구성됩니다. 권역별 가능 시간은 전화 상담에서 확인됩니다.'
            eyebrow_label = "행정구 전체"
        else:
            displayed = _consolidate_dongs(d["subs"])
            headline = f'{d["name"]} {len(displayed)}개 행정동'
            note = f'{d["name"]} 전체 행정동에서 안내가 가능합니다. 시간대·이동 가능 여부는 동별로 다르며, 정확한 가능 시간은 전화 상담에서 확인됩니다.'
            eyebrow_label = "행정동 전체"
        chips_html = "".join(f"<li>{s}</li>" for s in displayed)
        dong_card = (
            f'<section class="region-districts" aria-label="{eyebrow_label}">'
            '<header class="region-districts-head">'
            '<span class="region-districts-eyebrow">'
            '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
            f'{eyebrow_label}'
            '</span>'
            f'<h2 class="region-districts-headline">{headline}</h2>'
            f'<p class="region-districts-note">{note}</p>'
            '</header>'
            '<div class="region-districts-body">'
            '<div class="region-districts-group">'
            f'<ul class="region-districts-grid">{chips_html}</ul>'
            '</div>'
            '</div>'
            '</section>'
        )
        body_parts = [
            _district_facts_html(d["facts"]),
            dong_card,
            '<section class="block">'
            f'<h2>{d["name"]} 권역 특성</h2>'
            f'<p>{d["character"]}</p>'
            '</section>',
            '<section class="block">'
            f'<h2>{d["name"]} 이용 시간 패턴</h2>'
            f'<p>{d["pattern"]}</p>'
            '</section>',
            _district_faqs_html(d["name"], d["faqs"]),
            _region_cta_html(d["name"]),
        ]
        slug_to_name = {x["slug"]: x["name"] for x in GYEONGGI_DISTRICTS}
        neighbors = [
            (slug_to_name[n_slug], n_slug)
            for n_slug in d["neighbors"]
            if n_slug in slug_to_name
        ]
        add(
            path=f"area/gyeonggi/{d['slug']}/index.html",
            url=f"/area/gyeonggi/{d['slug']}/",
            slug=f"area-gyeonggi-{d['slug']}",
            title=_district_title(d['name'], "경기", d['facts']),
            description=_district_description(d['lede'], d['name'], "경기"),
            h1=f"{d['name']} 방문 마사지 이용 안내",
            intro=f'<p class="lede">{d["lede"]}</p>' + _district_hero_cta_html(d["name"]),
            breadcrumbs=[
                ("홈", "/"),
                ("지역별 찾기", "/area/"),
                ("경기", "/area/gyeonggi/"),
                (d["name"], f"/area/gyeonggi/{d['slug']}/"),
            ],
            body="".join(body_parts),
            related=_district_neighbor_related_html("gyeonggi", "경기", neighbors),
        )


# Pre-register Gyeonggi pages in the chip index so 1차 chips link.
for _d in GYEONGGI_DISTRICTS:
    DISTRICT_PAGE_INDEX[("gyeonggi", _d["name"])] = f"/area/gyeonggi/{_d['slug']}/"

_build_gyeonggi_districts()


# ============================================================
# 광역시 — 부산 / 인천 / 대구 / 대전 / 광주 / 울산 / 세종
# ============================================================
# Generic builder that re-uses Seoul/Gyeonggi page structure.

def _build_metro_district(parent_slug, parent_name, d, all_in_parent):
    sub_label = d.get("sub_label")
    if sub_label:
        displayed = d["subs"]
        headline = f'{d["name"]} {sub_label}'
        note = f'{d["name"]}는 행정상 {sub_label}로 구성됩니다. 권역별 가능 시간은 전화 상담에서 확인됩니다.'
        eyebrow_label = "행정구 전체"
    else:
        displayed = _consolidate_dongs(d["subs"])
        headline = f'{d["name"]} {len(displayed)}개 행정동'
        note = f'{d["name"]} 전체 행정동에서 안내가 가능합니다. 시간대·이동 가능 여부는 동별로 다르며, 정확한 가능 시간은 전화 상담에서 확인됩니다.'
        eyebrow_label = "행정동 전체"
    chips_html = "".join(f"<li>{s}</li>" for s in displayed)
    dong_card = (
        f'<section class="region-districts" aria-label="{eyebrow_label}">'
        '<header class="region-districts-head">'
        '<span class="region-districts-eyebrow">'
        '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
        f'{eyebrow_label}'
        '</span>'
        f'<h2 class="region-districts-headline">{headline}</h2>'
        f'<p class="region-districts-note">{note}</p>'
        '</header>'
        '<div class="region-districts-body">'
        '<div class="region-districts-group">'
        f'<ul class="region-districts-grid">{chips_html}</ul>'
        '</div></div></section>'
    )
    body_parts = [
        _district_facts_html(d["facts"]),
        dong_card,
        '<section class="block">'
        f'<h2>{d["name"]} 권역 특성</h2>'
        f'<p>{d["character"]}</p>'
        '</section>',
        '<section class="block">'
        f'<h2>{d["name"]} 이용 시간 패턴</h2>'
        f'<p>{d["pattern"]}</p>'
        '</section>',
        _district_faqs_html(d["name"], d["faqs"]),
        _region_cta_html(d["name"]),
    ]
    slug_to_name = {x["slug"]: x["name"] for x in all_in_parent}
    neighbors = [
        (slug_to_name[n], n)
        for n in d.get("neighbors", [])
        if n in slug_to_name
    ]
    add(
        path=f"area/{parent_slug}/{d['slug']}/index.html",
        url=f"/area/{parent_slug}/{d['slug']}/",
        slug=f"area-{parent_slug}-{d['slug']}",
        title=_district_title(d['name'], parent_name, d['facts']),
        description=_district_description(d['lede'], d['name'], parent_name),
        h1=f"{d['name']} 방문 마사지 이용 안내",
        intro=f'<p class="lede">{d["lede"]}</p>' + _district_hero_cta_html(d["name"]),
        breadcrumbs=[
            ("홈", "/"),
            ("지역별 찾기", "/area/"),
            (parent_name, f"/area/{parent_slug}/"),
            (d["name"], f"/area/{parent_slug}/{d['slug']}/"),
        ],
        body="".join(body_parts),
        related=_district_neighbor_related_html(parent_slug, parent_name, neighbors),
    )


# ---- 부산 16 ----
BUSAN_DISTRICTS = [
  {"slug":"jung","name":"중구",
   "lede":"부산 중구는 남포동·광복로·자갈치 등 부산 원도심 권역으로, 관광 일정 호텔 객실 방문 비중이 큰 자치구입니다.",
   "facts":[("행정동","9개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑"),("특이점","남포동·자갈치")],
   "subs":["중앙동","동광동","대청동","보수동","부평동","광복동","남포동","영주1동","영주2동"],
   "character":"남포동·자갈치·국제시장 인근 코모도호텔·이비스 앰배서더 부산·필 부산 호텔 등에서 관광 일정 후 객실 방문이 자주 안내됩니다. 부산항 국제여객터미널이 인접해 환승 일정 단시간 코스 문의도 들어옵니다.",
   "pattern":"부산 중구는 야간 시간대 비중이 큽니다. 도심 호텔 객실 정보 사전 확인이 필요합니다.",
   "faqs":[
     ("코모도호텔에서 가능한가요?","남포동 코모도호텔·이비스 앰배서더 부산 객실 방문이 안내됩니다."),
     ("국제여객터미널 환승 가능한가요?","환승 시간 2~3시간 이상 확보된 경우 단시간 코스 안내가 가능합니다."),
     ("자갈치·광복동 가능한가요?","구도심 호텔 객실 방문이 안내되며 외부 방문객 동선은 사전 확인이 필요합니다."),
   ],"neighbors":["seo","dong","yeongdo"]},
  {"slug":"seo","name":"서구",
   "lede":"부산 서구는 충무동·아미·동대신 일대의 구도심 권역으로, 부산대학교병원 인근 케어와 평일 저녁 가정 방문이 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","부산대병원")],
   "subs":["동대신1동","동대신2동","동대신3동","서대신1동","서대신3동","서대신4동","부민동","아미동","초장동","충무동","남부민1동","남부민2동","암남동"],
   "character":"서구는 부산대학교병원·동아대 부민캠퍼스 인근 권역과 충무·남부민 주거 권역에서 평일 저녁 가정 방문이 자주 안내됩니다. 호텔 인프라는 제한적입니다.",
   "pattern":"서구는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("부산대병원 인근 가능한가요?","아미·동대신 일대 가정 방문이 자주 안내됩니다."),
     ("동아대 부민캠퍼스 인근 가능한가요?","부민·동대신 일대 케어가 평일 저녁 안내됩니다."),
     ("중구·동구와 함께 가능한가요?","인접 자치구로 각각 권역 확인이 필요합니다."),
   ],"neighbors":["jung","dong","saha"]},
  {"slug":"dong","name":"동구",
   "lede":"부산 동구는 부산역·초량 일대 도심 권역과 차이나타운·텍사스촌이 함께 있는 자치구로, KTX 환승 호텔 객실 방문 비중이 큽니다.",
   "facts":[("행정동","12개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑"),("특이점","부산역·차이나타운")],
   "subs":["초량1동","초량2동","초량3동","초량6동","수정1동","수정2동","수정4동","수정5동","좌천1동","좌천4동","범일1동","범일2동","범일5동"],
   "character":"부산역 인근 코오롱호텔·아르반호텔·아스토리호텔 등에서 KTX 환승·관광 일정 객실 방문이 자주 안내됩니다. 초량 차이나타운·텍사스촌 일대는 외국인 케이스도 있어 영어/중국어 안내 가능 일정 사전 협의가 필요할 수 있습니다.",
   "pattern":"동구는 KTX 부산역 환승 일정과 야간 시간대 비중이 큽니다.",
   "faqs":[
     ("부산역 KTX 환승 가능한가요?","부산역 인근 호텔 단시간 코스가 자주 안내됩니다."),
     ("차이나타운 외국인 케이스 가능한가요?","사전 협의로 영어/중국어 안내 가능 일정이 확인됩니다."),
     ("범일동 단지 가능한가요?","범일·좌천 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["jung","seo","busanjin"]},
  {"slug":"yeongdo","name":"영도구",
   "lede":"영도구는 영도·동삼·청학 일대 주거 권역과 흰여울 관광지가 있는 자치구로, 평일 저녁 가정 방문과 관광 펜션 케어가 함께 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","흰여울 관광")],
   "subs":["남항동","영선1동","영선2동","신선동","봉래1동","봉래2동","청학1동","청학2동","동삼1동","동삼2동","동삼3동"],
   "character":"영도구는 동삼·청학 일대 주거 가정 방문과 흰여울 문화마을 인접 게스트하우스·펜션 객실 방문이 함께 안내됩니다. 한국해양대학교 인접이라 일부 외국인 케이스도 들어옵니다.",
   "pattern":"영도구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("동삼·청학 가능한가요?","동삼·청학 일대 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("흰여울 게스트하우스 가능한가요?","영선·봉래 일대 게스트하우스·펜션 객실 방문이 안내됩니다."),
     ("한국해양대 외국인 케이스 가능한가요?","사전 영어 안내 협의 일정에서 가능 여부 확인됩니다."),
   ],"neighbors":["jung","nam","busanjin"]},
  {"slug":"busanjin","name":"부산진구",
   "lede":"부산진구는 서면 일대의 부산 최대 도심·상업 권역으로, 야간 호텔·주거 가정 방문 비중이 큰 자치구입니다.",
   "facts":[("행정동","11개"),("주요 시간대","야간"),("호텔/가정","혼합 비중↑"),("특이점","서면 도심")],
   "subs":["부전1동","부전2동","연지동","초읍동","양정1동","양정2동","전포1동","전포2동","당감1동","당감2동","개금1동","개금2동","개금3동","가야1동","가야2동","범천1동","범천2동"],
   "character":"서면 일대 롯데호텔 부산·노보텔 앰배서더 부산 등 비즈니스 호텔 객실 방문이 야간 시간대 자주 안내됩니다. 전포 카페거리·양정 주거 권역 가정 방문도 함께 들어오는 부산 핵심 도심입니다.",
   "pattern":"부산진구는 야간 시간대 비중이 큽니다. 서면 호텔은 사전 객실 정보 확인이 필요합니다.",
   "faqs":[
     ("롯데호텔 부산 가능한가요?","서면 롯데호텔 부산·노보텔 객실 방문이 자주 안내됩니다."),
     ("전포 카페거리 인근 가능한가요?","전포·부전 일대 오피스텔·원룸 가정 방문이 안내됩니다."),
     ("양정·연지 단지 가능한가요?","양정·연지 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["dong","nam","yeonje"]},
  {"slug":"dongnae","name":"동래구",
   "lede":"동래구는 온천장·명륜·사직 일대의 전통 도심과 주거가 함께 있는 자치구로, 평일 저녁 가정 방문과 온천 관광 케어가 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","온천·사직야구장")],
   "subs":["수민동","복산동","명륜동","온천1동","온천2동","온천3동","사직1동","사직2동","사직3동","안락1동","안락2동","명장1동","명장2동"],
   "character":"동래구는 온천장 일대 호텔·온천 시설과 사직야구장 인근 권역, 명륜·안락 주거 단지가 함께 있습니다. 평일 저녁 가정 방문이 중심이고, 사직야구장 경기 일정은 인근 호텔 가능 시간이 변동합니다.",
   "pattern":"동래구는 평일 저녁 7~10시 시간대가 안정적입니다.",
   "faqs":[
     ("온천장 호텔에서 가능한가요?","온천1~3동 일대 호텔 객실 방문이 안내됩니다."),
     ("사직야구장 경기 일정 가능한가요?","사직 인근 호텔 가능 시간이 경기 일정 따라 변동합니다."),
     ("명륜·안락 가정 가능한가요?","명륜·안락 일대 평일 저녁 가정 방문이 자주 안내됩니다."),
   ],"neighbors":["geumjeong","yeonje","busanjin"]},
  {"slug":"nam","name":"남구",
   "lede":"부산 남구는 경성대·부경대·문현 일대 도심 권역과 용호·우암 주거가 함께 있는 자치구입니다. 평일 저녁 가정·호텔 방문이 균형 있게 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","경성대·문현")],
   "subs":["대연1동","대연3동","대연4동","대연5동","대연6동","용호1동","용호2동","용호3동","용호4동","용당동","문현1동","문현2동","문현3동","문현4동","우암동","감만1동","감만2동"],
   "character":"대연·용호 일대 주거 권역(LG메트로시티)과 문현금융단지 호텔(센텀호텔·머큐어 부산 문현) 객실 방문이 평일 저녁 자주 안내됩니다. 경성대·부경대 인근은 원룸·오피스텔 가정 방문이 들어옵니다.",
   "pattern":"부산 남구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("LG메트로시티 가능한가요?","용호 LG메트로시티 일대 가정 방문이 자주 안내됩니다."),
     ("문현금융단지 호텔 가능한가요?","문현 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("경성대·부경대 원룸 가능한가요?","대연 일대 원룸·오피스텔 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["busanjin","yeongdo","suyeong"]},
  {"slug":"buk","name":"북구",
   "lede":"부산 북구는 화명·만덕·구포 일대 주거 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","화명신도시")],
   "subs":["구포1동","구포2동","구포3동","금곡동","화명1동","화명2동","화명3동","덕천1동","덕천2동","덕천3동","만덕1동","만덕2동","만덕3동"],
   "character":"화명신도시(화명1~3)·구포·만덕 일대 대단지 가정 방문이 중심을 이룹니다. 호텔 인프라는 제한적이라 객실 방문 사례는 적은 편입니다.",
   "pattern":"부산 북구는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("화명신도시 가능한가요?","화명1~3동 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("만덕·구포 가능한가요?","만덕·구포 일대 평일 저녁 가정 방문이 안내됩니다."),
     ("사상·강서와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["sasang","geumjeong","gangseo"]},
  {"slug":"haeundae","name":"해운대구",
   "lede":"해운대구는 부산 관광·호텔의 중심 자치구로, 해운대해수욕장·동백섬·마린시티 일대 5성 호텔 객실 방문 비중이 부산에서 가장 큰 권역입니다.",
   "facts":[("행정동","18개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑↑"),("특이점","해운대·마린시티")],
   "subs":["우1동","우2동","우3동","중1동","중2동","좌1동","좌2동","좌3동","좌4동","송정동","반여1동","반여2동","반여3동","반여4동","반송1동","반송2동","재송1동","재송2동"],
   "character":"해운대·마린시티 일대 시그니엘 부산(에이앤피호텔)·파라다이스 부산·웨스틴 조선 부산·파크 하얏트 부산 등 5성 호텔이 모인 권역입니다. 관광·휴양 일정 후 야간 객실 방문 비중이 부산에서 가장 큽니다. 좌동·반여·재송은 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"해운대구는 야간·심야 시간대 가능 사례가 부산에서 가장 많습니다. 성수기는 가능 시간이 빠르게 마감됩니다.",
   "faqs":[
     ("시그니엘 부산·파라다이스 가능한가요?","해운대 5성 호텔 객실 방문이 자주 안내됩니다. 객실 정보 사전 확인 필요."),
     ("마린시티 입주민 가능한가요?","마린시티 일대 단지 가정 방문이 평일 저녁 안내됩니다."),
     ("성수기 사전 예약 필요한가요?","여름·연말 성수기는 사전 예약이 강력 권장됩니다."),
   ],"neighbors":["suyeong","gijang","dongnae"]},
  {"slug":"saha","name":"사하구",
   "lede":"사하구는 다대포·하단·괴정 일대 주거 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","다대포해수욕장")],
   "subs":["괴정1동","괴정2동","괴정3동","괴정4동","당리동","하단1동","하단2동","신평1동","신평2동","장림1동","장림2동","다대1동","다대2동","구평동","감천1동","감천2동"],
   "character":"하단·괴정·다대 일대 주거 단지 가정 방문이 평일 저녁 중심을 이룹니다. 다대포해수욕장 인근은 여름 시즌 관광 일정 케어가 일부 들어옵니다.",
   "pattern":"사하구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("하단·괴정 가능한가요?","하단·괴정 일대 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("다대포 인근 가능한가요?","다대1~2동·구평 일대 가정 방문이 안내됩니다."),
     ("서구와 함께 가능한가요?","서구는 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["seo","saha","sasang"]},
  {"slug":"geumjeong","name":"금정구",
   "lede":"금정구는 부산대·범어사 일대 대학가·전통 권역과 구서·장전 주거가 함께 있는 자치구입니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","부산대 인근")],
   "subs":["서1동","서2동","서3동","금사동","부곡1동","부곡2동","부곡3동","부곡4동","장전1동","장전2동","선두구동","청룡노포동","남산동","구서1동","구서2동","금성동","회동·석대동"],
   "character":"부산대학교 인근(장전·구서) 원룸·오피스텔 가정 방문이 자주 안내되며, 노포동 부산종합버스터미널 일대도 권역에 포함됩니다. 범어사 인근은 외곽 권역으로 마감이 빠른 편입니다.",
   "pattern":"금정구는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("부산대 인근 가능한가요?","장전·구서 일대 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
     ("노포 터미널 인근 가능한가요?","노포동 일대 가정 방문이 안내됩니다."),
     ("동래·북구와 같은 권역인가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["dongnae","buk","sasang"]},
  {"slug":"gangseo","name":"강서구",
   "lede":"부산 강서구는 김해국제공항·명지국제신도시·녹산 산업단지가 함께 있는 자치구로, 환승 호텔·신도시 가정·산업 출장 권역이 모두 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁·환승"),("호텔/가정","혼합"),("특이점","김해공항·명지")],
   "subs":["대저1동","대저2동","강동동","명지1동","명지2동","가락동","녹산동","가덕도동"],
   "character":"명지국제신도시 대단지(명지1·2) 가정 방문이 평일 저녁 자주 안내되며, 김해공항 인근 호텔(베스트웨스턴·이비스 등) 환승 단시간 코스 문의가 들어옵니다. 녹산산업단지는 출장 호텔 객실 방문 권역입니다.",
   "pattern":"부산 강서구는 평일 저녁 시간대와 공항 환승 시간대 모두 안내됩니다.",
   "faqs":[
     ("김해공항 환승 가능한가요?","김해공항 인근 호텔 단시간 코스가 안내됩니다."),
     ("명지신도시 가능한가요?","명지1·2동 대단지 가정 방문이 자주 안내됩니다."),
     ("녹산 산단 출장 가능한가요?","녹산 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
   ],"neighbors":["saha","buk","sasang"]},
  {"slug":"yeonje","name":"연제구",
   "lede":"연제구는 부산시청·부산지방법원이 자리한 행정 중심 자치구로, 평일 저녁 직장인 가정 방문 비중이 큽니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","부산시청")],
   "subs":["거제1동","거제2동","거제3동","거제4동","연산1동","연산2동","연산3동","연산4동","연산5동","연산6동","연산8동","연산9동"],
   "character":"부산시청·법조타운 인근 직장인 가정 방문이 평일 저녁 자주 안내되며, 거제·연산 일대 주거 단지에서 가정 방문이 중심을 이룹니다.",
   "pattern":"연제구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("거제·연산 단지 가능한가요?","거제1~4동·연산 일대 가정 방문이 자주 안내됩니다."),
     ("시청·법조타운 인근 가능한가요?","행정 권역 인근 직장인 가정 방문이 평일 저녁 안내됩니다."),
     ("부산진구·동래와 같은 권역인가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["busanjin","dongnae","suyeong"]},
  {"slug":"suyeong","name":"수영구",
   "lede":"수영구는 광안리해수욕장·민락수변공원 일대의 관광·휴양 권역으로, 야간 호텔 객실 방문 비중이 해운대 다음으로 큰 자치구입니다.",
   "facts":[("행정동","10개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑"),("특이점","광안리 야경")],
   "subs":["남천1동","남천2동","수영동","망미1동","망미2동","광안1동","광안2동","광안3동","광안4동","민락동"],
   "character":"광안리 일대 호텔(앰버서더 풀만 부산·골든튤립 등)과 민락수변공원 인근 객실 방문이 야경 일정과 맞물려 야간 시간대 자주 안내됩니다. 남천·망미 일대는 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"수영구는 야간 시간대 비중이 큽니다. 광안리 불꽃축제·해맞이 등 시즌은 사전 예약이 강력 권장됩니다.",
   "faqs":[
     ("광안리 호텔 가능한가요?","광안1~4동 일대 관광 호텔 객실 방문이 자주 안내됩니다."),
     ("민락수변공원 인근 가능한가요?","민락동 일대 호텔·펜션 객실 방문이 안내됩니다."),
     ("불꽃축제 당일 가능한가요?","축제 당일은 사전 예약 필수이며 당일 문의는 가능 권역이 제한될 수 있습니다."),
   ],"neighbors":["nam","haeundae","yeonje"]},
  {"slug":"sasang","name":"사상구",
   "lede":"사상구는 서부산터미널·사상공단 일대의 산업·교통 권역으로, 평일 저녁 출장 호텔·주거 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","서부산터미널")],
   "subs":["삼락동","모라1동","모라3동","덕포1동","덕포2동","괘법동","감전동","주례1동","주례2동","주례3동","학장동","엄궁동"],
   "character":"서부산터미널 인근 호텔에서 환승 일정 객실 방문이 일부 안내되며, 모라·덕포·주례 일대 주거 단지 가정 방문이 평일 저녁 중심입니다. 사상공단 출장 호텔도 함께 들어옵니다.",
   "pattern":"사상구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("서부산터미널 환승 가능한가요?","사상역·터미널 일대 호텔 단시간 코스가 안내됩니다."),
     ("모라·덕포 단지 가능한가요?","모라·덕포 일대 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("사상공단 출장 가능한가요?","산업단지 인근 비즈니스 호텔 객실 방문이 안내됩니다."),
   ],"neighbors":["buk","saha","gangseo"]},
  {"slug":"gijang","name":"기장군",
   "lede":"기장군은 정관신도시·일광·기장읍 일대로 이루어진 군으로, 평일 저녁 신도시 가정 방문과 해안 펜션 케어가 함께 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","정관신도시·기장읍")],
   "subs":["기장읍","장안읍","정관읍","일광읍","철마면"],
   "character":"정관신도시(정관읍) 대단지 가정 방문이 평일 저녁 중심이며, 일광·기장읍 해안 권역 펜션 객실 방문도 안내됩니다. 오시리아 관광단지(아난티 코브·힐튼 부산) 인접 호텔도 객실 방문 권역입니다.",
   "pattern":"기장군은 평일 저녁 7~10시 시간대가 안정적이며, 오시리아 관광단지는 주말 비중이 큽니다.",
   "faqs":[
     ("정관신도시 가능한가요?","정관읍 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("아난티 코브·힐튼 부산 가능한가요?","오시리아 권역 호텔·리조트 객실 방문이 안내됩니다."),
     ("일광·기장읍 펜션 가능한가요?","일광·기장 해안 권역 펜션 객실 방문이 안내됩니다."),
   ],"neighbors":["haeundae","dongnae","geumjeong"]},
]


# ---- 인천 10 ----
INCHEON_DISTRICTS = [
  {"slug":"jung","name":"중구",
   "lede":"인천 중구는 인천항·차이나타운·신포·자유공원 등 구도심 권역과 영종도(인천공항) 일부를 포함하는 자치구입니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁·환승"),("호텔/가정","혼합"),("특이점","구도심·영종")],
   "subs":["중앙동","동인천동","북성동","송월동","연안동","신포동","신흥동","도원동","율목동","용동","운서동","영종동"],
   "character":"인천항·신포 일대 구도심 호텔과 차이나타운 외국인 권역 객실 방문이 안내됩니다. 영종도(운서·영종)는 인천공항과 인접한 호텔 단시간 환승 코스가 자주 들어옵니다.",
   "pattern":"인천 중구는 평일 저녁 시간대와 공항 환승 시간대 모두 안내됩니다.",
   "faqs":[
     ("인천공항 환승 가능한가요?","영종도·운서동 호텔 환승 단시간 코스가 안내됩니다."),
     ("차이나타운 외국인 케이스 가능한가요?","사전 영어/중국어 안내 협의 일정에서 가능 여부 확인됩니다."),
     ("신포·동인천 가능한가요?","구도심 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["dong","seo","yeonsu"]},
  {"slug":"dong","name":"동구",
   "lede":"인천 동구는 송림·송현·만석 일대의 구도심 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","구도심 권역")],
   "subs":["만석동","화수1·화평동","화수2동","송현1·2동","송현3동","송림1동","송림2동","송림3·5동","송림4동","송림6동","금창동"],
   "character":"인천 동구는 송림·송현·만석 일대 구도심 주거 권역으로 평일 저녁 가정 방문이 중심을 이룹니다. 호텔 인프라는 제한적입니다.",
   "pattern":"인천 동구는 평일 저녁 7~10시 시간대가 가장 안정적입니다.",
   "faqs":[
     ("송림·송현 가능한가요?","송림·송현 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("만석동 가능한가요?","만석동 일대 가정 방문이 자주 안내됩니다."),
     ("중구와 함께 가능한가요?","중구는 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["jung","michuhol","seo"]},
  {"slug":"michuhol","name":"미추홀구",
   "lede":"미추홀구는 주안·도화·학익 일대의 도심·대학가가 함께 있는 자치구로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","인하대 인근")],
   "subs":["숭의1·3동","숭의2동","숭의4동","용현1·4동","용현2동","용현3동","용현5동","학익1동","학익2동","도화1동","도화2·3동","주안1동","주안2동","주안3동","주안4동","주안5동","주안6동","주안7동","주안8동","관교동","문학동"],
   "character":"인하대학교 인근(용현·학익) 원룸·오피스텔 가정 방문과 주안·도화 일대 주거 단지 가정 방문이 평일 저녁 자주 안내됩니다. 인천종합터미널 인근 호텔 객실 방문도 일부 들어옵니다.",
   "pattern":"미추홀구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("인하대 인근 가능한가요?","용현·학익 일대 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
     ("주안·도화 단지 가능한가요?","주안·도화 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("부평·남동과 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["nam-dong","bupyeong","yeonsu"]},
  {"slug":"yeonsu","name":"연수구",
   "lede":"연수구는 송도국제도시와 옥련·동춘·연수 일대 주거 권역이 함께 있는 자치구로, 비즈니스 호텔 출장·신도시 가정 방문 비중이 모두 큰 권역입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","송도국제도시")],
   "subs":["옥련1동","옥련2동","선학동","연수1동","연수2동","연수3동","청학동","동춘1동","동춘2동","동춘3동","송도1동","송도2동","송도3동"],
   "character":"송도국제도시(송도1~3) 인터컨티넨탈 송도·쉐라톤 그랜드 인천·오크우드 송도 등 5성·4성 호텔에서 비즈니스 출장 객실 방문이 평일 저녁 자주 안내됩니다. 옥련·동춘·연수 일대는 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"연수구는 평일 저녁 7~10시 시간대 비중이 큽니다. 송도 컨벤시아 행사 시즌은 인근 호텔이 빠르게 마감됩니다.",
   "faqs":[
     ("송도 인터컨티넨탈 가능한가요?","송도1~3동 인터컨티넨탈·쉐라톤 객실 방문이 자주 안내됩니다."),
     ("송도 컨벤시아 행사 일정 가능한가요?","행사 시즌 인근 호텔은 사전 예약 권장."),
     ("동춘·연수 단지 가능한가요?","동춘·연수 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["michuhol","nam-dong","jung"]},
  {"slug":"nam-dong","name":"남동구",
   "lede":"남동구는 인천시청·구월·간석 일대 행정·도심 권역과 논현·서창 신도시가 함께 있는 자치구입니다. 평일 저녁 가정·호텔 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","20개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","인천시청·논현")],
   "subs":["구월1동","구월2동","구월3동","구월4동","간석1동","간석2동","간석3동","간석4동","만수1동","만수2동","만수3동","만수4동","만수5동","만수6동","장수서창동","서창2동","남촌도림동","논현1동","논현2동","논현고잔동"],
   "character":"인천시청·구월·간석 일대 행정 권역 가정 방문과 논현·서창 신도시 대단지 가정 방문이 평일 저녁 자주 안내됩니다. 구월 라마다 송도·호텔 인천 등 비즈니스 호텔 객실 방문도 함께 들어옵니다.",
   "pattern":"남동구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("논현·서창 신도시 가능한가요?","논현1·2·서창 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("인천시청 인근 가능한가요?","구월·간석 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("부평·미추홀과 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["michuhol","bupyeong","yeonsu"]},
  {"slug":"bupyeong","name":"부평구",
   "lede":"부평구는 부평역 일대 도심 권역과 십정·갈산·청천 주거가 함께 있는 자치구로, 평일 저녁 가정 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","22개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","부평역 도심")],
   "subs":["부평1동","부평2동","부평3동","부평4동","부평5동","부평6동","산곡1동","산곡2동","산곡3동","산곡4동","청천1동","청천2동","갈산1동","갈산2동","삼산1동","삼산2동","부개1동","부개2동","부개3동","일신동","십정1동","십정2동"],
   "character":"부평역·부평지하상가·삼산·갈산 일대 주거 단지와 GM 한국부평공장 인근에서 평일 저녁 가정 방문이 매우 자주 안내됩니다. 호텔 인프라는 제한적이라 객실 방문 비중은 낮은 편입니다.",
   "pattern":"부평구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("부평역 인근 가능한가요?","부평1~6동 일대 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("삼산·갈산 단지 가능한가요?","삼산·갈산 일대 단지 가정 방문이 안내됩니다."),
     ("부천 중동과 같은 권역인가요?","부천은 경기도이며 별도 권역입니다. <a href=\"/area/gyeonggi/bucheon/\">부천 안내</a>를 참고해 주세요."),
   ],"neighbors":["gyeyang","nam-dong","seo"]},
  {"slug":"gyeyang","name":"계양구",
   "lede":"계양구는 계산·작전·임학 일대의 주거 권역과 김포공항 인접 권역이 함께 있는 자치구로, 평일 저녁 가정 방문 중심입니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","김포공항 인접")],
   "subs":["효성1동","효성2동","계산1동","계산2동","계산3동","계산4동","작전1동","작전2동","작전서운동","계양1동","계양2동","계양3동"],
   "character":"계산·작전·효성 일대 주거 단지 가정 방문이 평일 저녁 중심을 이룹니다. 김포공항(서울 강서)과 인접해 일부 환승 케이스도 들어옵니다.",
   "pattern":"계양구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("계산·작전 단지 가능한가요?","계산·작전 일대 가정 방문이 자주 안내됩니다."),
     ("김포공항과 함께 가능한가요?","김포공항은 서울 강서구이며 별도 권역입니다."),
     ("부평·서구와 같은 권역인가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["bupyeong","seo","jung"]},
  {"slug":"seo","name":"서구",
   "lede":"인천 서구는 청라국제도시·검단신도시·가정 일대 신도시 권역이 밀집한 자치구로, 평일 저녁 신도시 가정 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","22개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","청라·검단")],
   "subs":["검암경서동","연희동","청라1동","청라2동","청라3동","가정1동","가정2동","가정3동","석남1동","석남2동","석남3동","신현원창동","가좌1동","가좌2동","가좌3동","가좌4동","왕길동","검단동","마전동","당하동","원당동","불로대곡동","오류왕길동"],
   "character":"청라국제도시(청라1~3)·검단신도시·가정루원시티 등 대규모 신도시가 밀집해 평일 저녁 가정 방문 비중이 가장 큰 자치구 중 하나입니다. 청라 일대 비즈니스 호텔에서 객실 방문도 함께 들어옵니다.",
   "pattern":"인천 서구는 평일 저녁 7~11시 시간대 비중이 매우 큽니다.",
   "faqs":[
     ("청라국제도시 가능한가요?","청라1~3동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("검단신도시 가능한가요?","검단·당하·마전 일대 신축 단지 가정 방문이 안내됩니다."),
     ("김포 한강신도시와 같은 권역인가요?","김포 한강은 경기도이며 별도 권역입니다."),
   ],"neighbors":["gyeyang","bupyeong","jung"]},
  {"slug":"ganghwa","name":"강화군",
   "lede":"강화군은 강화도·교동도 등 도서 권역으로 이루어진 군으로, 평일 저녁 도심 권역 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","도서 권역")],
   "subs":["강화읍","선원면","불은면","길상면","화도면","양도면","내가면","하점면","양사면","송해면","교동면","삼산면","서도면"],
   "character":"강화읍 도심 가정 방문과 강화도 일대 펜션·게스트하우스 객실 방문이 함께 안내됩니다. 교동·삼산·서도 등 도서 면 단위는 이동 시간 특성상 사전 협의가 필요한 권역입니다.",
   "pattern":"강화군은 평일 저녁 7~9시 시간대가 안정적이며, 도서 권역은 마감이 빠릅니다.",
   "faqs":[
     ("강화 도심 가능한가요?","강화읍 일대 가정 방문이 안내됩니다."),
     ("강화도 펜션 가능한가요?","화도·길상 일대 펜션 객실 방문이 안내됩니다."),
     ("교동도·석모도 가능한가요?","도서 권역은 이동 시간상 사전 협의가 필요합니다."),
   ],"neighbors":["seo","gimpo-ext"]},
  {"slug":"ongjin","name":"옹진군",
   "lede":"옹진군은 백령·연평·덕적 등 서해 도서 권역으로 이루어진 군으로, 이동 시간 특성상 일정 사전 협의가 필요한 권역입니다.",
   "facts":[("행정동","7개"),("주요 시간대","사전 협의"),("호텔/가정","사전 협의"),("특이점","서해 도서")],
   "subs":["북도면","연평면","백령면","대청면","덕적면","자월면","영흥면"],
   "character":"옹진군은 백령·연평·덕적·자월·영흥 등 도서 권역으로, 정기 여객선 일정에 맞춘 사전 협의 일정에서 안내가 가능합니다. 영흥면 일대 펜션 권역이 비교적 접근 가능합니다.",
   "pattern":"옹진군은 도서 권역 특성상 사전 일정 협의가 필수입니다.",
   "faqs":[
     ("백령도 가능한가요?","백령·연평 등 원거리 도서는 사전 일정 협의가 필수입니다."),
     ("영흥도 펜션 가능한가요?","영흥면 일대 펜션 객실 방문이 비교적 접근 가능합니다."),
     ("덕적도 가능한가요?","덕적·자월은 정기 여객선 일정에 맞춘 사전 협의가 필요합니다."),
   ],"neighbors":["jung","ganghwa"]},
]


# ---- 대구 9 ----
DAEGU_DISTRICTS = [
  {"slug":"jung","name":"중구",
   "lede":"대구 중구는 동성로·교동·반월당 일대의 도심 권역으로, 비즈니스 호텔 객실 방문 비중이 큰 자치구입니다.",
   "facts":[("행정동","8개"),("주요 시간대","야간"),("호텔/가정","호텔 비중↑"),("특이점","동성로 도심")],
   "subs":["동인동","삼덕동","성내1동","성내2동","성내3동","대신동","남산동","대봉1동","대봉2동"],
   "character":"동성로·교동·반월당 일대 노보텔 앰배서더 대구·라온제나 호텔 대구·매리어트 대구 등 5성·4성 호텔에서 출장 객실 방문이 자주 안내됩니다.",
   "pattern":"대구 중구는 야간 시간대 비중이 큽니다.",
   "faqs":[
     ("노보텔 앰배서더 대구 가능한가요?","동성로 노보텔 객실 방문이 자주 안내됩니다."),
     ("동성로 일정 후 가능한가요?","도심 호텔 객실 방문이 야간 시간대 안내됩니다."),
     ("반월당역 인근 가능한가요?","반월당·교동 일대 호텔·오피스텔 방문이 안내됩니다."),
   ],"neighbors":["dong","seo","nam"]},
  {"slug":"dong","name":"동구",
   "lede":"대구 동구는 동대구역·신천·신서혁신도시 일대의 교통·신도시 권역으로, KTX 환승 호텔과 평일 저녁 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","20개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","KTX 동대구역")],
   "subs":["신암1동","신암2동","신암3동","신암4동","신암5동","신천1·2동","신천3동","신천4동","효목1동","효목2동","도평동","불로봉무동","지저동","동촌동","방촌동","해안동","안심1동","안심2동","안심3·4동","공산동"],
   "character":"동대구역(KTX·SRT) 인근 호텔(노보텔 앰배서더 동대구·메리어트 대구·인터불고 EXCO)에서 환승·출장 객실 방문이 자주 안내됩니다. 신서혁신도시(안심1~4)는 신축 단지 가정 방문 권역입니다.",
   "pattern":"대구 동구는 평일 저녁 시간대와 KTX 환승 시간대 모두 안내됩니다.",
   "faqs":[
     ("KTX 동대구역 환승 가능한가요?","동대구역 인근 호텔 단시간 코스가 자주 안내됩니다."),
     ("신서혁신도시 가능한가요?","안심 일대 신축 단지 가정 방문이 안내됩니다."),
     ("EXCO 행사 일정 가능한가요?","행사 시즌 인근 호텔은 사전 예약 권장."),
   ],"neighbors":["jung","buk","suseong"]},
  {"slug":"seo","name":"서구",
   "lede":"대구 서구는 평리·내당·중리 일대의 주거 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","주거 권역")],
   "subs":["내당1동","내당2·3동","내당4동","비산1동","비산2·3동","비산4동","비산5동","비산6동","비산7동","평리1동","평리2동","평리3동","평리4동","평리5동","평리6동","상중이동","원대동"],
   "character":"대구 서구는 내당·비산·평리 일대 주거 단지 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"대구 서구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("내당·비산 가능한가요?","내당·비산 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("평리 단지 가능한가요?","평리1~6동 일대 가정 방문이 자주 안내됩니다."),
     ("중구와 함께 가능한가요?","중구는 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["jung","buk","dalseo"]},
  {"slug":"nam","name":"남구",
   "lede":"대구 남구는 봉덕·대명 일대 주거 권역과 영남대 의료원 인접 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 중심입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","영남대의료원")],
   "subs":["이천동","봉덕1동","봉덕2동","봉덕3동","대명1동","대명2동","대명3동","대명4동","대명5동","대명6동","대명9동","대명10동","대명11동"],
   "character":"대구 남구는 봉덕·대명 일대 주거 단지와 영남대학교·의료원 인근 권역에서 평일 저녁 가정 방문이 자주 안내됩니다.",
   "pattern":"대구 남구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("영남대 인근 가능한가요?","대명 일대 원룸·오피스텔 가정 방문이 안내됩니다."),
     ("봉덕동 가능한가요?","봉덕1~3동 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("중구·수성과 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["jung","suseong","dalseo"]},
  {"slug":"buk","name":"북구",
   "lede":"대구 북구는 칠곡·복현·산격·검단 일대 주거 권역과 EXCO·경북대가 함께 있는 자치구로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","27개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","경북대·EXCO")],
   "subs":["고성동","칠성동","침산1동","침산2동","침산3동","산격1동","산격2동","산격3동","산격4동","대현동","복현1동","복현2동","검단동","무태조야동","관문동","태전1동","태전2동","구암동","관음동","읍내동","동천동","국우동","노원동","칠곡중앙대로","불로봉무동"],
   "character":"칠곡지구(태전·구암·관음·읍내)와 산격·복현 일대 주거 단지 가정 방문이 평일 저녁 중심입니다. 경북대학교 인근(대현·복현) 원룸·오피스텔과 EXCO 인근 호텔 객실 방문도 함께 들어옵니다.",
   "pattern":"대구 북구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("칠곡지구 가능한가요?","태전·구암·관음 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("경북대 인근 가능한가요?","대현·복현 일대 원룸·오피스텔 가정 방문이 안내됩니다."),
     ("EXCO 행사 일정 가능한가요?","EXCO 인근 호텔 객실 방문이 행사 시즌 안내됩니다."),
   ],"neighbors":["dong","seo","dalseong"]},
  {"slug":"suseong","name":"수성구",
   "lede":"수성구는 범어·만촌·황금 일대의 학원가와 대단지 주거가 밀집한 자치구로, 대구에서 평일 저녁 가정 방문 비중이 가장 큰 권역입니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","수성 학원가")],
   "subs":["범어1동","범어2동","범어3동","범어4동","만촌1동","만촌2동","만촌3동","수성1가동","수성2·3가동","수성4가동","황금1동","황금2동","중동","상동","파동","두산동","지산1동","지산2동","범물1동","범물2동","고산1동","고산2동","고산3동"],
   "character":"수성구는 범어·만촌·황금·수성 일대의 대구 최대 학원가와 대단지 아파트가 밀집해 평일 저녁 가정 방문 비중이 압도적입니다. 두산·상동 일대도 주거 권역으로 가정 방문이 중심입니다.",
   "pattern":"수성구는 평일 저녁 7~10시 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("범어·만촌 가능한가요?","범어·만촌 일대 대단지 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("수성구 학원가 인근 가능한가요?","학원가 권역은 주말 가족 시간대 외 늦은 저녁 권장."),
     ("동·남·중구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["dong","nam","jung"]},
  {"slug":"dalseo","name":"달서구",
   "lede":"달서구는 상인·진천·월배·죽전 일대의 주거 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","22개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","월배·상인")],
   "subs":["성당동","두류1·2동","두류3동","감삼동","죽전동","장기동","용산1동","용산2동","이곡1동","이곡2동","신당동","본리동","월성1동","월성2동","진천동","유천동","상인1동","상인2동","상인3동","도원동","송현1동","송현2동","본동"],
   "character":"상인·진천·월배(월성·유천) 일대 대단지 가정 방문과 죽전·장기·이곡 일대 주거 권역 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"달서구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("상인·진천 가능한가요?","상인1~3·진천 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("월배(월성·유천) 가능한가요?","월성·유천 일대 단지 가정 방문이 안내됩니다."),
     ("성서산단 출장 가능한가요?","이곡·신당 일대 비즈니스 호텔 객실 방문이 일부 안내됩니다."),
   ],"neighbors":["seo","nam","dalseong"]},
  {"slug":"dalseong","name":"달성군",
   "lede":"달성군은 화원·다사·옥포 일대 신축 단지와 대구테크노폴리스(현풍·구지)가 함께 있는 군으로, 평일 저녁 가정·산업 출장 방문이 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","테크노폴리스")],
   "subs":["화원읍","논공읍","다사읍","유가읍","옥포읍","현풍읍","가창면","하빈면","구지면"],
   "character":"화원·다사·옥포 일대 신축 단지 가정 방문과 대구테크노폴리스(현풍·구지) 산업단지 출장 호텔 객실 방문이 함께 안내됩니다.",
   "pattern":"달성군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("화원·다사 가능한가요?","화원·다사·옥포 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("테크노폴리스 출장 가능한가요?","현풍·구지 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("달서구와 같은 권역인가요?","달서는 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["dalseo","buk","gunwi"]},
  {"slug":"gunwi","name":"군위군",
   "lede":"군위군은 2023년 7월 대구광역시로 편입된 군으로, 군위읍·효령 일대 가정 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","2023 대구 편입")],
   "subs":["군위읍","소보면","효령면","부계면","우보면","의흥면","산성면","삼국유사면"],
   "character":"군위군은 2023년 7월 대구광역시로 편입된 군 단위 권역으로, 군위읍·효령·우보 일대 가정 방문이 안내됩니다. 외곽 면 단위는 사전 일정 협의가 필요한 권역입니다.",
   "pattern":"군위군은 평일 저녁 7~9시 시간대가 안정적이며, 외곽 면은 마감이 빠릅니다.",
   "faqs":[
     ("군위읍 가능한가요?","군위읍 일대 가정 방문이 안내됩니다."),
     ("외곽 면 단위 가능한가요?","면 단위 외곽은 이동 시간 특성상 사전 협의가 필요합니다."),
     ("대구 다른 자치구와 함께 가능한가요?","대구 본 시가지와 권역이 다르므로 각각 사전 확인이 필요합니다."),
   ],"neighbors":["dalseong","buk","dong"]},
]


# ---- 대전 5 ----
DAEJEON_DISTRICTS = [
  {"slug":"dong","name":"동구",
   "lede":"대전 동구는 대전역 일대 도심 권역과 가양·용운 주거가 함께 있는 자치구로, KTX 환승 호텔과 평일 저녁 가정 방문이 안내됩니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","대전역")],
   "subs":["중앙동","효동","신인동","판암1동","판암2동","대동","자양동","가양1동","가양2동","용운동","대청동","산내동","낭월동","성남동","홍도동","삼성동","천동"],
   "character":"대전역 인근 롯데시티호텔 대전·아드리아호텔·인터시티호텔 등에서 KTX 환승·출장 객실 방문이 자주 안내됩니다. 가양·용운 일대 주거 단지 가정 방문도 함께 들어옵니다.",
   "pattern":"대전 동구는 평일 저녁 시간대와 KTX 환승 시간대 모두 안내됩니다.",
   "faqs":[
     ("대전역 KTX 환승 가능한가요?","대전역 인근 호텔 단시간 코스가 자주 안내됩니다."),
     ("가양·용운 가능한가요?","가양1·2동 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("중구·서구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["jung","seo","daedeok"]},
  {"slug":"jung","name":"중구",
   "lede":"대전 중구는 은행동·대흥·문화 일대 도심 권역과 유천·태평 주거가 함께 있는 자치구입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","대전 구도심")],
   "subs":["은행선화동","목동","중촌동","대흥동","문창동","석교동","대사동","부사동","용두동","오류동","태평1동","태평2동","유천1동","유천2동"],
   "character":"대전 중구는 은행·대흥 도심 권역 가정 방문과 유천·태평 일대 주거 단지에서 평일 저녁 가정 방문이 자주 안내됩니다.",
   "pattern":"대전 중구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("은행·대흥 도심 가능한가요?","은행선화·대흥 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("유천·태평 가능한가요?","유천1·2·태평1·2 일대 가정 방문이 자주 안내됩니다."),
     ("동구·서구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["dong","seo","daedeok"]},
  {"slug":"seo","name":"서구",
   "lede":"대전 서구는 둔산·만년·갈마 일대의 행정·도심 권역으로, 정부대전청사 인접 평일 저녁 출장 호텔·가정 방문 비중이 큰 자치구입니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","정부대전청사")],
   "subs":["복수동","도마1동","도마2동","정림동","변동","용문동","탄방동","둔산1동","둔산2동","둔산3동","갈마1동","갈마2동","월평1동","월평2동","월평3동","만년동","가장동","내동","가수원동","관저1동","관저2동","기성동"],
   "character":"둔산동(정부대전청사)·갈마·만년 일대 행정·비즈니스 권역에서 평일 저녁 호텔 객실 방문(롯데시티호텔 대전·노보텔 앰배서더 대전 등) 비중이 큽니다. 도마·정림·관저 일대는 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"대전 서구는 평일 저녁 7~10시 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("롯데시티호텔 대전 가능한가요?","둔산 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("정부대전청사 출장 가능한가요?","둔산·갈마 일대 출장 호텔 객실 방문이 안내됩니다."),
     ("관저·가수원 단지 가능한가요?","관저1·2·가수원 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["jung","yuseong","daedeok"]},
  {"slug":"yuseong","name":"유성구",
   "lede":"유성구는 대덕연구단지·KAIST·정부출연연이 자리한 연구·과학 권역으로, 평일 저녁 출장 호텔 객실 방문 비중이 대전에서 가장 큰 자치구입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","호텔 비중↑"),("특이점","대덕연구단지")],
   "subs":["진잠동","온천1동","온천2동","노은1동","노은2동","노은3동","신성동","전민동","구즉동","관평동","원신흥동","상대동","학하동","덕명동"],
   "character":"유성구는 대덕연구단지(전민·구즉·신성)·KAIST(어은·구성) 출장 일정과 맞물려 평일 저녁 호텔 객실 방문 비중이 매우 큽니다. 유성온천 일대 호텔(호텔ICC·라온컨벤션호텔·인터시티 대전)과 노은신도시(노은1~3)는 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"유성구는 평일 저녁 7~10시 시간대 비중이 큽니다. 외국인 엔지니어 케이스는 영어 안내 협의가 필요할 수 있습니다.",
   "faqs":[
     ("호텔ICC·인터시티 대전 가능한가요?","유성 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("KAIST 인근 가능한가요?","구성·어은 일대 가정 방문과 호텔 객실 방문이 안내됩니다."),
     ("노은신도시 가능한가요?","노은1~3동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
   ],"neighbors":["seo","daedeok","sejong-ext"]},
  {"slug":"daedeok","name":"대덕구",
   "lede":"대덕구는 신탄진·법동·송촌 일대 주거 권역과 대덕산업단지가 함께 있는 자치구로, 평일 저녁 가정·산업 출장 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","대덕산단")],
   "subs":["오정동","대화동","회덕동","비래동","송촌동","중리동","신탄진동","석봉동","덕암동","목상동","법1동","법2동"],
   "character":"송촌·법·중리 일대 주거 단지와 신탄진·대화 일대 산업단지 권역에서 평일 저녁 가정·출장 호텔 객실 방문이 함께 안내됩니다.",
   "pattern":"대덕구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("송촌·법동 가능한가요?","송촌·법1·2 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("신탄진 산단 출장 가능한가요?","신탄진 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("동구·서구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["dong","seo","yuseong"]},
]


# ---- 광주 5 ----
GWANGJU_DISTRICTS = [
  {"slug":"dong","name":"동구",
   "lede":"광주 동구는 충장로·금남로·동명 일대 구도심 권역으로, 평일 저녁 가정·도심 호텔 방문이 함께 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","충장로·금남로")],
   "subs":["충장동","동명동","계림1동","계림2동","산수1동","산수2동","지산1동","지산2동","서남동","학동","학운동","지원1동","지원2동"],
   "character":"충장로·금남로 일대 도심 호텔과 동명·계림 일대 주거 권역에서 평일 저녁 가정·호텔 객실 방문이 함께 안내됩니다.",
   "pattern":"광주 동구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("충장로 도심 가능한가요?","충장·금남로 일대 도심 가정·호텔 방문이 안내됩니다."),
     ("동명·계림 가능한가요?","동명·계림1·2 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("서·남구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["seo","nam","buk"]},
  {"slug":"seo","name":"서구",
   "lede":"광주 서구는 상무지구·치평·금호 일대의 비즈니스·신도시 권역으로, 광주에서 평일 저녁 출장 호텔·가정 방문 비중이 가장 큰 자치구입니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","상무지구")],
   "subs":["양동","양3동","농성1동","농성2동","광천동","유덕동","치평동","상무1동","상무2동","화정1동","화정2동","화정3동","화정4동","서창동","금호1동","금호2동","풍암동","동천동"],
   "character":"상무지구(상무1·2·치평)는 광주김대중컨벤션센터 인근으로 라마다플라자 광주·홀리데이인 광주 등 비즈니스 호텔 객실 방문이 자주 안내됩니다. 금호·풍암·화정 일대 대단지 가정 방문도 평일 저녁 활발합니다.",
   "pattern":"광주 서구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("라마다플라자 광주 가능한가요?","상무지구 라마다플라자·홀리데이인 객실 방문이 자주 안내됩니다."),
     ("김대중컨벤션센터 행사 가능한가요?","행사 시즌 인근 호텔은 사전 예약 권장."),
     ("금호·풍암 단지 가능한가요?","금호1·2·풍암 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["dong","nam","gwangsan"]},
  {"slug":"nam","name":"남구",
   "lede":"광주 남구는 봉선·진월·주월 일대의 주거 권역으로 이루어진 자치구로, 평일 저녁 가정 방문 중심의 권역입니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","봉선동 주거")],
   "subs":["양림동","방림1동","방림2동","사직동","월산동","월산4동","월산5동","백운1동","백운2동","주월1동","주월2동","효덕동","송암동","대촌동","봉선1동","봉선2동","진월동"],
   "character":"봉선동(봉선1·2)·진월·주월 일대 대단지 가정 방문이 평일 저녁 자주 안내됩니다. 양림·방림은 일반 주거 권역입니다.",
   "pattern":"광주 남구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("봉선동 가능한가요?","봉선1·2동 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("진월·주월 가능한가요?","진월·주월1·2 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("동구·서구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["dong","seo","buk"]},
  {"slug":"buk","name":"북구",
   "lede":"광주 북구는 전남대·일곡·운암·문흥 일대 주거 권역과 광주역 인접 도심이 함께 있는 자치구로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","27개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","전남대·일곡")],
   "subs":["중흥1동","중흥2동","중흥3동","유동","우산동","풍향동","문화동","두암1동","두암2동","두암3동","삼각동","일곡동","매곡동","오치1동","오치2동","건국동","문흥1동","문흥2동","임동","용봉동","운암1동","운암2동","운암3동","동림동","서림동","석곡동","태봉동"],
   "character":"광주 북구는 전남대학교 인근(용봉·운암)과 일곡·문흥·두암 일대 대단지 주거 권역에서 평일 저녁 가정 방문이 자주 안내됩니다. 광주역 인근 호텔 객실 방문도 일부 들어옵니다.",
   "pattern":"광주 북구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("전남대 인근 가능한가요?","용봉·운암 일대 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
     ("일곡·문흥 단지 가능한가요?","일곡·문흥1·2 일대 대단지 가정 방문이 안내됩니다."),
     ("두암 가능한가요?","두암1~3 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["dong","seo","gwangsan"]},
  {"slug":"gwangsan","name":"광산구",
   "lede":"광산구는 첨단·수완·운남 일대 신도시 권역과 송정·하남산단이 함께 있는 자치구로, 평일 저녁 신도시 가정 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","첨단·수완")],
   "subs":["송정1동","송정2동","도산동","도호동","신흥동","어룡동","우산동","월곡1동","월곡2동","운남동","수완동","하남동","임곡동","동곡동","평동","삼도동","본량동","비아동","첨단1동","첨단2동","신가동"],
   "character":"첨단지구(첨단1·2·신가)·수완지구·운남 일대 대규모 신도시 단지에서 평일 저녁 가정 방문이 매우 자주 안내됩니다. 송정역(KTX) 인근 호텔 객실 방문도 들어옵니다.",
   "pattern":"광산구는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("첨단지구 가능한가요?","첨단1·2·신가 일대 대단지 가정 방문이 자주 안내됩니다."),
     ("수완지구 가능한가요?","수완 일대 신축 단지 가정 방문이 안내됩니다."),
     ("KTX 송정역 환승 가능한가요?","송정역 인근 호텔 단시간 코스가 안내됩니다."),
   ],"neighbors":["buk","seo","nam"]},
]


# ---- 울산 5 ----
ULSAN_DISTRICTS = [
  {"slug":"jung","name":"중구",
   "lede":"울산 중구는 성안·태화·우정 일대의 구도심 권역으로, 평일 저녁 가정 방문과 도심 호텔 객실 방문이 함께 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","울산 구도심")],
   "subs":["학성동","반구1동","반구2동","복산1동","복산2동","중앙동","우정동","태화동","다운동","병영1동","병영2동","약사동","성안동"],
   "character":"중앙·우정·태화 일대 도심 가정 방문과 성안 일대 신축 단지 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"울산 중구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("성안 신축 단지 가능한가요?","성안동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("우정·태화 가능한가요?","우정·태화 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("남·동구와 함께 가능한가요?","각각 별도 자치구로 권역별 확인이 필요합니다."),
   ],"neighbors":["nam","dong","buk"]},
  {"slug":"nam","name":"남구",
   "lede":"울산 남구는 삼산·달동·신정 일대의 비즈니스 호텔 권역과 옥동·신복 주거가 함께 있는 자치구로, 평일 저녁 출장 호텔 객실 방문 비중이 가장 큰 권역입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","호텔 비중↑"),("특이점","삼산 비즈니스")],
   "subs":["신정1동","신정2동","신정3동","신정4동","신정5동","달동","삼산동","야음장생포동","대현동","수암동","선암동","무거동","옥동","두왕동"],
   "character":"삼산·달동 일대 롯데호텔 울산·신라스테이 울산·현대호텔·라마다 울산 등 비즈니스 호텔이 모인 권역으로 평일 저녁 출장 객실 방문 비중이 큽니다. 옥동·신복 일대는 주거 권역으로 가정 방문이 함께 들어옵니다.",
   "pattern":"울산 남구는 평일 저녁 시간대 비중이 가장 큽니다. 산업단지 출장과 맞물려 야간 시간대도 자주 안내됩니다.",
   "faqs":[
     ("롯데호텔 울산 가능한가요?","삼산 롯데호텔 울산·신라스테이 객실 방문이 자주 안내됩니다."),
     ("울산 산업단지 출장 가능한가요?","SK·S-OIL 등 산단 출장과 맞물린 호텔 객실 방문이 안내됩니다."),
     ("옥동 가정 가능한가요?","옥동 일대 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["jung","dong","ulju"]},
  {"slug":"dong","name":"동구",
   "lede":"울산 동구는 현대중공업·미포조선이 자리한 조선·산업 권역으로, 평일 야간 장기 출장 호텔 객실 방문 비중이 큰 자치구입니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 야간"),("호텔/가정","호텔 비중↑↑"),("특이점","현대중공업·미포")],
   "subs":["방어동","화정동","대송동","전하1동","전하2동","남목1동","남목2동","남목3동","일산동"],
   "character":"동구는 현대중공업·미포조선 등 조선소 출장 권역으로 일산·방어·전하 일대 비즈니스 호텔·게스트하우스에서 장기 출장 객실 방문이 평일 야간 자주 안내됩니다. 외국인 엔지니어 케이스도 많아 영어 안내 협의 일정이 필요할 수 있습니다.",
   "pattern":"울산 동구는 평일 야간(9~12시) 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("현대중공업 출장 가능한가요?","방어·일산 일대 비즈니스 호텔 객실 방문이 평일 야간 자주 안내됩니다."),
     ("외국인 엔지니어 가능한가요?","영어 안내 협의 일정에서 가능 여부 확인됩니다."),
     ("장기 출장 정기 예약 가능한가요?","주차별 사전 확인을 통한 정기 예약이 가능합니다."),
   ],"neighbors":["nam","jung","buk"]},
  {"slug":"buk","name":"북구",
   "lede":"울산 북구는 매곡·연암·송정 일대 신도시와 농소 권역이 함께 있는 자치구로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","송정·매곡 신도시")],
   "subs":["농소1동","농소2동","농소3동","강동동","효문동","송정동","양정동","염포동","연암동"],
   "character":"매곡·연암·송정·양정 일대 신축 단지 가정 방문이 평일 저녁 중심을 이룹니다. 효문산단·매곡산단 출장 호텔 객실 방문도 일부 들어옵니다.",
   "pattern":"울산 북구는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("송정·매곡 신도시 가능한가요?","송정·매곡 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("농소 가능한가요?","농소1~3 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("효문산단 출장 가능한가요?","효문·매곡산단 인근 비즈니스 호텔 객실 방문이 안내됩니다."),
   ],"neighbors":["jung","dong","ulju"]},
  {"slug":"ulju","name":"울주군",
   "lede":"울주군은 KTX 울산역(언양)·온산공단·서생면 일대로 이루어진 군으로, 평일 저녁 출장·신도시 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","KTX 울산역·온산")],
   "subs":["온산읍","언양읍","온양읍","범서읍","청량읍","삼남읍","서생면","웅촌면","두서면","두동면","상북면","삼동면"],
   "character":"언양읍(KTX 울산역) 인근 호텔에서 환승·출장 객실 방문이 자주 안내되며, 온산읍 산업단지 출장 호텔과 범서·삼남 일대 신축 단지 가정 방문도 함께 들어옵니다.",
   "pattern":"울주군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("KTX 울산역 환승 가능한가요?","언양읍 인근 호텔 단시간 코스가 자주 안내됩니다."),
     ("온산공단 출장 가능한가요?","온산읍 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("범서·삼남 신축 단지 가능한가요?","범서·삼남 일대 신축 단지 가정 방문이 평일 저녁 안내됩니다."),
   ],"neighbors":["nam","jung","buk"]},
]


# ---- 세종 1 ----
SEJONG_DISTRICTS = [
  {"slug":"sejong-si","name":"세종특별자치시",
   "lede":"세종특별자치시는 행정중심복합도시로, 신도시 행정동(한솔·새롬·도담 등 17개)과 구도심 읍·면(조치원·연기 등 10개)이 함께 있는 특별자치시입니다.",
   "facts":[("행정동","27개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","정부세종청사")],
   "subs":["한솔동","새롬동","다정동","도담동","어진동","종촌동","아름동","고운동","보람동","대평동","소담동","반곡동","해밀동","산울동","합강동","나성동","가람동","조치원읍","연기면","연동면","부강면","금남면","장군면","연서면","전의면","전동면","소정면"],
   "character":"세종 신도시(한솔·새롬·도담·새롬·종촌·아름·보람·대평·소담·반곡 등)는 정부세종청사 공무원·연구원 거주가 밀집해 평일 저녁 가정 방문 비중이 매우 큽니다. 호텔 인프라가 광역시 대비 적어 객실 방문 비중은 낮습니다. 조치원읍·연기면 등 구도심은 일반 주거 권역입니다.",
   "pattern":"세종은 평일 저녁 7~10시 시간대 가정 방문 비중이 가장 큽니다.",
   "faqs":[
     ("정부세종청사 근처 가능한가요?","어진·도담·종촌 일대 청사 인근 가정 방문이 평일 저녁 자주 안내됩니다."),
     ("호텔 방문 가능한가요?","세종 호텔 수가 광역시 대비 적어 객실 방문 사례는 제한적입니다."),
     ("조치원 가능한가요?","조치원읍 일대 가정 방문이 안내됩니다."),
   ],"neighbors":[]},
]


for _d in BUSAN_DISTRICTS:
    DISTRICT_PAGE_INDEX[("busan", _d["name"])] = f"/area/busan/{_d['slug']}/"
for _d in INCHEON_DISTRICTS:
    DISTRICT_PAGE_INDEX[("incheon", _d["name"])] = f"/area/incheon/{_d['slug']}/"
for _d in DAEGU_DISTRICTS:
    DISTRICT_PAGE_INDEX[("daegu", _d["name"])] = f"/area/daegu/{_d['slug']}/"
for _d in DAEJEON_DISTRICTS:
    DISTRICT_PAGE_INDEX[("daejeon", _d["name"])] = f"/area/daejeon/{_d['slug']}/"
for _d in GWANGJU_DISTRICTS:
    DISTRICT_PAGE_INDEX[("gwangju", _d["name"])] = f"/area/gwangju/{_d['slug']}/"
for _d in ULSAN_DISTRICTS:
    DISTRICT_PAGE_INDEX[("ulsan", _d["name"])] = f"/area/ulsan/{_d['slug']}/"

for _d in BUSAN_DISTRICTS:
    _build_metro_district("busan", "부산", _d, BUSAN_DISTRICTS)
for _d in INCHEON_DISTRICTS:
    _build_metro_district("incheon", "인천", _d, INCHEON_DISTRICTS)
for _d in DAEGU_DISTRICTS:
    _build_metro_district("daegu", "대구", _d, DAEGU_DISTRICTS)
for _d in DAEJEON_DISTRICTS:
    _build_metro_district("daejeon", "대전", _d, DAEJEON_DISTRICTS)
for _d in GWANGJU_DISTRICTS:
    _build_metro_district("gwangju", "광주", _d, GWANGJU_DISTRICTS)
for _d in ULSAN_DISTRICTS:
    _build_metro_district("ulsan", "울산", _d, ULSAN_DISTRICTS)
for _d in SEJONG_DISTRICTS:
    _build_metro_district("sejong", "세종", _d, SEJONG_DISTRICTS)


# ============================================================
# 강원특별자치도 18 (시 7 + 군 11)
# ============================================================
GANGWON_DISTRICTS = [
  {"slug":"chuncheon","name":"춘천시",
   "lede":"춘천시는 강원도청 소재지이자 의암호·소양호가 어우러진 호반의 도시로, 평일 저녁 가정 방문과 호수변 펜션·호텔 객실 방문이 함께 안내됩니다.",
   "facts":[("행정동","25개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","강원도청")],
   "subs":["조운동","약사명동","교동","근화동","소양동","강남동","후평1동","후평2동","후평3동","효자1동","효자2동","효자3동","석사동","퇴계동","신사우동","신북읍","동면","서면","사북면","북산면","남면","남산면","동산면","동내면","신동면"],
   "character":"춘천시는 석사·퇴계·강남·후평 일대 주거 단지 가정 방문과 의암호 인근 호텔·펜션(라데나리조트·세종호텔) 객실 방문이 함께 안내됩니다. 한림대·강원대 인근 권역에서 원룸·오피스텔 가정 방문도 자주 들어옵니다.",
   "pattern":"춘천시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("의암호 펜션 가능한가요?","서면·신북 일대 호수변 펜션 객실 방문이 안내됩니다."),
     ("한림대·강원대 인근 가능한가요?","석사·후평 일대 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
     ("가평·홍천과 함께 가능한가요?","각각 별도 권역으로 사전 확인이 필요합니다."),
   ],"neighbors":["hongcheon","hwacheon","yanggu"]},
  {"slug":"wonju","name":"원주시",
   "lede":"원주시는 강원 최대 도시이자 의료·기업 도시로, 혁신도시·기업도시 권역에서 평일 저녁 출장 호텔·가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","25개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","혁신·기업도시")],
   "subs":["중앙동","원인동","개운동","명륜1동","명륜2동","단계동","일산동","학성동","단구동","무실동","반곡관설동","봉산동","행구동","우산동","태장1동","태장2동","문막읍","소초면","호저면","지정면","부론면","귀래면","흥업면","판부면","신림면"],
   "character":"무실·단구·반곡관설 일대 혁신도시 단지와 명륜·일산 도심 권역에서 평일 저녁 가정 방문이 자주 안내됩니다. 원주역(KTX) 인근 호텔과 기업도시 인접 비즈니스 호텔 객실 방문도 함께 들어옵니다.",
   "pattern":"원주시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("혁신도시 단지 가능한가요?","반곡관설·무실 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("KTX 원주역 환승 가능한가요?","원주역 인근 호텔 단시간 코스가 안내됩니다."),
     ("의료기기 클러스터 출장 가능한가요?","태장·문막 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
   ],"neighbors":["hoengseong","yeongwol","jecheon-ext"]},
  {"slug":"gangneung","name":"강릉시",
   "lede":"강릉시는 동해안 관광 거점 도시로, 경포·안목·정동진 일대 호텔·펜션 객실 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","13개"),("주요 시간대","시즌·야간"),("호텔/가정","호텔 비중↑"),("특이점","경포·안목·서핑")],
   "subs":["홍제동","중앙동","옥천동","교1동","교2동","포남1동","포남2동","초당동","송정동","강남동","성덕동","경포동","주문진읍","연곡면","사천면","성산면","왕산면","구정면","강동면","옥계면"],
   "character":"강릉시는 경포·안목·송정 일대 관광 호텔(세인트존스·스카이베이 경포·라카이 샌드파인 등)에서 휴양 일정 후 객실 방문이 자주 안내됩니다. 안목해변 카페거리·정동진 일대 펜션도 권역에 포함됩니다.",
   "pattern":"강릉시는 여름·동계 시즌과 주말 시간대 비중이 큽니다. 성수기는 사전 예약이 권장됩니다.",
   "faqs":[
     ("세인트존스·스카이베이 가능한가요?","경포 일대 5성 호텔 객실 방문이 자주 안내됩니다."),
     ("안목 카페거리 인근 가능한가요?","송정·안목 일대 호텔·펜션 객실 방문이 안내됩니다."),
     ("주문진·정동진 가능한가요?","주문진읍·강동면 일대 펜션 객실 방문이 안내됩니다."),
   ],"neighbors":["donghae","yangyang","pyeongchang"]},
  {"slug":"donghae","name":"동해시",
   "lede":"동해시는 묵호항·동해항이 있는 항만 도시로, 평일 저녁 가정 방문과 해안 펜션 객실 방문이 함께 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","묵호항·동해항")],
   "subs":["천곡동","송정동","북삼동","북평동","평릉동","부곡동","발한동","묵호동"],
   "character":"동해시는 천곡·발한·묵호 일대 도심 가정 방문과 묵호·망상 해변 인근 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"동해시는 평일 저녁 시간대와 주말 시즌이 안정적입니다.",
   "faqs":[
     ("묵호항 인근 가능한가요?","묵호·발한 일대 가정·펜션 방문이 안내됩니다."),
     ("망상해수욕장 펜션 가능한가요?","망상 일대 펜션 객실 방문이 안내됩니다."),
     ("삼척·강릉과 함께 가능한가요?","각각 별도 시이며 권역별 확인이 필요합니다."),
   ],"neighbors":["samcheok","gangneung","taebaek"]},
  {"slug":"taebaek","name":"태백시",
   "lede":"태백시는 해발 700m 고원도시로, 황지·장성 일대 가정 방문과 태백산·검룡소 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","가정 중심"),("특이점","고원 관광")],
   "subs":["황지동","상장동","문곡소도동","장성동","화광동","구문소동","철암동","삼수동"],
   "character":"태백시는 황지·상장 일대 도심 가정 방문과 태백산·매봉산 인근 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"태백시는 평일 저녁과 동계 시즌 비중이 큽니다.",
   "faqs":[
     ("황지·상장 가능한가요?","황지·상장 일대 가정 방문이 안내됩니다."),
     ("태백산 인근 펜션 가능한가요?","문곡소도 일대 펜션 객실 방문이 안내됩니다."),
     ("정선·영월과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeongseon","yeongwol","samcheok"]},
  {"slug":"sokcho","name":"속초시",
   "lede":"속초시는 설악산 국립공원·속초해변·외옹치가 있는 동해안 관광 거점 도시로, 호텔·리조트 객실 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","8개"),("주요 시간대","시즌·야간"),("호텔/가정","호텔 비중↑↑"),("특이점","설악산·해변")],
   "subs":["영랑동","동명동","금호동","청호동","대포동","교동","노학동","조양동"],
   "character":"속초시는 외옹치·청호·교동 일대 롯데리조트 속초·켄싱턴 호텔 설악·델피노 등 리조트·호텔에서 휴양 일정 후 객실 방문이 자주 안내됩니다. 속초해변·아바이마을 인근 펜션 객실 방문도 함께 들어옵니다.",
   "pattern":"속초시는 여름·단풍·동계 시즌과 주말 시간대 비중이 큽니다. 성수기는 사전 예약이 권장됩니다.",
   "faqs":[
     ("롯데리조트 속초 가능한가요?","외옹치 롯데리조트·켄싱턴 호텔 설악 객실 방문이 자주 안내됩니다."),
     ("설악산 일정 후 가능한가요?","설악동·대포 일대 호텔·펜션 객실 방문이 안내됩니다."),
     ("성수기 사전 예약 필요한가요?","여름·단풍·동계 성수기는 사전 예약이 강력 권장됩니다."),
   ],"neighbors":["yangyang","goseong","inje"]},
  {"slug":"samcheok","name":"삼척시",
   "lede":"삼척시는 동해안과 환선굴·죽서루 등 관광 권역이 있는 도시로, 평일 저녁 도심 가정 방문과 주말 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","환선굴·죽서루")],
   "subs":["남양동","교동","성내동","당저동","정라동","갈천동","근덕면","원덕읍","노곡면","미로면","가곡면","신기면","도계읍","하장면"],
   "character":"삼척시는 정라·당저·교동 일대 도심 가정 방문과 근덕·원덕 해안 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"삼척시는 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("도심 가정 가능한가요?","정라·당저·교동 일대 가정 방문이 안내됩니다."),
     ("근덕 해안 펜션 가능한가요?","근덕·원덕 일대 펜션 객실 방문이 안내됩니다."),
     ("동해·태백과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["donghae","taebaek","yeongwol"]},
  {"slug":"hongcheon","name":"홍천군",
   "lede":"홍천군은 강원에서 면적이 가장 넓은 군으로, 홍천읍 도심 가정 방문과 비발디파크·소노벨 등 리조트 객실 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁·시즌"),("호텔/가정","혼합"),("특이점","비발디파크")],
   "subs":["홍천읍","화촌면","두촌면","내촌면","서석면","영귀미면","남면","서면","북방면","내면"],
   "character":"홍천군은 홍천읍 도심 가정 방문과 서면 비발디파크·소노벨 비발디파크 리조트 객실 방문이 함께 안내됩니다.",
   "pattern":"홍천군은 평일 저녁과 동계·여름 시즌 비중이 큽니다.",
   "faqs":[
     ("비발디파크 가능한가요?","서면 비발디파크 리조트 객실 방문이 자주 안내됩니다."),
     ("홍천읍 도심 가능한가요?","홍천읍 일대 가정 방문이 안내됩니다."),
     ("춘천·횡성과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["chuncheon","hoengseong","inje"]},
  {"slug":"hoengseong","name":"횡성군",
   "lede":"횡성군은 한우의 고장으로 알려진 군으로, 횡성읍 도심 가정 방문과 휴양 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","한우·휴양")],
   "subs":["횡성읍","우천면","안흥면","둔내면","갑천면","청일면","공근면","서원면","강림면"],
   "character":"횡성군은 횡성읍 도심 가정 방문과 둔내·우천 일대 휴양 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"횡성군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("횡성읍 도심 가능한가요?","횡성읍 일대 가정 방문이 안내됩니다."),
     ("둔내 펜션 가능한가요?","둔내 일대 펜션 객실 방문이 안내됩니다."),
     ("원주·홍천과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["wonju","hongcheon","pyeongchang"]},
  {"slug":"yeongwol","name":"영월군",
   "lede":"영월군은 동강·청령포가 있는 자연 관광 군으로, 영월읍 도심 가정 방문과 동강 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","동강·청령포")],
   "subs":["영월읍","상동읍","산솔면","북면","남면","한반도면","주천면","무릉도원면","김삿갓면"],
   "character":"영월군은 영월읍 도심 가정 방문과 한반도·김삿갓·동강 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"영월군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("영월읍 가능한가요?","영월읍 일대 가정 방문이 안내됩니다."),
     ("동강 펜션 가능한가요?","한반도·김삿갓 일대 펜션 객실 방문이 안내됩니다."),
     ("정선·태백과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeongseon","taebaek","wonju"]},
  {"slug":"pyeongchang","name":"평창군",
   "lede":"평창군은 동계올림픽 개최지이자 알펜시아·용평·휘닉스파크 등 리조트가 모인 군으로, 동계 시즌 리조트 객실 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","8개"),("주요 시간대","동계 시즌·주말"),("호텔/가정","리조트 비중↑↑"),("특이점","알펜시아·용평")],
   "subs":["평창읍","대화면","봉평면","용평면","진부면","미탄면","방림면","대관령면"],
   "character":"평창군은 대관령면(알펜시아 리조트·올림픽파크) 일대와 봉평·용평·진부 일대 리조트(용평리조트·휘닉스파크 평창·켄싱턴 플로라 평창) 객실 방문이 동계 시즌에 자주 안내됩니다.",
   "pattern":"평창군은 동계 시즌(12~3월)과 주말 시간대 비중이 가장 큽니다. 사전 예약이 강력 권장됩니다.",
   "faqs":[
     ("알펜시아 리조트 가능한가요?","대관령면 알펜시아 일대 리조트 객실 방문이 자주 안내됩니다."),
     ("용평리조트 가능한가요?","용평·봉평 일대 리조트 객실 방문이 안내됩니다."),
     ("스키 시즌 예약 어렵나요?","동계 성수기는 사전 예약이 필수입니다."),
   ],"neighbors":["jeongseon","gangneung","hoengseong"]},
  {"slug":"jeongseon","name":"정선군",
   "lede":"정선군은 강원랜드·하이원리조트가 있는 군으로, 사북·고한 일대 리조트 객실 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","9개"),("주요 시간대","야간·주말"),("호텔/가정","리조트 비중↑↑"),("특이점","강원랜드·하이원")],
   "subs":["정선읍","고한읍","사북읍","신동읍","남면","북평면","임계면","화암면","여량면"],
   "character":"정선군은 사북읍·고한읍 일대 강원랜드·하이원리조트·하이원그랜드호텔 객실 방문이 가장 큰 비중을 차지합니다. 정선읍은 도심 가정 방문 권역입니다.",
   "pattern":"정선군은 야간·주말 시간대 비중이 큽니다.",
   "faqs":[
     ("하이원리조트 가능한가요?","고한·사북 일대 하이원리조트·그랜드호텔 객실 방문이 자주 안내됩니다."),
     ("강원랜드 일정 후 가능한가요?","사북 일대 호텔·리조트 객실 방문이 야간 시간대 안내됩니다."),
     ("정선읍 도심 가능한가요?","정선읍 일대 가정 방문이 안내됩니다."),
   ],"neighbors":["taebaek","yeongwol","pyeongchang"]},
  {"slug":"cheorwon","name":"철원군",
   "lede":"철원군은 DMZ·노동당사 등 안보 관광 권역으로, 와수·동송 일대 도심 가정 방문과 휴양 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","DMZ·안보 관광")],
   "subs":["갈말읍","동송읍","서면","근남면","근북면","근동면","원남면","원동면","임남면","김화읍","철원읍"],
   "character":"철원군은 갈말·동송 일대 도심 가정 방문과 서면 한탄강 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"철원군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("갈말·동송 가능한가요?","갈말·동송 일대 가정 방문이 안내됩니다."),
     ("한탄강 펜션 가능한가요?","서면 일대 펜션 객실 방문이 안내됩니다."),
     ("화천·연천과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["hwacheon","pocheon-ext","yanggu"]},
  {"slug":"hwacheon","name":"화천군",
   "lede":"화천군은 산천어축제로 알려진 강원 북부 군으로, 화천읍 도심 가정 방문과 휴양 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","5개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","산천어축제")],
   "subs":["화천읍","간동면","하남면","상서면","사내면"],
   "character":"화천군은 화천읍 도심 가정 방문과 사내면 등 휴양 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"화천군은 평일 저녁과 산천어축제 시즌 비중이 큽니다.",
   "faqs":[
     ("산천어축제 시즌 가능한가요?","축제 시즌 사전 예약이 권장됩니다."),
     ("화천읍 가능한가요?","화천읍 일대 가정 방문이 안내됩니다."),
     ("춘천·철원과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["chuncheon","cheorwon","yanggu"]},
  {"slug":"yanggu","name":"양구군",
   "lede":"양구군은 펀치볼·DMZ가 있는 강원 북부 군으로, 양구읍 도심 가정 방문과 휴양 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","5개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","펀치볼·DMZ")],
   "subs":["양구읍","남면","동면","방산면","해안면"],
   "character":"양구군은 양구읍 도심 가정 방문과 해안면 펀치볼 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"양구군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("양구읍 가능한가요?","양구읍 일대 가정 방문이 안내됩니다."),
     ("펀치볼 인근 가능한가요?","해안면 일대 펜션·민박 객실 방문이 안내됩니다."),
     ("화천·인제와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["hwacheon","inje","chuncheon"]},
  {"slug":"inje","name":"인제군",
   "lede":"인제군은 설악산·내린천·점봉산이 있는 강원 동북부 군으로, 인제읍 도심 가정 방문과 백담·미시령 일대 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","6개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","설악·내린천")],
   "subs":["인제읍","북면","기린면","서화면","상남면","남면"],
   "character":"인제군은 인제읍 도심과 북면 백담·미시령 일대 펜션·민박 객실 방문이 함께 안내됩니다. 내린천 래프팅 일정 후 회복 케어 문의도 들어옵니다.",
   "pattern":"인제군은 평일 저녁과 여름·가을 시즌 비중이 큽니다.",
   "faqs":[
     ("백담사 인근 가능한가요?","북면 일대 펜션·민박 방문이 안내됩니다."),
     ("내린천 래프팅 후 가능한가요?","인제읍·기린 일대 가정·펜션 방문이 안내됩니다."),
     ("속초·양양과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["sokcho","yanggu","yangyang"]},
  {"slug":"goseong","name":"고성군",
   "lede":"고성군은 통일전망대·DMZ박물관·화진포가 있는 강원 최북단 군으로, 거진·간성·화진포 일대 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","6개"),("주요 시간대","주말·시즌"),("호텔/가정","혼합"),("특이점","DMZ·화진포")],
   "subs":["간성읍","거진읍","현내면","죽왕면","토성면","수동면"],
   "character":"고성군은 간성읍·거진읍 도심 가정 방문과 화진포·송지호 일대 펜션·콘도 객실 방문이 함께 안내됩니다. 토성면 일대는 속초와 인접해 권역 흐름이 닿아 있습니다.",
   "pattern":"고성군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("화진포 펜션 가능한가요?","거진·현내 일대 펜션·콘도 방문이 안내됩니다."),
     ("통일전망대 일정 후 가능한가요?","현내면 일대 펜션 객실 방문이 안내됩니다."),
     ("속초와 함께 가능한가요?","속초는 별도 시이며 권역별 확인이 필요합니다."),
   ],"neighbors":["sokcho","yangyang","inje"]},
  {"slug":"yangyang","name":"양양군",
   "lede":"양양군은 서피비치·죽도·낙산 등 서핑 성지로 알려진 동해안 군으로, 평일 저녁 가정·펜션 객실 방문과 시즌 서핑 케어가 함께 안내됩니다.",
   "facts":[("행정동","6개"),("주요 시간대","주말·시즌"),("호텔/가정","펜션 비중↑"),("특이점","서피비치·낙산")],
   "subs":["양양읍","손양면","현북면","현남면","서면","강현면"],
   "character":"양양군은 강현면 낙산해변 일대 호텔(쏠비치 양양·낙산비치호텔)과 현남면 죽도·인구·서피비치 일대 서핑 게스트하우스에서 휴양·서핑 일정 후 객실 방문이 자주 안내됩니다.",
   "pattern":"양양군은 여름 서핑 시즌과 주말 시간대 비중이 큽니다.",
   "faqs":[
     ("쏠비치 양양 가능한가요?","강현면 쏠비치 양양 객실 방문이 자주 안내됩니다."),
     ("서피비치 서핑 후 회복 가능한가요?","현남면 일대 서핑 게스트하우스 객실 방문이 안내됩니다. <a href=\"/service/sports-massage/\">스포츠 마사지</a>가 자주 권해집니다."),
     ("속초·고성과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["sokcho","gangneung","goseong"]},
]

for _d in GANGWON_DISTRICTS:
    DISTRICT_PAGE_INDEX[("gangwon", _d["name"])] = f"/area/gangwon/{_d['slug']}/"
for _d in GANGWON_DISTRICTS:
    _build_metro_district("gangwon", "강원", _d, GANGWON_DISTRICTS)


# ============================================================
# 충북 11 (시 3 + 군 8)
# ============================================================
CHUNGBUK_DISTRICTS = [
  {"slug":"cheongju","name":"청주시","sub_label":"4개 구",
   "lede":"청주시는 충북의 도청 소재지이자 오송 바이오·청주공항 거점 도시로, 평일 저녁 가정·출장 호텔 케어 비중이 큰 시입니다.",
   "facts":[("구","4개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","오송·청주공항")],
   "subs":["상당구","서원구","흥덕구","청원구"],
   "character":"흥덕구(가경·복대)는 청주역·청주공항 인접 비즈니스 호텔 객실 방문 권역이며, 청원구(오송)는 KTX 오송역·바이오단지 출장과 맞물려 호텔 객실 방문 비중이 큽니다. 상당·서원은 도심 주거 권역으로 평일 저녁 가정 방문이 자주 안내됩니다.",
   "pattern":"청주시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("오송 바이오단지 출장 가능한가요?","청원구 오송 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("청주공항 환승 가능한가요?","공항 인근 호텔 단시간 코스가 안내됩니다."),
     ("KTX 오송역 환승 가능한가요?","오송역 인근 호텔에서 60·90분 단시간 코스가 안내됩니다."),
   ],"neighbors":["chungju","jincheon","eumseong"]},
  {"slug":"chungju","name":"충주시",
   "lede":"충주시는 충주호·수안보온천이 있는 충북 북부 거점 도시로, 평일 저녁 가정 방문과 휴양 호텔·펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","수안보·충주호")],
   "subs":["성내·충인동","교현·안림동","교현2동","용산동","지현동","문화동","호암·직동","달천동","봉방동","칠금·금릉동","연수동","목행·용탄동","주덕읍","살미면","수안보면","대소원면","신니면","노은면","앙성면","엄정면","산척면","동량면","소태면","금가면"],
   "character":"충주시는 연수·칠금 일대 도심 가정 방문과 수안보온천 일대 호텔(수안보파크호텔·켄싱턴리조트) 객실 방문이 함께 안내됩니다.",
   "pattern":"충주시는 평일 저녁 시간대와 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("수안보온천 호텔 가능한가요?","수안보면 일대 호텔·리조트 객실 방문이 자주 안내됩니다."),
     ("연수·칠금 가정 가능한가요?","연수·칠금 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("제천·청주와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["jecheon","cheongju","eumseong"]},
  {"slug":"jecheon","name":"제천시",
   "lede":"제천시는 의림지·청풍호·박달재가 있는 충북 동부 도시로, 평일 저녁 도심 가정 방문과 청풍호 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","청풍호·의림지")],
   "subs":["청전동","화산동","남현동","교동","의림지동","용두동","중앙동","신백동","장락동","영서동","바이오밸리","봉양읍","금성면","청풍면","수산면","덕산면","한수면","백운면","송학면"],
   "character":"제천시는 청전·화산 일대 도심 가정 방문과 청풍·금성 일대 청풍호 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"제천시는 평일 저녁 시간대와 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("청풍호 펜션 가능한가요?","청풍·금성 일대 펜션·콘도 객실 방문이 안내됩니다."),
     ("제천 도심 가정 가능한가요?","청전·화산·중앙 일대 가정 방문이 안내됩니다."),
     ("단양과 함께 가능한가요?","단양은 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["chungju","danyang","yeongwol"]},
  {"slug":"boeun","name":"보은군",
   "lede":"보은군은 속리산 국립공원이 있는 군으로, 보은읍 도심 가정 방문과 속리산 인근 콘도 객실 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","속리산")],
   "subs":["보은읍","속리산면","장안면","마로면","탄부면","삼승면","수한면","회남면","회인면","내북면","산외면"],
   "character":"보은군은 보은읍 도심 가정 방문과 속리산면 호텔·콘도 객실 방문이 함께 안내됩니다.",
   "pattern":"보은군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("속리산 콘도 가능한가요?","속리산면 일대 콘도·펜션 객실 방문이 안내됩니다."),
     ("보은읍 도심 가능한가요?","보은읍 일대 가정 방문이 안내됩니다."),
     ("청주와 함께 가능한가요?","청주는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["okcheon","cheongju","yeongdong"]},
  {"slug":"okcheon","name":"옥천군",
   "lede":"옥천군은 정지용 시인의 고향으로 알려진 군으로, 옥천읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","KTX 인근")],
   "subs":["옥천읍","동이면","안남면","안내면","청성면","청산면","이원면","군서면","군북면"],
   "character":"옥천군은 옥천읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"옥천군은 평일 저녁 7~9시 시간대가 안정적입니다.",
   "faqs":[
     ("옥천읍 가능한가요?","옥천읍 일대 가정 방문이 안내됩니다."),
     ("대전과 함께 가능한가요?","대전은 별도 광역시로 권역별 확인이 필요합니다."),
     ("영동과 함께 가능한가요?","영동은 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["boeun","yeongdong","jeungpyeong"]},
  {"slug":"yeongdong","name":"영동군",
   "lede":"영동군은 포도·와인의 고장으로 알려진 군으로, 영동읍 도심 가정 방문과 휴양 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","와인·포도")],
   "subs":["영동읍","용산면","황간면","추풍령면","매곡면","상촌면","양강면","용화면","학산면","양산면","심천면"],
   "character":"영동군은 영동읍 도심 가정 방문과 추풍령·황간 일대 휴양 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"영동군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("영동읍 가능한가요?","영동읍 일대 가정 방문이 안내됩니다."),
     ("황간·추풍령 가능한가요?","황간·추풍령 일대 휴양 펜션 객실 방문이 안내됩니다."),
     ("옥천·보은과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["okcheon","boeun","muju"]},
  {"slug":"jeungpyeong","name":"증평군",
   "lede":"증평군은 충북 중부의 소규모 군으로, 증평읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","2개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","소규모 군")],
   "subs":["증평읍","도안면"],
   "character":"증평군은 증평읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"증평군은 평일 저녁 7~9시 시간대가 안정적입니다.",
   "faqs":[
     ("증평읍 가능한가요?","증평읍 일대 가정 방문이 안내됩니다."),
     ("청주와 함께 가능한가요?","청주는 별도 시로 권역별 확인이 필요합니다."),
     ("진천·괴산과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jincheon","goesan","cheongju"]},
  {"slug":"jincheon","name":"진천군",
   "lede":"진천군은 충북 혁신도시가 자리한 군으로, 진천읍·덕산 일대 신축 단지 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","7개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","혁신도시")],
   "subs":["진천읍","덕산읍","초평면","문백면","백곡면","이월면","광혜원면"],
   "character":"진천군은 덕산읍 충북 혁신도시 신축 단지와 진천읍 도심에서 평일 저녁 가정 방문이 자주 안내됩니다.",
   "pattern":"진천군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("혁신도시(덕산) 가능한가요?","덕산읍 혁신도시 신축 단지 가정 방문이 자주 안내됩니다."),
     ("진천읍 가능한가요?","진천읍 일대 가정 방문이 안내됩니다."),
     ("음성·증평과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["eumseong","jeungpyeong","cheongju"]},
  {"slug":"goesan","name":"괴산군",
   "lede":"괴산군은 화양구곡·산막이옛길이 있는 자연 관광 군으로, 괴산읍 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","화양구곡")],
   "subs":["괴산읍","감물면","장연면","연풍면","칠성면","문광면","청천면","청안면","사리면","소수면","불정면"],
   "character":"괴산군은 괴산읍 도심 가정 방문과 청천·칠성 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"괴산군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("괴산읍 가능한가요?","괴산읍 일대 가정 방문이 안내됩니다."),
     ("화양구곡 인근 펜션 가능한가요?","청천 일대 펜션 객실 방문이 안내됩니다."),
     ("증평·청주와 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeungpyeong","cheongju","eumseong"]},
  {"slug":"eumseong","name":"음성군",
   "lede":"음성군은 LG에너지솔루션·하이닉스 등 산업단지가 있는 군으로, 평일 저녁 출장 호텔·신축 단지 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","LG·하이닉스 산단")],
   "subs":["음성읍","금왕읍","대소면","삼성면","생극면","감곡면","원남면","맹동면","소이면"],
   "character":"음성군은 맹동·금왕 일대 산업단지 출장 호텔 객실 방문과 음성읍 도심 가정 방문이 함께 안내됩니다.",
   "pattern":"음성군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("LG에너지솔루션 출장 가능한가요?","맹동·금왕 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("음성읍 가능한가요?","음성읍 일대 가정 방문이 안내됩니다."),
     ("진천·괴산과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jincheon","jeungpyeong","chungju"]},
  {"slug":"danyang","name":"단양군",
   "lede":"단양군은 도담삼봉·고수동굴·소백산이 있는 자연 관광 군으로, 단양읍 도심 가정 방문과 단양강 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","도담삼봉·소백산")],
   "subs":["단양읍","매포읍","대강면","가곡면","영춘면","어상천면","적성면","단성면"],
   "character":"단양군은 단양읍 도심 가정 방문과 단양강·도담삼봉 인근 펜션·호텔(대명리조트 단양·소노문 단양) 객실 방문이 함께 안내됩니다.",
   "pattern":"단양군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("대명리조트 단양 가능한가요?","단양읍 일대 리조트·호텔 객실 방문이 자주 안내됩니다."),
     ("도담삼봉 인근 가능한가요?","단양읍 일대 펜션·호텔 객실 방문이 안내됩니다."),
     ("제천과 함께 가능한가요?","제천은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["jecheon","yeongju","yeongwol"]},
]

for _d in CHUNGBUK_DISTRICTS:
    _build_metro_district("chungbuk", "충북", _d, CHUNGBUK_DISTRICTS)


# ============================================================
# 충남 15 (시 8 + 군 7)
# ============================================================
CHUNGNAM_DISTRICTS = [
  {"slug":"cheonan","name":"천안시","sub_label":"2개 구",
   "lede":"천안시는 충남 최대 도시이자 KTX 천안아산역·삼성디스플레이 사업장이 있는 산업·교통 거점 도시로, 평일 저녁 출장 호텔·가정 방문 비중이 큰 시입니다.",
   "facts":[("구","2개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","KTX·삼성디스플레이")],
   "subs":["동남구","서북구"],
   "character":"서북구(불당·백석·두정)는 신축 신도시 권역으로 평일 저녁 가정 방문 비중이 매우 큽니다. 동남구(신부·다가·구성)는 KTX 천안아산역 인근 호텔(롯데시티호텔 천안·라마다 천안)과 단국대·상명대 인근 권역에서 출장·가정 방문이 안내됩니다.",
   "pattern":"천안시는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("KTX 천안아산역 환승 가능한가요?","역 인근 호텔 단시간 코스가 자주 안내됩니다."),
     ("불당신도시 가능한가요?","서북구 불당 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("삼성디스플레이 출장 가능한가요?","아산 탕정과 인접해 천안 호텔 객실 방문이 함께 안내됩니다."),
   ],"neighbors":["asan","sejong-ext","gongju"]},
  {"slug":"asan","name":"아산시",
   "lede":"아산시는 삼성디스플레이 탕정 캠퍼스·현대자동차 아산공장이 있는 산업 도시로, 평일 저녁 출장 호텔 객실 방문 비중이 매우 큰 시입니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","호텔 비중↑"),("특이점","삼성·현대차")],
   "subs":["온양1동","온양2동","온양3동","온양4동","온양5동","온양6동","배방읍","송악면","탕정면","음봉면","둔포면","영인면","인주면","염치읍","도고면","신창면","선장면"],
   "character":"탕정면(삼성디스플레이)·배방읍(현대자동차)은 출장 일정과 맞물려 평일 저녁 비즈니스 호텔 객실 방문 비중이 매우 큽니다. 온양 일대는 온천 관광 권역으로 호텔·콘도(파라다이스 스파 도고·아산 온양관광호텔) 객실 방문이 함께 안내됩니다.",
   "pattern":"아산시는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("삼성디스플레이 탕정 출장 가능한가요?","탕정·음봉 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("현대자동차 아산공장 출장 가능한가요?","인주·둔포 일대 호텔 객실 방문이 안내됩니다."),
     ("온양온천 호텔 가능한가요?","온양1~6동 일대 온천 호텔·콘도 객실 방문이 안내됩니다."),
   ],"neighbors":["cheonan","dangjin","yesan"]},
  {"slug":"gongju","name":"공주시",
   "lede":"공주시는 백제 고도이자 공산성·무령왕릉 등 세계유산이 있는 도시로, 평일 저녁 가정 방문과 관광 일정 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","백제 세계유산")],
   "subs":["중학동","웅진동","금학동","옥룡동","신관동","월송동","유구읍","이인면","탄천면","계룡면","반포면","의당면","정안면","우성면","사곡면","신풍면"],
   "character":"공주시는 신관·월송·금학 일대 도심 가정 방문과 공산성 인근 호텔(공주한옥마을·라궁리조트 인근) 객실 방문이 함께 안내됩니다.",
   "pattern":"공주시는 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("공산성·무령왕릉 인근 가능한가요?","웅진·금학·신관 일대 호텔·한옥 객실 방문이 안내됩니다."),
     ("신관·월송 가정 가능한가요?","신관·월송 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("세종·대전과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["sejong-ext","buyeo","cheongyang"]},
  {"slug":"boryeong","name":"보령시",
   "lede":"보령시는 대천해수욕장·머드축제로 알려진 서해안 관광 도시로, 평일 저녁 도심 가정 방문과 해변 호텔·펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","대천·머드축제")],
   "subs":["대천1동","대천2동","대천3동","대천4동","대천5동","주포면","주교면","웅천읍","주산면","미산면","남포면","청라면","청소면","오천면","천북면","성주면"],
   "character":"보령시는 대천 일대 도심 가정 방문과 대천해수욕장 인근 호텔·콘도(한화리조트 대천파로스 등) 객실 방문이 함께 안내됩니다. 머드축제 시즌(7월)은 가능 시간이 빠르게 마감됩니다.",
   "pattern":"보령시는 평일 저녁과 여름 시즌 비중이 큽니다.",
   "faqs":[
     ("한화리조트 대천파로스 가능한가요?","대천해수욕장 인근 호텔·콘도 객실 방문이 자주 안내됩니다."),
     ("머드축제 당일 가능한가요?","축제 시즌은 사전 예약이 필수입니다."),
     ("서천·홍성과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["seocheon","cheongyang","hongseong"]},
  {"slug":"seosan","name":"서산시",
   "lede":"서산시는 대산석유화학단지·서산해미읍성이 있는 충남 서해안 산업·관광 도시로, 평일 저녁 출장 호텔·가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","대산 석유화학")],
   "subs":["부춘동","동문1동","동문2동","수석동","석남동","대산읍","인지면","부석면","팔봉면","지곡면","성연면","음암면","운산면","해미면","고북면"],
   "character":"서산시는 대산읍(석유화학단지) 출장 호텔 객실 방문과 부춘·동문 일대 도심 가정 방문이 함께 안내됩니다.",
   "pattern":"서산시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("대산석유화학 출장 가능한가요?","대산읍 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("해미읍성 인근 가능한가요?","해미면 일대 펜션·민박 방문이 안내됩니다."),
     ("당진·태안과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["dangjin","taean","hongseong"]},
  {"slug":"nonsan","name":"논산시",
   "lede":"논산시는 육군훈련소가 있는 군 행정 도시로, 평일 저녁 가정·면회 호텔 방문이 함께 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","육군훈련소")],
   "subs":["취암동","부창동","연무읍","연산면","벌곡면","양촌면","가야곡면","은진면","채운면","광석면","노성면","상월면","부적면","강경읍","성동면"],
   "character":"논산시는 연무읍(육군훈련소) 인근 호텔에서 면회 일정 가족 객실 방문이 자주 안내되며, 취암·부창 도심 가정 방문도 함께 들어옵니다.",
   "pattern":"논산시는 평일 저녁과 주말 면회 시즌 비중이 큽니다.",
   "faqs":[
     ("육군훈련소 면회 일정 가능한가요?","연무읍 일대 호텔 객실 방문이 주말 면회 시즌 안내됩니다."),
     ("강경 가능한가요?","강경읍 일대 가정 방문이 안내됩니다."),
     ("계룡·공주와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gyeryong","buyeo","gongju"]},
  {"slug":"gyeryong","name":"계룡시",
   "lede":"계룡시는 계룡대(육·해·공군 본부)가 있는 군 행정 중심 소도시로, 평일 저녁 군인 가족 가정 방문 비중이 큰 시입니다.",
   "facts":[("행정동","4개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","계룡대")],
   "subs":["금암동","두마면","엄사면","신도안면"],
   "character":"계룡시는 금암동(시청)·엄사·두마 일대 군인 가족 거주 권역에서 평일 저녁 가정 방문이 자주 안내됩니다.",
   "pattern":"계룡시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("금암동 군인 가족 가능한가요?","금암·엄사 일대 군인 가족 가정 방문이 자주 안내됩니다."),
     ("계룡대 방문객 가능한가요?","계룡대 인근 호텔이 적어 인근 시(논산·대전)로 안내드릴 수 있습니다."),
     ("논산과 함께 가능한가요?","논산은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["nonsan","gongju","sejong-ext"]},
  {"slug":"dangjin","name":"당진시",
   "lede":"당진시는 현대제철·동부제철 등 철강 산업과 당진항이 있는 산업·물류 도시로, 평일 저녁 출장 호텔 객실 방문 비중이 큰 시입니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","호텔 비중↑"),("특이점","현대제철·당진항")],
   "subs":["당진1동","당진2동","당진3동","합덕읍","송악읍","고대면","석문면","대호지면","정미면","면천면","순성면","우강면","신평면","송산면"],
   "character":"당진시는 송악읍(현대제철)·석문면(당진항) 일대 출장 호텔 객실 방문이 평일 저녁 자주 안내됩니다. 당진 도심(당진1~3) 가정 방문도 함께 들어옵니다.",
   "pattern":"당진시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("현대제철 출장 가능한가요?","송악읍 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("당진 도심 가능한가요?","당진1~3 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("서산·아산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["seosan","asan","yesan"]},
  {"slug":"geumsan","name":"금산군",
   "lede":"금산군은 인삼의 고장으로 알려진 군으로, 금산읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","인삼·약초")],
   "subs":["금산읍","금성면","제원면","부리면","군북면","남일면","남이면","진산면","복수면","추부면"],
   "character":"금산군은 금산읍 도심과 추부·복수 일대 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"금산군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("금산읍 가능한가요?","금산읍 일대 가정 방문이 안내됩니다."),
     ("대전과 함께 가능한가요?","대전은 별도 광역시로 권역별 확인이 필요합니다."),
     ("논산과 함께 가능한가요?","논산은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["nonsan","yeongdong","muju"]},
  {"slug":"buyeo","name":"부여군",
   "lede":"부여군은 백제 고도이자 부소산성·낙화암이 있는 군으로, 부여읍 도심 가정 방문과 관광 일정 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","백제 세계유산")],
   "subs":["부여읍","규암면","은산면","외산면","내산면","구룡면","홍산면","옥산면","남면","충화면","양화면","임천면","장암면","세도면","석성면","초촌면"],
   "character":"부여군은 부여읍 도심 가정 방문과 규암·은산 일대 호텔·펜션(롯데부여리조트) 객실 방문이 함께 안내됩니다.",
   "pattern":"부여군은 평일 저녁 시간대와 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("롯데부여리조트 가능한가요?","규암 일대 리조트·호텔 객실 방문이 자주 안내됩니다."),
     ("부여읍 도심 가능한가요?","부여읍 일대 가정 방문이 안내됩니다."),
     ("공주와 함께 가능한가요?","공주는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gongju","seocheon","cheongyang"]},
  {"slug":"seocheon","name":"서천군",
   "lede":"서천군은 국립생태원·금강하구가 있는 충남 서남부 군으로, 서천읍·장항읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","국립생태원")],
   "subs":["서천읍","장항읍","화양면","마산면","시초면","문산면","판교면","기산면","한산면","마서면","종천면","비인면","서면","월포면"],
   "character":"서천군은 서천읍·장항읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"서천군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("장항·서천 가능한가요?","장항읍·서천읍 일대 가정 방문이 안내됩니다."),
     ("국립생태원 인근 가능한가요?","마서·한산 일대 펜션·민박 방문이 안내됩니다."),
     ("보령·군산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["boryeong","buyeo","gunsan"]},
  {"slug":"cheongyang","name":"청양군",
   "lede":"청양군은 칠갑산이 있는 충남 중부 군으로, 청양읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","칠갑산")],
   "subs":["청양읍","운곡면","대치면","정산면","목면","청남면","장평면","남양면","화성면","비봉면"],
   "character":"청양군은 청양읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"청양군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("청양읍 가능한가요?","청양읍 일대 가정 방문이 안내됩니다."),
     ("공주·홍성과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
     ("부여와 함께 가능한가요?","부여는 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gongju","hongseong","buyeo"]},
  {"slug":"hongseong","name":"홍성군",
   "lede":"홍성군은 충남도청 소재지가 자리한 충남 중부 군으로, 홍성읍·홍북읍 일대 도심 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","충남도청")],
   "subs":["홍성읍","광천읍","홍북읍","금마면","홍동면","장곡면","은하면","결성면","서부면","갈산면","구항면"],
   "character":"홍성군은 홍북읍(충남도청 신청사) 일대 신축 단지와 홍성읍 도심 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"홍성군은 평일 저녁 시간대 비중이 큽니다.",
   "faqs":[
     ("홍북읍 도청 신도시 가능한가요?","홍북 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("홍성읍 가능한가요?","홍성읍 일대 가정 방문이 안내됩니다."),
     ("예산·서산과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["yesan","seosan","cheongyang"]},
  {"slug":"yesan","name":"예산군",
   "lede":"예산군은 윤봉길 의사 생가·수덕사가 있는 충남 중부 군으로, 예산읍·삽교읍 일대 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","수덕사·삽교")],
   "subs":["예산읍","삽교읍","대술면","신양면","광시면","대흥면","응봉면","덕산면","봉산면","고덕면","신암면","오가면"],
   "character":"예산군은 예산읍·삽교읍 도심 가정 방문과 덕산면(수덕사) 일대 펜션·민박 객실 방문이 함께 안내됩니다.",
   "pattern":"예산군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("예산·삽교 가능한가요?","예산읍·삽교읍 일대 가정 방문이 안내됩니다."),
     ("수덕사 인근 가능한가요?","덕산면 일대 펜션·민박 방문이 안내됩니다."),
     ("당진·아산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["dangjin","hongseong","asan"]},
  {"slug":"taean","name":"태안군",
   "lede":"태안군은 만리포·안면도가 있는 서해안 관광 군으로, 태안읍 도심 가정 방문과 해안 펜션·리조트 객실 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","8개"),("주요 시간대","주말·시즌"),("호텔/가정","펜션 비중↑"),("특이점","안면도·만리포")],
   "subs":["태안읍","안면읍","고남면","남면","근흥면","소원면","원북면","이원면"],
   "character":"태안군은 안면읍·남면 안면도 일대 펜션·리조트(롯데리조트 태안·소노벨 비발디 등)에서 휴양 일정 후 객실 방문이 자주 안내됩니다. 태안읍은 도심 가정 방문 권역입니다.",
   "pattern":"태안군은 여름·봄 시즌과 주말 시간대 비중이 큽니다.",
   "faqs":[
     ("롯데리조트 태안 가능한가요?","안면읍 일대 리조트 객실 방문이 자주 안내됩니다."),
     ("만리포·안면도 펜션 가능한가요?","소원·안면 일대 펜션 객실 방문이 안내됩니다."),
     ("서산과 함께 가능한가요?","서산은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["seosan","hongseong","boryeong"]},
]

for _d in CHUNGNAM_DISTRICTS:
    _build_metro_district("chungnam", "충남", _d, CHUNGNAM_DISTRICTS)


# ============================================================
# 전북특별자치도 14 (시 6 + 군 8)
# ============================================================
JEONBUK_DISTRICTS = [
  {"slug":"jeonju","name":"전주시","sub_label":"2개 구",
   "lede":"전주시는 전북특별자치도의 도청 소재지이자 한옥마을·전주비빔밥으로 알려진 관광 도시로, 평일 저녁 가정 방문과 한옥 게스트하우스 객실 방문이 함께 안내됩니다.",
   "facts":[("구","2개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","한옥마을")],
   "subs":["완산구","덕진구"],
   "character":"완산구(중앙·풍남)는 한옥마을·전주객사 일대 한옥 게스트하우스·호텔(라한호텔 전주·전주한옥숙박체험관) 객실 방문이 자주 안내됩니다. 덕진구(서신·송천·인후)는 도심·신축 단지 가정 방문 권역입니다.",
   "pattern":"전주시는 평일 저녁 시간대와 주말 관광 시즌 비중이 큽니다.",
   "faqs":[
     ("한옥마을 게스트하우스 가능한가요?","완산구 풍남 일대 한옥 객실 방문이 안내됩니다. 한옥 구조 특성상 매트 안내 등 사전 확인이 필요합니다."),
     ("라한호텔 전주 가능한가요?","완산구 라한호텔 전주 객실 방문이 자주 안내됩니다."),
     ("서신·송천 신도시 가능한가요?","덕진구 서신·송천 일대 가정 방문이 자주 안내됩니다."),
   ],"neighbors":["wanju","gimje","iksan"]},
  {"slug":"gunsan","name":"군산시",
   "lede":"군산시는 새만금사업단지·군산항이 있는 항만·산업 도시로, 평일 저녁 출장 호텔·도심 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","26개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","새만금")],
   "subs":["해신동","월명동","신풍동","삼학동","중앙동","흥남동","조촌동","경암동","구암동","개정동","나운1동","나운2동","나운3동","미성동","소룡동","수송동","오식도동","옥구읍","옥산면","회현면","임피면","서수면","대야면","개정면","성산면","나포면","옥도면","옥서면"],
   "character":"군산시는 나운·수송·미성 일대 도심 가정 방문과 군산내항·소룡 비즈니스 호텔(베스트웨스턴 군산·라마다 군산 등) 객실 방문이 함께 안내됩니다.",
   "pattern":"군산시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("새만금 출장 가능한가요?","소룡·옥서 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("나운·수송 가능한가요?","나운1~3·수송 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("익산과 함께 가능한가요?","익산은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["iksan","gimje","buan"]},
  {"slug":"iksan","name":"익산시",
   "lede":"익산시는 KTX·SRT 정차역인 익산역이 있는 호남 교통 거점 도시로, 평일 저녁 환승 호텔과 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","25개"),("주요 시간대","평일 저녁·환승"),("호텔/가정","혼합"),("특이점","KTX 익산역")],
   "subs":["중앙동","평화동","인화동","마동","송학동","신동","남중동","모현동","송수동","어양동","팔봉동","삼성동","영등1동","영등2동","동산동","함열읍","오산면","황등면","함라면","웅포면","성당면","용안면","낭산면","망성면","여산면","금마면","왕궁면","춘포면","삼기면","용동면","익산"],
   "character":"익산시는 익산역 인근 호텔(라마다 익산·KW호텔)에서 KTX·SRT 환승·출장 객실 방문이 자주 안내됩니다. 어양·영등·동산 일대 신축 단지 가정 방문도 평일 저녁 함께 들어옵니다.",
   "pattern":"익산시는 평일 저녁 시간대와 환승 시간대 모두 안내됩니다.",
   "faqs":[
     ("KTX 익산역 환승 가능한가요?","익산역 인근 호텔에서 60·90분 단시간 코스가 자주 안내됩니다."),
     ("어양·영등 신축 단지 가능한가요?","어양·영등1·2 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("전주·군산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeonju","gunsan","gimje"]},
  {"slug":"jeongeup","name":"정읍시",
   "lede":"정읍시는 내장산국립공원·정읍사가 있는 전북 남부 도시로, 평일 저녁 도심 가정 방문과 단풍철 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","내장산")],
   "subs":["수성동","장명동","시기동","연지동","농소동","상교동","초산동","과교동","상동","내장상동","신태인읍","북면","입암면","소성면","고부면","영원면","덕천면","이평면","정우면","태인면","감곡면","옹동면","칠보면","산내면","산외면"],
   "character":"정읍시는 수성·장명·연지 일대 도심 가정 방문과 내장산면 일대 단풍철 호텔·콘도 객실 방문이 함께 안내됩니다.",
   "pattern":"정읍시는 평일 저녁 시간대와 단풍철(10~11월) 비중이 큽니다.",
   "faqs":[
     ("내장산 단풍철 호텔 가능한가요?","내장상·태인 일대 호텔·콘도 객실 방문이 안내됩니다. 단풍철은 사전 예약 권장."),
     ("수성·장명 가정 가능한가요?","수성·장명 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("김제·고창과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gimje","gochang","sunchang"]},
  {"slug":"namwon","name":"남원시",
   "lede":"남원시는 광한루원·지리산이 있는 전북 동부 관광 도시로, 평일 저녁 도심 가정 방문과 지리산 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","광한루·지리산")],
   "subs":["죽항동","노암동","왕정동","향교동","도통동","금동","동충동","산곡동","조산동","월락동","고죽동","운봉읍","주천면","수지면","송동면","주생면","금지면","대강면","대산면","사매면","덕과면","보절면","아영면","산내면","인월면"],
   "character":"남원시는 죽항·노암·향교 일대 도심 가정 방문과 운봉·인월 지리산 둘레길 인근 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"남원시는 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("광한루원 인근 가능한가요?","죽항·향교 일대 호텔·게스트하우스 방문이 안내됩니다."),
     ("지리산 둘레길 펜션 가능한가요?","운봉·인월·산내 일대 펜션 객실 방문이 안내됩니다."),
     ("순창·임실과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["sunchang","imsil","jangsu"]},
  {"slug":"gimje","name":"김제시",
   "lede":"김제시는 김제평야가 있는 전북 서부 도시로, 평일 저녁 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","김제평야")],
   "subs":["요촌동","신풍동","검산동","교동·월촌동","검산동","서암동","송산동","월촌동","만경읍","죽산면","백산면","공덕면","청하면","성덕면","진봉면","광활면","부량면","봉남면","황산면","금구면","금산면","백구면","용지면","백산"],
   "character":"김제시는 요촌·신풍 일대 도심 가정 방문과 만경읍 일대 농촌 권역에서 가정 방문이 평일 저녁 안내됩니다.",
   "pattern":"김제시는 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("김제 도심 가능한가요?","요촌·신풍 일대 가정 방문이 안내됩니다."),
     ("전주·익산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("부안과 함께 가능한가요?","부안은 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeonju","iksan","buan"]},
  {"slug":"wanju","name":"완주군",
   "lede":"완주군은 전주를 둘러싼 군으로, 봉동·삼례 일대 산업·신축 단지 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","현대차 전주공장")],
   "subs":["삼례읍","봉동읍","용진읍","상관면","소양면","구이면","고산면","비봉면","운주면","화산면","동상면","경천면","이서면"],
   "character":"완주군은 봉동읍(현대자동차 전주공장)·삼례·이서 일대 산업·신축 단지에서 평일 저녁 가정·호텔 방문이 함께 안내됩니다.",
   "pattern":"완주군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("현대차 전주공장 출장 가능한가요?","봉동읍 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("삼례·이서 가능한가요?","삼례읍·이서면 일대 신축 단지 가정 방문이 안내됩니다."),
     ("전주와 함께 가능한가요?","전주는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeonju","iksan","jinan"]},
  {"slug":"jinan","name":"진안군",
   "lede":"진안군은 마이산·진안고원이 있는 전북 동부 군으로, 진안읍 도심 가정 방문과 마이산 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","마이산")],
   "subs":["진안읍","용담면","안천면","동향면","상전면","백운면","성수면","마령면","부귀면","정천면","주천면"],
   "character":"진안군은 진안읍 도심과 마령·부귀 마이산 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"진안군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("마이산 인근 가능한가요?","마령·부귀 일대 펜션·민박 방문이 안내됩니다."),
     ("진안읍 가능한가요?","진안읍 일대 가정 방문이 안내됩니다."),
     ("무주·장수와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["muju","jangsu","wanju"]},
  {"slug":"muju","name":"무주군",
   "lede":"무주군은 무주리조트·덕유산이 있는 동계 스포츠 권역으로, 평일 저녁 도심 가정 방문과 동계 시즌 리조트 객실 방문 비중이 큰 군입니다.",
   "facts":[("행정동","6개"),("주요 시간대","동계 시즌"),("호텔/가정","리조트 비중↑"),("특이점","무주리조트")],
   "subs":["무주읍","무풍면","설천면","적상면","안성면","부남면"],
   "character":"무주군은 설천면 무주덕유산리조트·무주티롤리조트 일대 동계 시즌 객실 방문 비중이 가장 큰 군 중 하나입니다. 무주읍은 도심 가정 방문 권역입니다.",
   "pattern":"무주군은 동계 시즌(12~3월) 비중이 가장 큽니다.",
   "faqs":[
     ("무주덕유산리조트 가능한가요?","설천면 무주리조트 객실 방문이 자주 안내됩니다."),
     ("동계 시즌 사전 예약 필요한가요?","동계 성수기는 사전 예약이 강력 권장됩니다."),
     ("진안·장수와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jinan","jangsu","yeongdong"]},
  {"slug":"jangsu","name":"장수군",
   "lede":"장수군은 장수읍 도심과 덕유산·팔공산 인접 자연 권역이 있는 전북 동부 군으로, 평일 저녁 가정·펜션 방문이 안내됩니다.",
   "facts":[("행정동","7개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","덕유·팔공")],
   "subs":["장수읍","산서면","번암면","장계면","천천면","계남면","계북면"],
   "character":"장수군은 장수읍·장계 일대 도심 가정 방문이 평일 저녁 안내됩니다.",
   "pattern":"장수군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("장수읍 가능한가요?","장수읍 일대 가정 방문이 안내됩니다."),
     ("무주·진안과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
     ("남원과 함께 가능한가요?","남원은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["muju","jinan","namwon"]},
  {"slug":"imsil","name":"임실군",
   "lede":"임실군은 임실치즈가 유명한 전북 중부 군으로, 임실읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","임실치즈")],
   "subs":["임실읍","청웅면","운암면","신평면","성수면","오수면","신덕면","삼계면","관촌면","강진면","덕치면","지사면"],
   "character":"임실군은 임실읍·관촌 도심 가정 방문이 평일 저녁 안내됩니다.",
   "pattern":"임실군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("임실읍 가능한가요?","임실읍 일대 가정 방문이 안내됩니다."),
     ("남원·순창과 함께 가능한가요?","각각 별도 군·시로 권역별 확인이 필요합니다."),
     ("전주와 함께 가능한가요?","전주는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["sunchang","namwon","wanju"]},
  {"slug":"sunchang","name":"순창군",
   "lede":"순창군은 고추장으로 알려진 전북 남부 군으로, 순창읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","순창고추장")],
   "subs":["순창읍","인계면","동계면","적성면","팔덕면","쌍치면","복흥면","유등면","풍산면","금과면","구림면"],
   "character":"순창군은 순창읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"순창군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("순창읍 가능한가요?","순창읍 일대 가정 방문이 안내됩니다."),
     ("정읍·남원과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("임실과 함께 가능한가요?","임실은 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jeongeup","namwon","imsil"]},
  {"slug":"gochang","name":"고창군",
   "lede":"고창군은 선운사·고창읍성·청보리밭이 있는 전북 서남부 군으로, 고창읍 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","선운사·청보리밭")],
   "subs":["고창읍","고수면","아산면","무장면","공음면","상하면","해리면","성송면","대산면","심원면","흥덕면","성내면","신림면","부안면"],
   "character":"고창군은 고창읍 도심과 선운사·심원·아산 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"고창군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("선운사 인근 가능한가요?","아산·심원 일대 펜션·민박 방문이 안내됩니다."),
     ("고창읍성 인근 가능한가요?","고창읍 일대 가정 방문이 안내됩니다."),
     ("부안·정읍과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["buan","jeongeup","yeonggwang"]},
  {"slug":"buan","name":"부안군",
   "lede":"부안군은 변산반도 국립공원·내소사가 있는 서해안 관광 군으로, 부안읍 도심 가정 방문과 격포·변산 일대 펜션·호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","변산반도")],
   "subs":["부안읍","주산면","동진면","행안면","계화면","보안면","변산면","진서면","백산면","상서면","하서면","줄포면","위도면"],
   "character":"부안군은 변산면·진서 격포·내소사 일대 펜션·호텔(소노 변산·솔섬리조트 등) 객실 방문이 자주 안내되며, 부안읍은 도심 가정 방문 권역입니다.",
   "pattern":"부안군은 평일 저녁과 주말·여름 시즌 비중이 큽니다.",
   "faqs":[
     ("변산 격포 펜션 가능한가요?","변산·진서 일대 펜션·호텔 객실 방문이 안내됩니다."),
     ("부안읍 가능한가요?","부안읍 일대 가정 방문이 안내됩니다."),
     ("고창·김제와 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gochang","gimje","gunsan"]},
]

for _d in JEONBUK_DISTRICTS:
    _build_metro_district("jeonbuk", "전북", _d, JEONBUK_DISTRICTS)


# ============================================================
# 전남 22 (시 5 + 군 17)
# ============================================================
JEONNAM_DISTRICTS = [
  {"slug":"mokpo","name":"목포시",
   "lede":"목포시는 전남 서남부의 항만 도시로, 평화광장·하당 일대 도심 가정 방문과 유달산·근대역사거리 인근 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","목포항·유달산")],
   "subs":["용당1동","용당2동","연동","산정동","대성동","목원동","동명동","삼학동","만호동","유달동","죽교동","북항동","용해동","이로동","상동","하당동","신흥동","원산동","부주동","옥암동","부흥동"],
   "character":"목포시는 하당·옥암 일대 신축 단지 가정 방문과 평화광장 인근 호텔(쉐라톤 그랜드 목포·신안비치호텔) 객실 방문이 함께 안내됩니다.",
   "pattern":"목포시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("쉐라톤 그랜드 목포 가능한가요?","평화광장 일대 쉐라톤 그랜드 목포 객실 방문이 자주 안내됩니다."),
     ("하당·옥암 가능한가요?","하당·옥암 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("무안·신안과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["muan","sinan","haenam"]},
  {"slug":"yeosu","name":"여수시",
   "lede":"여수시는 여수밤바다·돌산대교로 알려진 동해안 관광 도시로, 종포·돌산·웅천 일대 호텔·리조트 객실 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","25개"),("주요 시간대","야간·시즌"),("호텔/가정","호텔 비중↑↑"),("특이점","여수밤바다")],
   "subs":["동문동","한려동","중앙동","충무동","광림동","서강동","대교동","국동","월호동","여서동","문수동","미평동","오림동","쌍봉동","시전동","여천동","주삼동","삼일동","묘도동","돌산읍","소라면","율촌면","화양면","남면","화정면","삼산면"],
   "character":"여수시는 종포·돌산·웅천 일대 디오션리조트·MVL호텔 여수·여수베네치아호텔·소노캄 여수 등 관광 호텔 객실 방문이 야경 일정과 맞물려 야간 시간대 자주 안내됩니다.",
   "pattern":"여수시는 야간·여름 시즌·연말 시즌 비중이 큽니다.",
   "faqs":[
     ("디오션리조트 가능한가요?","웅천 일대 디오션리조트 객실 방문이 자주 안내됩니다."),
     ("MVL호텔 여수 가능한가요?","웅천 MVL 객실 방문이 안내됩니다."),
     ("성수기 사전 예약 필요한가요?","여름·연말 시즌은 사전 예약이 강력 권장됩니다."),
   ],"neighbors":["suncheon","gwangyang","goheung"]},
  {"slug":"suncheon","name":"순천시",
   "lede":"순천시는 순천만국가정원·낙안읍성이 있는 자연 관광 도시로, 평일 저녁 도심 가정 방문과 정원 시즌 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","24개"),("주요 시간대","평일 저녁·시즌"),("호텔/가정","혼합"),("특이점","순천만정원")],
   "subs":["향동","매곡동","삼산동","조곡동","덕연동","풍덕동","남제동","저전동","장천동","중앙동","도사동","왕조1동","왕조2동","해룡면","서면","황전면","월등면","주암면","송광면","외서면","낙안면","별량면","상사면","승주읍"],
   "character":"순천시는 왕조·해룡·연향 일대 신축 단지 가정 방문과 순천만정원 인근 호텔(에코그라드호텔·코아루리조트) 객실 방문이 함께 안내됩니다.",
   "pattern":"순천시는 평일 저녁과 봄·가을 시즌 비중이 큽니다.",
   "faqs":[
     ("순천만정원 인근 호텔 가능한가요?","해룡·도사 일대 호텔 객실 방문이 안내됩니다."),
     ("정원박람회 시즌 사전 예약 필요한가요?","봄·가을 박람회 시즌은 사전 예약이 권장됩니다."),
     ("여수·광양과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeosu","gwangyang","boseong"]},
  {"slug":"naju","name":"나주시",
   "lede":"나주시는 광주전남공동혁신도시가 자리한 전남 중부 도시로, 빛가람동 일대 신축 단지 가정 방문 비중이 큰 시입니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","혁신도시")],
   "subs":["성북동","영강동","금남동","영산동","이창동","송월동","영산포","남평읍","세지면","왕곡면","반남면","공산면","동강면","다시면","문평면","노안면","금천면","산포면","다도면","봉황면","빛가람동"],
   "character":"나주시는 빛가람동(광주전남공동혁신도시) 신축 대단지 가정 방문이 평일 저녁 자주 안내됩니다. 한국전력·한전KPS 등 출장 호텔 객실 방문도 들어옵니다.",
   "pattern":"나주시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("빛가람 혁신도시 가능한가요?","빛가람동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("한전 출장 가능한가요?","빛가람 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("광주와 함께 가능한가요?","광주는 별도 광역시로 권역별 확인이 필요합니다."),
   ],"neighbors":["hwasun","damyang","muan"]},
  {"slug":"gwangyang","name":"광양시",
   "lede":"광양시는 광양제철소가 있는 산업 도시로, 평일 저녁 출장 호텔·중마동 신축 단지 가정 방문 비중이 큰 시입니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","광양제철")],
   "subs":["광양읍","봉강면","옥룡면","옥곡면","진상면","진월면","다압면","골약동","중마동","광영동","태인동","금호동"],
   "character":"광양시는 광영·중마동 일대 광양제철소 출장 호텔 객실 방문과 중마·옥곡 신축 단지 가정 방문이 함께 안내됩니다.",
   "pattern":"광양시는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("광양제철 출장 가능한가요?","중마·광영 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("중마동 신축 단지 가능한가요?","중마동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("순천·여수와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["suncheon","yeosu","hadong"]},
  {"slug":"damyang","name":"담양군",
   "lede":"담양군은 죽녹원·메타세쿼이아길이 있는 자연 관광 군으로, 담양읍 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","죽녹원")],
   "subs":["담양읍","봉산면","고서면","창평면","대덕면","무정면","금성면","용면","월산면","수북면","대전면","남면"],
   "character":"담양군은 담양읍 도심 가정 방문과 죽녹원·메타세쿼이아길 인근 펜션·한옥 객실 방문이 함께 안내됩니다.",
   "pattern":"담양군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("죽녹원 인근 가능한가요?","담양읍 일대 펜션·한옥 객실 방문이 안내됩니다."),
     ("담양읍 가능한가요?","담양읍 일대 가정 방문이 안내됩니다."),
     ("광주와 함께 가능한가요?","광주는 별도 광역시로 권역별 확인이 필요합니다."),
   ],"neighbors":["jangseong","gokseong","gwangju-ext"]},
  {"slug":"gokseong","name":"곡성군",
   "lede":"곡성군은 섬진강 기차마을이 있는 전남 동부 군으로, 곡성읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","섬진강기차마을")],
   "subs":["곡성읍","오곡면","삼기면","석곡면","목사동면","죽곡면","고달면","옥과면","입면","겸면","오산면"],
   "character":"곡성군은 곡성읍·옥과 일대 도심 가정 방문이 평일 저녁 안내됩니다.",
   "pattern":"곡성군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("곡성읍 가능한가요?","곡성읍 일대 가정 방문이 안내됩니다."),
     ("섬진강 인근 가능한가요?","오곡·고달 일대 펜션 객실 방문이 안내됩니다."),
     ("순천·구례와 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gurye","suncheon","damyang"]},
  {"slug":"gurye","name":"구례군",
   "lede":"구례군은 지리산 국립공원·화엄사·산수유마을이 있는 전남 동부 군으로, 구례읍 도심 가정 방문과 지리산 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","지리산·화엄사")],
   "subs":["구례읍","문척면","간전면","토지면","마산면","광의면","용방면","산동면"],
   "character":"구례군은 구례읍 도심 가정 방문과 마산·토지 일대 지리산 인근 펜션·콘도 객실 방문이 함께 안내됩니다.",
   "pattern":"구례군은 평일 저녁과 주말·봄(산수유) 시즌 비중이 큽니다.",
   "faqs":[
     ("지리산 인근 가능한가요?","마산·토지 일대 펜션·민박 방문이 안내됩니다."),
     ("산수유 시즌 사전 예약 필요한가요?","3월 산수유 시즌은 사전 예약이 권장됩니다."),
     ("곡성·하동과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gokseong","hadong","namwon"]},
  {"slug":"goheung","name":"고흥군",
   "lede":"고흥군은 나로우주센터·소록도가 있는 전남 남부 군으로, 고흥읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","나로우주센터")],
   "subs":["고흥읍","도양읍","풍양면","도덕면","금산면","도화면","포두면","봉래면","동일면","점암면","과역면","남양면","동강면","대서면","두원면","영남면"],
   "character":"고흥군은 고흥읍·도양읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"고흥군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("고흥읍 가능한가요?","고흥읍 일대 가정 방문이 안내됩니다."),
     ("나로우주센터 인근 가능한가요?","봉래·동일 일대 펜션·민박 방문이 안내됩니다."),
     ("여수와 함께 가능한가요?","여수는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeosu","boseong","jangheung"]},
  {"slug":"boseong","name":"보성군",
   "lede":"보성군은 보성녹차밭·득량만이 있는 전남 남부 군으로, 보성읍 도심 가정 방문과 녹차밭 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","보성녹차밭")],
   "subs":["보성읍","벌교읍","노동면","미력면","겸백면","율어면","복내면","문덕면","조성면","득량면","회천면","웅치면"],
   "character":"보성군은 보성읍·벌교읍 도심 가정 방문과 회천·득량 일대 녹차밭·해안 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"보성군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("녹차밭 인근 가능한가요?","회천·노동 일대 펜션 객실 방문이 안내됩니다."),
     ("벌교 가능한가요?","벌교읍 일대 가정 방문이 안내됩니다."),
     ("순천·고흥과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["suncheon","goheung","jangheung"]},
  {"slug":"hwasun","name":"화순군",
   "lede":"화순군은 광주와 인접한 전남 중부 군으로, 화순읍 도심 가정 방문과 신축 단지 케어가 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","광주 인접")],
   "subs":["화순읍","한천면","춘양면","청풍면","이양면","능주면","도곡면","도암면","이서면","북면","동복면","남면","동면"],
   "character":"화순군은 화순읍 도심 가정 방문이 평일 저녁 중심을 이룹니다. 광주와 인접해 권역 흐름이 닿아 있습니다.",
   "pattern":"화순군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("화순읍 가능한가요?","화순읍 일대 가정 방문이 안내됩니다."),
     ("광주와 함께 가능한가요?","광주는 별도 광역시로 권역별 확인이 필요합니다."),
     ("담양·나주와 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["damyang","naju","boseong"]},
  {"slug":"jangheung","name":"장흥군",
   "lede":"장흥군은 정남진·천관산이 있는 전남 남부 군으로, 장흥읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","정남진")],
   "subs":["장흥읍","관산읍","대덕읍","용산면","안양면","장동면","장평면","유치면","부산면","회진면","천관산도립공원"],
   "character":"장흥군은 장흥읍·관산읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"장흥군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("장흥읍 가능한가요?","장흥읍 일대 가정 방문이 안내됩니다."),
     ("정남진 인근 가능한가요?","회진·관산 일대 펜션 방문이 안내됩니다."),
     ("강진·보성과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["gangjin","boseong","goheung"]},
  {"slug":"gangjin","name":"강진군",
   "lede":"강진군은 다산초당·청자도요지가 있는 전남 남부 군으로, 강진읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","청자도요지")],
   "subs":["강진읍","군동면","칠량면","대구면","마량면","도암면","신전면","성전면","작천면","병영면","옴천면"],
   "character":"강진군은 강진읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"강진군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("강진읍 가능한가요?","강진읍 일대 가정 방문이 안내됩니다."),
     ("청자도요지 인근 가능한가요?","대구·칠량 일대 펜션·민박 방문이 안내됩니다."),
     ("해남·장흥과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["haenam","jangheung","yeongam"]},
  {"slug":"haenam","name":"해남군",
   "lede":"해남군은 두륜산·땅끝마을이 있는 한반도 최남단 군으로, 해남읍 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","땅끝마을")],
   "subs":["해남읍","삼산면","화산면","현산면","송지면","북평면","북일면","옥천면","계곡면","마산면","황산면","산이면","문내면","화원면"],
   "character":"해남군은 해남읍 도심과 송지·북평 땅끝 일대 펜션·호텔(땅끝호텔·솔비치 해남) 객실 방문이 함께 안내됩니다.",
   "pattern":"해남군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("땅끝마을 인근 가능한가요?","송지·북평 일대 펜션·호텔 객실 방문이 안내됩니다."),
     ("두륜산 인근 가능한가요?","삼산·현산 일대 펜션 객실 방문이 안내됩니다."),
     ("진도·완도와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jindo","wando","gangjin"]},
  {"slug":"yeongam","name":"영암군",
   "lede":"영암군은 월출산·F1 경기장이 있는 전남 서남부 군으로, 영암읍 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","월출산·F1")],
   "subs":["영암읍","삼호읍","덕진면","금정면","신북면","시종면","도포면","군서면","서호면","학산면","미암면"],
   "character":"영암군은 영암읍·삼호읍 도심 가정 방문이 평일 저녁 중심을 이루며, 군서·삼호 일대 펜션 객실 방문도 함께 안내됩니다.",
   "pattern":"영암군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("영암읍·삼호 가능한가요?","영암읍·삼호읍 일대 가정 방문이 안내됩니다."),
     ("월출산 인근 가능한가요?","군서·덕진 일대 펜션 방문이 안내됩니다."),
     ("목포·해남과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["mokpo","gangjin","muan"]},
  {"slug":"muan","name":"무안군",
   "lede":"무안군은 무안국제공항·전남도청이 있는 군으로, 남악신도시 일대 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","전남도청·무안공항")],
   "subs":["무안읍","일로읍","삼향읍","몽탄면","청계면","현경면","망운면","해제면","운남면"],
   "character":"무안군은 삼향읍 남악신도시(전남도청 인접) 신축 단지 가정 방문이 평일 저녁 자주 안내됩니다. 무안공항 인근 일부 호텔 객실 방문도 들어옵니다.",
   "pattern":"무안군은 평일 저녁 시간대 비중이 큽니다.",
   "faqs":[
     ("남악신도시 가능한가요?","삼향 남악 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("무안국제공항 환승 가능한가요?","공항 인근 호텔 단시간 코스가 일부 안내됩니다."),
     ("목포·신안과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["mokpo","sinan","hampyeong"]},
  {"slug":"hampyeong","name":"함평군",
   "lede":"함평군은 나비축제로 알려진 전남 서부 군으로, 함평읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","나비축제")],
   "subs":["함평읍","손불면","신광면","학교면","엄다면","대동면","나산면","해보면","월야면"],
   "character":"함평군은 함평읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"함평군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("함평읍 가능한가요?","함평읍 일대 가정 방문이 안내됩니다."),
     ("나비축제 시즌 가능한가요?","축제 시즌은 사전 예약이 권장됩니다."),
     ("영광·무안과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeonggwang","muan","jangseong"]},
  {"slug":"yeonggwang","name":"영광군",
   "lede":"영광군은 굴비로 유명한 전남 서북부 군으로, 영광읍 도심 가정 방문과 백수해안도로 인근 펜션 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","영광굴비")],
   "subs":["영광읍","백수읍","홍농읍","대마면","묘량면","불갑면","군서면","군남면","염산면","법성면","낙월면"],
   "character":"영광군은 영광읍·법성 도심 가정 방문이 평일 저녁 중심을 이룹니다. 백수해안도로 인근 펜션 객실 방문도 일부 들어옵니다.",
   "pattern":"영광군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("영광읍 가능한가요?","영광읍 일대 가정 방문이 안내됩니다."),
     ("백수해안 펜션 가능한가요?","백수읍 일대 펜션 방문이 안내됩니다."),
     ("고창·함평과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["hampyeong","jangseong","gochang"]},
  {"slug":"jangseong","name":"장성군",
   "lede":"장성군은 백양사·축령산이 있는 전남 북부 군으로, 장성읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","백양사")],
   "subs":["장성읍","진원면","남면","동화면","삼서면","삼계면","황룡면","서삼면","북일면","북이면","북하면"],
   "character":"장성군은 장성읍 도심 가정 방문이 평일 저녁 중심을 이룹니다. 광주와 인접해 권역 흐름이 닿아 있습니다.",
   "pattern":"장성군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("장성읍 가능한가요?","장성읍 일대 가정 방문이 안내됩니다."),
     ("백양사 인근 가능한가요?","북하·북이 일대 펜션·민박 방문이 안내됩니다."),
     ("광주와 함께 가능한가요?","광주는 별도 광역시로 권역별 확인이 필요합니다."),
   ],"neighbors":["damyang","yeonggwang","hampyeong"]},
  {"slug":"wando","name":"완도군",
   "lede":"완도군은 청산도·보길도·완도 등 다도해 도서로 이루어진 군으로, 완도읍 도심 가정 방문과 해안 펜션·민박 객실 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","청산도·보길도")],
   "subs":["완도읍","금일읍","노화읍","군외면","신지면","고금면","약산면","청산면","소안면","금당면","보길면","생일면"],
   "character":"완도군은 완도읍 도심 가정 방문과 청산·보길·신지 일대 도서 펜션·민박 객실 방문이 함께 안내됩니다.",
   "pattern":"완도군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("청산도 가능한가요?","청산면 일대 펜션·민박 방문이 안내되며, 도서 이동 시간 고려가 필요합니다."),
     ("보길도 가능한가요?","보길면 일대 펜션 방문이 안내됩니다."),
     ("해남·진도와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["haenam","jindo","gangjin"]},
  {"slug":"jindo","name":"진도군",
   "lede":"진도군은 진도개·울돌목·신비의 바닷길로 알려진 군으로, 진도읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","7개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","울돌목")],
   "subs":["진도읍","군내면","고군면","의신면","임회면","지산면","조도면"],
   "character":"진도군은 진도읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"진도군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("진도읍 가능한가요?","진도읍 일대 가정 방문이 안내됩니다."),
     ("울돌목 인근 가능한가요?","군내·고군 일대 펜션 방문이 안내됩니다."),
     ("해남·완도와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["haenam","wando","sinan"]},
  {"slug":"sinan","name":"신안군",
   "lede":"신안군은 1004개 섬이 모인 다도해 군으로, 압해·자은·임자 일대 도서 권역 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","1004개 섬")],
   "subs":["지도읍","압해읍","증도면","임자면","자은면","비금면","도초면","흑산면","하의면","신의면","장산면","안좌면","팔금면","암태면"],
   "character":"신안군은 압해·지도 일대 도심 가정 방문과 자은·임자·증도 일대 도서 펜션·민박 객실 방문이 함께 안내됩니다.",
   "pattern":"신안군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("자은도·임자도 가능한가요?","자은면·임자면 일대 펜션·민박 방문이 안내되며 이동 시간 고려가 필요합니다."),
     ("증도 가능한가요?","증도면 일대 펜션 방문이 안내됩니다."),
     ("목포와 함께 가능한가요?","목포는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["mokpo","muan","jindo"]},
]

for _d in JEONNAM_DISTRICTS:
    _build_metro_district("jeonnam", "전남", _d, JEONNAM_DISTRICTS)


# ============================================================
# 경북 22 (시 10 + 군 12) — 2023년 군위군 대구 편입으로 22개
# ============================================================
GYEONGBUK_DISTRICTS = [
  {"slug":"pohang","name":"포항시","sub_label":"2개 구",
   "lede":"포항시는 포항제철소·포스코가 자리한 철강 산업 도시로, 평일 저녁 출장 호텔과 도심·신축 단지 가정 방문 비중이 큰 시입니다.",
   "facts":[("구","2개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑"),("특이점","포스코·영일대")],
   "subs":["남구","북구"],
   "character":"남구(상도·해도·송도·오천)는 포항제철소·포스코 본사 출장 호텔(쉐라톤 포항·베스트웨스턴 포항) 객실 방문 비중이 매우 큽니다. 북구(양덕·장량·죽도·환호)는 영일대해수욕장 인근 호텔과 신축 단지 가정 방문이 함께 안내됩니다.",
   "pattern":"포항시는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("포스코 출장 가능한가요?","남구 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("영일대해수욕장 호텔 가능한가요?","북구 영일대 일대 호텔 객실 방문이 안내됩니다."),
     ("외국인 엔지니어 영어 안내 가능한가요?","사전 협의 일정에서 가능 여부 확인됩니다."),
   ],"neighbors":["gyeongju","yeongdeok","yeongcheon"]},
  {"slug":"gyeongju","name":"경주시",
   "lede":"경주시는 신라 천년 고도이자 보문관광단지·불국사·석굴암이 있는 대표 관광 도시로, 보문 일대 호텔·리조트 객실 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","23개"),("주요 시간대","시즌·주말"),("호텔/가정","호텔 비중↑↑"),("특이점","보문관광단지")],
   "subs":["중부동","황오동","성건동","황남동","월성동","선도동","용강동","황성동","현곡면","불국동","천북면","건천읍","감포읍","외동읍","안강읍","서면","산내면","문무대왕면","강동면","양남면","양북","내남면","보덕동","탑정동"],
   "character":"경주시는 보문관광단지(보덕·황성·동천) 일대 힐튼 경주·코오롱호텔·켄싱턴리조트 경주·라궁리조트·블루원리조트 등 리조트 객실 방문이 봄·가을 관광 시즌에 매우 자주 안내됩니다.",
   "pattern":"경주시는 봄(벚꽃)·가을(단풍) 시즌과 주말 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("힐튼 경주 가능한가요?","보문 힐튼 경주·코오롱호텔 객실 방문이 자주 안내됩니다."),
     ("켄싱턴 경주 가능한가요?","보문 켄싱턴리조트 객실 방문이 안내됩니다."),
     ("벚꽃·단풍 시즌 사전 예약 필요한가요?","봄·가을 성수기는 사전 예약이 강력 권장됩니다."),
   ],"neighbors":["pohang","ulsan-ext","yeongcheon"]},
  {"slug":"gimcheon","name":"김천시",
   "lede":"김천시는 KTX 김천구미역이 있는 경북 서부 도시로, 평일 저녁 도심 가정 방문과 환승 호텔 객실 방문이 함께 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","KTX 김천구미역")],
   "subs":["자산동","평화·남산동","양금동","대신동","대광동","감호동","신음동","지좌동","율곡동","아포읍","농소면","남면","개령면","어모면","감천면","조마면","구성면","지례면","부항면","대덕면","증산면"],
   "character":"김천시는 신음·지좌·평화 일대 도심 가정 방문과 KTX 김천구미역 인근 호텔 객실 방문이 함께 안내됩니다. 김천혁신도시(율곡)는 신축 단지 권역입니다.",
   "pattern":"김천시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("KTX 김천구미역 환승 가능한가요?","역 인근 호텔 60·90분 단시간 코스가 자주 안내됩니다."),
     ("율곡 혁신도시 가능한가요?","율곡 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("구미와 함께 가능한가요?","구미는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gumi","sangju","chilgok"]},
  {"slug":"andong","name":"안동시",
   "lede":"안동시는 경북도청 소재지이자 하회마을·도산서원이 있는 유교 문화 도시로, 도심 가정 방문과 관광 호텔·한옥 객실 방문이 함께 안내됩니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","하회마을")],
   "subs":["중구동","명륜동","용상동","서구동","태화동","평화동","안기동","송천동","송하동","법상동","강남동","북후면","서후면","북면","풍산읍","풍천면","와룡면","녹전면","일직면","남후면","남선면","임동면","임하면","길안면","예안면","도산면"],
   "character":"안동시는 송천·용상·태화 일대 도심 가정 방문과 풍천면 하회마을 인근 한옥·게스트하우스 객실 방문이 함께 안내됩니다.",
   "pattern":"안동시는 평일 저녁과 봄·가을 시즌 비중이 큽니다.",
   "faqs":[
     ("하회마을 한옥 가능한가요?","풍천면 일대 한옥 객실 방문이 안내됩니다."),
     ("송천·용상 가정 가능한가요?","송천·용상 일대 가정 방문이 자주 안내됩니다."),
     ("영주·예천과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeongju","yecheon","cheongsong"]},
  {"slug":"gumi","name":"구미시",
   "lede":"구미시는 구미국가산업단지가 있는 경북 최대 산업 도시로, 평일 저녁 출장 호텔과 신축 단지 가정 방문 비중이 매우 큰 시입니다.",
   "facts":[("행정동","27개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑↑"),("특이점","구미산단")],
   "subs":["송정동","원평동","지산동","도량동","선주원남동","형곡동","신평동","비산동","공단동","광평동","상모사곡동","임오동","인동동","진미동","양포동","산동읍","장천면","해평면","구포동","고아읍","무을면","선산읍","옥성면","도개면","옥계동"],
   "character":"구미시는 송정·인동·진미 일대 비즈니스 호텔(코모도호텔 구미·호텔 금오산·소노캄 구미) 출장 객실 방문과 양포·산동 신축 단지 가정 방문이 함께 안내됩니다.",
   "pattern":"구미시는 평일 저녁 7~11시 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("코모도호텔 구미 가능한가요?","송정 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("구미산단 출장 가능한가요?","송정·공단 일대 호텔 객실 방문이 평일 저녁 안내됩니다."),
     ("외국인 엔지니어 영어 안내 가능한가요?","사전 협의 일정에서 가능 여부 확인됩니다."),
   ],"neighbors":["gimcheon","chilgok","gunwi-ext"]},
  {"slug":"yeongju","name":"영주시",
   "lede":"영주시는 부석사·소수서원·풍기인삼이 있는 경북 북부 도시로, 평일 저녁 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","부석사·풍기")],
   "subs":["영주1동","영주2동","휴천1동","휴천2동","휴천3동","상망동","하망동","문수면","평은면","이산면","장수면","안정면","봉현면","순흥면","단산면","부석면","풍기읍","풍기"],
   "character":"영주시는 영주·휴천 일대 도심 가정 방문과 풍기읍 일대 펜션·민박 객실 방문이 함께 안내됩니다.",
   "pattern":"영주시는 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("영주 도심 가능한가요?","영주1·2·휴천 일대 가정 방문이 안내됩니다."),
     ("부석사 인근 가능한가요?","부석면 일대 펜션·민박 방문이 안내됩니다."),
     ("안동·예천과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["andong","yecheon","bonghwa"]},
  {"slug":"yeongcheon","name":"영천시",
   "lede":"영천시는 경주·포항·대구 인접 경북 남부 도시로, 평일 저녁 도심 가정 방문과 출장 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","경주·대구 인접")],
   "subs":["동부동","중앙동","서부동","완산동","남부동","북안면","임고면","고경면","화북면","화남면","신령면","청통면","화산면","대창면","자양면","금호읍","금호","화북"],
   "character":"영천시는 동부·중앙·서부 일대 도심 가정 방문과 금호읍 신축 단지 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"영천시는 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("영천 도심 가능한가요?","동부·중앙 일대 가정 방문이 안내됩니다."),
     ("경주·경산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("대구와 함께 가능한가요?","대구는 별도 광역시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gyeongju","gyeongsan","cheongdo"]},
  {"slug":"sangju","name":"상주시",
   "lede":"상주시는 곶감으로 유명한 경북 북서부 도시로, 평일 저녁 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","곶감")],
   "subs":["남원동","북문동","계림동","동문동","동성동","신흥동","서성동","중앙동","서문동","사벌국면","외남면","낙동면","청리면","공성면","외서면","내서면","모동면","모서면","화동면","화서면","화북면","함창읍","공검면","이안면","은척면","화남면"],
   "character":"상주시는 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"상주시는 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("상주 도심 가능한가요?","중앙·남원 일대 가정 방문이 안내됩니다."),
     ("문경·예천과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
     ("김천과 함께 가능한가요?","김천은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["mungyeong","gimcheon","yecheon"]},
  {"slug":"mungyeong","name":"문경시",
   "lede":"문경시는 문경새재·문경온천이 있는 경북 북부 도시로, 평일 저녁 도심 가정 방문과 휴양 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","문경새재·온천")],
   "subs":["점촌1동","점촌2동","점촌3동","점촌4동","점촌5동","문경읍","가은읍","호계면","산북면","마성면","산양면","영순면","동로면","농암면"],
   "character":"문경시는 점촌 일대 도심 가정 방문과 문경읍 일대 온천 호텔(STX리조트 문경·문경새재유스호스텔) 객실 방문이 함께 안내됩니다.",
   "pattern":"문경시는 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("STX리조트 문경 가능한가요?","문경읍 일대 리조트 객실 방문이 안내됩니다."),
     ("문경온천 가능한가요?","문경읍 온천 호텔 객실 방문이 안내됩니다."),
     ("상주와 함께 가능한가요?","상주는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["sangju","yecheon","bonghwa"]},
  {"slug":"gyeongsan","name":"경산시",
   "lede":"경산시는 대구와 인접한 경북 남부 도시로, 영남대·대구가톨릭대 등 대학가와 신축 단지 가정 방문 비중이 매우 큰 권역입니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","대학가")],
   "subs":["중앙동","서부1동","서부2동","동부동","남부동","북부동","남천면","압량읍","진량읍","와촌면","자인면","용성면","남산면","하양읍","와촌","자인","용성"],
   "character":"경산시는 중앙·서부·동부 일대 도심 가정 방문과 진량(영남대)·하양(대구가톨릭대) 일대 대학가 원룸·오피스텔 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"경산시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("영남대 인근 가능한가요?","진량읍 일대 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
     ("대구가톨릭대 인근 가능한가요?","하양읍 일대 원룸·오피스텔 가정 방문이 안내됩니다."),
     ("대구와 함께 가능한가요?","대구는 별도 광역시로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeongcheon","cheongdo","gyeongju"]},
  {"slug":"uiseong","name":"의성군",
   "lede":"의성군은 마늘로 유명한 경북 중부 군으로, 의성읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","18개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","의성마늘")],
   "subs":["의성읍","단촌면","점곡면","옥산면","사곡면","춘산면","가음면","금성면","봉양면","비안면","구천면","단밀면","단북면","안계면","다인면","신평면","안평면","안사면"],
   "character":"의성군은 의성읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"의성군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("의성읍 가능한가요?","의성읍 일대 가정 방문이 안내됩니다."),
     ("안동·청송과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
     ("군위와 함께 가능한가요?","군위는 대구로 편입되었습니다."),
   ],"neighbors":["andong","cheongsong","yecheon"]},
  {"slug":"cheongsong","name":"청송군",
   "lede":"청송군은 주왕산국립공원·청송백자가 있는 경북 동부 군으로, 청송읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","주왕산")],
   "subs":["청송읍","파천면","주왕산면","부남면","현동면","현서면","안덕면","진보면"],
   "character":"청송군은 청송읍 도심 가정 방문과 주왕산면 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"청송군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("주왕산 인근 가능한가요?","주왕산면 일대 펜션·민박 방문이 안내됩니다."),
     ("청송읍 가능한가요?","청송읍 일대 가정 방문이 안내됩니다."),
     ("의성·영덕과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["uiseong","yeongdeok","yeongyang"]},
  {"slug":"yeongyang","name":"영양군",
   "lede":"영양군은 일월산·반딧불이가 있는 경북 동북부 군으로, 영양읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","6개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","반딧불이")],
   "subs":["영양읍","입암면","청기면","일월면","수비면","석보면"],
   "character":"영양군은 영양읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"영양군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("영양읍 가능한가요?","영양읍 일대 가정 방문이 안내됩니다."),
     ("청송·봉화와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
     ("안동과 함께 가능한가요?","안동은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["bonghwa","cheongsong","andong"]},
  {"slug":"yeongdeok","name":"영덕군",
   "lede":"영덕군은 영덕대게·강구항이 있는 경북 동해안 군으로, 영덕읍·강구 도심 가정 방문과 해안 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","9개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","영덕대게·강구항")],
   "subs":["영덕읍","강구면","남정면","달산면","지품면","축산면","영해면","병곡면","창수면"],
   "character":"영덕군은 영덕읍·강구면 도심 가정 방문과 강구·축산 일대 해안 펜션·민박 객실 방문이 함께 안내됩니다.",
   "pattern":"영덕군은 평일 저녁과 대게철(11~3월) 시즌 비중이 큽니다.",
   "faqs":[
     ("강구항 인근 펜션 가능한가요?","강구면 일대 펜션·민박 방문이 안내됩니다."),
     ("영덕읍 가능한가요?","영덕읍 일대 가정 방문이 안내됩니다."),
     ("울진·청송과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["uljin","cheongsong","pohang"]},
  {"slug":"cheongdo","name":"청도군",
   "lede":"청도군은 청도반시(곶감)와 청도소싸움이 있는 경북 남부 군으로, 청도읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","청도반시·소싸움")],
   "subs":["화양읍","청도읍","각남면","풍각면","각북면","이서면","운문면","금천면","매전면"],
   "character":"청도군은 청도읍·화양읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"청도군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("청도읍 가능한가요?","청도읍 일대 가정 방문이 안내됩니다."),
     ("대구와 함께 가능한가요?","대구는 별도 광역시로 권역별 확인이 필요합니다."),
     ("경산·영천과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gyeongsan","yeongcheon","goryeong"]},
  {"slug":"goryeong","name":"고령군",
   "lede":"고령군은 가야 고분이 있는 경북 남부 군으로, 고령읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","가야 고분군")],
   "subs":["대가야읍","덕곡면","운수면","성산면","다산면","개진면","우곡면","쌍림면"],
   "character":"고령군은 대가야읍 도심 가정 방문이 평일 저녁 중심을 이룹니다. 대구·달성과 인접해 권역 흐름이 닿아 있습니다.",
   "pattern":"고령군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("대가야읍 가능한가요?","대가야읍 일대 가정 방문이 안내됩니다."),
     ("대구·달성과 함께 가능한가요?","각각 별도 광역시·군으로 권역별 확인이 필요합니다."),
     ("성주·합천과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["seongju","cheongdo","hapcheon"]},
  {"slug":"seongju","name":"성주군",
   "lede":"성주군은 참외로 유명한 경북 남부 군으로, 성주읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","성주참외")],
   "subs":["성주읍","선남면","용암면","수륜면","가천면","금수면","대가면","벽진면","초전면","월항면"],
   "character":"성주군은 성주읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"성주군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("성주읍 가능한가요?","성주읍 일대 가정 방문이 안내됩니다."),
     ("대구·구미와 함께 가능한가요?","각각 별도 광역시·시로 권역별 확인이 필요합니다."),
     ("고령·칠곡과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["chilgok","goryeong","gimcheon"]},
  {"slug":"chilgok","name":"칠곡군",
   "lede":"칠곡군은 왜관·약목 일대 신도시와 산업단지가 함께 있는 경북 남부 군으로, 평일 저녁 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","왜관산단·대구 인접")],
   "subs":["왜관읍","북삼읍","석적읍","지천면","동명면","가산면","약목면","기산면"],
   "character":"칠곡군은 왜관·북삼·석적 일대 신축 단지와 약목 도심 가정 방문이 평일 저녁 자주 안내됩니다. 대구와 인접해 권역 흐름이 닿아 있습니다.",
   "pattern":"칠곡군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("왜관·북삼 가능한가요?","왜관·북삼·석적 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("대구와 함께 가능한가요?","대구는 별도 광역시로 권역별 확인이 필요합니다."),
     ("구미와 함께 가능한가요?","구미는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gumi","seongju","gimcheon"]},
  {"slug":"yecheon","name":"예천군",
   "lede":"예천군은 경북도청 신청사가 자리한 군으로, 예천읍·호명 일대 가정 방문 비중이 큰 권역입니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","경북도청")],
   "subs":["예천읍","용문면","감천면","보문면","호명면","유천면","용궁면","개포면","지보면","풍양면","효자면","은풍면"],
   "character":"예천군은 호명면(경북도청 신청사) 일대 신축 단지와 예천읍 도심 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"예천군은 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("호명 도청 신도시 가능한가요?","호명면 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("예천읍 가능한가요?","예천읍 일대 가정 방문이 안내됩니다."),
     ("안동·영주와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["andong","yeongju","mungyeong"]},
  {"slug":"bonghwa","name":"봉화군",
   "lede":"봉화군은 청량산이 있는 경북 북부 군으로, 봉화읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","청량산")],
   "subs":["봉화읍","물야면","봉성면","법전면","춘양면","소천면","석포면","재산면","명호면","상운면"],
   "character":"봉화군은 봉화읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"봉화군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("봉화읍 가능한가요?","봉화읍 일대 가정 방문이 안내됩니다."),
     ("청량산 인근 가능한가요?","명호 일대 펜션·민박 방문이 안내됩니다."),
     ("영주·안동과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeongju","yeongyang","mungyeong"]},
  {"slug":"uljin","name":"울진군",
   "lede":"울진군은 백암온천·덕구온천이 있는 경북 동해안 군으로, 울진읍·후포 도심 가정 방문과 온천·해안 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","백암·덕구온천")],
   "subs":["울진읍","평해읍","북면","서면","근남면","원남면","기성면","온정면","죽변면","후포면"],
   "character":"울진군은 울진읍·평해읍·후포 도심 가정 방문과 온정면 백암온천·북면 덕구온천 일대 호텔·콘도 객실 방문이 함께 안내됩니다.",
   "pattern":"울진군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("백암온천 가능한가요?","온정면 일대 온천 호텔 객실 방문이 안내됩니다."),
     ("덕구온천 가능한가요?","북면 일대 온천 호텔 객실 방문이 안내됩니다."),
     ("영덕·삼척과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["yeongdeok","ulleung","bonghwa"]},
  {"slug":"ulleung","name":"울릉군",
   "lede":"울릉군은 울릉도·독도가 있는 도서 군으로, 도서 권역 특성상 정기 여객선 일정에 맞춘 사전 협의가 필요합니다.",
   "facts":[("행정동","3개"),("주요 시간대","사전 협의"),("호텔/가정","사전 협의"),("특이점","울릉도·독도")],
   "subs":["울릉읍","서면","북면"],
   "character":"울릉군은 울릉도 도서 권역으로 도동·저동 일대 호텔·펜션 객실 방문이 정기 여객선 일정에 맞춰 안내됩니다.",
   "pattern":"울릉군은 도서 권역 특성상 사전 협의가 필수입니다.",
   "faqs":[
     ("울릉도 가능한가요?","울릉읍·서·북면 일대 호텔·펜션 객실 방문이 사전 협의로 안내됩니다."),
     ("여객선 일정에 맞춰 가능한가요?","울릉도 출입 여객선 일정과 체류 일정 사전 협의가 필요합니다."),
     ("육지 동해안과 함께 가능한가요?","울진·강원 동해안과 권역별 확인이 필요합니다."),
   ],"neighbors":["uljin"]},
]

for _d in GYEONGBUK_DISTRICTS:
    _build_metro_district("gyeongbuk", "경북", _d, GYEONGBUK_DISTRICTS)


# ============================================================
# 경남 18 (시 8 + 군 10)
# ============================================================
GYEONGNAM_DISTRICTS = [
  {"slug":"changwon","name":"창원시","sub_label":"5개 구",
   "lede":"창원시는 경남 도청 소재지이자 두산·LG·현대로템 등 기계 산업이 밀집한 경남 최대 도시로, 평일 저녁 출장 호텔·신축 단지 가정 방문 비중이 매우 큰 시입니다.",
   "facts":[("구","5개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합 비중↑↑"),("특이점","기계 산단·해군")],
   "subs":["의창구","성산구","마산합포구","마산회원구","진해구"],
   "character":"성산구(상남·중앙·반송)는 창원국가산업단지 출장과 호텔 객실 방문이 가장 큰 권역입니다. 의창구(명서·봉림)는 신축 단지, 마산합포·마산회원은 마산만 일대 호텔과 주거 권역이며, 진해구는 해군기지·진해 군항제로 알려진 권역입니다.",
   "pattern":"창원시는 평일 저녁 7~11시 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("성산구(상남) 호텔 가능한가요?","상남·중앙 일대 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
     ("진해 군항제 시즌 가능한가요?","진해 벚꽃 시즌은 사전 예약이 권장됩니다."),
     ("김해·양산과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gimhae","yangsan","haman"]},
  {"slug":"jinju","name":"진주시",
   "lede":"진주시는 진주성·남강·진주국제민속축제로 알려진 경남 서부 도시로, 평일 저녁 도심 가정 방문과 신축 단지 가정 방문 비중이 큰 시입니다.",
   "facts":[("행정동","21개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","진주성·유등축제")],
   "subs":["천전동","성북동","중앙동","상봉동","상대동","하대동","상평동","초장동","평거동","신안동","이현동","판문동","가호동","충무공동","문산읍","내동면","정촌면","미천면","명석면","대평면","수곡면","금산면","집현면","대곡면","사봉면","지수면","일반성면","이반성면"],
   "character":"진주시는 평거·신안·상대 일대 도심 가정 방문과 충무공동(혁신도시) 신축 단지 가정 방문이 평일 저녁 자주 안내됩니다.",
   "pattern":"진주시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("진주혁신도시(충무공동) 가능한가요?","충무공동 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("평거·신안 가능한가요?","평거·신안 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("유등축제 시즌 사전 예약 필요한가요?","축제 시즌은 사전 예약이 권장됩니다."),
   ],"neighbors":["sacheon","sancheong","hadong"]},
  {"slug":"tongyeong","name":"통영시",
   "lede":"통영시는 한산도·동피랑·미륵산이 있는 경남 남부 관광 도시로, 도남·무전 일대 호텔 객실 방문과 도심 가정 방문이 함께 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","한산도·동피랑")],
   "subs":["중앙동","정량동","북신동","무전동","미수동","봉평동","도천동","명정동","평림동","산양읍","용남면","도산면","광도면","욕지면","한산면","사량면"],
   "character":"통영시는 무전·도남 일대 호텔(스탠포드 호텔 통영·금호리조트 통영) 객실 방문과 정량·중앙 도심 가정 방문이 함께 안내됩니다.",
   "pattern":"통영시는 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("스탠포드 호텔 통영 가능한가요?","무전 일대 스탠포드·금호리조트 객실 방문이 자주 안내됩니다."),
     ("동피랑·중앙시장 가능한가요?","정량·중앙 일대 호텔·게스트하우스 방문이 안내됩니다."),
     ("거제·사천과 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["geoje","goseong-nam","sacheon"]},
  {"slug":"sacheon","name":"사천시",
   "lede":"사천시는 사천공항·KAI(한국항공우주산업)가 있는 경남 남부 도시로, 평일 저녁 출장 호텔·도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","15개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","사천공항·KAI")],
   "subs":["향촌동","동서동","선구동","동서금동","벌용동","사천읍","정동면","사남면","용현면","축동면","곤양면","곤명면","서포면","남양동","좌룡동"],
   "character":"사천시는 동서·향촌 일대 도심 가정 방문과 사남·용현 일대 KAI 출장 호텔 객실 방문이 함께 안내됩니다.",
   "pattern":"사천시는 평일 저녁 7~10시 시간대 비중이 큽니다.",
   "faqs":[
     ("KAI 출장 가능한가요?","사남·용현 일대 비즈니스 호텔 객실 방문이 안내됩니다."),
     ("사천공항 환승 가능한가요?","공항 인근 일부 호텔 단시간 코스가 안내됩니다."),
     ("진주·고성과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jinju","goseong-nam","namhae"]},
  {"slug":"gimhae","name":"김해시",
   "lede":"김해시는 김해국제공항(부산 강서 인접)·김해평야가 있는 경남 동남부 도시로, 평일 저녁 신축 단지 가정 방문과 공항 인접 호텔 객실 방문 비중이 큰 시입니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","김해공항·물류")],
   "subs":["동상동","부원동","북부동","활천동","삼안동","불암동","내외동","칠산서부동","장유1동","장유2동","장유3동","주촌면","진례면","진영읍","진영","한림면","생림면","상동면","대동면"],
   "character":"김해시는 장유1~3·내외·삼안 일대 신축 단지 가정 방문이 평일 저녁 자주 안내됩니다. 부산 김해공항 인접 호텔(롯데시티호텔 김해 등) 객실 방문도 함께 들어옵니다.",
   "pattern":"김해시는 평일 저녁 7~11시 시간대 비중이 큽니다.",
   "faqs":[
     ("장유신도시 가능한가요?","장유1~3 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("김해공항 환승 가능한가요?","공항 인근 호텔 단시간 코스가 안내됩니다."),
     ("창원·부산과 함께 가능한가요?","각각 별도 시·광역시로 권역별 확인이 필요합니다."),
   ],"neighbors":["changwon","yangsan","busan-ext"]},
  {"slug":"miryang","name":"밀양시",
   "lede":"밀양시는 영남루·표충사가 있는 경남 동부 도시로, 평일 저녁 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","16개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","KTX 밀양역")],
   "subs":["내일동","내이동","교동","삼문동","가곡동","산내면","산외면","부북면","상동면","상남면","하남읍","초동면","무안면","청도면","단장면","삼랑진읍"],
   "character":"밀양시는 내이·삼문 일대 도심 가정 방문과 KTX 밀양역 인근 호텔 객실 방문이 함께 안내됩니다.",
   "pattern":"밀양시는 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("KTX 밀양역 환승 가능한가요?","역 인근 호텔 단시간 코스가 안내됩니다."),
     ("내이·삼문 가정 가능한가요?","내이·삼문 일대 가정 방문이 평일 저녁 안내됩니다."),
     ("창원·김해와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["changwon","gimhae","changnyeong"]},
  {"slug":"geoje","name":"거제시",
   "lede":"거제시는 한화오션(옥포)·삼성중공업(고현) 등 조선소가 있는 경남 남부 도시로, 평일 야간 장기 출장 호텔 객실 방문 비중이 매우 큰 시입니다.",
   "facts":[("행정동","19개"),("주요 시간대","평일 야간"),("호텔/가정","호텔 비중↑↑"),("특이점","조선소·외국인")],
   "subs":["일운면","동부면","남부면","거제면","둔덕면","사등면","연초면","하청면","장목면","장승포동","능포동","아주동","아양동","옥포1동","옥포2동","상문동","고현동","수양동","마전동"],
   "character":"거제시는 옥포(한화오션)·고현(삼성중공업) 일대 비즈니스 호텔(소노캄 거제·거제삼성호텔·라온블루리조트) 객실 방문이 장기 출장과 맞물려 평일 야간 자주 안내됩니다. 외국인 엔지니어 케이스가 많아 영어 안내 협의가 필요한 경우가 있습니다.",
   "pattern":"거제시는 평일 야간(9~12시) 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("한화오션·삼성중공업 출장 가능한가요?","옥포·고현 일대 비즈니스 호텔 객실 방문이 평일 야간 자주 안내됩니다."),
     ("외국인 엔지니어 영어 안내 가능한가요?","사전 협의 일정에서 가능 여부 확인됩니다."),
     ("장기 출장 정기 예약 가능한가요?","주차별 사전 확인을 통한 정기 예약이 가능합니다."),
   ],"neighbors":["tongyeong","goseong-nam","changwon"]},
  {"slug":"yangsan","name":"양산시",
   "lede":"양산시는 부산 노포·물금 인접 경남 동부 도시로, 물금·동면 신도시 신축 단지 가정 방문 비중이 매우 큰 시입니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","부산 노포 인접")],
   "subs":["중앙동","삼성동","강서동","서창동","소주동","평산동","덕계동","웅상","물금읍","동면","원동면","상북면","하북면"],
   "character":"양산시는 물금읍·동면 신도시 대단지 가정 방문이 평일 저녁 매우 자주 안내됩니다. 부산 노포·금정과 인접해 권역 흐름이 닿아 있습니다.",
   "pattern":"양산시는 평일 저녁 7~11시 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("물금신도시 가능한가요?","물금읍 일대 신축 단지 가정 방문이 자주 안내됩니다."),
     ("부산 노포와 같은 권역인가요?","행정상 별도이며 인접하지만 각각 권역 확인이 필요합니다."),
     ("김해와 함께 가능한가요?","김해는 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["gimhae","busan-ext","miryang"]},
  {"slug":"uiryeong","name":"의령군",
   "lede":"의령군은 망개떡·솥발이가 있는 경남 중부 군으로, 의령읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","망개떡")],
   "subs":["의령읍","가례면","칠곡면","대의면","화정면","용덕면","정곡면","지정면","낙서면","부림면","봉수면","궁류면","유곡면"],
   "character":"의령군은 의령읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"의령군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("의령읍 가능한가요?","의령읍 일대 가정 방문이 안내됩니다."),
     ("창원·진주와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("함안·합천과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["haman","hapcheon","jinju"]},
  {"slug":"haman","name":"함안군",
   "lede":"함안군은 가야리유적이 있는 경남 중부 군으로, 가야읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","가야 유적")],
   "subs":["가야읍","칠원읍","함안면","군북면","법수면","대산면","칠서면","칠북면","산인면","여항면"],
   "character":"함안군은 가야읍·칠원읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"함안군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("가야·칠원 가능한가요?","가야읍·칠원읍 일대 가정 방문이 안내됩니다."),
     ("창원·진주와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("의령·창녕과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["changwon","uiryeong","changnyeong"]},
  {"slug":"changnyeong","name":"창녕군",
   "lede":"창녕군은 우포늪·부곡온천이 있는 경남 동부 군으로, 창녕읍 도심 가정 방문과 부곡 온천 호텔 객실 방문이 안내됩니다.",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","우포늪·부곡온천")],
   "subs":["창녕읍","고암면","성산면","대합면","이방면","유어면","대지면","계성면","영산면","장마면","도천면","길곡면","부곡면","남지읍"],
   "character":"창녕군은 창녕읍 도심 가정 방문과 부곡면 온천 호텔·콘도 객실 방문이 함께 안내됩니다.",
   "pattern":"창녕군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("부곡온천 가능한가요?","부곡면 일대 온천 호텔 객실 방문이 자주 안내됩니다."),
     ("창녕읍 가능한가요?","창녕읍 일대 가정 방문이 안내됩니다."),
     ("밀양과 함께 가능한가요?","밀양은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["miryang","haman","hapcheon"]},
  {"slug":"goseong-nam","name":"고성군",
   "lede":"고성군(경남)은 공룡엑스포·당항포가 있는 경남 남부 군으로, 고성읍 도심 가정 방문이 안내됩니다. (강원도 고성군과 다릅니다.)",
   "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","공룡엑스포")],
   "subs":["고성읍","삼산면","하일면","하이면","상리면","대가면","영현면","영오면","개천면","구만면","회화면","마암면","동해면","거류면"],
   "character":"고성군(경남)은 고성읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"고성군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("고성읍 가능한가요?","고성읍 일대 가정 방문이 안내됩니다."),
     ("통영·거제와 함께 가능한가요?","각각 별도 시로 권역별 확인이 필요합니다."),
     ("강원도 고성과 헷갈리지 않나요?","행정상 별도이며 강원 고성은 <a href=\"/area/gangwon/goseong/\">강원 고성 안내</a> 참고."),
   ],"neighbors":["tongyeong","sacheon","jinju"]},
  {"slug":"namhae","name":"남해군",
   "lede":"남해군은 보리암·독일마을·다랭이마을이 있는 경남 남부 도서 군으로, 남해읍 도심 가정 방문과 해안 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","10개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","독일마을·다랭이")],
   "subs":["남해읍","이동면","상주면","삼동면","미조면","남면","서면","고현면","설천면","창선면"],
   "character":"남해군은 남해읍 도심 가정 방문과 미조·상주·삼동 일대 해안 펜션·리조트(힐튼 남해·소노벨 남해) 객실 방문이 함께 안내됩니다.",
   "pattern":"남해군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("힐튼 남해 가능한가요?","남면 일대 힐튼 남해 객실 방문이 자주 안내됩니다."),
     ("독일마을 인근 가능한가요?","삼동면 일대 펜션·민박 방문이 안내됩니다."),
     ("사천과 함께 가능한가요?","사천은 별도 시로 권역별 확인이 필요합니다."),
   ],"neighbors":["sacheon","hadong","tongyeong"]},
  {"slug":"hadong","name":"하동군",
   "lede":"하동군은 지리산 남쪽·섬진강이 있는 경남 서부 군으로, 하동읍 도심 가정 방문과 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","13개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","지리산·섬진강")],
   "subs":["하동읍","화개면","악양면","적량면","횡천면","고전면","금남면","금성면","진교면","양보면","북천면","청암면","옥종면"],
   "character":"하동군은 하동읍·진교 도심 가정 방문과 화개·악양 지리산·섬진강 일대 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"하동군은 평일 저녁과 봄·가을 시즌 비중이 큽니다.",
   "faqs":[
     ("하동읍 가능한가요?","하동읍 일대 가정 방문이 안내됩니다."),
     ("화개장터 인근 가능한가요?","화개·악양 일대 펜션 객실 방문이 안내됩니다."),
     ("구례·남해와 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["sancheong","namhae","gwangyang"]},
  {"slug":"sancheong","name":"산청군",
   "lede":"산청군은 지리산·산청한방약초축제가 있는 경남 서부 군으로, 산청읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","지리산·한방")],
   "subs":["산청읍","차황면","오부면","생초면","금서면","삼장면","시천면","단성면","신안면","생비량면","신등면"],
   "character":"산청군은 산청읍 도심 가정 방문과 시천·금서 일대 지리산 인근 펜션 객실 방문이 함께 안내됩니다.",
   "pattern":"산청군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("산청읍 가능한가요?","산청읍 일대 가정 방문이 안내됩니다."),
     ("지리산 시천 가능한가요?","시천면 일대 펜션 객실 방문이 안내됩니다."),
     ("진주·하동과 함께 가능한가요?","각각 별도 시·군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["jinju","hadong","hamyang"]},
  {"slug":"hamyang","name":"함양군",
   "lede":"함양군은 지리산·상림숲이 있는 경남 서북부 군으로, 함양읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","상림숲")],
   "subs":["함양읍","마천면","휴천면","유림면","수동면","지곡면","안의면","서상면","서하면","병곡면","백전면"],
   "character":"함양군은 함양읍·안의 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"함양군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("함양읍 가능한가요?","함양읍 일대 가정 방문이 안내됩니다."),
     ("지리산 마천 가능한가요?","마천면 일대 펜션·민박 방문이 안내됩니다."),
     ("산청·거창과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["sancheong","geochang","namwon"]},
  {"slug":"geochang","name":"거창군",
   "lede":"거창군은 거창국제연극제·수승대가 있는 경남 서북부 군으로, 거창읍 도심 가정 방문이 안내됩니다.",
   "facts":[("행정동","12개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 중심"),("특이점","수승대·연극제")],
   "subs":["거창읍","주상면","웅양면","고제면","북상면","위천면","마리면","남상면","남하면","신원면","가조면","가북면"],
   "character":"거창군은 거창읍 도심 가정 방문이 평일 저녁 중심을 이룹니다.",
   "pattern":"거창군은 평일 저녁 시간대가 안정적입니다.",
   "faqs":[
     ("거창읍 가능한가요?","거창읍 일대 가정 방문이 안내됩니다."),
     ("연극제 시즌 사전 예약 필요한가요?","축제 시즌은 사전 예약이 권장됩니다."),
     ("합천·함양과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["hapcheon","hamyang","muju"]},
  {"slug":"hapcheon","name":"합천군",
   "lede":"합천군은 해인사·합천호가 있는 경남 북부 군으로, 합천읍 도심 가정 방문과 해인사 인근 펜션 객실 방문이 안내됩니다.",
   "facts":[("행정동","17개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","해인사")],
   "subs":["합천읍","봉산면","묘산면","가야면","야로면","율곡면","초계면","쌍책면","덕곡면","청덕면","적중면","대양면","쌍백면","삼가면","가회면","대병면","용주면"],
   "character":"합천군은 합천읍 도심 가정 방문과 가야면 해인사 인근 펜션·민박 객실 방문이 함께 안내됩니다.",
   "pattern":"합천군은 평일 저녁과 주말 시즌 비중이 큽니다.",
   "faqs":[
     ("해인사 인근 가능한가요?","가야·야로 일대 펜션·민박 방문이 안내됩니다."),
     ("합천읍 가능한가요?","합천읍 일대 가정 방문이 안내됩니다."),
     ("거창·고령과 함께 가능한가요?","각각 별도 군으로 권역별 확인이 필요합니다."),
   ],"neighbors":["geochang","uiryeong","goryeong"]},
]

for _d in GYEONGNAM_DISTRICTS:
    _build_metro_district("gyeongnam", "경남", _d, GYEONGNAM_DISTRICTS)


# ============================================================
# 제주특별자치도 2 (시 2)
# ============================================================
JEJU_DISTRICTS = [
  {"slug":"jeju-si","name":"제주시",
   "lede":"제주시는 제주국제공항·연동·노형 일대 도심과 애월·조천·구좌·한림·한경 등 외곽 읍·면이 함께 있는 제주 북부 도시로, 도착 당일·출도 전 호텔 객실 방문 비중이 큰 시입니다.",
   "facts":[("행정동","23개"),("주요 시간대","평일 저녁·시즌"),("호텔/가정","호텔 비중↑"),("특이점","공항·관광")],
   "subs":["일도1동","일도2동","이도1동","이도2동","삼도1동","삼도2동","용담1동","용담2동","건입동","화북동","삼양동","봉개동","아라동","오라동","연동","노형동","외도동","이호동","도두동","한림읍","애월읍","구좌읍","조천읍","한경면","추자면","우도면"],
   "character":"제주시는 노형·연동 일대 메종글래드 제주·라마다 제주·롯데시티호텔 제주공항 등 호텔과 애월·함덕 펜션·리조트 객실 방문이 함께 안내됩니다. 제주국제공항 인접 권역 특성상 도착 당일·출도 전 객실 방문이 자주 들어옵니다.",
   "pattern":"제주시는 여름·봄·가을 시즌과 주말 시간대 비중이 큽니다.",
   "faqs":[
     ("메종글래드 제주 가능한가요?","연동·노형 일대 호텔 객실 방문이 자주 안내됩니다."),
     ("애월 펜션 가능한가요?","애월읍 일대 펜션·풀빌라 객실 방문이 안내됩니다. 진입로 사전 확인이 필요한 경우가 있습니다."),
     ("도착 당일 늦은 시간 가능한가요?","공항 입도 후 시내 호텔 객실 방문이 자주 안내됩니다. 성수기는 사전 예약 권장."),
   ],"neighbors":["seogwipo"]},
  {"slug":"seogwipo","name":"서귀포시",
   "lede":"서귀포시는 중문관광단지·정방폭포·표선·성산 일대가 함께 있는 제주 남부 도시로, 휴양 리조트 객실 방문 비중이 제주에서 가장 큰 권역입니다.",
   "facts":[("행정동","17개"),("주요 시간대","주말·시즌"),("호텔/가정","리조트 비중↑↑"),("특이점","중문·성산")],
   "subs":["송산동","정방동","중앙동","천지동","효돈동","영천동","동홍동","서홍동","대륜동","대천동","중문동","예래동","대정읍","남원읍","성산읍","안덕면","표선면"],
   "character":"서귀포시는 중문관광단지(중문동·예래동)의 신라호텔 제주·롯데호텔 제주·하얏트 리젠시 제주·해비치 호텔앤리조트 등 5성 리조트 객실 방문이 휴양 일정과 맞물려 자주 안내됩니다. 안덕·표선·성산 일대 펜션·풀빌라(핀크스·웰컴호텔 제주) 객실 방문도 큰 비중을 차지합니다.",
   "pattern":"서귀포시는 여름·봄·가을 시즌과 주말 시간대 비중이 가장 큽니다.",
   "faqs":[
     ("신라호텔·롯데호텔 제주 가능한가요?","중문 일대 5성 리조트 객실 방문이 자주 안내됩니다."),
     ("핀크스·해비치 가능한가요?","안덕·표선 일대 풀빌라·리조트 객실 방문이 안내됩니다."),
     ("성수기 사전 예약 필요한가요?","여름·연말·황금연휴는 사전 예약이 강력 권장됩니다."),
   ],"neighbors":["jeju-si"]},
]

for _d in JEJU_DISTRICTS:
    _build_metro_district("jeju", "제주", _d, JEJU_DISTRICTS)


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
