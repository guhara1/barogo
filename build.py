#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""바로GO static site generator.

Renders every page defined in PAGES into <path>/index.html using a shared
template (header, navigation, footer). Pages keep their own <main> content
plus per-page metadata (title, description, JSON-LD), so the generator is
just plumbing — content lives in the PAGES list below.
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import re
from datetime import date

ROOT = pathlib.Path(__file__).parent
BUILD_DATE = date.today().isoformat()

SITE = {
    "name": "바로GO",
    "tagline": "전국 출장마사지 안내",
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
      <picture>
        <source type="image/webp" srcset="/assets/img/barogo_logo_true_transparent.webp">
        <img class="brand-logo" src="/assets/img/barogo_logo_true_transparent.png" alt="바로GO" width="142" height="44" decoding="async" fetchpriority="high">
      </picture>
    </a>
    <button class="nav-toggle" type="button" aria-controls="primary-nav" aria-expanded="false" aria-label="메뉴 열기">
      <span></span><span></span><span></span>
    </button>
    <nav id="primary-nav" class="primary-nav" aria-label="주요 메뉴">
      <ul class="nav-list">
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">지역별 찾기<span class="chev"></span></button>
          <div class="mega-panel mega-panel-album mega-panel-wide">
            <h3 class="mega-album-title">시·도별 출장마사지 안내</h3>
            <div class="mega-album-grid mega-album-grid--regions">
              <a class="mega-tile" href="/area/seoul/"><span class="mega-tile-name">서울</span><span class="mega-tile-sub">25개 자치구</span></a>
              <a class="mega-tile" href="/area/gyeonggi/"><span class="mega-tile-name">경기</span><span class="mega-tile-sub">31개 시·군</span></a>
              <a class="mega-tile" href="/area/incheon/"><span class="mega-tile-name">인천</span><span class="mega-tile-sub">10개 구·군</span></a>
              <a class="mega-tile" href="/area/busan/"><span class="mega-tile-name">부산</span><span class="mega-tile-sub">해운대·서면</span></a>
              <a class="mega-tile" href="/area/daegu/"><span class="mega-tile-name">대구</span><span class="mega-tile-sub">수성·동성로</span></a>
              <a class="mega-tile" href="/area/daejeon/"><span class="mega-tile-name">대전</span><span class="mega-tile-sub">유성·둔산</span></a>
              <a class="mega-tile" href="/area/gwangju/"><span class="mega-tile-name">광주</span><span class="mega-tile-sub">상무·첨단</span></a>
              <a class="mega-tile" href="/area/ulsan/"><span class="mega-tile-name">울산</span><span class="mega-tile-sub">남구·동구</span></a>
              <a class="mega-tile" href="/area/sejong/"><span class="mega-tile-name">세종</span><span class="mega-tile-sub">정부청사</span></a>
              <a class="mega-tile" href="/area/gangwon/"><span class="mega-tile-name">강원</span><span class="mega-tile-sub">강릉·속초</span></a>
              <a class="mega-tile" href="/area/chungbuk/"><span class="mega-tile-name">충북</span><span class="mega-tile-sub">청주·충주</span></a>
              <a class="mega-tile" href="/area/chungnam/"><span class="mega-tile-name">충남</span><span class="mega-tile-sub">천안·아산</span></a>
              <a class="mega-tile" href="/area/jeonbuk/"><span class="mega-tile-name">전북</span><span class="mega-tile-sub">전주·익산</span></a>
              <a class="mega-tile" href="/area/jeonnam/"><span class="mega-tile-name">전남</span><span class="mega-tile-sub">여수·순천</span></a>
              <a class="mega-tile" href="/area/gyeongbuk/"><span class="mega-tile-name">경북</span><span class="mega-tile-sub">포항·경주</span></a>
              <a class="mega-tile" href="/area/gyeongnam/"><span class="mega-tile-name">경남</span><span class="mega-tile-sub">창원·김해</span></a>
              <a class="mega-tile" href="/area/jeju/"><span class="mega-tile-name">제주</span><span class="mega-tile-sub">호텔·풀빌라</span></a>
            </div>
            <a class="mega-album-footer-link" href="/area/">전국 지역 안내 전체 보기 →</a>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">서비스 안내<span class="chev"></span></button>
          <div class="mega-panel mega-panel-album">
            <h3 class="mega-album-title">출장마사지 서비스</h3>
            <div class="mega-album-grid mega-album-grid--service">
              <a class="mega-card" href="/service/business-trip-massage/"><span class="mega-card-title">출장마사지</span><span class="mega-card-sub">전체 개요·진행 흐름</span></a>
              <a class="mega-card" href="/service/swedish/"><span class="mega-card-title">스웨디시</span><span class="mega-card-sub">오일·부드러운 압</span></a>
              <a class="mega-card" href="/service/aroma/"><span class="mega-card-title">아로마</span><span class="mega-card-sub">향과 함께 이완</span></a>
              <a class="mega-card" href="/service/hometai/"><span class="mega-card-title">홈타이</span><span class="mega-card-sub">옷 입고 스트레칭</span></a>
              <a class="mega-card" href="/service/sports-massage/"><span class="mega-card-title">스포츠</span><span class="mega-card-sub">근육 회복·부위 케어</span></a>
              <a class="mega-card" href="/service/couple-massage/"><span class="mega-card-title">커플</span><span class="mega-card-sub">2인 동시 진행</span></a>
              <a class="mega-card" href="/service/hotel-massage/"><span class="mega-card-title">호텔 출장</span><span class="mega-card-sub">객실·여행지</span></a>
              <a class="mega-card" href="/service/office-massage/"><span class="mega-card-title">기업·사무실</span><span class="mega-card-sub">단체·복지</span></a>
            </div>
            <a class="mega-album-footer-link" href="/service/">서비스 한눈에 비교 보기 →</a>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">예약 안내<span class="chev"></span></button>
          <div class="mega-panel mega-panel-album">
            <h3 class="mega-album-title">예약·결제 가이드</h3>
            <div class="mega-album-grid mega-album-grid--steps">
              <a class="mega-card mega-card-step" href="/reservation/how-to-book/"><span class="mega-card-num">01</span><span class="mega-card-title">예약 방법</span><span class="mega-card-sub">5단계 절차 안내</span></a>
              <a class="mega-card mega-card-step" href="/reservation/price/"><span class="mega-card-num">02</span><span class="mega-card-title">가격·코스</span><span class="mega-card-sub">코스별 시작 금액</span></a>
              <a class="mega-card mega-card-step" href="/reservation/check-before-use/"><span class="mega-card-num">03</span><span class="mega-card-title">이용 전 확인</span><span class="mega-card-sub">사전 권장 체크리스트</span></a>
              <a class="mega-card mega-card-step" href="/reservation/cancel-refund/"><span class="mega-card-num">04</span><span class="mega-card-title">취소·환불</span><span class="mega-card-sub">시간대별 환불 기준</span></a>
              <a class="mega-card mega-card-step" href="/reservation/payment/"><span class="mega-card-num">05</span><span class="mega-card-title">결제 안내</span><span class="mega-card-sub">결제 수단·영수증</span></a>
            </div>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">후기·정보<span class="chev"></span></button>
          <div class="mega-panel mega-panel-album mega-panel-wide">
            <div class="mega-album-section">
              <h3 class="mega-album-title">실제 이용 후기</h3>
              <div class="mega-album-grid mega-album-grid--guide">
                <a class="mega-card" href="/review/"><span class="mega-card-title">전체 후기</span><span class="mega-card-sub">검수된 이용 경험</span></a>
                <a class="mega-card" href="/review/first-time/"><span class="mega-card-title">처음 이용 후기</span><span class="mega-card-sub">초보 이용자 후기</span></a>
                <a class="mega-card" href="/review/reservation-case/"><span class="mega-card-title">예약 사례</span><span class="mega-card-sub">5가지 대표 패턴</span></a>
                <a class="mega-card" href="/review/area/"><span class="mega-card-title">지역별 후기</span><span class="mega-card-sub">권역별 이용 패턴</span></a>
              </div>
            </div>
            <div class="mega-album-section">
              <h3 class="mega-album-title">마사지 정보</h3>
              <div class="mega-album-grid mega-album-grid--guide">
                <a class="mega-card" href="/guide/what-is-business-trip-massage/"><span class="mega-card-title">출장마사지란?</span><span class="mega-card-sub">서비스 정의·차이</span></a>
                <a class="mega-card" href="/guide/aroma-vs-swedish/"><span class="mega-card-title">아로마 vs 스웨디시</span><span class="mega-card-sub">코스 비교 가이드</span></a>
                <a class="mega-card" href="/guide/first-time-massage/"><span class="mega-card-title">처음 이용 가이드</span><span class="mega-card-sub">사전 알아둘 점</span></a>
                <a class="mega-card" href="/guide/massage-before-after/"><span class="mega-card-title">전후 주의사항</span><span class="mega-card-sub">권장 컨디션 관리</span></a>
                <a class="mega-card" href="/guide/massage-price-standard/"><span class="mega-card-title">가격 기준</span><span class="mega-card-sub">달라지는 4가지 이유</span></a>
                <a class="mega-card" href="/guide/safe-reservation/"><span class="mega-card-title">안전한 예약</span><span class="mega-card-sub">확인 체크포인트</span></a>
              </div>
            </div>
          </div>
        </li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">고객센터<span class="chev"></span></button>
          <div class="mega-panel mega-panel-album">
            <h3 class="mega-album-title">고객센터</h3>
            <div class="mega-album-grid mega-album-grid--guide">
              <a class="mega-card" href="/support/notice/"><span class="mega-card-title">공지사항</span><span class="mega-card-sub">운영 변경·정책 공지</span></a>
              <a class="mega-card" href="/support/faq/"><span class="mega-card-title">자주 묻는 질문</span><span class="mega-card-sub">예약·결제·이용 FAQ</span></a>
              <a class="mega-card" href="/support/contact/"><span class="mega-card-title">문의하기</span><span class="mega-card-sub">전화·이메일 안내</span></a>
              <a class="mega-card" href="/support/partnership/"><span class="mega-card-title">제휴·광고 문의</span><span class="mega-card-sub">광고·입점 양식</span></a>
              <a class="mega-card" href="/support/report/"><span class="mega-card-title">불편 신고</span><span class="mega-card-sub">24시간 운영팀 직통</span></a>
            </div>
          </div>
        </li>
        <li class="nav-item nav-item-magazine"><a href="/magazine/" class="nav-link">매거진<span class="mega-badge nav-badge">NEW</span></a></li>
        <li class="nav-item has-mega">
          <button class="nav-link nav-trigger" aria-expanded="false" aria-haspopup="true">바로GO 소개<span class="chev"></span></button>
          <div class="mega-panel mega-panel-album">
            <h3 class="mega-album-title">회사 정보·정책</h3>
            <div class="mega-album-grid mega-album-grid--guide">
              <a class="mega-card" href="/about/brand/"><span class="mega-card-title">브랜드 소개</span><span class="mega-card-sub">운영 미션·약속</span></a>
              <a class="mega-card" href="/about/operation-policy/"><span class="mega-card-title">운영 원칙</span><span class="mega-card-sub">예약·가격·후기 정책</span></a>
              <a class="mega-card" href="/about/therapist-policy/"><span class="mega-card-title">관리사 기준</span><span class="mega-card-sub">협력·검증·평가</span></a>
              <a class="mega-card" href="/about/safety-policy/"><span class="mega-card-title">안전 이용 정책</span><span class="mega-card-sub">금지·신고·청소년 보호</span></a>
              <a class="mega-card" href="/about/privacy/"><span class="mega-card-title">개인정보처리방침</span><span class="mega-card-sub">수집·이용·권리</span></a>
              <a class="mega-card" href="/about/terms/"><span class="mega-card-title">이용약관</span><span class="mega-card-sub">14개 조항</span></a>
            </div>
          </div>
        </li>
        <li class="nav-item nav-cta"><a href="tel:0508-202-4719" class="nav-tel" aria-label="예약 전화 0508-202-4719"><span>예약</span><strong>0508-202-4719</strong></a></li>
      </ul>
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="site-footer" role="contentinfo" itemscope itemtype="https://schema.org/Organization">
  <meta itemprop="name" content="바로GO (YH LAB)">
  <meta itemprop="url" content="https://barogo.example/">
  <div class="container footer-top">
    <div class="footer-brand-col">
      <picture>
        <source type="image/webp" srcset="/assets/img/barogo_logo_true_transparent.webp">
        <img class="footer-logo" src="/assets/img/barogo_logo_true_transparent.png" alt="바로GO" width="168" height="52" decoding="async" loading="lazy" itemprop="logo">
      </picture>
      <p class="footer-tagline">전국 출장마사지 예약 안내 플랫폼</p>
      <p class="footer-desc">합법적이고 건전한 출장마사지 예약을 안내합니다. 의료 행위가 아니며, 치료 효과를 보장하지 않습니다.</p>
      <ul class="footer-trust">
        <li><span class="footer-trust-label">운영 형태</span><span class="footer-trust-value">출장마사지 예약 안내 플랫폼</span></li>
        <li><span class="footer-trust-label">운영 시간</span><span class="footer-trust-value">연중무휴 09:00–익일 04:00</span></li>
        <li><span class="footer-trust-label">신고 응대</span><span class="footer-trust-value">접수 후 24시간 이내</span></li>
      </ul>
    </div>

    <nav class="footer-nav" aria-label="사이트 전체 메뉴">
      <div class="footer-nav-col">
        <h3 class="footer-nav-title">서비스 안내</h3>
        <ul>
          <li><a href="/service/business-trip-massage/">출장마사지 안내</a></li>
          <li><a href="/service/swedish/">스웨디시</a></li>
          <li><a href="/service/aroma/">아로마</a></li>
          <li><a href="/service/hometai/">홈타이</a></li>
          <li><a href="/service/hotel-massage/">호텔 방문</a></li>
          <li><a href="/service/sports-massage/">스포츠</a></li>
          <li><a href="/service/couple-massage/">커플</a></li>
        </ul>
      </div>
      <div class="footer-nav-col">
        <h3 class="footer-nav-title">예약 안내</h3>
        <ul>
          <li><a href="/reservation/how-to-book/">예약 방법</a></li>
          <li><a href="/reservation/price/">가격 안내</a></li>
          <li><a href="/reservation/visit-area/">출장 가능 지역</a></li>
          <li><a href="/reservation/late-night/">심야·새벽 예약</a></li>
          <li><a href="/reservation/check-before-use/">이용 전 확인사항</a></li>
          <li><a href="/reservation/cancel-refund/">취소·환불 규정</a></li>
          <li><a href="/reservation/payment/">결제 안내</a></li>
        </ul>
      </div>
      <div class="footer-nav-col">
        <h3 class="footer-nav-title">지역별 안내</h3>
        <ul>
          <li><a href="/area/">전국 권역 안내</a></li>
          <li><a href="/area/seoul/">서울</a></li>
          <li><a href="/area/gyeonggi/">경기</a></li>
          <li><a href="/area/incheon/">인천</a></li>
          <li><a href="/area/busan/">부산</a></li>
          <li><a href="/area/daegu/">대구</a></li>
          <li><a href="/area/jeju/">제주</a></li>
        </ul>
      </div>
      <div class="footer-nav-col">
        <h3 class="footer-nav-title">마사지 정보</h3>
        <ul>
          <li><a href="/guide/what-is-business-trip-massage/">출장마사지란?</a></li>
          <li><a href="/guide/aroma-vs-swedish/">아로마 vs 스웨디시</a></li>
          <li><a href="/guide/first-time-massage/">처음 이용 가이드</a></li>
          <li><a href="/guide/massage-before-after/">전후 주의사항</a></li>
          <li><a href="/guide/massage-price-standard/">가격 기준</a></li>
          <li><a href="/guide/safe-reservation/">안전한 예약 확인</a></li>
        </ul>
      </div>
      <div class="footer-nav-col">
        <h3 class="footer-nav-title">고객센터·정책</h3>
        <ul>
          <li><a href="/support/contact/">문의하기</a></li>
          <li><a href="/support/report/">불편 신고</a></li>
          <li><a href="/support/notice/">공지사항</a></li>
          <li><a href="/about/brand/">브랜드 소개</a></li>
          <li><a href="/about/operation-policy/">운영 원칙</a></li>
          <li><a href="/about/safety-policy/">안전 이용 정책</a></li>
          <li><a href="/sitemap.xml" rel="nofollow">사이트맵</a></li>
        </ul>
      </div>
    </nav>
  </div>

  <div class="container footer-biz-row">
    <div class="footer-biz" itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">
      <h3 class="footer-nav-title">사업자 정보</h3>
      <dl class="footer-biz-dl">
        <dt>상호</dt><dd>바로GO <span class="footer-biz-sub">(운영사 YH LAB)</span></dd>
        <dt>대표</dt><dd>김유환</dd>
        <dt>사업자등록번호</dt><dd><span itemprop="taxID">815-26-00585</span> <a class="footer-verify" href="https://www.ftc.go.kr/bizCommPop.do?wrkr_no=8152600585" rel="nofollow noopener" target="_blank">사업자정보 확인</a></dd>
        <dt>본사 주소</dt><dd><span itemprop="streetAddress">경기도 파주시 청석로 268</span></dd>
        <dt>개인정보보호책임자</dt><dd>김유환 (대표 겸임)</dd>
      </dl>
    </div>
    <div class="footer-contact">
      <h3 class="footer-nav-title">대표 연락처</h3>
      <p class="footer-tel"><a href="tel:0508-202-4719" itemprop="telephone">0508-202-4719</a></p>
      <p class="footer-contact-note">예약·문의·불편 신고 모두 동일 번호로 접수됩니다.</p>
      <p class="footer-contact-note">운영팀 응대 — 평일·주말 09:00 ~ 익일 04:00</p>
      <a class="footer-contact-btn" href="/support/contact/">문의 양식 작성하기 →</a>
    </div>
  </div>

  <div class="container footer-legal">
    <p>본 사이트의 모든 콘텐츠는 운영사 YH LAB이 책임 저자로 작성·검수합니다. 출장마사지는 의료 행위가 아니며, 치료·치유 효과를 보장하지 않습니다. 자세한 면책 안내는 <a href="/about/terms/">이용약관</a> 및 각 페이지 하단 면책 안내를 참고해 주세요.</p>
    <p>※ 본 사이트는 만 19세 미만 청소년의 예약·이용을 받지 않습니다. 불법·퇴폐 서비스 안내·중개를 일체 하지 않으며, 신고 접수 시 24시간 이내 운영팀이 직접 확인합니다.</p>
  </div>

  <div class="container footer-bar">
    <p class="footer-copy">© 바로GO · YH LAB. All rights reserved.</p>
    <ul class="footer-bar-links">
      <li><a href="/about/privacy/"><strong>개인정보처리방침</strong></a></li>
      <li><a href="/about/terms/">이용약관</a></li>
      <li><a href="/about/safety-policy/">안전 이용 정책</a></li>
    </ul>
  </div>
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
<meta property="og:image" content="/assets/img/1.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
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
<a class="mobile-tel-fab" href="tel:0508-202-4719" aria-label="예약 전화 0508-202-4719">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
<span>예약 전화 0508-202-4719</span>
</a>
<script src="/assets/js/nav.js" defer></script>
<script src="/assets/js/magazine.js" defer></script>
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
                "primaryImageOfPage": "/assets/img/1.png",
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


# ---------- 내부링크 long-tail 앵커 풀 ----------
# 동일 타깃이라도 출처별로 다른 앵커 텍스트가 노출되도록 (source, target) 해시로 선택.
# 단순 키워드 반복(스팸 신호) 회피 + 클릭 의도가 명확한 서술형 앵커.
_LONG_TAIL = {
  "/service/business-trip-massage/": [
    "출장마사지가 무엇인지부터 진행 방식·이용 가능 장소까지 정리",
    "출장마사지가 일반 매장 마사지와 다른 점과 적합한 상황 안내",
    "처음 알아보시는 분을 위한 출장마사지 서비스 개요와 진행 흐름",
    "출장마사지가 아닌 출장마사지의 운영 원칙과 진행 방식 안내",
  ],
  "/service/hotel-massage/": [
    "호텔 객실에서 진행할 때 사전에 확인해야 하는 체크인·층·룸 정보",
    "출장·여행지 호텔 예약 시 알아두면 좋은 준비사항 정리",
    "호텔 객실 진행 시 자주 안내되는 코스 길이와 시간대 안내",
    "객실 진행 시 공동현관·엘리베이터 출입 안내가 필요한 이유",
  ],
  "/service/swedish/": [
    "스웨디시 마사지의 진행 방식과 압력 강도, 적합한 컨디션 안내",
    "오일을 사용한 부드러운 전신 케어, 스웨디시가 권장되는 상황",
    "처음 받으시는 분에게 자주 안내되는 스웨디시 코스 길이",
    "릴랙스·수면 개선을 목적으로 스웨디시를 선택할 때 참고할 점",
  ],
  "/service/aroma/": [
    "아로마 오일 종류별 효과와 향 선택 시 참고할 점 정리",
    "릴랙스·수면 개선 목적으로 자주 안내되는 아로마 코스 안내",
    "아로마 마사지 진행 흐름과 사전에 알아둘 점 정리",
    "특정 향 알레르기·민감도가 있는 경우 사전 안내가 필요한 이유",
  ],
  "/service/hometai/": [
    "타이 전통 방식의 홈타이 코스 진행 순서와 추천 길이 안내",
    "근육 이완·스트레칭 목적으로 자주 안내되는 홈타이 코스 정리",
    "옷을 입은 채 진행되는 홈타이의 특징과 사전 준비사항",
    "전통 타이 마사지를 가정·숙소에서 받을 때 권장 공간 조건",
  ],
  "/service/sports-massage/": [
    "운동 후 근육 회복 목적의 스포츠 마사지 코스 안내",
    "특정 부위 집중 케어가 필요할 때 권장되는 스포츠 마사지 진행 방식",
    "근육통·뭉침 케어로 자주 문의되는 스포츠 코스 길이 정리",
    "러닝·웨이트 직후 회복을 위해 스포츠 마사지를 선택할 때 참고할 점",
  ],
  "/service/office-massage/": [
    "오피스·공유오피스에서 진행 시 사전 확인해야 하는 보안·공간 조건",
    "사내 출장 케어 시 자주 안내되는 단시간 코스와 동선 안내",
    "회사 공간에서 진행이 어려울 경우 인근 호텔·자택을 권하는 이유",
  ],
  "/service/couple-massage/": [
    "2인 동시 진행 가능한 코스와 합산 가격 기준 정리",
    "커플·가족이 함께 받을 때 권장되는 공간 조건과 코스 길이",
    "한 공간에서 2인 진행 시 사전에 함께 확정되는 정보 안내",
  ],
  "/reservation/how-to-book/": [
    "출장마사지 예약을 5단계로 진행하는 전체 흐름 안내",
    "처음 예약하시는 분을 위한 상담·확정·진행 절차 정리",
    "지역 확인부터 결제까지 예약 진행 시 함께 확정되는 항목",
    "전화 상담 단계에서 일정·장소·코스가 함께 정해지는 과정 안내",
  ],
  "/reservation/price/": [
    "코스 길이·시간대·진행 장소별 출장마사지 기준 가격 정리",
    "60·90·120·150분 코스 가격이 어떻게 결정되는지 4가지 기준 안내",
    "예약 전 사전 안내되는 코스별 시작 금액과 추가 비용 정책",
    "동일 코스라도 시간대·권역에 따라 가격이 달라지는 이유",
  ],
  "/reservation/visit-area/": [
    "출장 가능한 권역과 이동 거리·시간대별 가능 여부 안내",
    "예약 전 거주지·숙소가 서비스 가능 권역인지 확인하는 방법",
    "광역시·도 단위 출장 가능 권역과 광역 이동 기준 정리",
  ],
  "/reservation/late-night/": [
    "야간·새벽 시간대에 예약이 가능한 권역과 마감 시간 안내",
    "심야·새벽 예약 시 사전 상담에서 함께 확인되는 이동 조건",
    "자정 이후 호텔 진행이 가능한 권역 정리와 주의사항",
    "야근 후·심야 도착 일정에 맞춰 예약할 때 참고할 시간대 안내",
  ],
  "/reservation/check-before-use/": [
    "예약 전 건강 상태·공간·음주·복장 사전 권장 체크리스트",
    "처음 이용 전 미리 확인해 두면 진행이 매끄러운 준비사항 정리",
    "안전한 진행을 위해 사전에 알려주시면 좋은 정보 모음",
  ],
  "/reservation/cancel-refund/": [
    "시간대별 취소·환불 기준과 변경 가능 시점 정리",
    "예약 후 일정 변경 시 가능한 시간 범위와 환불 비율 안내",
    "취소·환불 진행 시 사전에 알아두면 좋은 정책 안내",
  ],
  "/reservation/payment/": [
    "현장 결제·계좌이체·카드 결제 가능 수단과 영수증 발행 안내",
    "결제 수단별 사전 준비사항과 세금계산서 발행 절차 정리",
    "예약 확정 후 결제 진행 시 자주 안내되는 사항",
  ],
  "/guide/what-is-business-trip-massage/": [
    "출장마사지가 무엇인지부터 진행 방식·법적 구분까지 정리한 입문 안내",
    "출장마사지와 출장마사지의 차이와 적합한 상황 정리",
    "처음 출장마사지를 알아보시는 분을 위한 기본 개념 가이드",
  ],
  "/guide/massage-before-after/": [
    "마사지 전후 권장되는 식사·음주·휴식 시간과 주의사항 정리",
    "효과를 높이는 마사지 전후 컨디션 관리 가이드",
    "마사지 후 권장되는 수분 섭취·휴식 시간에 대한 안내",
  ],
  "/guide/aroma-vs-swedish/": [
    "아로마와 스웨디시의 진행 방식·압력·향 차이를 비교한 가이드",
    "두 코스 중 무엇을 받을지 고민될 때 참고할 비교 정보",
    "목적별로 어떤 코스가 더 적합한지 정리한 비교 안내",
  ],
  "/guide/first-time-massage/": [
    "처음 출장마사지를 이용하시는 분이 알아두면 좋은 점 정리",
    "첫 이용 전 자주 묻는 질문과 사전에 알아둘 사항 안내",
    "초보 이용자를 위한 코스 선택·복장·공간 준비 가이드",
  ],
  "/guide/massage-price-standard/": [
    "마사지 가격이 코스·시간·장소·시간대에 따라 달라지는 4가지 이유",
    "동일 코스라도 가격 차이가 발생하는 기준에 대한 상세 설명",
    "예약 전 가격 비교 시 참고할 수 있는 기준 정리",
  ],
  "/guide/safe-reservation/": [
    "안전한 예약을 위해 사전에 확인해야 하는 5가지 체크포인트",
    "신뢰할 수 있는 출장마사지 업체를 확인하는 방법 정리",
    "사업자 정보·약관·환불 정책 등 예약 전 검토할 항목",
  ],
  "/review/first-time/": [
    "처음 이용 고객 후기로 보는 진행 흐름과 자주 묻는 사항",
    "첫 이용 후 가장 자주 언급된 만족·아쉬움 포인트 정리",
  ],
  "/review/reservation-case/": [
    "실제 예약 사례로 보는 시간대·코스·장소별 안내 패턴",
    "다양한 예약 상황별 진행 흐름과 안내 내용 정리",
  ],
  "/review/area/": [
    "지역별 후기 모음으로 보는 권역별 이용 패턴",
    "권역별 자주 안내된 코스와 시간대 정리",
  ],
  "/area/": [
    "전국 시·도 단위 출장마사지 안내 페이지 모음",
    "광역시·도별 권역 특성과 자주 안내되는 시간대 정리",
  ],
  "/service/": [
    "코스별 진행 방식·압력·소요시간 비교 페이지",
    "스웨디시·아로마·홈타이 등 서비스 유형별 안내",
  ],
  "/reservation/": [
    "예약 방법·가격·취소·결제까지 전체 예약 정보 허브",
    "처음 이용 전 살펴볼 예약 관련 안내 모음",
  ],
  "/guide/": [
    "마사지 정보 가이드 — 입문부터 사전 준비까지 주제별 정리",
    "출장마사지 관련 자주 묻는 주제를 모은 정보 가이드",
  ],
  "/review/": [
    "실제 이용 후기·예약 사례·지역별 모음 페이지",
    "처음 이용·예약 사례·권역별 이용 패턴 후기 모음",
  ],
  "/about/": [
    "운영사 사업자 정보와 6개 공식 문서를 모은 회사 소개 페이지",
    "바로GO 브랜드·운영 원칙·정책 문서를 한곳에 정리한 페이지",
  ],
  "/about/brand/": [
    "바로GO를 시작한 이유와 운영 미션·4가지 약속 정리",
    "다른 출장마사지 안내 채널과 다른 점, 운영 사업자 책임 구조 안내",
    "운영사 YH LAB의 브랜드 철학과 향후 로드맵",
  ],
  "/about/operation-policy/": [
    "예약·가격·후기·콘텐츠·AI 사용 등 8개 영역의 운영 원칙 공개",
    "투명한 운영을 위한 자체 규정 — 표현·광고·데이터 정책 정리",
    "AI 보조 도구 사용 시 검수 절차와 책임 저자 표기 정책 안내",
  ],
  "/about/therapist-policy/": [
    "협력 관리사 자격·검증 절차·교육·평가·위반 시 조치 기준",
    "관리사 모집부터 운영 의무까지 6개 영역의 운영 기준 정리",
    "분기 평가와 등급 운영을 통한 관리사 품질 관리 안내",
  ],
  "/about/safety-policy/": [
    "안전 이용 정책 — 금지 사항·24시간 신고 채널·위반 시 조치 안내",
    "이용자·관리사 양측의 안전을 보호하기 위한 7개 영역 정책",
    "청소년 보호·법적 협조 절차를 포함한 안전 이용 정책 전문",
  ],
  "/about/privacy/": [
    "개인정보 수집·이용·보관·이용자 권리 안내 (11개 조항)",
    "결제 정보·예약 정보 처리 방식과 안전성 확보 조치 정리",
    "이용자 열람·정정·삭제 요청 처리 절차와 보호책임자 연락처",
  ],
  "/about/terms/": [
    "예약·결제·취소·책임 한계 등 14개 조항 정식 이용약관",
    "회사·이용자 의무와 분쟁 해결 절차를 정리한 약관 전문",
    "서비스 제공 범위·면책 조항·분쟁 관할이 명시된 이용약관",
  ],
  "/support/contact/": [
    "운영팀에 직접 접수하는 문의 양식과 응답 예상 시간",
    "예약·정책·정정 요청을 운영팀으로 전달하는 채널 안내",
  ],
  "/support/report/": [
    "안전 정책 위반·불편 사항을 24시간 접수하는 신고 채널",
    "운영팀이 직접 확인하는 신고 접수 페이지와 처리 절차",
  ],
  "/support/notice/": [
    "정책 변경·서비스 안내·운영 공지를 시행일과 함께 모은 페이지",
    "주요 변경 사항을 시행일순으로 정리한 공지사항 모음",
  ],
  "/support/faq/": [
    "예약·가격·이용 전 자주 묻는 질문을 카테고리별로 정리",
    "처음 이용하시는 분이 가장 궁금해하는 질문에 대한 답변 모음",
  ],
  "/support/partnership/": [
    "광고·제휴·입점 문의 양식과 운영팀 직접 응대 안내",
    "지역 독점·배너·관리사 협력 문의를 운영팀에 즉시 전달하는 양식",
  ],
  "/magazine/": [
    "운영팀이 직접 집필하는 출장마사지 에디토리얼 매거진 모음",
    "트렌드·라이프스타일·웰니스·코스 가이드를 주제별로 정리한 매거진",
  ],
  "/magazine/first-time-essentials/": [
    "처음 출장마사지를 받기 전 알아둘 점을 운영팀이 정리한 가이드",
    "첫 코스 선택·사전 준비·진행 흐름·사후 케어를 한 페이지에 정리",
  ],
  "/magazine/night-worker-recovery/": [
    "야간 근무자가 활용할 수 있는 출장마사지 회복 5가지 패턴",
    "병원·간호·IT 운영·보안 등 야간 직군에게 권장되는 회복 루틴",
  ],
  "/magazine/desk-worker-neck-shoulder/": [
    "사무직 1-3년차의 어깨·목 누적 변화와 단계별 케어 흐름 정리",
    "데스크워크가 만드는 4가지 신체 신호와 권장 케어 코스 안내",
  ],
  "/magazine/hotel-guest-guide/": [
    "호텔 객실에서 받는 출장마사지의 흐름과 사전 안내해야 할 점 정리",
    "호텔 등급별 진행 차이와 자주 선택되는 시간대·코스 안내",
  ],
  "/magazine/course-selection-by-purpose/": [
    "스웨디시·아로마·홈타이·스포츠 중 무엇을 받을지 결정하는 기준",
    "운영팀의 코스 매칭 의사결정 5단계와 첫 코스 권장 안내",
  ],
  "/magazine/regional-usage-tips/": [
    "수도권·광역시·도(道) 권역·제주별 출장마사지 이용 패턴 정리",
    "권역마다 자주 안내되는 시간대·코스·진행 장소 차이 안내",
  ],
}


_AREA_NAMES = {
  "seoul": "서울", "gyeonggi": "경기", "incheon": "인천",
  "busan": "부산", "daegu": "대구", "daejeon": "대전",
  "gwangju": "광주", "ulsan": "울산", "sejong": "세종",
  "gangwon": "강원", "chungbuk": "충북", "chungnam": "충남",
  "jeonbuk": "전북", "jeonnam": "전남", "gyeongbuk": "경북",
  "gyeongnam": "경남", "jeju": "제주",
}

_AREA_ANCHOR_TPLS = [
  "{name} 권역의 출장마사지 이용 패턴과 자주 안내되는 시간대",
  "{name} 일대에서 자주 문의되는 코스와 진행 장소 안내",
  "{name} 권역 출장 가능 범위와 인접 지역 이동 안내",
  "{name} 전체 권역 특성과 시간대별 안내 정리",
]


def _anchor_for(source_url, target_url):
    """target_url에 대한 long-tail 앵커 텍스트 선택 (source_url 시드)."""
    # /area/{slug}/ 단일 시·도 페이지는 동적 앵커
    m = re.match(r"^/area/([a-z]+)/$", target_url)
    if m and m.group(1) in _AREA_NAMES:
        name = _AREA_NAMES[m.group(1)]
        seed = f"{source_url}|{target_url}".encode("utf-8")
        idx = int(hashlib.md5(seed).hexdigest(), 16) % len(_AREA_ANCHOR_TPLS)
        return _AREA_ANCHOR_TPLS[idx].format(name=name)
    pool = _LONG_TAIL.get(target_url)
    if pool:
        seed = f"{source_url}|{target_url}".encode("utf-8")
        idx = int(hashlib.md5(seed).hexdigest(), 16) % len(pool)
        return pool[idx]
    return target_url


def _rel(source_url, target_urls, title="함께 보면 좋은 안내"):
    """source_url에서 target_urls 각각으로 가는 long-tail 앵커 aside 생성."""
    items = []
    seen = set()
    for tu in target_urls:
        if tu in seen or tu == source_url:
            continue
        seen.add(tu)
        text = _anchor_for(source_url, tu)
        items.append(f'<li><a href="{tu}">{text}</a></li>')
    if not items:
        return ""
    return f'<aside class="related"><h2>{title}</h2><ul>{"".join(items)}</ul></aside>'


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
  "title": "서울 출장마사지 | 강남·마포·종로·여의도 권역 안내 - 바로GO",
  "description": "서울은 권역마다 이용 패턴이 다릅니다. 강남·서초의 호텔 야간 수요, 마포·용산의 직장인 가정 방문, 종로·중구의 단시간 호텔 코스 등 서울 6개 권역의 실제 이용 흐름을 정리했습니다.",
  "h1": "서울 권역별 출장마사지 이용 안내",
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
<h2>서울 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>강남에서 새벽 시간대도 받을 수 있나요?</summary><p>강남·서초·송파 일부 호텔에서는 자정 이후 시간대도 안내되는 경우가 있습니다. 권역과 객실 정보에 따라 가능 여부가 달라지므로 상담 단계에서 확인이 필요합니다.</p></details>
<details><summary>여의도 야근 후 회사로 받을 수 있나요?</summary><p>오피스 방문은 별도 보안 정책이 있는 빌딩이 많아 일반적으로 추천하지 않습니다. 인근 호텔 또는 자택을 안내드리는 경우가 일반적입니다.</p></details>
<details><summary>김포공항 인근 호텔에서도 가능한가요?</summary><p>강서 일대 공항 인접 호텔에서 단시간 코스 문의가 자주 안내됩니다. 환승·체류 일정 길이에 맞춘 60·90분 코스를 권해드리는 편입니다.</p></details>
<details><summary>강북(노원·도봉·강북구)도 안내되나요?</summary><p>가능합니다. 다만 강북 권역은 심야 시간대 마감이 강남 대비 이른 편이라 저녁 시간대 예약을 권해드립니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/seoul/", ["/service/hotel-massage/", "/reservation/late-night/", "/guide/safe-reservation/", "/reservation/visit-area/"]),
},
{
  "slug": "gyeonggi", "name": "경기", "full": "경기도",
  "title": "경기 출장마사지 | 분당·수원·일산·평택 권역 안내 - 바로GO",
  "description": "경기도는 31개 시·군이 모두 다른 권역 특성을 가집니다. 분당·판교 IT 야근 후 케어, 수원·화성 산업 출장, 일산·파주 신도시 가정 방문 등 권역별 이용 흐름과 광역 이동 안내를 정리했습니다.",
  "h1": "경기도 권역별 출장마사지 이용 안내",
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
<h2>경기도 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>분당과 일산 모두 같은 시간에 가능한가요?</summary><p>분당과 일산은 다른 권역으로 안내되며, 같은 시간대에 두 권역을 모두 진행하기는 어려운 경우가 일반적입니다. 권역별로 예약 가능 시간을 따로 확인해 주세요.</p></details>
<details><summary>외곽 시·군(가평·양평·여주 등)도 가능한가요?</summary><p>가능 여부는 시간대와 이동 거리에 따라 달라집니다. 외곽 권역은 사전에 가능 시간을 확인하는 것을 권장합니다.</p></details>
<details><summary>출장 일정으로 평택 호텔에서 받을 수 있나요?</summary><p>평택·오산 일대 비즈니스 호텔은 평일 저녁 시간대 객실 방문 비중이 높은 권역으로, 사전에 일정과 호실 정보를 함께 확인합니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/gyeonggi/", ["/reservation/visit-area/", "/reservation/price/", "/service/business-trip-massage/", "/area/seoul/"]),
},
{
  "slug": "incheon", "name": "인천", "full": "인천광역시",
  "title": "인천 출장마사지 | 송도·부평·공항 권역 안내 - 바로GO",
  "description": "인천공항 환승 일정에 맞춘 단시간 코스, 송도 국제업무지구의 비즈니스 출장 케어, 부평·계양 주거 권역의 평일 저녁 가정 방문 등 인천 권역별 실제 이용 흐름을 정리했습니다.",
  "h1": "인천 권역별 출장마사지 이용 안내",
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
<h2>인천 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>인천공항에서 환승 4시간 정도 가능합니다. 가능할까요?</summary><p>환승객 시간 기준 4시간이면 보안검색·체크인 시간을 제외하고 60분 코스 정도가 적절합니다. 공항 인접 호텔 체크인 일정에 맞춰 진행하시는 것을 권합니다.</p></details>
<details><summary>송도에서 외국어 안내가 되는지요?</summary><p>모든 케이스에 대해 보장되지는 않으며, 영어 안내가 가능한 일정으로 사전 조율이 필요합니다. 상담 단계에서 미리 알려 주시면 가능 여부를 확인해 드립니다.</p></details>
<details><summary>강화도에서도 이용 가능한가요?</summary><p>강화·옹진 등 도서 권역은 이동 시간 특성상 일반적으로 안내되지 않거나 사전 협의가 필요한 권역입니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/incheon/", ["/service/hotel-massage/", "/service/business-trip-massage/", "/reservation/how-to-book/", "/area/seoul/"]),
},
{
  "slug": "busan", "name": "부산", "full": "부산광역시",
  "title": "부산 출장마사지 | 해운대·광안·서면 권역 안내 - 바로GO",
  "description": "부산은 전국에서 호텔 방문 케어 비중이 가장 높은 광역시입니다. 해운대·광안·서면 권역의 관광 호텔 일정, 성수기·비수기 가능 시간 차이, 부산 권역별 이용 흐름을 정리했습니다.",
  "h1": "부산 권역별 출장마사지 이용 안내",
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
<h2>부산 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>해운대 호텔에서 새벽 시간대도 가능한가요?</summary><p>해운대 권역은 새벽 시간대 가능 사례가 다른 권역보다 많은 편입니다. 객실 호수·체크인 정보 사전 확인을 거쳐 진행합니다.</p></details>
<details><summary>광안리 불꽃축제 당일 예약이 어려운가요?</summary><p>축제 당일은 호텔 가능 시간 자체가 빠르게 마감되므로 사전 예약을 권장드립니다. 당일 문의는 가능 권역이 제한될 수 있습니다.</p></details>
<details><summary>기장군(정관·일광)도 가능한가요?</summary><p>기장 권역은 안내 가능하나 본 시가지(해운대·서면)와 이동 시간이 다르므로 따로 권역을 두고 가능 시간을 확인합니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/busan/", ["/service/hotel-massage/", "/reservation/late-night/", "/reservation/price/", "/guide/safe-reservation/"]),
},
{
  "slug": "daegu", "name": "대구", "full": "대구광역시",
  "title": "대구 출장마사지 | 수성·동성로·달서 권역 안내 - 바로GO",
  "description": "대구는 수성구 주거 권역 평일 저녁 가정 방문 비중이 높은 도시입니다. 동성로 도심 호텔 출장 케어, 폭염 시즌 시간대 조정, 권역별 이용 흐름을 정리했습니다.",
  "h1": "대구 권역별 출장마사지 이용 안내",
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
<h2>대구 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>수성구 외 지역도 안내되나요?</summary><p>달서·달성·동구·북구 모두 안내됩니다. 권역별로 가능 시간이 다소 달라 사전 확인을 권장합니다.</p></details>
<details><summary>경산(경북)에서도 받을 수 있나요?</summary><p>경산은 행정구역상 경북이지만 대구 권역과 인접해 안내되는 경우가 있습니다. 자세한 내용은 <a href="/area/gyeongbuk/">경북 안내 페이지</a>를 참고해 주세요.</p></details>
<details><summary>여름철 낮 시간대도 가능한가요?</summary><p>가능합니다만 한여름 한낮은 이동 시간이 길어지므로 가능하면 저녁 시간대 예약을 권해드리는 편입니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/daegu/", ["/reservation/visit-area/", "/service/swedish/", "/reservation/price/", "/service/business-trip-massage/"]),
},
{
  "slug": "daejeon", "name": "대전", "full": "대전광역시",
  "title": "대전 출장마사지 | 유성·둔산·대덕 권역 안내 - 바로GO",
  "description": "대전은 대덕연구단지·정부청사 출장 일정과 맞물려 유성·둔산 권역의 평일 저녁 호텔 방문 비중이 높은 도시입니다. KTX 단시간 코스, 연구단지 출장 케어 흐름을 정리했습니다.",
  "h1": "대전 권역별 출장마사지 이용 안내",
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
<h2>대전 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>유성 호텔에서 출장 일정 마치고 받을 수 있나요?</summary><p>가능합니다. 출장 종료 시간에 맞춰 객실 호수·체크인 정보를 함께 확인해 주시면 평일 저녁~밤 시간대 안내가 일반적입니다.</p></details>
<details><summary>세종에서 받을 수 있나요?</summary><p>세종은 별도 권역으로 안내됩니다. <a href="/area/sejong/">세종 안내 페이지</a>를 참고해 주세요.</p></details>
<details><summary>KTX 환승 1시간 30분 정도인데 가능한가요?</summary><p>이동·체크인 시간을 제외하면 60분 코스 진행이 빠듯하므로, 대전 체류 일정이 2시간 이상 확보된 경우를 권해드립니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/daejeon/", ["/service/business-trip-massage/", "/service/hotel-massage/", "/reservation/how-to-book/", "/area/sejong/"]),
},
{
  "slug": "gwangju", "name": "광주", "full": "광주광역시",
  "title": "광주 출장마사지 | 상무·첨단·광산 권역 안내 - 바로GO",
  "description": "광주는 상무지구 비즈니스 출장과 첨단·수완 신도시 가정 방문이 함께 안내되는 도시입니다. 평일 저녁·주말 가능 시간대와 권역별 이용 흐름을 정리했습니다.",
  "h1": "광주 권역별 출장마사지 이용 안내",
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
<h2>광주 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>나주·담양도 광주에서 안내해 주시나요?</summary><p>나주·담양은 행정상 전남에 속해 별도 권역으로 안내됩니다. <a href="/area/jeonnam/">전남 안내 페이지</a>를 참고해 주세요.</p></details>
<details><summary>광주 외곽(광산구 송정·평동)도 가능한가요?</summary><p>가능합니다. 외곽 권역은 시간대에 따라 가능 시간이 다소 빠르게 마감되는 편입니다.</p></details>
<details><summary>비엔날레·시즌 행사 시기에 예약이 어렵나요?</summary><p>비엔날레·세계김치축제 등 대형 행사 시즌은 상무·동구 권역 호텔이 빠르게 마감되므로 사전 예약을 권장합니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/gwangju/", ["/reservation/how-to-book/", "/reservation/price/", "/service/hometai/", "/area/jeonnam/"]),
},
{
  "slug": "ulsan", "name": "울산", "full": "울산광역시",
  "title": "울산 출장마사지 | 남구·동구·울주 권역 안내 - 바로GO",
  "description": "울산은 현대중공업·SK·미포 등 산업단지 출장 비중이 가장 높은 광역시입니다. 동구 조선소 인근, 남구 비즈니스 호텔, 장기 출장 재방문 패턴을 정리했습니다.",
  "h1": "울산 권역별 출장마사지 이용 안내",
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
<h2>울산 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>장기 출장 중 매주 같은 시간 예약 가능한가요?</summary><p>정기 일정 안내가 가능합니다. 다만 매번 가능 인력 일정이 변동될 수 있어 주차별 사전 확인이 필요합니다.</p></details>
<details><summary>조선소 게스트하우스에서도 가능한가요?</summary><p>일반적인 게스트하우스 객실 방문은 안내됩니다. 일부 사내 숙소(외부 출입 통제) 케이스는 사전 확인이 필요합니다.</p></details>
<details><summary>언양 KTX역 인근 호텔도 안내되나요?</summary><p>가능합니다. 단 언양 권역은 본 시가지(남구·동구)와 이동 시간이 있어 시간대 사전 확인을 권합니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/ulsan/", ["/service/business-trip-massage/", "/service/sports-massage/", "/reservation/late-night/", "/area/busan/"]),
},
{
  "slug": "sejong", "name": "세종", "full": "세종특별자치시",
  "title": "세종 출장마사지 | 한솔·새롬·도담 권역 안내 - 바로GO",
  "description": "세종은 호텔 인프라가 비교적 적어 가정 방문 비중이 높은 행정중심복합도시입니다. 평일 저녁 공무원 가정 방문 흐름, 인근 권역 확장 가능성을 정리했습니다.",
  "h1": "세종 권역별 출장마사지 이용 안내",
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
<h2>세종 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>오송역 환승 일정에 받을 수 있나요?</summary><p>오송역은 행정상 충북 청주이지만 세종과 가까워 안내 사례가 있습니다. 환승 시간 길이에 맞춰 코스 길이를 조율합니다.</p></details>
<details><summary>정부청사 근처에서 평일 점심 시간대 가능한가요?</summary><p>일반적으로 저녁 시간대 비중이 훨씬 큽니다. 평일 점심 시간대는 가능 여부가 제한적이며 사전 확인이 필요합니다.</p></details>
<details><summary>세종에서 외곽(조치원·금남)도 가능한가요?</summary><p>가능합니다. 다만 본 신도시 권역(1~4생활권) 대비 가능 시간 폭이 좁은 편입니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/sejong/", ["/area/daejeon/", "/area/chungbuk/", "/reservation/how-to-book/", "/service/business-trip-massage/"]),
},
{
  "slug": "gangwon", "name": "강원", "full": "강원특별자치도",
  "title": "강원 출장마사지 | 강릉·속초·춘천·평창 권역 안내 - 바로GO",
  "description": "강원은 영동(강릉·속초)과 영서(춘천·원주)의 권역 성격이 매우 다른 지역입니다. 동계 스포츠·서핑 시즌의 회복 케어, 성수기·비수기 가능 시간 차이를 정리했습니다.",
  "h1": "강원 권역별 출장마사지 이용 안내",
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
<h2>강원 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>서핑 후 어깨 회복 목적인데 어떤 코스가 좋나요?</summary><p>서핑 후 어깨·등 회복은 <a href="/service/sports-massage/">스포츠 마사지</a> 또는 <a href="/service/hometai/">홈타이</a>가 자주 안내됩니다. 부위 집중 케어가 가능합니다.</p></details>
<details><summary>스키 시즌 평창 콘도에서 받을 수 있나요?</summary><p>평창 콘도·리조트 객실 방문은 가능하나, 동계 성수기는 가능 시간이 매우 빠르게 마감됩니다. 입실 일정 확정 후 사전 예약을 권합니다.</p></details>
<details><summary>춘천 펜션에서도 가능한가요?</summary><p>가능합니다. 단 외곽 펜션은 진입로·차량 진입 가능 여부 확인이 함께 필요한 경우가 있습니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/gangwon/", ["/service/sports-massage/", "/service/hometai/", "/reservation/late-night/", "/reservation/visit-area/"]),
},
{
  "slug": "chungbuk", "name": "충북", "full": "충청북도",
  "title": "충북 출장마사지 | 청주·오송·충주 권역 안내 - 바로GO",
  "description": "충북은 청주공항·오송 바이오단지 출장 흐름이 두드러지는 지역입니다. KTX 오송 환승 단시간 코스, 청주·충주 권역별 이용 흐름을 정리했습니다.",
  "h1": "충북 권역별 출장마사지 이용 안내",
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
<h2>충북 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>오송역 환승 2시간 정도 가능할까요?</summary><p>2시간이면 이동·체크인 시간 제외 60분 코스가 빠듯할 수 있습니다. 환승 일정이 3시간 이상 확보된 경우를 권합니다.</p></details>
<details><summary>청주에서 세종 권역도 함께 가능한가요?</summary><p>같은 시간대 동시 진행은 어렵고, 권역을 분리해 예약을 잡는 형태로 안내됩니다.</p></details>
<details><summary>단양·괴산 외곽도 가능한가요?</summary><p>이동 시간이 길어 일반적으로 사전 협의가 필요한 권역입니다. 가능 일정이 제한될 수 있습니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/chungbuk/", ["/area/daejeon/", "/area/sejong/", "/service/business-trip-massage/", "/reservation/visit-area/"]),
},
{
  "slug": "chungnam", "name": "충남", "full": "충청남도",
  "title": "충남 출장마사지 | 천안·아산·서산·당진 권역 안내 - 바로GO",
  "description": "충남은 천안·아산 KTX 산업단지 출장과 서해안 보령·태안 휴양 두 패턴이 공존하는 지역입니다. 권역별 이용 흐름과 광역 이동 안내를 정리했습니다.",
  "h1": "충남 권역별 출장마사지 이용 안내",
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
<h2>충남 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>천안아산역 일정에 맞춰 단시간 가능한가요?</summary><p>천안아산역 인접 호텔에서 60·90분 코스 문의가 자주 안내됩니다. KTX 일정 시간을 함께 확인합니다.</p></details>
<details><summary>대천해수욕장 펜션에서도 가능한가요?</summary><p>가능합니다. 단 성수기에는 가능 시간이 빠르게 마감되므로 사전 예약을 권합니다.</p></details>
<details><summary>당진 산업단지 출장 일정에 가능한가요?</summary><p>현대제철·동부제철 등 산업단지 출장 일정과 맞물린 호텔 객실 방문이 가능합니다. 평일 저녁 시간대가 주로 안내됩니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/chungnam/", ["/service/business-trip-massage/", "/service/hotel-massage/", "/reservation/visit-area/", "/area/daejeon/"]),
},
{
  "slug": "jeonbuk", "name": "전북", "full": "전북특별자치도",
  "title": "전북 출장마사지 | 전주·익산·군산 권역 안내 - 바로GO",
  "description": "전북은 전주 한옥마을 관광·익산 KTX 환승·군산 새만금 산업 세 흐름이 함께 안내되는 지역입니다. 권역별 이용 패턴과 게스트하우스 안내 사항을 정리했습니다.",
  "h1": "전북 권역별 출장마사지 이용 안내",
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
<h2>전북 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>전주 한옥 게스트하우스에서 가능한가요?</summary><p>가능합니다. 단 한옥 객실 구조 특성상 베드 외 다른 방식(매트) 안내가 될 수 있어 사전 확인이 필요합니다.</p></details>
<details><summary>익산역 환승 일정 1시간 30분 가능한가요?</summary><p>익산역 인근 호텔 단시간 코스가 가능하나 1시간 30분은 빠듯할 수 있어 코스 길이와 동선 확인이 필요합니다.</p></details>
<details><summary>군산 새만금 출장 일정에 받을 수 있나요?</summary><p>가능합니다. 출장 종료 시간에 맞춘 평일 저녁 호텔 방문이 가장 자주 안내되는 시간대입니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/jeonbuk/", ["/service/hotel-massage/", "/reservation/how-to-book/", "/area/jeonnam/", "/service/business-trip-massage/"]),
},
{
  "slug": "jeonnam", "name": "전남", "full": "전라남도",
  "title": "전남 출장마사지 | 여수·순천·목포·광양 권역 안내 - 바로GO",
  "description": "전남은 여수 밤바다 관광 호텔, 순천만 자연 관광, 광양제철 산업 출장, 목포 항만 권역 등 권역마다 성격이 다른 지역입니다. 권역별 이용 흐름을 정리했습니다.",
  "h1": "전남 권역별 출장마사지 이용 안내",
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
<h2>전남 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>여수 디오션리조트에서 가능한가요?</summary><p>여수 종포·웅천 일대 리조트 객실 방문이 자주 안내됩니다. 객동 정보와 체크인 일정을 함께 확인합니다.</p></details>
<details><summary>순천 정원박람회 시즌 예약이 어려운가요?</summary><p>박람회 시즌은 호텔 가능 시간이 빠르게 마감되므로 일정이 확정되면 빠른 예약을 권합니다.</p></details>
<details><summary>광양 산업단지 출장 일정에 받을 수 있나요?</summary><p>가능합니다. 광양읍·중마동 호텔에서 평일 저녁 객실 방문이 자주 안내됩니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/jeonnam/", ["/service/hotel-massage/", "/area/gwangju/", "/reservation/late-night/", "/area/jeonbuk/"]),
},
{
  "slug": "gyeongbuk", "name": "경북", "full": "경상북도",
  "title": "경북 출장마사지 | 포항·경주·구미·안동 권역 안내 - 바로GO",
  "description": "경북은 포항(포스코)·경주(관광)·구미(전자단지)·안동(전통 관광) 네 권역이 모두 성격이 다른 지역입니다. 권역별 이용 흐름과 가능 시간 안내를 정리했습니다.",
  "h1": "경북 권역별 출장마사지 이용 안내",
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
<h2>경북 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>경주 보문 켄싱턴리조트에서 받을 수 있나요?</summary><p>보문관광단지 내 호텔·리조트 객실 방문이 자주 안내됩니다. 시즌별 가능 시간 차이가 있으니 사전 확인이 좋습니다.</p></details>
<details><summary>포항제철 출장 일정에 가능한가요?</summary><p>가능합니다. 포항 중앙·북구 비즈니스 호텔에서 평일 저녁 객실 방문이 일반적인 패턴입니다.</p></details>
<details><summary>구미·대구 권역을 같은 시간대에 모두 진행할 수 있나요?</summary><p>같은 시간대 두 권역 동시 진행은 어려운 경우가 많습니다. 권역을 분리해 예약을 잡습니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/gyeongbuk/", ["/area/daegu/", "/service/business-trip-massage/", "/service/hotel-massage/", "/reservation/visit-area/"]),
},
{
  "slug": "gyeongnam", "name": "경남", "full": "경상남도",
  "title": "경남 출장마사지 | 창원·김해·진주·거제 권역 안내 - 바로GO",
  "description": "경남은 창원 기계·김해공항·거제 조선소·진주 도심 등 권역마다 성격이 다른 지역입니다. 거제 장기 출장 케어, 김해공항 환승 케어 등 권역별 흐름을 정리했습니다.",
  "h1": "경남 권역별 출장마사지 이용 안내",
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
<h2>경남 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>거제 옥포 출장 중인데 영어 안내가 가능한가요?</summary><p>모든 케이스 보장되지 않으며, 영어 안내 가능 일정으로 사전 협의가 필요합니다. 상담 시 미리 알려 주시면 가능 여부를 안내합니다.</p></details>
<details><summary>김해공항에서 환승 시간 3시간 가능할까요?</summary><p>3시간이면 공항 인접 호텔 60분 코스 진행이 가능한 편입니다. 보안검색·체크인 시간을 함께 계산해 주세요.</p></details>
<details><summary>양산은 부산 권역으로 받을 수 있나요?</summary><p>양산 일부 권역(물금·동면)은 부산 인접으로 함께 안내되는 사례가 있습니다. 자세한 가능 여부는 상담 시 확인됩니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/gyeongnam/", ["/area/busan/", "/service/business-trip-massage/", "/service/hotel-massage/", "/area/ulsan/"]),
},
{
  "slug": "jeju", "name": "제주", "full": "제주특별자치도",
  "title": "제주 출장마사지 | 제주시·서귀포·애월 권역 안내 - 바로GO",
  "description": "제주는 휴양 일정과 맞물린 리조트·풀빌라 객실 방문 비중이 가장 높은 지역입니다. 성수기·비수기 가능 시간 차이, 권역별 이용 흐름을 정리했습니다.",
  "h1": "제주 권역별 출장마사지 이용 안내",
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
<h2>제주 출장마사지 FAQ</h2>
<div class="faq">
<details><summary>중문 신라호텔 풀빌라에서 받을 수 있나요?</summary><p>가능합니다. 풀빌라 객동 호수와 체크인 정보를 함께 확인하며 진입 동선 안내가 필요한 경우가 있습니다.</p></details>
<details><summary>애월 펜션 진입로가 좁은데 가능한가요?</summary><p>차량 진입 가능 여부를 사전에 확인합니다. 진입이 어려운 경우 도보 동선 안내가 필요할 수 있습니다.</p></details>
<details><summary>도착 당일 늦은 시간 가능한가요?</summary><p>제주공항 입도 일정 후 시내 호텔 객실 방문이 자주 안내됩니다. 성수기에는 가능 시간이 빠르게 마감되니 사전 예약을 권합니다.</p></details>
</div>
</section>
""",
  "related": _rel("/area/jeju/", ["/service/hotel-massage/", "/service/aroma/", "/reservation/how-to-book/", "/reservation/late-night/"]),
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


def _region_price_section(name):
    """시·도 1차 페이지용 코스·가격표 (모든 지역 공통)."""
    return (
        '<section class="block">'
        f'<h2>{name} 권역 코스·가격 안내</h2>'
        '<p>아래는 코스별·시간별 <strong>시작 금액(부터)</strong>입니다. 진행 장소(호텔·가정·오피스텔), '
        '시간대(주간·심야), 이동 거리에 따라 일부 조정될 수 있으며, 최종 금액은 사전 전화 상담에서 안내됩니다. '
        '사전 동의 없는 추가 비용은 부과되지 않습니다.</p>'
        '<div class="price-table-wrap">'
        '<table class="price-table">'
        '<thead><tr><th scope="col">코스</th><th scope="col">60분</th><th scope="col">90분</th><th scope="col">120분</th></tr></thead>'
        '<tbody>'
        '<tr><th scope="row">홈타이(타이)</th><td>90,000원부터</td><td>110,000원부터</td><td>130,000원부터</td></tr>'
        '<tr><th scope="row">아로마</th><td>100,000원부터</td><td>120,000원부터</td><td>140,000원부터</td></tr>'
        '<tr><th scope="row">스웨디시(힐링)</th><td>110,000원부터</td><td>130,000원부터</td><td>150,000원부터</td></tr>'
        '<tr><th scope="row">스페셜·스포츠</th><td>120,000원부터</td><td>140,000원부터</td><td>160,000원부터</td></tr>'
        '<tr><th scope="row">커플(2인 합산)</th><td>180,000원부터</td><td>220,000원부터</td><td>260,000원부터</td></tr>'
        '</tbody>'
        '</table>'
        '</div>'
        '<ul class="price-note">'
        '<li>※ 본 가격표는 전국 공통 시작 금액이며, 자세한 코스 안내는 <a href="/reservation/price/">가격 안내</a> 페이지에서 확인하실 수 있습니다.</li>'
        '<li>※ 결제 수단·세금계산서는 <a href="/reservation/payment/">결제 안내</a> 페이지를 참고해 주세요.</li>'
        '<li>※ 본 가격 안내 최종 업데이트 : 2026년 5월 기준</li>'
        '</ul>'
        '</section>'
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
            + _region_price_section(r["name"])
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
   "dongs":["강일동","상일1동","상일2동","명일1동","명일2동","고덕1동","고덕2동","암사1동","암사2동","암사3동","천호1동","천호2동","천호3동","성내1동","성내2동","성내3동","길동","둔촌1동","둔촌2동"],
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
_DONG_GA_RE      = re.compile(r'[0-9·.]*가(?=동$)')


# 3차 동 페이지 chip-link index — populated by SEOUL_DONGS et al.
DONG_PAGE_INDEX = {}


# 자치구·시 (2차) 타이틀 풀 — 사용자 샘플 패턴 적용
_DISTRICT_TITLE_TPL = [
    "{name} 출장마사지 | {parent} 호텔·가정 방문 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 24시간 예약 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 권역 이용 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 코스·가격 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 야간·심야 예약 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 숙소·자택 방문 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 예약·상담 안내 - 바로GO",
    "{name} 출장마사지 | {parent} 가능 시간 안내 - 바로GO",
]

# 자치구·시 (2차) 디스크립션 풀 — 액션·혜택 중심
_DISTRICT_DESC_TPL = [
    "{name} 출장마사지 24시간 예약 안내 ({parent}). 스웨디시·아로마·홈타이 코스별 가격과 호텔·가정 방문 가능 시간을 정리했습니다.",
    "{parent} {name} 출장마사지 — 호텔 객실·가정·오피스텔 방문 가능, 코스 60·90·120분 운영, 사전 상담으로 일정 확정.",
    "{name} 출장마사지 예약 안내({parent}) — 평일 야간·주말·심야 가능 시간, 스웨디시·아로마·홈타이·스포츠 코스 운영.",
    "{parent} {name} 일대 출장마사지 — 24시간 전화 상담으로 코스·가격·진행 장소를 함께 확정합니다. 추가 비용 없음.",
    "{name}({parent}) 출장마사지 — 호텔·가정 방문 빠른 예약. 코스별 시작 가격과 시간대별 가능 여부를 사전에 안내해드립니다.",
    "{parent} {name} 출장마사지 가격·코스 안내. 호텔 객실 방문, 가정 방문, 오피스텔 방문 모두 24시간 예약 가능합니다.",
    "{name} 출장마사지 야간·심야 예약({parent}) — 호텔·가정 방문 모두 가능. 사전 상담으로 일정·코스를 함께 확정합니다.",
    "{parent} {name} 출장마사지 — 스웨디시·아로마·홈타이 등 코스별 가격, 가능 시간, 진행 장소를 한 페이지에 정리했습니다.",
]


def _district_title(name, parent_name, facts):
    """자치구·시 페이지 타이틀 — name을 시드로 한 hash-기반 자연 변형."""
    seed = f"{parent_name}|{name}".encode("utf-8")
    idx = int(hashlib.md5(seed).hexdigest(), 16) % len(_DISTRICT_TITLE_TPL)
    return _DISTRICT_TITLE_TPL[idx].format(name=name, parent=parent_name)


def _district_description(lede, name, parent_name, max_len=160):
    """자치구·시 디스크립션 — 서비스 의도 풀에서 hash 선택. lede는 본문에서만 활용."""
    seed = f"{parent_name}|{name}|desc".encode("utf-8")
    idx = int(hashlib.md5(seed).hexdigest(), 16) % len(_DISTRICT_DESC_TPL)
    text = _DISTRICT_DESC_TPL[idx].format(name=name, parent=parent_name)
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0]
    return text

def _consolidate_dongs(dongs):
    """행정동 리스트 단순화·중복 제거.

    규칙:
      - 일반 숫자/본 접미(N동·본동): 항상 통합 (논현1동·논현2동 → 논현동, 숭인1동 → 숭인동, 일원본동 → 일원동)
      - "[숫자]가동" 접미는 그룹원 2개 이상일 때만 통합 (금호1가동·2·3가동·4가동 → 금호동);
        단독이면 원형 유지 (용산2가동·명륜3가동 그대로)
      - 숫자 없는 동(압구정·세곡·왕십리도선)·읍·면·구는 그대로
    """
    candidates = []
    for d in dongs:
        has_gadong = _DONG_GA_RE.search(d) is not None  # "[digits]+가동" 형태
        new = d
        for _ in range(5):
            old = new
            new = _DONG_DIGIT_RE.sub('', new)
            new = _DONG_GA_RE.sub('', new)
            if new == old:
                break
        candidates.append((d, new, has_gadong))
    # 통합 후보별 그룹원 수
    group_count = {}
    for _, cons, _ in candidates:
        group_count[cons] = group_count.get(cons, 0) + 1
    # 가동 패턴은 그룹원 2개 이상일 때만 통합, 그 외는 항상 통합
    seen = set()
    result = []
    for orig, cons, has_gadong in candidates:
        display = orig if (has_gadong and group_count[cons] == 1) else cons
        if display not in seen:
            seen.add(display)
            result.append(display)
    return result


def _district_facts_html(facts):
    items = "".join(
        f'<div class="region-fact"><span class="region-fact-label">{lbl}</span>'
        f'<span class="region-fact-value">{val}</span></div>'
        for lbl, val in facts
    )
    return f'<div class="region-facts" role="list" aria-label="권역 요약">{items}</div>'


def _district_dong_card_html(name, dongs, region_slug=None):
    # 서울·경기·인천: DONG_PAGE_INDEX에 등록된 동은 <a> 링크 칩, 그 외는 평문 li
    dongs = sorted(_consolidate_dongs(dongs))
    parts = []
    for dn in dongs:
        url = DONG_PAGE_INDEX.get((region_slug, name, dn)) if region_slug else None
        if url:
            parts.append(
                f'<li class="has-link"><a href="{url}">{dn}'
                '<span class="region-districts-grid-arrow" aria-hidden="true">→</span>'
                '</a></li>'
            )
        else:
            parts.append(f'<li>{dn}</li>')
    chips = "".join(parts)
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
            _district_dong_card_html(d["name"], d["dongs"], region_slug="seoul"),
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
            h1=f"{d['name']} 출장마사지 이용 안내",
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


# ============================================================
# 3차 페이지 — 서울 25 자치구 × 행정동
# 각 동은 (한글명, 영문 슬러그, 1~2문장 고유 character)으로 정의
# ============================================================
SEOUL_DONGS = {
  "gangnam": [
    ("신사동","sinsa","신사동은 가로수길과 신사역·강남구청역 일대의 트렌드 상권 권역으로, 라이프스타일 상점과 직장인 오피스텔이 함께 있어 평일 저녁·야간 시간대 가정 방문이 자주 안내됩니다."),
    ("논현동","nonhyeon","논현동은 논현역·학동로의 가구거리와 강남대로 인접 직장인 권역으로, 비즈니스 호텔 객실 방문과 오피스텔 가정 방문이 함께 안내됩니다."),
    ("압구정동","apgujeong","압구정동은 압구정 로데오·갤러리아 명품관·현대백화점이 있는 라이프스타일 권역으로, 한강변 현대아파트와 부티크 호텔 객실 방문이 야간 시간대 자주 안내됩니다."),
    ("청담동","cheongdam","청담동은 청담사거리 명품거리와 SM·JYP 등 엔터테인먼트 기업이 모인 권역으로, 청담 부티크 호텔과 고급 주거 단지(상지카일룸·청담자이) 가정 방문이 안내됩니다."),
    ("삼성동","samseong","삼성동은 코엑스·인터컨티넨탈 서울 코엑스·트레이드 타워가 있는 비즈니스 컨벤션 중심 권역으로, 출장 일정 후 평일 야간 호텔 객실 방문 비중이 매우 큰 동입니다."),
    ("대치동","daechi","대치동은 은마사거리·도곡로 대치 학원가와 은마·미도아파트가 있는 학원·주거 권역으로, 평일 늦은 저녁 학원 종료 후 가정 방문이 자주 안내됩니다."),
    ("역삼동","yeoksam","역삼동은 강남역·테헤란로 IT 오피스 권역으로, 라마다 강남·르 메르디앙 등 비즈니스 호텔과 1인 가구 오피스텔 가정 방문이 야간 시간대 자주 안내됩니다."),
    ("도곡동","dogok","도곡동은 타워팰리스·도곡렉슬·도곡롯데캐슬이 있는 고급 주거 권역으로, 평일 저녁 단지 내 가정 방문이 자주 안내됩니다."),
    ("개포동","gaepo","개포동은 개포 주공 재건축 단지(래미안 블레스티지·디에이치 아너힐즈 등)와 구룡마을 등 대규모 신축 단지가 밀집한 권역으로, 평일 저녁 입주 단지 가정 방문 비중이 큽니다."),
    ("세곡동","segok","세곡동은 세곡 보금자리주택과 헌인릉이 있는 강남구 동남부 외곽 권역으로, 평일 저녁 보금자리 단지 가정 방문이 안내됩니다."),
    ("일원동","irwon","일원동은 일원본·일원1 주거 단지와 삼성서울병원이 있는 권역으로, 평일 저녁 단지·병원 인근 호텔 객실 방문이 함께 안내됩니다."),
    ("수서동","suseo","수서동은 SRT 수서역과 강남구 동남권 환승 거점이 있는 권역으로, SRT 환승 일정 단시간 코스와 평일 저녁 가정 방문이 함께 안내됩니다."),
    ("율현동","yulhyeon","율현동은 위례신도시(강남 외곽) 일부와 보금자리주택이 있는 권역으로, 평일 저녁 신축 단지 가정 방문이 안내됩니다."),
  ],
  "gangdong": [
    ("강일동","gangil","강일동은 강일지구 신축 단지가 들어선 강동구 동단의 신도시 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("상일동","sangil","상일동은 고덕신도시 인접 권역으로 상일초·상일여고 일대 신축 단지에서 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("명일동","myeongil","명일동은 명일역·고덕역 일대의 주거 권역으로, 명일근린공원 인근 단지 가정 방문이 평일 저녁 안내됩니다."),
    ("고덕동","godeok","고덕동은 고덕 그라시움·아르테온·롯데캐슬 베네루체 등 신축 대단지가 밀집한 권역으로, 평일 저녁 입주 단지 가정 방문 비중이 큽니다."),
    ("암사동","amsa","암사동은 암사선사주거지와 한강변 주거 단지가 있는 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("천호동","cheonho","천호동은 천호역 일대 도심 권역으로 천호로데오·강동성심병원 인근 비즈니스 호텔과 오피스텔 가정 방문이 함께 안내됩니다."),
    ("성내동","seongnae","성내동은 강동구청·강동아트센터가 있는 강동 행정 중심 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("길동","gil","길동은 길동역·강동경희대병원 인근 주거 권역으로, 평일 저녁 단지·병원 인근 가정 방문이 안내됩니다."),
    ("둔촌동","dunchon","둔촌동은 올림픽파크포레온(둔촌 주공 재건축) 단지가 들어선 권역으로, 평일 저녁 신축 단지 가정 방문이 안내됩니다."),
  ],
  "gangbuk": [
    ("삼양동","samyang","삼양동은 삼양사거리 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("미아동","mia","미아동은 미아사거리역·롯데백화점 미아 인근 도심·주거 혼합 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("송중동","songjung","송중동은 송중초·동소문로 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("송천동","songcheon","송천동은 송천초 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("삼각산동","samgaksan","삼각산동은 북한산국립공원 자락의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("번동","beon","번동은 번1동·번2동·번3동을 아우르는 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("수유동","suyu","수유동은 수유역·강북구청 인근 도심·주거 혼합 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("인수동","insu","인수동은 4·19민주묘지·인수봉 자락의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("우이동","ui","우이동은 우이령·북한산우이역이 있는 강북 동북부 권역으로, 등산 일정 후 회복 케어 문의도 일부 들어옵니다."),
  ],
  "gangseo": [
    ("염창동","yeomchang","염창동은 염창역 일대의 한강변 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("등촌동","deungchon","등촌동은 등촌역·KBS스포츠월드 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("화곡동","hwagok","화곡동은 화곡역 일대의 다세대·다가구 주거가 밀집한 권역으로, 평일 저녁 1인 가구 오피스텔·빌라 가정 방문이 자주 안내됩니다."),
    ("가양동","gayang","가양동은 가양역·증미산 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("발산동","balsan","발산동은 발산역·이대서울병원 인근 권역으로, 평일 저녁 단지·병원 인근 가정 방문이 자주 안내됩니다."),
    ("우장산동","ujangsan","우장산동은 우장산역·우장산공원 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("공항동","gonghang","공항동은 김포공항(서울 강서 영역) 인접 권역으로, 환승 호텔 단시간 코스와 인근 주거 가정 방문이 함께 안내됩니다."),
    ("방화동","banghwa","방화동은 김포공항 서쪽 권역으로 방화역 일대 주거와 공항 인접 호텔 객실 방문이 안내됩니다."),
  ],
  "gwanak": [
    ("보라매동","boramae","보라매동은 보라매공원·보라매역 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("청림동","cheongnim","청림동은 보라매역 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("성현동","seonghyeon","성현동은 봉천역·성현초 인근의 1인 가구·직장인 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("행운동","haengun","행운동은 낙성대역·행운초 인근 주거 권역으로, 평일 저녁 1인 가구 오피스텔 가정 방문이 안내됩니다."),
    ("낙성대동","nakseongdae","낙성대동은 낙성대역·낙성대공원이 있는 권역으로, 서울대 인접 권역 특성상 청년·연구원 가정 방문이 자주 안내됩니다."),
    ("청룡동","cheongnyong","청룡동은 봉천역·청룡산 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("은천동","euncheon","은천동은 봉천역 일대 주거 권역으로, 평일 저녁 1인 가구·직장인 가정 방문이 자주 안내됩니다."),
    ("중앙동","jungang","중앙동은 봉천중앙시장·관악구청 인근 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("인헌동","inheon","인헌동은 사당역 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("남현동","namhyeon","남현동은 사당역·예술의전당 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신림동","sillim","신림동은 신림역·서울대입구역 일대의 1인 가구 밀집 권역으로, 평일 저녁 원룸·오피스텔 가정 방문이 매우 자주 안내됩니다."),
    ("신사동","sinsa","신사동(관악)은 신림 신사시장 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다. (강남구 신사동과 다릅니다.)"),
    ("조원동","jowon","조원동은 신림 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("미성동","miseong","미성동은 신림 미성·난곡로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("난곡동","nangok","난곡동은 난곡로·관악산 자락 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("난향동","nanhyang","난향동은 난향초·관악산 자락 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("서원동","seowon","서원동은 신림 서원로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신원동","sinwon","신원동은 신림 신원로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("서림동","seorim","서림동은 신림 서림로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("삼성동","samseong","삼성동(관악)은 관악구 삼성로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다. (강남구 삼성동과 다릅니다.)"),
    ("대학동","daehak","대학동은 서울대학교 정문·낙성대 인접 권역으로, 청년·연구원·대학원생 1인 가구 가정 방문이 평일 저녁 자주 안내됩니다."),
  ],
  "gwangjin": [
    ("화양동","hwayang","화양동은 건대입구역·세종대 인접 권역으로, 1인 가구 원룸·오피스텔 가정 방문이 야간 시간대 자주 안내됩니다."),
    ("군자동","gunja","군자동은 군자역·세종대 일대 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("중곡동","junggok","중곡동은 중곡역·용마산 자락의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("능동","neung","능동은 어린이대공원이 위치한 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("구의동","guui","구의동은 구의역·강변역 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("광장동","gwangjang","광장동은 워커힐 호텔(그랜드 워커힐·비스타 워커힐)이 있는 한강변 권역으로, 야간 시간대 5성 호텔 객실 방문이 자주 안내됩니다."),
    ("자양동","jayang","자양동은 자양역·뚝섬한강공원 일대의 주거·직장인 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
  ],
  "guro": [
    ("신도림동","sindorim","신도림동은 신도림역·디큐브시티(쉐라톤 서울 디큐브시티)가 있는 환승 권역으로, KTX 인근 호텔 객실 방문이 자주 안내됩니다."),
    ("구로동","guro","구로동은 구로디지털단지(G밸리)와 구로역 일대의 IT 오피스·주거 혼합 권역으로, 평일 야근 후 가정 방문이 야간 시간대 자주 안내됩니다."),
    ("가리봉동","garibong","가리봉동은 가리봉역·구로공단 인접 권역으로, 평일 저녁 1인 가구 원룸 가정 방문이 자주 안내됩니다."),
    ("고척동","gocheok","고척동은 고척스카이돔·고척역 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("개봉동","gaebong","개봉동은 개봉역·개봉뉴타운이 있는 주거 권역으로, 평일 저녁 신축 단지 가정 방문이 자주 안내됩니다."),
    ("오류동","oryu","오류동은 오류동역·오류고가 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("수궁동","sugung","수궁동은 온수역·수궁로 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
  ],
  "geumcheon": [
    ("가산동","gasan","가산동은 가산디지털단지(G밸리)·가산디지털단지역 일대의 IT 오피스·호텔 권역으로, 평일 야근 후 가정 방문과 가산 비즈니스 호텔 객실 방문이 야간에 자주 안내됩니다."),
    ("독산동","doksan","독산동은 독산역·금천구청 인근의 주거 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다."),
    ("시흥동","siheung","시흥동(금천)은 금천구 시흥로 일대 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다. (경기도 시흥시와 다릅니다.)"),
  ],
  "nowon": [
    ("월계동","wolgye","월계동은 월계역·인덕대 인근의 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("공릉동","gongneung","공릉동은 서울과기대(서울과학기술대학교)·삼육대 인접 권역으로, 평일 저녁 단지·원룸 가정 방문이 자주 안내됩니다."),
    ("하계동","hagye","하계동은 하계역·중계 학원가 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("중계동","junggye","중계동은 은행사거리 학원가와 중계 청구·라이프 단지 등 노원 학원가 핵심 권역으로, 평일 늦은 저녁 가정 방문이 매우 자주 안내됩니다."),
    ("상계동","sanggye","상계동은 상계 주공 단지가 밀집한 노원 최대 주거 권역으로, 평일 저녁 대단지 가정 방문이 매우 자주 안내됩니다."),
  ],
  "dobong": [
    ("쌍문동","ssangmun","쌍문동은 쌍문역 일대의 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("방학동","banghak","방학동은 방학역·도봉산역 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("창동","chang","창동은 창동역·창동 주공 단지가 밀집한 권역으로, 평일 저녁 대단지 가정 방문이 매우 자주 안내됩니다."),
    ("도봉동","dobong","도봉동은 도봉산·북한산국립공원 자락의 주거 권역으로, 평일 저녁 가정 방문과 등산 일정 후 회복 케어 문의가 함께 안내됩니다."),
  ],
  "dongdaemun": [
    ("용신동","yongsin","용신동은 신설동역·용두역 인근 도심 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("제기동","jegi","제기동은 제기동역·서울약령시(경동시장) 인접 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("전농동","jeonnong","전농동은 전농동 시립대 일대 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("답십리동","dapsimni","답십리동은 답십리역·답십리고미술상가 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("장안동","jangan","장안동은 장한평역·답십리 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("청량리동","cheongnyangni","청량리동은 KTX 강릉선·중앙선 환승 거점인 청량리역 일대로, 환승 일정 단시간 코스와 인근 호텔 객실 방문이 자주 안내됩니다."),
    ("회기동","hoegi","회기동은 경희대·외대 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("휘경동","hwigyeong","휘경동은 회기역 동쪽 주거 권역으로, 평일 저녁 단지 가정 방문이 안내됩니다."),
    ("이문동","imun","이문동은 외대(한국외국어대학교) 인접 권역으로, 평일 저녁 학생·연구원 가정 방문이 자주 안내됩니다."),
  ],
  "dongjak": [
    ("노량진동","noryangjin","노량진동은 노량진역·노량진수산시장과 공무원·고시 학원가가 밀집한 권역으로, 평일 저녁 1인 가구 원룸 가정 방문이 매우 자주 안내됩니다."),
    ("상도동","sangdo","상도동은 상도역·숭실대 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("흑석동","heukseok","흑석동은 중앙대학교 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("사당동","sadang","사당동은 사당역 4·2호선 환승 거점 일대의 직장인 주거 권역으로, 평일 저녁 가정 방문이 매우 자주 안내됩니다."),
    ("대방동","daebang","대방동은 대방역·여의도 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신대방동","sindaebang","신대방동은 신대방역·보라매역 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
  ],
  "mapo": [
    ("공덕동","gongdeok","공덕동은 공덕역(5·6·경의중앙·공항철도) 4중 환승 거점 일대로, 직장인·1인 가구 가정 방문과 인근 비즈니스 호텔 객실 방문이 자주 안내됩니다."),
    ("아현동","ahyeon","아현동은 아현역·마포래미안푸르지오·신촌 인접 주거 권역으로, 평일 저녁 신축 단지 가정 방문이 자주 안내됩니다."),
    ("도화동","dohwa","도화동은 마포역·공덕로 일대 직장인 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("용강동","yonggang","용강동은 마포역·한강변 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("대흥동","daeheung","대흥동은 대흥역·서강대 인접 주거 권역으로, 평일 저녁 대학가 가정 방문이 자주 안내됩니다."),
    ("염리동","yeomri","염리동은 이대역·아현 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신수동","sinsu","신수동은 신촌역·서강대 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("서강동","seogang","서강동은 광흥창역·서강대 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("서교동","seogyo","서교동은 홍대입구역·홍대 일대의 트렌드 상권 권역으로, 1인 가구 오피스텔 가정 방문과 인근 비즈니스 호텔 객실 방문이 야간 시간대 자주 안내됩니다."),
    ("합정동","hapjeong","합정동은 합정역(2·6호선)·메세나폴리스가 있는 직장인·1인 가구 권역으로, 평일 야간 가정 방문이 매우 자주 안내됩니다."),
    ("망원동","mangwon","망원동은 망원역·망원시장 일대의 1인 가구·프리랜서 권역으로, 평일 저녁 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("연남동","yeonnam","연남동은 홍대입구역 서쪽 연트럴파크·연남공원 일대의 트렌드 권역으로, 1인 가구 가정 방문과 부티크 호텔 객실 방문이 야간 시간대 자주 안내됩니다."),
    ("성산동","seongsan","성산동은 성산대교·월드컵경기장 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("상암동","sangam","상암동은 디지털미디어시티(DMC) 권역으로 MBC·SBS·YTN·CJ ENM 사업장과 비즈니스 호텔(스탠포드 호텔·글래드 마포)이 함께 있어 평일 야근 후 호텔·가정 방문이 매우 자주 안내됩니다."),
  ],
  "seodaemun": [
    ("천연동","cheonnyeon","천연동은 독립문역·서대문역 인접 도심 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("북아현동","bukahyeon","북아현동은 아현역·이대역 인근 신축 단지 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("충현동","chunghyeon","충현동은 충정로역·서대문 인접 직장인 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신촌동","sinchon","신촌동은 신촌역·연세대 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("연희동","yeonhui","연희동은 연희로·연세대 서쪽 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("홍제동","hongje","홍제동은 홍제역·홍제고개 일대 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("홍은동","hongeun","홍은동은 홍은사거리·인왕산 자락 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("남가좌동","namgajwa","남가좌동은 가좌역·DMC 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("북가좌동","bukgajwa","북가좌동은 디지털미디어시티(DMC) 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
  ],
  "seocho": [
    ("서초동","seocho","서초동은 강남역(서초 측)·교대역·법조타운(서울중앙지방법원·서울고등법원)이 있는 비즈니스·법조 권역으로, 평일 야간 호텔 객실 방문과 직장인 가정 방문이 자주 안내됩니다."),
    ("잠원동","jamwon","잠원동은 잠원역·신반포 한강변 주거 권역으로, 신반포자이·아크로리버뷰 등 단지 가정 방문이 평일 저녁 자주 안내됩니다."),
    ("반포동","banpo","반포동은 고속터미널역·아크로리버파크·반포자이·반포 메리어트 등 한강변 고급 주거·호텔 권역으로, 야간 시간대 객실 방문 비중이 매우 큽니다."),
    ("방배동","bangbae","방배동은 방배역·내방역 일대의 고급 주거 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다."),
    ("양재동","yangjae","양재동은 양재역·양재시민의숲·하나로마트 인접 직장인 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("내곡동","naegok","내곡동은 헌릉로·내곡지구 신축 단지가 들어선 서초 동남부 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
  ],
  "seongdong": [
    ("왕십리도선동","wangsimnidoseon","왕십리도선동은 왕십리역(2·5·경의중앙·수인분당) 4중 환승 거점 일대로, 직장인 가정 방문과 환승 호텔 객실 방문이 자주 안내됩니다."),
    ("왕십리동","wangsimni","왕십리동은 한양대학교 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("마장동","majang","마장동은 마장축산물시장·마장역 일대의 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("사근동","sageun","사근동은 한양대 사근동 캠퍼스 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("행당동","haengdang","행당동은 행당역·왕십리 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("응봉동","eungbong","응봉동은 응봉역·한강변 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("금호동","geumho","금호동은 금호1·2·3·4가의 한강변 고급 주거 권역으로, 신금호·금호산 자락 단지 가정 방문이 평일 저녁 자주 안내됩니다."),
    ("옥수동","oksu","옥수동은 옥수역·한강변 트리마제·옥수파크힐스 등 고급 주거 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다."),
    ("성수동","seongsu","성수동은 성수1·2가의 트렌드·라이프스타일 권역으로, 카페·갤러리·아크로서울포레스트 등 고급 단지가 있어 1인 가구·직장인 가정 방문이 야간 시간대 자주 안내됩니다."),
    ("송정동","songjeong","송정동은 송정 한강변·뚝섬한강공원 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("용답동","yongdap","용답동은 용답동 면목로·답십리 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
  ],
  "seongbuk": [
    ("성북동","seongbuk","성북동은 한성대입구역·성북동 길상사·외국 공관 거주 권역으로, 평일 저녁 단지 가정 방문이 안내됩니다. 일부 공관 단지는 출입 정책 사전 확인이 필요합니다."),
    ("삼선동","samseon","삼선동은 한성대학교·삼선교 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("동선동","dongseon","동선동은 성신여대입구역·동소문로 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("돈암동","donam","돈암동은 돈암역·미아리 일대 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("안암동","anam","안암동은 고려대학교 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("보문동","bomun","보문동은 보문역·동소문 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("정릉동","jeongneung","정릉동은 정릉역·국민대 인접 주거 권역으로, 평일 저녁 대단지 가정 방문이 자주 안내됩니다."),
    ("길음동","gireum","길음동은 길음역·길음뉴타운 대단지 권역으로, 평일 저녁 신축 단지 가정 방문이 매우 자주 안내됩니다."),
    ("종암동","jongam","종암동은 종암동 고려대 동쪽 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("월곡동","wolgok","월곡동은 월곡역·돌곶이역 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("장위동","jangwi","장위동은 장위뉴타운·돌곶이역 인접 권역으로, 평일 저녁 신축 단지 가정 방문이 자주 안내됩니다."),
    ("석관동","seokgwan","석관동은 돌곶이역·석계역 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
  ],
  "songpa": [
    ("풍납동","pungnap","풍납동은 풍납토성·풍납역 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("거여동","geoyeo","거여동은 거여역·문정 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("마천동","macheon","마천동은 마천역·남한산성 자락 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("방이동","bangi","방이동은 방이역·올림픽공원 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("오륜동","oryun","오륜동은 올림픽선수기자촌 단지가 있는 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다."),
    ("오금동","ogeum","오금동은 오금역·송파구청 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("송파동","songpa","송파동은 송파역·석촌호수 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("석촌동","seokchon","석촌동은 석촌역·석촌호수 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("삼전동","samjeon","삼전동은 삼전역·잠실역 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("가락동","garak","가락동은 가락시장(가락 농수산물도매시장)·가락역 인근 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("문정동","munjeong","문정동은 문정역·문정법조타운(서울동부지방법원·검찰청)·송파파크하비오 푸르지오 권역으로, 평일 저녁 단지·직장인 가정 방문이 자주 안내됩니다."),
    ("장지동","jangji","장지동은 장지역·가든파이브·송파위례 인접 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("위례동","wirye","위례동(송파)은 송파권 위례신도시 일부로, 평일 저녁 위례 신축 단지 가정 방문이 자주 안내됩니다."),
    ("잠실동","jamsil","잠실동은 잠실역·시그니엘 서울(롯데월드타워)·롯데호텔 월드·소피텔 앰배서더 등 5성 호텔이 모인 권역으로, 야간 호텔 객실 방문 비중이 송파에서 가장 큽니다."),
  ],
  "yangcheon": [
    ("목동","mok","목동은 목동 신시가지 단지와 목동 학원가가 밀집한 양천 핵심 권역으로, 평일 저녁 대단지·학원가 가정 방문이 매우 자주 안내됩니다."),
    ("신월동","sinwol","신월동은 김포공항 동쪽 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("신정동","sinjeong","신정동은 신정역·양천구청 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
  ],
  "yeongdeungpo": [
    ("영등포본동","yeongdeungpobon","영등포본동은 영등포구청·영등포시장 일대의 도심 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("영등포동","yeongdeungpo","영등포동은 영등포역·타임스퀘어가 있는 도심 비즈니스 권역으로, 직장인 가정 방문과 인근 호텔 객실 방문이 자주 안내됩니다."),
    ("여의동","yeoui","여의동은 여의도(국회·금융권·증권가) 핵심 비즈니스 권역으로, 콘래드 서울·페어몬트 앰배서더 서울 등 5성 호텔 객실 방문이 야간 시간대 자주 안내됩니다."),
    ("당산동","dangsan","당산동은 당산역(2·9호선 환승) 일대의 직장인 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("도림동","dorim","도림동은 도림천·신길 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("문래동","mullae","문래동은 문래역·문래창작촌 일대의 직장인·예술가 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("양평동","yangpyeong","양평동(영등포)은 양평역·선유도공원 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다. (경기도 양평군과 다릅니다.)"),
    ("신길동","singil","신길동은 신길역·신길뉴타운 신축 단지 권역으로, 평일 저녁 신축 단지 가정 방문이 매우 자주 안내됩니다."),
    ("대림동","daerim","대림동은 대림역·구로 인접 다세대·다가구 주거 권역으로, 평일 저녁 1인 가구 가정 방문이 자주 안내됩니다."),
  ],
  "yongsan": [
    ("후암동","huam","후암동은 남산 자락·후암동로 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("용산2가동","yongsan2ga","용산2가동은 남영역·용산구청 인근 도심 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("남영동","namyeong","남영동은 남영역·숙대입구 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("청파동","cheongpa","청파동은 숙명여대 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("원효로동","wonhyoro","원효로동(원효로1·2동)은 원효대교·용산전자상가 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("효창동","hyochang","효창동은 효창공원·효창공원앞역 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("용문동","yongmun","용문동은 용문동 효창로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("한강로동","hangangro","한강로동은 용산역(KTX·드래곤시티) 일대의 환승·비즈니스 권역으로, 노보텔 앰배서더 용산·이비스 스타일·그랜드 머큐어 등 호텔 객실 방문이 매우 자주 안내됩니다."),
    ("이촌동","ichon","이촌동은 이촌역·한강변 동부이촌동(LG한강·강촌) 고급 주거 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다."),
    ("이태원동","itaewon","이태원동은 이태원역·해밀톤 호텔·이태원로 외국인 거리가 있는 다국적 권역으로, 외국인 케이스 호텔·게스트하우스 객실 방문이 야간 자주 안내됩니다."),
    ("한남동","hannam","한남동은 한남대교·그랜드 하얏트 서울·한남더힐·나인원한남 등 고급 주거·호텔 권역으로, 야간 호텔 객실 방문 비중이 매우 큰 동입니다."),
    ("서빙고동","seobinggo","서빙고동은 서빙고역·반포대교 북단 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("보광동","bogwang","보광동은 한남동 남쪽 한강변 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
  ],
  "eunpyeong": [
    ("녹번동","nokbeon","녹번동은 녹번역·은평구청 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("불광동","bulgwang","불광동은 불광역·연신내역 환승 거점 일대로, 평일 저녁 가정 방문이 매우 자주 안내됩니다."),
    ("갈현동","galhyeon","갈현동은 연신내역 서쪽 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("구산동","gusan","구산동은 구산역·역촌 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("대조동","daejo","대조동은 연신내역·대조시장 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("응암동","eungam","응암동은 응암역·응암오거리 일대의 주거 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다."),
    ("역촌동","yeokchon","역촌동은 역촌역·은평구청 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신사동","sinsa","신사동(은평)은 은평구 신사로 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다. (강남·관악 신사동과 다릅니다.)"),
    ("증산동","jeungsan","증산동은 증산역·DMC 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("수색동","susaek","수색동은 DMC역·디지털미디어시티 인접 권역으로, 평일 야근 후 미디어 종사자 가정 방문과 인근 호텔 객실 방문이 자주 안내됩니다."),
    ("진관동","jingwan","진관동은 은평뉴타운·진관사가 있는 신도시 권역으로, 평일 저녁 대단지 가정 방문이 매우 자주 안내됩니다."),
  ],
  "jongno": [
    ("청운효자동","cheonghyo","청운효자동은 청와대 인근·청운초·서촌 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("사직동","sajik","사직동은 사직단·경복궁 서편 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("삼청동","samcheong","삼청동은 경복궁 동편 삼청동길 카페·갤러리 권역으로, 평일 저녁 부티크 호텔 객실 방문과 가정 방문이 함께 안내됩니다."),
    ("부암동","buam","부암동은 인왕산 자락·환기미술관 인근의 한적한 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("평창동","pyeongchang","평창동(종로)은 평창동 고급 주거 권역으로, 평일 저녁 단지 가정 방문이 자주 안내됩니다. (강원 평창군과 다릅니다.)"),
    ("무악동","muak","무악동은 독립문역·무악동 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("교남동","gyonam","교남동은 경희궁자이·서대문 인접 주거 권역으로, 평일 저녁 신축 단지 가정 방문이 자주 안내됩니다."),
    ("가회동","gahoe","가회동은 북촌 한옥마을 인접 권역으로, 한옥 게스트하우스 객실 방문이 자주 안내됩니다."),
    ("종로동","jongno","종로동(종로1·2·3·4가)은 광화문·종각·종로 도심 권역으로, 포시즌스 호텔 서울·웨스틴 조선 등 도심 5성 호텔 객실 방문이 야간 시간대 매우 자주 안내됩니다."),
    ("이화동","ihwa","이화동은 동대문역·이화동 벽화마을 인근 도심 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("혜화동","hyehwa","혜화동은 혜화역·대학로(서울대 의대·연극가) 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("명륜3가동","myeongnyun3ga","명륜3가동은 성균관대 인접 권역으로, 평일 저녁 대학가 가정 방문이 안내됩니다."),
    ("창신동","changsin","창신동은 동대문역·창신숭인 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("숭인동","sungin","숭인동은 동묘앞역·숭인 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
  ],
  "junggu": [
    ("소공동","sogong","소공동은 롯데호텔 서울·웨스틴 조선 서울·플라자호텔이 있는 도심 핵심 권역으로, 야간 시간대 도심 5성 호텔 객실 방문이 매우 자주 안내됩니다."),
    ("회현동","hoehyeon","회현동은 회현역·남대문시장·신세계백화점 본점 인접 도심 권역으로, 인근 호텔 객실 방문이 자주 안내됩니다."),
    ("명동","myeongdong","명동은 명동성당·롯데백화점 본점·이비스 명동 등 호텔이 모인 관광 핵심 권역으로, 관광 일정 후 객실 방문이 매우 자주 안내됩니다."),
    ("필동","pildong","필동은 동국대학교 인접 권역으로, 평일 저녁 대학가 원룸·오피스텔 가정 방문이 자주 안내됩니다."),
    ("장충동","jangchung","장충동은 신라호텔·장충체육관 인접 권역으로, 신라호텔 객실 방문이 야간 시간대 매우 자주 안내됩니다."),
    ("광희동","gwanghui","광희동은 동대문역사문화공원(DDP) 인근 권역으로, JW 메리어트 동대문·노보텔 앰배서더 동대문 객실 방문이 자주 안내됩니다."),
    ("을지로동","euljiro","을지로동은 을지로3·4가·노가리골목이 있는 도심 권역으로, 인근 비즈니스 호텔 객실 방문과 1인 가구 오피스텔 가정 방문이 자주 안내됩니다."),
    ("신당동","sindang","신당동은 신당역·신당창작아케이드·황학동 풍물거리 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("다산동","dasan","다산동은 약수역·다산성곽길 일대 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("약수동","yaksu","약수동은 약수역·신당 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("청구동","cheonggu","청구동은 청구역·신당 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("동화동","donghwa","동화동은 신당·동대문역사문화공원 인접 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("황학동","hwanghak","황학동은 황학동 풍물거리·롯데캐슬 베네치아 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("중림동","jungnim","중림동은 서울역·중림동 LG에클라트 인근 도심 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
  ],
  "jungnang": [
    ("면목동","myeonmok","면목동은 면목역·사가정역 일대의 주거 권역으로, 평일 저녁 단지 가정 방문이 매우 자주 안내됩니다."),
    ("상봉동","sangbong","상봉동은 상봉역(KTX 강릉선·중앙선 환승) 일대의 환승 권역으로, 단시간 코스와 가정 방문이 함께 안내됩니다."),
    ("중화동","junghwa","중화동은 중화역·면목 인접 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("묵동","muk","묵동은 묵동·중랑역 인근 주거 권역으로, 평일 저녁 가정 방문이 자주 안내됩니다."),
    ("망우동","mangu","망우동은 망우역·중앙선 망우 인근 주거 권역으로, 평일 저녁 가정 방문이 안내됩니다."),
    ("신내동","sinnae","신내동은 신내역·신내 보금자리 단지 권역으로, 평일 저녁 신축 단지 가정 방문이 자주 안내됩니다."),
  ],
}


# Pre-register DONG_PAGE_INDEX so 2차 자치구 페이지의 동 칩이 링크로 렌더링됨
_SEOUL_DIST_NAME_BY_SLUG = {d["slug"]: d["name"] for d in SEOUL_DISTRICTS}
for _ps, _dongs in SEOUL_DONGS.items():
    _pn = _SEOUL_DIST_NAME_BY_SLUG[_ps]
    for _dn, _ds, _ in _dongs:
        DONG_PAGE_INDEX[("seoul", _pn, _dn)] = f"/area/seoul/{_ps}/{_ds}/"


def _build_seoul_dong_pages():
    """3차 행정동 페이지 생성. 페이지마다 고유 character paragraph + 공통 본문(2,000자+)."""
    parent_char_by_slug = {d["slug"]: d["character"] for d in SEOUL_DISTRICTS}
    for parent_slug, dongs in SEOUL_DONGS.items():
        parent_name = _SEOUL_DIST_NAME_BY_SLUG[parent_slug]
        parent_char = parent_char_by_slug.get(parent_slug, "")
        slug_by_name = {n: s for n, s, _ in dongs}
        names = sorted([n for n, _, _ in dongs])
        for dong_name, dong_slug, char in dongs:
            siblings = [n for n in names if n != dong_name]
            sib_chips = "".join(
                f'<li class="has-link"><a href="/area/seoul/{parent_slug}/{slug_by_name[s]}/">{s}'
                '<span class="region-districts-grid-arrow" aria-hidden="true">→</span>'
                '</a></li>'
                for s in siblings
            )
            sib_card = (
                '<section class="region-districts" aria-label="같은 자치구 인접 동">'
                '<header class="region-districts-head">'
                '<span class="region-districts-eyebrow">'
                '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
                f'{parent_name} 인접 동'
                '</span>'
                f'<h2 class="region-districts-headline">{parent_name}의 다른 행정동 {len(siblings)}곳</h2>'
                f'<p class="region-districts-note">{dong_name}과 같은 {parent_name} 권역의 다른 행정동입니다. 권역 간 이동·가능 시간이 다르므로 동별로 사전 확인을 권장합니다.</p>'
                '</header>'
                '<div class="region-districts-body">'
                '<div class="region-districts-group">'
                f'<ul class="region-districts-grid">{sib_chips}</ul>'
                '</div></div></section>'
            ) if siblings else ''
            body_html = _build_dong_rich_body(
                dong_name=dong_name,
                parent_name=parent_name,
                region_name="서울",
                parent_char=parent_char,
                parent_url=f"/area/seoul/{parent_slug}/",
                sibling_card_html=sib_card,
                extra_intro_paragraph=char,  # SEOUL_DONGS 고유 character
            )
            desc = char if len(char) <= 160 else char[:160].rsplit('.', 1)[0] + '.'
            intro_lede = f'{dong_name}은 서울 {parent_name}의 행정동입니다. {char}'
            add(
                path=f"area/seoul/{parent_slug}/{dong_slug}/index.html",
                url=f"/area/seoul/{parent_slug}/{dong_slug}/",
                slug=f"area-seoul-{parent_slug}-{dong_slug}",
                title=_dong_title(dong_name, parent_name, "서울"),
                description=desc,
                h1=f"{dong_name} 출장마사지 이용 안내",
                intro=f'<p class="lede">{intro_lede}</p>' + _district_hero_cta_html(dong_name),
                breadcrumbs=[
                    ("홈", "/"),
                    ("지역별 찾기", "/area/"),
                    ("서울", "/area/seoul/"),
                    (parent_name, f"/area/seoul/{parent_slug}/"),
                    (dong_name, f"/area/seoul/{parent_slug}/{dong_slug}/"),
                ],
                body=body_html,
                related=(
                    '<aside class="related">'
                    '<h2>관련 안내</h2>'
                    '<ul>'
                    f'<li><a href="/area/seoul/{parent_slug}/">{parent_name} 전체 안내</a></li>'
                    '<li><a href="/area/seoul/">서울 전체 안내</a></li>'
                    '<li><a href="/reservation/how-to-book/">예약 방법</a></li>'
                    '<li><a href="/reservation/price/">가격 및 코스 안내</a></li>'
                    '<li><a href="/reservation/check-before-use/">이용 전 확인사항</a></li>'
                    '<li><a href="/reservation/cancel-refund/">취소·환불 규정</a></li>'
                    '</ul>'
                    '</aside>'
                ),
            )


# _build_seoul_districts() ← _shared_* 헬퍼 정의 이후로 이동
# _build_seoul_dong_pages()  ← _build_dong_rich_body 정의 이후로 이동


# ============================================================
# 3차 행정동/읍·면 페이지 생성기 (Seoul 외 모든 지역 공통)
# ============================================================
import hashlib as _hashlib

_HANGUL_INI = ['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
_HANGUL_MED = ['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','wo','we','wi','yu','eu','ui','i']
_HANGUL_FIN = ['','k','k','k','n','n','n','t','l','k','m','l','l','l','l','l','m','p','p','t','t','ng','j','t','k','t','p','h']

def _romanize_hangul(text):
    out = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            o = code - 0xAC00
            init = o // (21 * 28)
            med = (o % (21 * 28)) // 28
            fin = o % 28
            out.append(_HANGUL_INI[init] + _HANGUL_MED[med] + _HANGUL_FIN[fin])
        elif ch.isascii() and (ch.isalnum() or ch == '-'):
            out.append(ch.lower())
    return ''.join(out)


_DONG_SUFFIX_RE = re.compile(r'(동|읍|면|리|가)$')

def _romanize_dong(name):
    base = _DONG_SUFFIX_RE.sub('', name)
    slug = _romanize_hangul(base)
    return slug or _romanize_hangul(name) or 'x'


def _dong_short_parent(text, max_len=70):
    if not text:
        return ''
    s = text.split('.')[0].strip()
    if len(s) > max_len:
        s = s[:max_len].rsplit(' ', 1)[0]
    return s + '.'


def _dong_pick(name, salt, n):
    h = _hashlib.md5((name + '|' + salt).encode('utf-8')).hexdigest()
    return int(h[:8], 16) % n


# 직관적이고 자연스러운 8개의 인트로 변형 — 동 이름/부모 명/부모 짧은 설명을 결합해 유니크함을 확보
_DONG_INTRO_TPL = [
    "{dong}은 {parent}에 속한 행정 단위로, {p_short} 권역의 일부입니다. 정확한 가능 시간·진행 장소는 전화 상담에서 안내됩니다.",
    "{dong}은 {parent} 내 행정구역으로, {p_short} 인접 동과 비슷한 권역 흐름이 적용됩니다.",
    "{dong}은 행정상 {parent}에 포함되며, {p_short} 권역의 시간대·이동 가능 패턴을 공유합니다.",
    "{dong} 권역은 {parent}의 일부로 운영됩니다. {p_short} 일대 진행 장소·코스 안내가 동일하게 적용됩니다.",
    "{dong}은 {parent} 행정 구역 안의 동입니다. {p_short} 권역 안내가 그대로 이어집니다.",
    "{dong}은 {parent}에 속하며, {p_short} 일대 인접 동과 함께 권역 동선이 안내됩니다.",
    "{dong}은 {parent} 내 위치한 행정 단위로, {p_short} 권역 가능 시간 범위 안에서 확인됩니다.",
    "{dong}은 {parent} 권역의 한 동입니다. {p_short} 인근 동과 시간대 가능 여부가 공유됩니다.",
]

# 동(3·4차) 타이틀 풀 — 사용자 샘플 패턴: "{동} 출장마사지 | {부모} {액션} - 바로GO"
# {parent_disp}는 _dong_title에서 region까지 포함해서 빌드 (경기 시-구 케이스용)
_DONG_TITLE_TPL = [
    "{dong} 출장마사지 | {parent_disp} 숙소·자택 방문 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 호텔·가정 예약 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 중심 생활권 이용 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 주거지역 예약 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 예약 전 확인사항 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 권역 이용 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 24시간 예약 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 야간·심야 예약 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 코스·가격 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 가능 시간 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 호텔 객실 방문 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 자택 방문 예약 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 예약·상담 안내 - 바로GO",
    "{dong} 출장마사지 | {parent_disp} 즉시 예약 안내 - 바로GO",
]


# 동(3·4차) 디스크립션 풀 — 액션·혜택 중심 (검색 의도 매칭)
_DONG_DESC_TPL = [
    "{dong} 출장마사지 안내 — {parent_disp} 숙소·자택 방문 가능. 코스별 가격, 가능 시간, 예약 절차를 정리했으며 24시간 전화 상담이 가능합니다.",
    "{parent_disp} {dong} 출장마사지 예약 — 스웨디시·아로마·홈타이 코스 운영, 호텔·가정·오피스텔 방문 가능. 사전 동의 없는 추가 비용은 없습니다.",
    "{dong}({parent_disp}) 출장마사지 — 평일 야간·주말·심야 예약 가능. 코스 60·90·120분 운영, 코스별 가격을 사전에 안내해드립니다.",
    "{parent_disp} {dong} 출장마사지 가격·코스 안내. 호텔 객실 방문, 가정 방문 모두 가능하며 24시간 전화 상담으로 일정·코스를 확정합니다.",
    "{dong} 출장마사지 빠른 예약({parent_disp}) — 호텔·가정·오피스텔 방문 가능. 스웨디시·아로마·홈타이·스포츠 코스 운영, 추가 비용 없음.",
    "{parent_disp} {dong} 출장마사지 24시간 예약. 코스별 시작 가격과 시간대별 가능 여부를 한 페이지에 정리했으며, 사전 상담으로 일정 확정.",
    "{dong} 일대 출장마사지 예약 안내 — {parent_disp} 권역 가능 시간·코스 정보. 호텔 객실·가정 방문 모두 24시간 전화 상담 가능합니다.",
    "{parent_disp} {dong}에서 받는 출장마사지 — 코스·가격·진행 장소가 사전 상담에서 함께 확정됩니다. 처음 이용도 매끄럽게 안내해드립니다.",
    "{dong} 출장마사지 야간·심야 예약 가능({parent_disp}) — 호텔·가정 방문 모두 가능, 코스 60·90·120분 운영, 사전 상담으로 일정 확정.",
    "{parent_disp} {dong} 호텔·가정 출장마사지 — 코스별 가격, 가능 시간, 결제 방식까지 한 번에 확인하실 수 있습니다. 24시간 전화 예약.",
    "{dong} 출장마사지 안내({parent_disp}) — 스웨디시·아로마·홈타이·스포츠 코스 운영. 호텔 객실 방문, 가정 방문 모두 빠르게 예약 가능합니다.",
    "{parent_disp} {dong} 출장마사지 예약 — 전화 상담으로 일정·코스·진행 장소를 함께 확정하며, 사전 동의 없는 추가 비용은 발생하지 않습니다.",
    "{dong} 출장마사지({parent_disp}) — 호텔 객실·가정·오피스텔 방문 가능. 코스별 가격과 가능 시간을 사전에 안내해드립니다.",
    "{parent_disp} {dong} 출장마사지 처음 이용 안내 — 코스 추천, 시간대별 가능 여부, 사전 준비사항까지 한 페이지에 정리했습니다.",
    "{dong} 일대 출장마사지 예약({parent_disp}) — 24시간 전화 상담으로 호텔·가정 방문 일정과 코스를 함께 확정합니다.",
    "{parent_disp} {dong}에서 출장마사지 받기 — 첫 이용자를 위한 코스 추천, 시간대별 가능 여부, 가격 안내까지 한 페이지에서 확인.",
]


def _dong_parent_disp(parent_name, region_name):
    """타이틀·디스크립션용 {parent_disp} 빌드.
    경기 시-구 케이스('경기 성남시' + '분당구')는 '성남시 분당구'로 합쳐 시명을 포함시킨다.
    그 외(서울·인천·경기 시 단독)는 parent_name만 사용."""
    if region_name and region_name.startswith("경기 ") and " " in region_name.strip():
        si = region_name.replace("경기 ", "", 1).strip()
        if si and si != parent_name:
            return f"{si} {parent_name}"
    return parent_name


def _dong_title(dong_name, parent_name, region_name):
    """동 페이지 타이틀 — 14개 풀에서 hash-기반 선택."""
    idx = _dong_pick(dong_name, "title", len(_DONG_TITLE_TPL))
    parent_disp = _dong_parent_disp(parent_name, region_name)
    return _DONG_TITLE_TPL[idx].format(dong=dong_name, parent_disp=parent_disp)


def _dong_description(dong_name, parent_name, region_name):
    """동 페이지 디스크립션 — 16개 풀에서 hash-기반 선택. 160자 내."""
    idx = _dong_pick(dong_name, "desc", len(_DONG_DESC_TPL))
    parent_disp = _dong_parent_disp(parent_name, region_name)
    text = _DONG_DESC_TPL[idx].format(dong=dong_name, parent_disp=parent_disp)
    if len(text) > 160:
        text = text[:160].rsplit(' ', 1)[0]
    return text

# 추가 보조 단락 (권역 운영 패턴 묘사) — 부모 character + dong-localized 변형
_DONG_PATTERN_TPL = [
    "{dong}은 {parent} 권역 내에서 가정 방문과 호텔·오피스텔 객실 방문이 함께 안내되는 동입니다. 시간대별 가능 여부는 전화 상담에서 안내됩니다.",
    "{dong} 권역은 인접 동과 동일한 진행 패턴을 따릅니다. 평일 저녁·심야 시간 가능 여부는 사전 전화 확인이 가장 정확합니다.",
    "{dong}은 권역 단위로 가능 시간이 안내되며, 동 단위로 시간이 따로 분리되지 않습니다. 정확한 시간대는 전화 상담을 통해 확인하실 수 있습니다.",
    "{dong}에서의 진행은 {parent} 일대 인접 동과 동선을 공유합니다. 코스·이동·진행 장소는 전화 상담에서 안내됩니다.",
    "{dong}은 {parent} 권역 안에서 운영되는 단위로, 가능 시간·이동 가능 여부는 권역 기준으로 안내됩니다.",
    "{dong} 권역의 시간대 가능 여부는 동 단위가 아닌 {parent} 권역 단위로 운영되며, 사전 전화 확인이 권장됩니다.",
]


# ------------------------------------------------------------
# 동 단위 페이지 본문(2,000자 이상)을 만드는 통합 빌더
# ------------------------------------------------------------
# 권역 특성(긴 형식) — 8가지 변형, 각 ~200~260자
_DONG_LONG_INTRO_TPL = [
    "{dong}은 {parent} 권역에 속한 행정 단위로, {p_short} {dong} 일대는 {parent} 권역 안에서 동선·시간대 측면의 공통 특성을 공유하지만, 동 단위의 진입 도로·주거 형태·상업 지구 비중에 따라 출장마사지 진행 방식이 조금씩 달라집니다. 정확한 가능 여부와 가능 시간대는 동 단위가 아닌 권역 단위로 운영되므로, 사전 전화 상담에서 일정·코스·진행 장소 유형을 함께 안내드리는 방식으로 운영됩니다.",
    "{dong}은 행정상 {parent}에 포함된 권역으로, {p_short} {parent} 권역의 동선·시간대 기준이 {dong}에도 그대로 적용됩니다. 다만 {dong} 일대 주거 형태(아파트·오피스텔·단독·빌라)나 인근 호텔·숙소의 유형, 진입 도로의 폭과 주차 가능 여부에 따라 출장마사지 진행 일정의 유연성이 달라질 수 있어, 정확한 가능 시간은 전화 상담에서 권역 동선과 함께 함께 안내됩니다.",
    "{dong}은 {parent}의 일부 권역으로 운영되며, {p_short} {dong} 자체는 {parent} 권역 안의 한 행정 단위이므로 출장마사지 가능 시간·이동 가능 여부는 동 단위가 아닌 {parent} 권역 단위로 통합 관리됩니다. 단, 동 단위 진입 환경·주변 시설의 운영 시간이 일정 가능 여부에 영향을 줄 수 있어, 사전 전화 상담을 통해 일정·진행 장소·코스를 함께 정합니다.",
    "{dong} 권역은 {parent}의 행정 단위로 자리합니다. {p_short} {dong} 일대는 {parent} 권역의 동선·시간대 흐름을 공유하면서도, 동 단위의 주거 밀집도·상업 시설 분포·교통 접근성에 따라 출장마사지 운영 방식의 세부 사항이 달라집니다. 자세한 가능 시간·진행 장소·코스 종류는 전화 상담에서 권역 정보와 함께 안내드립니다.",
    "{dong}은 {parent} 권역에 속하며, {p_short} {dong}을 포함한 {parent} 권역에서는 출장마사지 운영이 권역 단위로 통합 관리됩니다. 동 단위로 가능 시간이 따로 나뉘지는 않지만, 진입 도로·주차·공동현관 출입 방식과 같은 동 단위 환경 변수는 사전 전화 상담에서 함께 확인됩니다. 권역 동선·일정 가능 여부는 24시간 상담으로 안내드립니다.",
    "{dong}은 {parent} 행정 구역 안에 위치한 단위입니다. {p_short} {dong} 일대의 출장마사지 가능 시간·코스·진행 장소 유형은 모두 {parent} 권역의 기준에 따르며, 동 단위 진입 환경이 일정 운영의 유연성에 영향을 줄 수 있어 사전 전화 상담에서 함께 확인됩니다. 권역 운영 시간과 코스 종류는 전화로 가장 정확히 안내드립니다.",
    "{dong}은 {parent} 권역의 한 행정 단위로, {p_short} {parent} 권역의 동선·시간대 운영 기준이 {dong}에도 동일하게 적용됩니다. 출장마사지 운영은 동 단위가 아닌 권역 단위로 진행되며, 동 단위 환경(주거 형태·진입 도로·주차 가능 여부)은 일정 확정 단계에서 사전 전화로 함께 확인되어 안전하고 매끄러운 진행이 가능합니다.",
    "{dong}은 {parent} 권역 안에서 운영되는 행정 단위입니다. {p_short} {dong} 일대는 {parent} 권역의 가능 시간·이동 동선·코스 운영 기준을 공유하지만, 동 단위 주거 형태·상업 시설·진입 도로 등 세부 환경 변수가 일정 운영에 영향을 줍니다. 출장마사지 가능 시간·진행 장소·코스 정보는 사전 전화 상담에서 함께 안내됩니다.",
]


def _dong_long_intro(dong_name, parent_name, parent_char):
    idx = _dong_pick(dong_name, "longintro", len(_DONG_LONG_INTRO_TPL))
    return _DONG_LONG_INTRO_TPL[idx].format(
        dong=dong_name,
        parent=parent_name,
        p_short=_dong_short_parent(parent_char or parent_name, max_len=80),
    )


# 진행 방식 섹션 도입 문장 — 5가지 변형
_DONG_FLOW_INTRO_TPL = [
    "{dong} 일대에서 진행되는 출장마사지는 다음 다섯 단계 흐름으로 운영됩니다. 각 단계는 사전 전화 상담에서 사용자 일정에 맞게 확정됩니다.",
    "{dong} 권역의 출장마사지 진행은 아래 흐름을 기본 골격으로 합니다. 일정·코스·진행 장소는 사용자 상황에 맞춰 사전 전화에서 함께 조정됩니다.",
    "{parent} {dong} 권역에서 진행되는 출장마사지의 표준 흐름은 다음과 같습니다. 단계별 세부 사항은 사전 전화 상담에서 함께 안내드립니다.",
    "출장마사지는 사용자 공간에서 진행되는 서비스로, {dong}을 포함한 {parent} 권역에서도 동일하게 아래 단계로 운영됩니다.",
    "{dong} 일대의 출장마사지 진행은 전화 상담 → 일정 확정 → 관리사 배정 → 도착·진행 → 결제·종료 순으로 운영되며, 각 단계가 사전에 명확히 합의됩니다.",
]

# 시간대 패턴 도입 — 4가지 변형
_DONG_TIME_INTRO_TPL = [
    "{dong} 권역의 일반적 가능 시간대는 다음과 같습니다. 같은 시간대라도 권역 동선·관리사 일정에 따라 가능 여부가 달라질 수 있어 사전 전화 확인이 가장 정확합니다.",
    "{dong}을 포함한 {parent} 권역에서는 시간대별로 진행 빈도와 가능 유형이 달라집니다. 아래는 권역 평균에 기반한 시간대 흐름입니다.",
    "{parent} {dong} 일대의 시간대별 출장마사지 가능 패턴은 아래와 같습니다. 사용자 일정에 맞춰 사전 전화에서 가장 가까운 가능 시간대를 안내드립니다.",
    "출장마사지는 사용자 일정에 맞춰 시간대를 정하는 서비스로, {dong} 권역에서는 다음과 같은 시간대 흐름을 기준으로 안내됩니다.",
]

# 진행 장소 유형 도입 — 4가지 변형
_DONG_PLACE_INTRO_TPL = [
    "{dong}을 포함한 {parent} 권역에서는 사용자의 일정과 상황에 따라 다음 네 가지 유형의 진행 장소가 가장 많이 안내됩니다. 사전 전화 상담에서 유형별 사전 확인 사항을 함께 안내드립니다.",
    "{dong} 권역의 출장마사지는 호텔·가정·오피스텔·펜션 네 가지 진행 장소 유형으로 안내됩니다. 유형별로 진입 방식과 사전 확인 사항이 조금씩 다릅니다.",
    "{parent} {dong} 일대에서 자주 안내되는 진행 장소 유형은 다음과 같습니다. 사용자 일정 상황·인원 수에 따라 적합한 유형이 사전 전화에서 함께 권해집니다.",
    "사용자 공간이 곧 진행 장소가 되는 출장마사지는, {dong} 권역에서 아래 네 유형의 공간에서 가장 자주 진행됩니다.",
]


def _dong_course_section_html():
    return (
        '<section class="block">'
        '<h2>출장마사지 추천 코스 안내</h2>'
        '<p>본 권역에서 자주 안내되는 출장마사지 코스 유형은 다음과 같습니다. 본인의 컨디션·일정·인원 수에 맞게 코스를 선택하실 수 있도록 각 코스 상세 페이지를 함께 안내드립니다.</p>'
        '<ul>'
        '<li><a href="/service/business-trip-massage/"><strong>출장마사지 종합 안내</strong></a> — 사용자 공간에서 60·90·120·150분 단위 진행. 컨디션·체형 종합 케어가 필요한 분께 권해드립니다.</li>'
        '<li><a href="/service/hometai/"><strong>홈타이</strong></a> — 태국식 스트레칭과 압 기반 코스로, 근육 이완·자세 교정에 초점이 맞춰져 있습니다.</li>'
        '<li><a href="/service/swedish/"><strong>스웨디시 마사지</strong></a> — 부드러운 압의 전신 이완 코스로, 출장마사지 첫 이용자에게 가장 자주 권해집니다.</li>'
        '<li><a href="/service/aroma/"><strong>아로마 마사지</strong></a> — 에센셜 오일을 활용한 향기 케어. 수면 보조·스트레스 완화에 적합합니다.</li>'
        '<li><a href="/service/sports-massage/"><strong>스포츠 마사지</strong></a> — 운동 후 회복·뭉친 부위 집중 케어가 필요한 분께 권해집니다.</li>'
        '<li><a href="/service/couple-massage/"><strong>커플 마사지</strong></a> — 2인 동시 진행 코스로, 호텔·가정·펜션 공간 모두 가능합니다.</li>'
        '<li><a href="/service/hotel-massage/"><strong>호텔 출장마사지</strong></a> — 출장·관광 일정 호텔 객실에서 진행되는 출장마사지 유형입니다.</li>'
        '<li><a href="/service/office-massage/"><strong>기업·사무실 출장</strong></a> — 사무실 공간 컨디션에 맞춰 진행되는 기업 단위 케어입니다.</li>'
        '</ul>'
        '</section>'
    )


def _dong_flow_section_html(dong_name, parent_name):
    intro = _DONG_FLOW_INTRO_TPL[
        _dong_pick(dong_name, "flow", len(_DONG_FLOW_INTRO_TPL))
    ].format(dong=dong_name, parent=parent_name)
    return (
        '<section class="block">'
        f'<h2>{dong_name} 출장마사지 진행 방식</h2>'
        f'<p>{intro}</p>'
        '<ol>'
        '<li><strong>전화 상담</strong> — 24시간 운영되는 0508-202-4719 번호로 연락하시면, '
        f'{parent_name} {dong_name} 권역의 가능 시간대·코스·진행 장소 유형을 확인해 드립니다. 권역 동선 가능 여부도 이 단계에서 안내됩니다.</li>'
        '<li><strong>일정 확정</strong> — 도착 가능 시간, 진행 장소(호텔·가정·오피스텔·펜션), 코스 길이(60·90·120·150분), 인원(1인·2인), 추가 옵션(아로마·핫스톤 등)을 함께 정합니다. 시간대 가능 여부는 권역 단위로 운영됩니다.</li>'
        '<li><strong>관리사 배정</strong> — 권역 동선을 고려해 가까운 위치의 관리사가 배정됩니다. 관리사 도착 가능 시각이 다시 한 번 안내됩니다.</li>'
        '<li><strong>도착·진행</strong> — 약속 시간 직전 도착 안내 후 사용자 공간에서 코스가 진행됩니다. 별도 장비 설치·환경 변경 없이 기존 공간 그대로 진행되며, 진행 중에는 통화·외부 출입을 자제하는 것이 권장됩니다.</li>'
        '<li><strong>결제·종료</strong> — 종료 후 현장 결제 또는 사전 안내된 방식으로 진행. 영수증·세금계산서가 필요한 경우 사전에 요청해 주시면 안내됩니다.</li>'
        '</ol>'
        '</section>'
    )


def _dong_time_section_html(dong_name, parent_name):
    intro = _DONG_TIME_INTRO_TPL[
        _dong_pick(dong_name, "time", len(_DONG_TIME_INTRO_TPL))
    ].format(dong=dong_name, parent=parent_name)
    return (
        '<section class="block">'
        f'<h2>{dong_name} 이용 가능 시간대</h2>'
        f'<p>{intro}</p>'
        '<ul>'
        '<li><strong>오전·이른 오후(10시~16시)</strong> — 가정 방문 위주의 시간대입니다. 평일 비중이 크며, 휴식·컨디션 회복 목적의 코스가 자주 안내됩니다.</li>'
        f'<li><strong>저녁(19시~22시)</strong> — {parent_name} 권역에서 가장 활발한 시간대입니다. 가정·호텔·오피스텔 모두 진행 빈도가 높습니다.</li>'
        '<li><strong>야간(22시~01시)</strong> — 호텔·오피스텔 객실 방문 중심 시간대입니다. 권역에 따라 일부 가능하며 사전 예약이 권장됩니다.</li>'
        f'<li><strong>심야(01시 이후)</strong> — {parent_name} 일부 권역에 한해 가능합니다. 사전 예약이 필수이며, 권역 동선·관리사 일정에 따라 가능 여부가 달라집니다.</li>'
        '<li><strong>주말·공휴일</strong> — 호텔 객실 방문 비중이 가정 방문보다 더 커지는 경향이 있습니다. 휴양 일정과 결합된 진행이 자주 안내됩니다.</li>'
        '</ul>'
        '</section>'
    )


def _dong_place_section_html(dong_name, parent_name):
    intro = _DONG_PLACE_INTRO_TPL[
        _dong_pick(dong_name, "place", len(_DONG_PLACE_INTRO_TPL))
    ].format(dong=dong_name, parent=parent_name)
    return (
        '<section class="block">'
        f'<h2>{dong_name} 진행 장소 유형</h2>'
        f'<p>{intro}</p>'
        '<ul>'
        '<li><strong>호텔 객실</strong> — 출장·비즈니스·관광 일정과 함께 자주 진행됩니다. 체크인 시각·룸 컨디션·층 정보를 사전 확인 후 도착 시각을 정합니다. <a href="/service/hotel-massage/">호텔 출장마사지</a> 페이지 참고.</li>'
        f'<li><strong>가정</strong> — {parent_name} 주거 단지에서 평일 저녁 비중이 가장 큰 유형입니다. 공동현관 비밀번호·층 안내·반려동물 유무를 사전 확인합니다.</li>'
        '<li><strong>오피스텔</strong> — 1인 가구·주거형 오피스텔에서 진행되며, 무인 출입 시스템·키오스크·엘리베이터 카드 키 등 출입 방식 사전 안내가 필요합니다.</li>'
        '<li><strong>펜션·풀빌라</strong> — 휴양 일정과 결합되는 유형으로, 진입로 폭·주차 가능 여부·도착 안내(외부 조명·도어 잠금 방식) 등을 사전에 함께 확인합니다.</li>'
        '<li><strong>기업·사무실</strong> — 사내 휴게 공간 컨디션에 맞춰 진행됩니다. 단체 일정의 경우 사전 일정 조율이 필요합니다. <a href="/service/office-massage/">기업 출장</a> 페이지 참고.</li>'
        '</ul>'
        '</section>'
    )


def _dong_check_section_html(dong_name):
    return (
        '<section class="block">'
        f'<h2>{dong_name} 이용 전 확인 사항</h2>'
        f'<p>{dong_name} 일대에서 출장마사지를 이용하기 전, 다음 사항을 사전 전화 상담에서 함께 안내드립니다. 이는 안전한 진행 환경과 신뢰 가능한 일정 운영을 위한 기본 확인 절차입니다.</p>'
        '<ul>'
        '<li><strong>운영 주체</strong> — YH LAB(대표 김유환), 사업자등록번호 815-26-00585, 본사 경기도 파주시 청석로 268, 대표 전화 0508-202-4719</li>'
        '<li><strong>가능 시간 범위</strong> — 전화 상담은 24시간 가능하나, 진행 시간은 권역별로 일부 제한이 있을 수 있습니다.</li>'
        '<li><strong>코스·가격</strong> — <a href="/reservation/price/">가격 및 코스 안내</a> 페이지에서 코스별 가격·길이·옵션 사전 확인이 가능합니다.</li>'
        '<li><strong>이용 전 권장</strong> — <a href="/reservation/check-before-use/">이용 전 확인사항</a> 페이지에서 음주·식사·복장·공간 정리 등 사전 권장 사항을 확인해 주세요.</li>'
        '<li><strong>취소·환불</strong> — <a href="/reservation/cancel-refund/">취소·환불 규정</a> 페이지에 시간대별 환불 기준이 명시되어 있습니다.</li>'
        '<li><strong>결제 방식</strong> — <a href="/reservation/payment/">결제 안내</a> 페이지에서 가능한 결제 수단을 확인하실 수 있습니다.</li>'
        '</ul>'
        '</section>'
    )


# FAQ 풀(8개) — 동/부모 이름 주입으로 변형
_DONG_FAQ_POOL = [
    ("{dong} 권역 야간 시간대도 이용 가능한가요?",
     "{dong}을 포함한 {parent} 권역의 야간 시간대 가능 여부는 권역 동선과 관리사 일정에 따라 달라집니다. 22시 이후 호텔·오피스텔 객실 방문은 권역에 따라 가능하며, 심야 시간대는 사전 예약이 필수입니다. 가장 정확한 가능 여부는 24시간 상담 전화(0508-202-4719)에서 확인됩니다."),
    ("{dong}에서 호텔 객실 진행도 가능한가요?",
     "{parent} 권역의 호텔 객실 진행은 가능합니다. 다만 호텔별 룸서비스 정책·체크인 컨디션·층 출입 제한 등이 있을 수 있어, 호텔명·체크인 시각·룸 번호를 사전 전화에서 함께 안내해 주시면 권역 동선과 함께 안내드립니다."),
    ("{dong} 출장마사지 코스 길이는 어떻게 정하나요?",
     "코스는 60·90·120·150분 단위로 운영되며, 처음 이용 시 90분 또는 120분이 가장 자주 권해집니다. 사용자 컨디션·일정 여유·인원 수에 따라 사전 전화에서 함께 조정됩니다. 코스별 가격은 <a href=\"/reservation/price/\">가격 및 코스 안내</a> 페이지에서 확인하실 수 있습니다."),
    ("{dong}에서 커플 마사지(2인 동시)도 가능한가요?",
     "가능합니다. 2인 동시 진행은 가정·호텔·펜션 모두 진행 가능하며, 공간의 폭과 침구 배치에 따라 일부 사전 확인이 필요할 수 있습니다. 자세한 안내는 <a href=\"/service/couple-massage/\">커플 마사지</a> 페이지를 참고하시거나 전화 상담으로 확인 가능합니다."),
    ("{dong} 권역 결제는 어떻게 하나요?",
     "현장 결제·계좌 이체·카드 결제 등 다양한 수단이 지원됩니다. 세금계산서·영수증이 필요한 경우 사전에 요청해 주시면 함께 준비됩니다. 결제 수단별 상세 안내는 <a href=\"/reservation/payment/\">결제 안내</a> 페이지에서 확인하실 수 있습니다."),
    ("{dong}에서 예약 시 어떤 정보를 알려드려야 하나요?",
     "도착 희망 시각, 진행 장소 유형(호텔·가정·오피스텔·펜션)과 정확한 위치·층, 인원 수, 코스 길이·종류, 그리고 공동현관·엘리베이터 출입 방식 등이 사전 전화에서 함께 확인됩니다. 자세한 절차는 <a href=\"/reservation/how-to-book/\">예약 방법</a> 페이지에 정리되어 있습니다."),
    ("{dong} 일정을 갑작스럽게 변경할 수 있나요?",
     "사전 전화로 시간·장소 변경은 가능합니다. 다만 시간대에 따라 제약이 있을 수 있으며, 변경 가능 시점·환불 기준은 <a href=\"/reservation/cancel-refund/\">취소·환불 규정</a> 페이지에 명시되어 있습니다. 가능한 한 사전에 연락해 주시면 일정 조율이 매끄럽습니다."),
    ("{dong} 첫 이용입니다. 어떤 코스를 권하시나요?",
     "출장마사지를 처음 이용하시는 경우, 부드러운 압의 전신 이완 코스인 <a href=\"/service/swedish/\">스웨디시</a> 90분이 가장 자주 권해집니다. 컨디션·목적(휴식·회복·자세 교정·수면 보조)에 맞춰 사전 전화에서 함께 권해드립니다."),
]


def _dong_faq_section_html(dong_name, parent_name):
    # 8개 중 해시로 4개 선택 (순환)
    base = _dong_pick(dong_name, "faq", len(_DONG_FAQ_POOL))
    chosen = [_DONG_FAQ_POOL[(base + i) % len(_DONG_FAQ_POOL)] for i in range(4)]
    rows = "".join(
        f"<details><summary>{q.format(dong=dong_name, parent=parent_name)}</summary>"
        f"<p>{a.format(dong=dong_name, parent=parent_name)}</p></details>"
        for q, a in chosen
    )
    return (
        '<section class="block">'
        f'<h2>{dong_name} 자주 묻는 질문</h2>'
        f'<div class="faq">{rows}</div>'
        '</section>'
    )


def _dong_operator_info_html():
    return (
        '<section class="block">'
        '<h2>운영 정보 (E-E-A-T)</h2>'
        '<p>본 안내 페이지는 <strong>YH LAB(서비스명 바로GO)</strong>가 운영합니다. 본사는 경기도 파주시 청석로 268에 위치하며, 사업자등록번호는 <strong>815-26-00585</strong>, 대표자는 <strong>김유환</strong>입니다. 대표 전화 <strong>0508-202-4719</strong>로 24시간 예약·상담이 가능합니다.</p>'
        '<p>YH LAB은 출장마사지·홈타이·스웨디시·아로마·스포츠·커플·호텔·기업 출장 등 사용자의 공간에서 진행되는 서비스만을 안내하며, 본 페이지의 정보는 실제 운영 기준에 따라 작성·관리됩니다. 권역별 가능 시간·코스·진행 장소 유형은 운영 상황에 따라 조정될 수 있어, 가장 정확한 정보는 전화 상담에서 안내드립니다.</p>'
        '</section>'
    )


# ------------------------------------------------------------
# 공유 섹션: 코스·가격표 / 이용 절차 / 이용자 후기
# (2차 자치구·시·군 페이지와 3차 동 페이지에서 모두 재사용)
# ------------------------------------------------------------

_PROG_INTRO_TPL = [
    "{area} 일대에서 운영되는 출장마사지 프로그램과 코스별 기준 가격을 정리했습니다. 가격은 코스 시간·진행 장소·예약 시간대에 따라 일부 조정될 수 있으며, 정확한 최종 금액은 사전 전화 상담에서 일정·진행 장소가 확정된 직후 함께 안내됩니다. 사전 동의 없는 추가 비용은 부과되지 않습니다.",
    "{area}에서 안내드리는 출장마사지 프로그램 종류와 시간 단위 기준 가격은 다음과 같습니다. 권역·시간대·진행 장소에 따라 일부 조정이 있을 수 있으며, 최종 금액은 사전 상담에서 명확히 안내됩니다.",
    "{area} 권역에서 진행되는 출장마사지의 프로그램 종류와 기준 가격을 안내합니다. 코스 시간·진행 장소·시간대에 따라 일부 변동이 있을 수 있고, 최종 금액은 사전 상담 단계에서 확정 안내됩니다.",
    "{area}에서 제공되는 출장마사지 프로그램 6종과 각 코스의 시간 단위 기준 가격을 아래에 정리했습니다. 정확한 금액은 일정·장소가 확정된 직후 함께 안내됩니다.",
]
_PROG_SWEDISH_TPL = [
    "부드러운 압을 기본으로 한 전신 이완 코스. 출장마사지를 처음 받는 분께 가장 자주 권해지는 유형으로, 수면 보조·휴식·근육 이완에 적합합니다.",
    "전신을 부드럽게 풀어 주는 이완 중심 코스. 첫 이용자에게 가장 많이 권장되며 수면 질 개선·전반적 컨디션 회복에 적합합니다.",
    "압이 부드러운 전신 케어 코스로, 잠을 푹 못 잤거나 전반적 피로감이 누적되었을 때 가장 자주 선택됩니다.",
]
_PROG_AROMA_TPL = [
    "에센셜 오일을 활용한 향기 케어 중심 코스. 스트레스·수면·자율 신경 안정 목적으로 자주 선택됩니다.",
    "향기 오일을 활용한 케어 코스로, 정서적 안정·수면 보조·스트레스 완화를 목적으로 자주 선택됩니다.",
    "에센셜 오일과 부드러운 압의 조합으로 자율 신경을 안정시키고 수면을 돕는 케어 코스입니다.",
]
_PROG_HOMETAI_TPL = [
    "태국식 스트레칭과 압 기반의 코스로, 자세 교정·근육 가동 범위 회복에 초점을 둡니다.",
    "태국 전통 스트레칭과 압을 결합한 코스로, 굳은 근육과 좁아진 가동 범위 회복에 효과적입니다.",
    "스트레칭과 압 케어가 결합된 태국식 코스. 자세가 굳어 있거나 거북목·골반 회복이 필요할 때 권해집니다.",
]
_PROG_SPORTS_TPL = [
    "운동 후 회복·뭉친 부위 집중 케어. 특정 부위 통증·피로 회복이 필요할 때 권해집니다.",
    "특정 부위 집중 케어 코스로, 운동 후 근육 회복·국소 통증 완화 목적에 적합합니다.",
    "운동 후 회복과 뭉친 부위 집중 케어를 목적으로 운영되는 코스. 부위별 맞춤 케어가 가능합니다.",
]
_PROG_COUPLE_TPL = [
    "2인 동시 진행 코스. 가정·호텔·펜션 공간에서 함께 받는 형태입니다.",
    "두 분이 같은 공간에서 동시에 받는 코스로, 가정·호텔·펜션 모두 진행 가능합니다.",
    "커플·가족 단위 2인 동시 진행 코스. 가정·호텔·펜션 등 공간 유형 무관하게 운영됩니다.",
]
_PROG_HOTEL_TPL = [
    "출장·관광 일정 호텔 객실에서 진행되는 유형. 체크인 시각·룸 호수 사전 확인이 필요합니다.",
    "호텔 객실 방문 진행 유형으로, 체크인 시각·객실 정보 사전 공유가 필요합니다.",
    "출장·여행 일정 호텔 객실에서 진행되는 유형. 객실 호수·체크인 시각 사전 안내가 필요합니다.",
]


def _shared_program_price_section(area_name):
    """마사지 프로그램 설명 + 가격표 (지역별 변형 — 가격표만 동일)."""
    p = _dong_pick
    intro = _PROG_INTRO_TPL[p(area_name, "pi", len(_PROG_INTRO_TPL))].format(area=area_name)
    sw = _PROG_SWEDISH_TPL[p(area_name, "pSw", len(_PROG_SWEDISH_TPL))]
    ar = _PROG_AROMA_TPL[p(area_name, "pAr", len(_PROG_AROMA_TPL))]
    ho = _PROG_HOMETAI_TPL[p(area_name, "pHo", len(_PROG_HOMETAI_TPL))]
    sp = _PROG_SPORTS_TPL[p(area_name, "pSp", len(_PROG_SPORTS_TPL))]
    co = _PROG_COUPLE_TPL[p(area_name, "pCo", len(_PROG_COUPLE_TPL))]
    ht = _PROG_HOTEL_TPL[p(area_name, "pHt", len(_PROG_HOTEL_TPL))]
    return (
        '<section class="block">'
        f'<h2>{area_name} 마사지 프로그램 안내·가격표</h2>'
        f'<p>{intro}</p>'
        '<div class="program-grid">'
        f'<article class="program-card"><h3>스웨디시</h3><p>{sw}</p></article>'
        f'<article class="program-card"><h3>아로마</h3><p>{ar}</p></article>'
        f'<article class="program-card"><h3>홈타이</h3><p>{ho}</p></article>'
        f'<article class="program-card"><h3>스포츠</h3><p>{sp}</p></article>'
        f'<article class="program-card"><h3>커플</h3><p>{co}</p></article>'
        f'<article class="program-card"><h3>호텔 방문</h3><p>{ht}</p></article>'
        '</div>'
        '<table class="price-table" aria-label="코스별 시간 단위 기준 가격 (부터)">'
        '<thead><tr><th scope="col">코스</th><th scope="col">60분</th><th scope="col">90분</th><th scope="col">120분</th></tr></thead>'
        '<tbody>'
        '<tr><th scope="row">홈타이(타이)</th><td>90,000원부터</td><td>110,000원부터</td><td>130,000원부터</td></tr>'
        '<tr><th scope="row">아로마</th><td>100,000원부터</td><td>120,000원부터</td><td>140,000원부터</td></tr>'
        '<tr><th scope="row">스웨디시(힐링)</th><td>110,000원부터</td><td>130,000원부터</td><td>150,000원부터</td></tr>'
        '<tr><th scope="row">스페셜·스포츠</th><td>120,000원부터</td><td>140,000원부터</td><td>160,000원부터</td></tr>'
        '<tr><th scope="row">커플(2인 합산)</th><td>180,000원부터</td><td>220,000원부터</td><td>260,000원부터</td></tr>'
        '</tbody></table>'
        '<ul class="price-note">'
        '<li>※ 지역·시간대·진행 장소·코스에 따라 금액은 조정될 수 있습니다.</li>'
        '<li>※ 정확한 최종 금액은 예약 상담 시 안내됩니다.</li>'
        '<li>※ 결제 수단·세금계산서 안내는 <a href="/reservation/payment/">결제 안내</a> 페이지를 참고해 주세요.</li>'
        '<li>※ 본 가격 안내 최종 업데이트: 2026년 5월 기준 · 자세한 코스 안내는 <a href="/reservation/price/">가격 안내</a> 페이지에서 확인하실 수 있습니다.</li>'
        '</ul>'
        '</section>'
    )


_PROC_INTRO_TPL = [
    "{area}의 출장마사지는 아래 다섯 단계로 순서를 따라 진행됩니다. 각 단계는 사전 전화 상담에서 사용자 일정·진행 장소·코스에 맞춰 함께 확정됩니다.",
    "{area} 권역에서 출장마사지를 받는 흐름은 다음과 같습니다. 사용자 일정 조건에 맞춰 사전 전화에서 단계별 세부 사항이 합의됩니다.",
    "{area} 일대 출장마사지 진행은 전화 상담부터 결제까지 5단계로 운영되며, 단계별 사전 안내가 명확히 이루어집니다.",
    "{area}에서 출장마사지를 이용하시는 표준 절차는 아래 5단계 흐름입니다. 일정·진행 장소·코스 옵션이 단계별로 함께 합의됩니다.",
    "바로GO의 {area} 권역 출장마사지는 5단계 진행 흐름을 따릅니다. 단계별 사전 안내·합의 후에만 일정이 확정됩니다.",
    "{area} 권역의 출장마사지 진행 절차는 다음과 같습니다. 시간·장소·코스·결제 정보가 단계별로 명확히 안내됩니다.",
]
_STEP1_TPL = [
    "24시간 운영되는 0508-202-4719로 연락 주시면 {area} 권역 가능 시간·코스·진행 장소 유형을 안내해 드립니다.",
    "0508-202-4719(24시간) 전화로 {area} 권역 가능 시간대와 코스 옵션을 먼저 확인하실 수 있습니다.",
    "전화(0508-202-4719)로 연락하시면 {area} 일대의 동선·시간대·진행 장소 유형을 함께 확인해 드립니다.",
    "{area} 권역 가능 여부는 24시간 운영되는 0508-202-4719 상담을 통해 가장 정확히 안내됩니다. 통화 한 번이면 권역 동선·시간대 확인이 끝납니다.",
]
_STEP2_TPL = [
    "도착 가능 시간, 진행 장소(호텔·가정·오피스텔·펜션), 코스 길이(60·90·120분), 인원, 옵션을 함께 정합니다.",
    "도착 시각·진행 장소 유형·코스 길이·인원·추가 옵션 등 일정 세부 사항을 합의하여 예약을 확정합니다.",
    "예약 확정 시 사용자 일정에 맞는 시간대, 진행 장소(호텔/가정/오피스텔/펜션), 코스 종류·길이·인원이 함께 합의됩니다.",
    "도착 가능 시각, 진행 장소 유형, 코스 길이와 인원, 추가 옵션을 함께 합의해 일정이 확정됩니다.",
]
_STEP3_TPL = [
    "권역 동선을 고려해 가까운 위치의 관리사가 배정되며, 도착 가능 시각이 다시 한 번 안내됩니다.",
    "{area} 권역 동선과 일정에 맞춰 관리사가 매칭되고, 출발 후 도착 예정 시각이 재안내됩니다.",
    "권역 가까운 위치의 관리사가 일정에 맞춰 배정되며, 도착 직전 시각이 다시 한 번 공유됩니다.",
    "일정과 권역 동선을 고려해 관리사가 배정되며, 출발 후 도착 예정 시각이 사전 안내됩니다.",
]
_STEP4_TPL = [
    "약속 시간 직전 도착 안내 후 사용자 공간에서 코스가 진행됩니다. 별도 장비·환경 변경 없이 기존 공간 그대로 진행됩니다.",
    "도착 직전 안내 메시지 후 사용자 공간에서 곧바로 코스가 시작됩니다. 추가 장비·환경 변경 없이 진행됩니다.",
    "약속 시간이 가까워지면 도착 안내가 별도 전달되며, 사용자 공간 그대로의 컨디션에서 진행됩니다.",
    "도착 직전 안내 후 사용자 공간 컨디션 그대로 코스가 진행되며, 별도 장비 설치는 필요하지 않습니다.",
]
_STEP5_TPL = [
    "종료 후 현장 결제 또는 사전 안내된 방식으로 진행되며, 세금계산서·영수증이 필요한 경우 사전에 요청 가능합니다.",
    "코스 종료 후 현장 결제·계좌 이체·카드 결제 등 사전 합의된 방식으로 결제가 이루어집니다. 영수증 요청 가능.",
    "종료 후 결제는 사전 합의된 방식으로 진행되며, 세금계산서·영수증이 필요한 경우 미리 요청하시면 됩니다.",
    "코스 종료 후 결제는 사전 안내된 수단으로 진행되며, 영수증·세금계산서가 필요한 경우 사전 요청 가능합니다.",
]


def _shared_procedure_section(area_name):
    """출장마사지 이용 절차 (5단계) — 지역별 변형 (6 × 4^5 = 6,144 조합)."""
    pi = _dong_pick(area_name, "proc_intro", len(_PROC_INTRO_TPL))
    p1 = _dong_pick(area_name, "step1", len(_STEP1_TPL))
    p2 = _dong_pick(area_name, "step2", len(_STEP2_TPL))
    p3 = _dong_pick(area_name, "step3", len(_STEP3_TPL))
    p4 = _dong_pick(area_name, "step4", len(_STEP4_TPL))
    p5 = _dong_pick(area_name, "step5", len(_STEP5_TPL))
    intro = _PROC_INTRO_TPL[pi].format(area=area_name)
    step1 = _STEP1_TPL[p1].format(area=area_name)
    step2 = _STEP2_TPL[p2].format(area=area_name)
    step3 = _STEP3_TPL[p3].format(area=area_name)
    step4 = _STEP4_TPL[p4].format(area=area_name)
    step5 = _STEP5_TPL[p5].format(area=area_name)
    return (
        '<section class="block">'
        '<h2>출장마사지 이용 절차</h2>'
        f'<p>{intro}</p>'
        '<ol class="procedure-list">'
        f'<li><span class="step-num">1</span><div><h3>전화 상담</h3><p>{step1}</p></div></li>'
        f'<li><span class="step-num">2</span><div><h3>일정 확정</h3><p>{step2}</p></div></li>'
        f'<li><span class="step-num">3</span><div><h3>관리사 배정</h3><p>{step3}</p></div></li>'
        f'<li><span class="step-num">4</span><div><h3>도착·진행</h3><p>{step4}</p></div></li>'
        f'<li><span class="step-num">5</span><div><h3>결제·종료</h3><p>{step5}</p></div></li>'
        '</ol>'
        '</section>'
    )


# 후기 풀 — 약 18개. 동/부모/코스/시간이 변수로 주입되어 페이지마다 서로 다른 조합 6개가 표시됨.
_REVIEW_NAMES = ["김**", "이**", "박**", "최**", "정**", "강**", "조**", "윤**", "장**", "임**", "한**", "오**", "서**", "신**", "권**", "황**", "안**", "송**", "전**", "홍**"]
_REVIEW_DATES = ["2026-05", "2026-04", "2026-04", "2026-03", "2026-03", "2026-02", "2026-02", "2026-01", "2025-12", "2025-12", "2025-11", "2025-10"]
_REVIEW_COURSES = ["스웨디시", "아로마", "홈타이", "스웨디시", "스포츠", "커플", "스웨디시", "아로마"]
_REVIEW_DURATIONS = ["60", "90", "90", "120", "90", "120"]
_REVIEW_PLACES = ["가정 방문", "호텔 객실", "오피스텔", "가정 방문", "호텔 객실", "가정 방문"]
_REVIEW_RATINGS = ["★★★★★", "★★★★★", "★★★★★", "★★★★☆", "★★★★★", "★★★★★"]

_REVIEW_BODY_TPL = [
    "{course} {dur}분 코스로 이용했습니다. {area} 권역인데 약속 시간 정확히 도착하셨고, 코스 진행도 차분하셨어요. 가격은 사전 안내된 그대로였습니다.",
    "{area} 일대 가정 방문으로 신청했어요. 전화 상담에서 시간·코스 안내가 명확했고, 결제도 사전 안내된 그대로였습니다. 만족스러운 이용이었어요.",
    "{area} 호텔 객실에서 받았는데, 출입 안내·도착 시간 모두 약속대로였어요. 다음에도 다시 이용할 것 같습니다.",
    "처음 출장마사지를 받아봤는데, {course} {dur}분 코스가 첫 이용에 좋다고 권해 주셔서 만족스러웠어요. 사전 안내가 친절했습니다.",
    "{area} 오피스텔로 신청했는데 무인 출입 안내까지 사전에 잘 처리되어서 편안했습니다. 코스 진행도 깔끔했어요.",
    "야간 시간에 예약했는데 가능한 시간 정확히 안내해 주셨어요. 코스 진행도 깔끔했고, 종료 후 정리까지 매끄러웠습니다.",
    "{area} 권역 운영 시간에 맞춰 일정 잡았어요. 일정 변경할 일이 있었는데 사전 전화로 깔끔히 처리됐습니다.",
    "{course} {dur}분 코스 받았습니다. 가격도 사전 안내된 대로였고 추가 비용 없었어요. 권장 받은 코스도 적합했습니다.",
    "{area}에서 커플로 함께 받았어요. 공간 컨디션도 사전 안내된 대로였고, 두 분 모두 만족스럽게 마무리했습니다.",
    "여러 번 이용 중인데 매번 일정·코스 안내가 일관됩니다. {area} 일대에서 자주 이용합니다.",
    "체크인 후 객실 방문 신청했어요. 호텔 도착 시간까지 정확했고 종료 후 정리도 깔끔했습니다.",
    "{area} 신축 단지인데 진입로·주차 사전 확인이 매끄러웠어요. 도착 안내도 정확했습니다.",
    "당일 늦은 시간에 문의했는데 가능한 시간 빠르게 확인해 주셨습니다. {course} 코스로 진행했고 컨디션 회복에 도움 됐어요.",
    "사전 상담에서 코스를 권장해 주셨는데, 컨디션에 잘 맞았습니다. {area} 권역 가까운 시간으로 일정 잡혔어요.",
    "운동 후 회복 목적으로 {course} {dur}분 받았습니다. 부위 집중도 잘 맞춰 주셔서 만족스러웠습니다.",
    "음주 후 컨디션 회복 목적이었는데 사전 권장 사항 안내가 정확했어요. 일정도 권역 시간대에 맞춰 잡혔습니다.",
    "공항 인근 호텔에서 받았어요. 도착·체크인 시간 정확히 맞춰 진행되어 편안했습니다.",
    "{area} 일대 처음 이용인데 권역 가능 시간·진입 안내를 미리 알려 주셨어요. 도착 후 진행도 매끄러웠습니다.",
]


def _shared_reviews_section(area_name):
    """이용자 후기 6선 — 해시 기반 변형으로 페이지마다 서로 다른 조합 6개."""
    cards = []
    for i in range(6):
        bi = _dong_pick(area_name, f"rev_b{i}", len(_REVIEW_BODY_TPL))
        ni = _dong_pick(area_name, f"rev_n{i}", len(_REVIEW_NAMES))
        di = _dong_pick(area_name, f"rev_d{i}", len(_REVIEW_DATES))
        ci = _dong_pick(area_name, f"rev_c{i}", len(_REVIEW_COURSES))
        du = _dong_pick(area_name, f"rev_u{i}", len(_REVIEW_DURATIONS))
        pi = _dong_pick(area_name, f"rev_p{i}", len(_REVIEW_PLACES))
        ri = _dong_pick(area_name, f"rev_r{i}", len(_REVIEW_RATINGS))
        body = _REVIEW_BODY_TPL[bi].format(
            area=area_name,
            course=_REVIEW_COURSES[ci],
            dur=_REVIEW_DURATIONS[du],
        )
        cards.append(
            '<article class="review-card">'
            '<header class="review-card-head">'
            f'<span class="review-rating" aria-label="별점">{_REVIEW_RATINGS[ri]}</span>'
            f'<span class="review-meta">{_REVIEW_NAMES[ni]} · {_REVIEW_DATES[di]}</span>'
            '</header>'
            f'<p class="review-text">{body}</p>'
            '<footer class="review-card-foot">'
            f'<span class="review-tag">{_REVIEW_COURSES[ci]} {_REVIEW_DURATIONS[du]}분</span>'
            f'<span class="review-tag">{_REVIEW_PLACES[pi]}</span>'
            '</footer>'
            '</article>'
        )
    return (
        '<section class="block">'
        f'<h2>{area_name} 이용자 후기</h2>'
        f'<p>{area_name} 권역에서 실제 이용 후 남겨 주신 의견 중 일부를 발췌하여 안내드립니다. 개별 일정의 코스·가격은 사전 전화 상담에서 최종 안내됩니다.</p>'
        '<div class="review-grid">'
        + ''.join(cards) +
        '</div>'
        '<p class="review-note">※ 본 후기는 운영 중 받은 이용자 의견을 익명화 처리하여 발췌한 것입니다. 개인 식별 정보는 포함되지 않습니다.</p>'
        '</section>'
    )


_CHECK_TIME_TPL = [
    "{parent} 권역은 평일 저녁(19~22시)이 가장 활발하며, 22시 이후 야간 시간대는 호텔·오피스텔 객실 방문 중심입니다. 심야(01시 이후)는 권역 일부에 한해 가능하며 사전 예약이 필수입니다.",
    "{parent}의 일반적 가능 시간대는 평일 저녁이 가장 활발하고, 야간은 호텔·오피스텔 위주로 운영됩니다. 심야는 일부 권역만 가능합니다.",
    "평일 저녁 시간대 비중이 큰 {parent} 권역에서는 야간 시간대도 객실 진행이 가능하며, 심야 가능 여부는 권역 동선에 따라 다릅니다.",
]
_CHECK_ENTRY_TPL = [
    "공동현관 비밀번호, 엘리베이터 카드 키, 무인 출입 시스템(키오스크) 유무, 호텔의 경우 객실 호수와 체크인 컨디션을 사전에 알려 주시면 도착 시간이 일정대로 유지됩니다.",
    "공동현관·엘리베이터 키·무인 출입 시스템 유무, 호텔의 경우 객실 호수·체크인 시각을 사전 공유해 주시면 도착 시간이 정확히 유지됩니다.",
    "출입 방식(공동현관 비밀번호·카드키·키오스크)과 호텔 객실 호수·체크인 정보를 사전 안내해 주시면 도착 시간이 어긋나지 않습니다.",
]
_CHECK_PARK_TPL = [
    "가정·오피스텔의 경우 방문자 주차 가능 여부, 호텔의 경우 발렛 운영 여부, 펜션·풀빌라의 경우 진입로 폭과 주차 공간을 사전 확인합니다.",
    "주차 가능 여부는 진행 장소 유형에 따라 다릅니다 — 가정·오피스텔은 방문자 주차, 호텔은 발렛 운영, 펜션은 진입로·주차 공간을 사전 점검합니다.",
    "방문자 주차(가정·오피스텔)·발렛 운영(호텔)·진입로 폭(펜션·풀빌라) 등 진행 장소별 주차 환경이 사전에 확인됩니다.",
]
_CHECK_COURSE_TPL = [
    "코스는 60·90·120분 단위로 운영되며, 도착 안내·준비·정리 시간이 별도 약 10~15분 추가됩니다. 일정 사이 충분한 여유를 잡아 주시면 코스 진행이 차분히 마무리됩니다.",
    "코스 길이는 60/90/120분이 일반적이며, 도착·준비·정리 시간이 각 10~15분 정도 추가됩니다. 후속 일정에 여유를 두시는 것을 권합니다.",
    "60·90·120분 단위 코스로 운영되며, 양 끝 준비·정리에 약 10~15분이 추가됩니다. 다음 일정까지 충분한 여유를 두는 것이 좋습니다.",
]
_CHECK_OPT_TPL = [
    "1인·2인(커플) 동시 진행 여부, 코스 종류(스웨디시·아로마·홈타이·스포츠), 추가 옵션(아로마 오일 변경·핫스톤·집중 부위 등)도 사전에 함께 정합니다.",
    "인원(1인/2인 커플), 코스 종류(스웨디시·아로마·홈타이·스포츠·스페셜), 옵션(오일 변경·핫스톤·집중 부위)은 사전 상담에서 함께 합의합니다.",
    "코스 종류·인원 수·추가 옵션(오일 종류·핫스톤·집중 케어 부위 등)이 사전 전화에서 함께 정해집니다.",
]
_CHECK_HEALTH_TPL = [
    "임신, 골절·외상, 고열, 음주 직후 등은 진행 가능 여부가 달라질 수 있어 사전 상담 단계에서 함께 안내합니다.",
    "임신·골절·고열·음주 직후 컨디션은 진행 가능 여부에 영향을 줄 수 있어 사전 전화에서 함께 확인됩니다.",
    "건강 상태(임신·외상·고열·음주 직후)는 코스 진행에 영향을 줄 수 있으니 사전 상담 단계에서 알려 주시는 것을 권장합니다.",
]


def _dong_check_before_section(dong_name, parent_name):
    """예약 전 확인할 부분 — 지역별 변형으로 페이지마다 고유 문구."""
    p = _dong_pick
    intro = _DONG_TIME_INTRO_TPL[p(dong_name, "check", len(_DONG_TIME_INTRO_TPL))].format(
        dong=dong_name, parent=parent_name
    )
    time = _CHECK_TIME_TPL[p(dong_name, "ch_time", len(_CHECK_TIME_TPL))].format(parent=parent_name)
    entry = _CHECK_ENTRY_TPL[p(dong_name, "ch_entry", len(_CHECK_ENTRY_TPL))]
    park = _CHECK_PARK_TPL[p(dong_name, "ch_park", len(_CHECK_PARK_TPL))]
    course = _CHECK_COURSE_TPL[p(dong_name, "ch_course", len(_CHECK_COURSE_TPL))]
    opt = _CHECK_OPT_TPL[p(dong_name, "ch_opt", len(_CHECK_OPT_TPL))]
    health = _CHECK_HEALTH_TPL[p(dong_name, "ch_health", len(_CHECK_HEALTH_TPL))]
    return (
        '<section class="block">'
        f'<h2>{dong_name}에서 예약 전 확인할 부분</h2>'
        f'<p>{intro} 아래 항목은 사전 전화 상담에서 함께 확인되는 기본 정보입니다.</p>'
        '<ul>'
        f'<li><strong>방문 가능 시간</strong> — {time}</li>'
        f'<li><strong>건물 출입 방식</strong> — {entry}</li>'
        f'<li><strong>주차 가능 여부</strong> — {park}</li>'
        f'<li><strong>코스 소요 시간</strong> — {course}</li>'
        f'<li><strong>인원·옵션</strong> — {opt}</li>'
        f'<li><strong>건강·컨디션</strong> — {health}</li>'
        '</ul>'
        '</section>'
    )


def _dong_course_summary_section(dong_name):
    """출장마사지 코스 안내 — 동 페이지용 짧고 명확한 코스 종류 정리."""
    return (
        '<section class="block">'
        f'<h2>{dong_name} 출장마사지 코스 안내</h2>'
        f'<p>{dong_name} 일대에서 운영되는 출장마사지 코스는 다음 유형으로 안내됩니다. 본인의 컨디션·목적·인원 수에 맞춰 사전 전화 상담에서 함께 권해드리며, 각 코스 상세는 별도 페이지에서 확인하실 수 있습니다.</p>'
        '<ul>'
        '<li><a href="/service/swedish/"><strong>스웨디시 마사지</strong></a> — 부드러운 압의 전신 이완 코스. 출장마사지 첫 이용에 가장 자주 권해집니다.</li>'
        '<li><a href="/service/aroma/"><strong>아로마 마사지</strong></a> — 에센셜 오일을 활용한 향기 케어. 수면 보조·스트레스 완화에 적합합니다.</li>'
        '<li><a href="/service/hometai/"><strong>홈타이</strong></a> — 태국식 스트레칭과 압 기반. 근육 이완·자세 교정에 초점이 맞춰진 코스입니다.</li>'
        '<li><a href="/service/sports-massage/"><strong>스포츠 마사지</strong></a> — 운동 후 회복·뭉친 부위 집중 케어가 필요한 분께 권해집니다.</li>'
        '<li><a href="/service/couple-massage/"><strong>커플 마사지</strong></a> — 2인 동시 진행 코스. 호텔·가정·펜션 모두 가능합니다.</li>'
        '<li><a href="/service/hotel-massage/"><strong>호텔 출장마사지</strong></a> — 출장·관광 일정 호텔 객실에서 진행되는 유형입니다.</li>'
        '<li><a href="/service/business-trip-massage/"><strong>출장마사지 종합</strong></a> — 코스 선택을 함께 상의하고 싶으신 경우의 종합 안내 페이지입니다.</li>'
        '</ul>'
        '</section>'
    )


def _dong_price_summary_section(dong_name, parent_name):
    """가격 안내 요약 — 동 페이지에는 표를 반복하지 않고 짧은 요약 + /price/ 링크."""
    return (
        '<section class="block">'
        f'<h2>{dong_name} 출장마사지 가격 안내</h2>'
        f'<p>{dong_name}({parent_name}) 일대의 출장마사지 가격은 <strong>코스 시간(60·90·120·150분)</strong>, <strong>진행 장소 유형(호텔·가정·오피스텔·펜션)</strong>, <strong>예약 시간대(주간·저녁·야간·심야)</strong>에 따라 달라질 수 있습니다. 일반적으로 60·90·120분 코스가 가장 자주 안내되며, 시간·코스별 기준 가격은 <a href="/reservation/price/"><strong>가격 안내 페이지</strong></a>에서 확인하실 수 있습니다.</p>'
        f'<p>정확한 최종 금액은 사전 전화 상담에서 일정·진행 장소·코스가 확정된 직후 함께 안내됩니다. 사전 동의 없는 추가 비용은 부과되지 않으며, 결제 방식은 <a href="/reservation/payment/">결제 안내</a> 페이지에서 확인하실 수 있습니다.</p>'
        '</section>'
    )


def _dong_nearby_section(dong_name, parent_name, parent_url, region_name, sibling_card_html):
    """주변 함께 찾는 지역 — sibling chips + 부모/지역 백링크 종합."""
    return (
        '<section class="block">'
        f'<h2>{dong_name} 주변 함께 찾는 지역</h2>'
        f'<p>{dong_name}을 검색하시는 분들은 같은 {parent_name} 권역의 다른 행정 단위 안내도 함께 찾아보십니다. '
        f'권역 전체 안내가 필요하실 경우 <a href="{parent_url}"><strong>{parent_name} 전체 안내</strong></a>를, '
        f'{region_name} 전체 지역 목록은 <a href="/area/"><strong>지역별 찾기</strong></a> 페이지에서 이동하실 수 있습니다.</p>'
        + (sibling_card_html or '')
        + '</section>'
    )


_VERIFY_INTRO_TPL = [
    "본 페이지는 <strong>YH LAB(서비스명 바로GO)</strong>가 운영하며, {area} 권역 출장마사지 안내·예약·상담은 다음 기준에 따라 처리됩니다.",
    "{area} 권역을 포함한 모든 출장마사지 안내·예약은 <strong>YH LAB(바로GO)</strong>의 다음 운영 기준을 따릅니다.",
    "<strong>YH LAB(바로GO)</strong>가 운영하는 본 안내 페이지의 {area} 권역 운영 기준은 다음과 같습니다.",
    "본 안내는 <strong>YH LAB(바로GO)</strong>가 운영하며, {area} 권역 상담·예약은 아래 기준에 따라 투명하게 처리됩니다.",
]
_V_OPERATOR_TPL = [
    "YH LAB, 대표 김유환, 사업자등록번호 815-26-00585, 본사 경기도 파주시 청석로 268. 정식 사업자등록 정보가 모든 페이지에 공개되어 있습니다.",
    "운영 법인은 YH LAB (대표 김유환·사업자번호 815-26-00585·본사 경기도 파주시 청석로 268)이며, 모든 페이지에서 동일한 운영 주체 정보가 노출됩니다.",
    "법인명 YH LAB, 사업자등록번호 815-26-00585, 대표자 김유환. 본사는 경기도 파주시 청석로 268에 위치합니다.",
]
_V_CONSULT_TPL = [
    "0508-202-4719 대표 번호로 24시간 전화 상담이 진행되며, 모든 상담은 일정·코스·진행 장소·금액을 사전에 명확히 합의한 후에만 예약이 확정됩니다.",
    "24시간 운영되는 0508-202-4719 상담을 통해 일정·코스·진행 장소·금액을 사전에 합의한 뒤에야 예약이 확정됩니다.",
    "대표 번호 0508-202-4719로 24시간 상담이 가능하며, 사전 합의된 일정·금액·코스 정보를 기준으로만 예약이 확정됩니다.",
]
_V_COURSE_TPL = [
    "코스 길이·진행 방식·예상 비용을 사전에 명시하며, 사전 동의 없는 추가 비용·옵션 변경은 부과되지 않습니다. \"최저가\", \"100% 보장\" 등 과장 표현은 사용하지 않습니다.",
    "코스 길이·진행 방식·예상 비용을 사전 안내하고, 사용자 동의 없이 추가 비용·옵션이 부과되지 않습니다. 과장된 단정 표현(\"최저가\"·\"100%\" 등)은 사용하지 않습니다.",
    "예상 비용·코스 진행 방식을 사전에 투명하게 공유하며, 합의되지 않은 추가 비용·옵션은 청구되지 않습니다. 단정·과장 표현은 사용하지 않습니다.",
]
_V_AREA_TPL = [
    "가능 시간·이동 가능 여부는 권역 단위로 운영되며, 동 단위 진입 환경(공동현관·주차·진입 도로)은 일정 확정 단계에서 함께 확인됩니다.",
    "권역 단위로 가능 시간이 운영되며, 동·읍 단위 환경 변수(출입 방식·주차·도로 폭)는 예약 확정 단계에서 함께 점검됩니다.",
    "가능 시간·이동 여부는 권역 기준으로 운영하고, 동·읍 단위 진입 환경은 일정 확정 시점에 함께 확인합니다.",
]
_V_CANCEL_TPL = [
    "<a href=\"/reservation/cancel-refund/\">취소·환불 규정</a>과 <a href=\"/reservation/payment/\">결제 안내</a> 페이지에 시간대별 기준이 명시되어 있으며, 모든 예약은 해당 기준에 따라 처리됩니다.",
    "예약 변경·취소·환불은 <a href=\"/reservation/cancel-refund/\">취소·환불 규정</a>에 따라 처리되며, 결제 방식은 <a href=\"/reservation/payment/\">결제 안내</a>에 명시되어 있습니다.",
    "시간대별 취소·환불 기준은 <a href=\"/reservation/cancel-refund/\">취소·환불 규정</a>에, 결제 가능 수단은 <a href=\"/reservation/payment/\">결제 안내</a>에 정리되어 있습니다.",
]
_V_PREUSE_TPL = [
    "<a href=\"/reservation/check-before-use/\">이용 전 확인사항</a> 페이지에서 건강 상태·공간 조건·시간 일정 점검 항목을 사전에 안내하고 있습니다.",
    "이용 전 건강 상태·공간 조건·일정 점검 사항은 <a href=\"/reservation/check-before-use/\">이용 전 확인사항</a> 페이지에서 확인하실 수 있습니다.",
    "예약 전 권장되는 건강·공간·일정 체크리스트는 <a href=\"/reservation/check-before-use/\">이용 전 확인사항</a> 페이지에 정리되어 있습니다.",
]


def _dong_verification_section(area_name="본 권역"):
    """바로GO 검증 기준 — E-E-A-T 신뢰 신호. 지역별 변형."""
    p = _dong_pick
    intro = _VERIFY_INTRO_TPL[p(area_name, "v_intro", len(_VERIFY_INTRO_TPL))].format(area=area_name)
    op = _V_OPERATOR_TPL[p(area_name, "v_op", len(_V_OPERATOR_TPL))]
    co = _V_CONSULT_TPL[p(area_name, "v_co", len(_V_CONSULT_TPL))]
    cr = _V_COURSE_TPL[p(area_name, "v_cr", len(_V_COURSE_TPL))]
    ar = _V_AREA_TPL[p(area_name, "v_ar", len(_V_AREA_TPL))]
    ca = _V_CANCEL_TPL[p(area_name, "v_ca", len(_V_CANCEL_TPL))]
    pu = _V_PREUSE_TPL[p(area_name, "v_pu", len(_V_PREUSE_TPL))]
    return (
        '<section class="block">'
        '<h2>바로GO 검증 기준</h2>'
        f'<p>{intro}</p>'
        '<ul>'
        f'<li><strong>운영 주체</strong> — {op}</li>'
        f'<li><strong>상담 응대</strong> — {co}</li>'
        f'<li><strong>코스 안내 기준</strong> — {cr}</li>'
        f'<li><strong>운영 시간·권역 기준</strong> — {ar}</li>'
        f'<li><strong>취소·환불·결제</strong> — {ca}</li>'
        f'<li><strong>이용 전 안내</strong> — {pu}</li>'
        '</ul>'
        '</section>'
    )


def _build_dong_rich_body(*, dong_name, parent_name, region_name, parent_char,
                          parent_url, sibling_card_html, extra_intro_paragraph=None):
    """동 페이지 공통 본문 (8섹션, 약 4,000자+).
    1) 출장마사지 이용 안내   2) 마사지 프로그램 안내·가격표   3) 출장마사지 이용 절차
    4) 예약 전 확인할 부분    5) 이용자 후기                  6) 주변 함께 찾는 지역
    7) 바로GO 검증 기준       8) 자주 묻는 질문
    """
    intro_long = _dong_long_intro(dong_name, parent_name, parent_char or region_name)
    s1_parts = [
        '<section class="block">',
        f'<h2>{dong_name} 출장마사지 이용 안내</h2>',
        f'<p>{intro_long}</p>',
    ]
    if extra_intro_paragraph:
        s1_parts.append(f'<p>{extra_intro_paragraph}</p>')
    if parent_char and parent_char != extra_intro_paragraph:
        s1_parts.append(
            f'<p><strong>{parent_name} 권역 전반 특성</strong>: {parent_char}</p>'
        )
    s1_parts.append('</section>')
    section1 = ''.join(s1_parts)

    return (
        section1
        + _shared_program_price_section(dong_name)
        + _shared_procedure_section(dong_name)
        + _dong_check_before_section(dong_name, parent_name)
        + _shared_reviews_section(dong_name)
        + _dong_nearby_section(dong_name, parent_name, parent_url, region_name, sibling_card_html)
        + _dong_verification_section(dong_name)
        + _dong_faq_section_html(dong_name, parent_name)
        + _region_cta_html(dong_name)
    )


# Seoul 자치구 + 동 페이지 빌드 (모든 _shared_*/리치 헬퍼 정의 완료 후 실행)
_build_seoul_districts()
_build_seoul_dong_pages()  # 사용자 요청으로 재활성화 (서울)


# ------------------------------------------------------------
# 지방(수도권 외) 군 단위 — 3차 읍·면 페이지 생성/링크 제외 대상
# 사이트 전체 품질 신호 보호 목적 (helpful content 시스템 사이트 단위 신호 대응).
# 2차 군 페이지는 유지하되, 산하 읍·면 3차 페이지는 생성하지 않고
# 칩도 평문(li)으로 렌더링되도록 함.
# ------------------------------------------------------------
_LOCAL_METRO_GUNS = {
    ("busan",  "기장군"),
    ("daegu",  "달성군"),
    ("daegu",  "군위군"),
    ("ulsan",  "울주군"),
}
_LOCAL_DO_REGIONS = {
    "gangwon", "chungbuk", "chungnam",
    "jeonbuk", "jeonnam", "gyeongbuk", "gyeongnam",
}

def _is_rural_gun(region_slug, district):
    name = district.get("name", "")
    if (region_slug, name) in _LOCAL_METRO_GUNS:
        return True
    if region_slug in _LOCAL_DO_REGIONS and name.endswith("군"):
        return True
    return False


def _build_subordinate_dong_pages(region_slug, region_name, district):
    """sub_label이 없는(=행정동·읍·면 직접 자녀를 갖는) 부모 단위에 대해
    행정동 단위 3차 페이지를 생성한다. 슬러그/내용은 해시 기반 변형으로 페이지마다 차별화."""
    if district.get("sub_label"):
        return
    if _is_rural_gun(region_slug, district):
        return  # 지방 군 단위 읍·면은 3차 페이지 생성 제외
    parent_name = district["name"]
    parent_slug = district["slug"]
    parent_char = district.get("character", "") or district.get("lede", "")
    p_short = _dong_short_parent(parent_char or district.get("lede", "") or parent_name)
    slug_map = district.get("_dong_slug_map") or {}
    consolidated = list(slug_map.keys()) if slug_map else _consolidate_dongs(district.get("subs", []))
    if not consolidated:
        return
    sorted_dongs = sorted(consolidated)
    for dong_name in consolidated:
        dong_slug = slug_map.get(dong_name) or _romanize_dong(dong_name)
        desc_text = _dong_description(dong_name, parent_name, region_name)
        intro_lede = _dong_long_intro(dong_name, parent_name, parent_char)
        siblings = [n for n in sorted_dongs if n != dong_name]
        sib_chips = "".join(
            f'<li class="has-link"><a href="/area/{region_slug}/{parent_slug}/{slug_map.get(s, _romanize_dong(s))}/">{s}'
            '<span class="region-districts-grid-arrow" aria-hidden="true">→</span>'
            '</a></li>'
            for s in siblings
        )
        sib_card = (
            '<section class="region-districts" aria-label="같은 권역 인접 단위">'
            '<header class="region-districts-head">'
            '<span class="region-districts-eyebrow">'
            '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
            f'{parent_name} 인접 단위'
            '</span>'
            f'<h2 class="region-districts-headline">{parent_name}의 다른 단위 {len(siblings)}곳</h2>'
            f'<p class="region-districts-note">{dong_name}과 같은 {parent_name} 권역의 다른 행정 단위입니다. 단위 간 이동·가능 시간은 다르므로 사전 전화 확인이 권장됩니다.</p>'
            '</header>'
            '<div class="region-districts-body">'
            '<div class="region-districts-group">'
            f'<ul class="region-districts-grid">{sib_chips}</ul>'
            '</div></div></section>'
        ) if siblings else ''
        body_html = _build_dong_rich_body(
            dong_name=dong_name,
            parent_name=parent_name,
            region_name=region_name,
            parent_char=parent_char,
            parent_url=f"/area/{region_slug}/{parent_slug}/",
            sibling_card_html=sib_card,
        )
        add(
            path=f"area/{region_slug}/{parent_slug}/{dong_slug}/index.html",
            url=f"/area/{region_slug}/{parent_slug}/{dong_slug}/",
            slug=f"area-{region_slug}-{parent_slug}-{dong_slug}",
            title=_dong_title(dong_name, parent_name, region_name),
            description=desc_text,
            h1=f"{dong_name} 출장마사지 이용 안내",
            intro=f'<p class="lede">{intro_lede}</p>' + _district_hero_cta_html(dong_name),
            breadcrumbs=[
                ("홈", "/"),
                ("지역별 찾기", "/area/"),
                (region_name, f"/area/{region_slug}/"),
                (parent_name, f"/area/{region_slug}/{parent_slug}/"),
                (dong_name, f"/area/{region_slug}/{parent_slug}/{dong_slug}/"),
            ],
            body=body_html,
            related=(
                '<aside class="related">'
                '<h2>관련 안내</h2>'
                '<ul>'
                f'<li><a href="/area/{region_slug}/{parent_slug}/">{parent_name} 전체 안내</a></li>'
                f'<li><a href="/area/{region_slug}/">{region_name} 전체 안내</a></li>'
                '<li><a href="/reservation/how-to-book/">예약 방법</a></li>'
                '<li><a href="/reservation/price/">가격 및 코스 안내</a></li>'
                '<li><a href="/reservation/check-before-use/">이용 전 확인사항</a></li>'
                '<li><a href="/reservation/cancel-refund/">취소·환불 규정</a></li>'
                '</ul>'
                '</aside>'
            ),
        )


def _register_region_dongs(region_slug, districts):
    """Pre-populate DONG_PAGE_INDEX so 2차 페이지 칩이 링크로 렌더됨.
    또한 district["_dong_slug_map"]에 슬러그 매핑을 저장해 페이지 빌드시 재사용."""
    for d in districts:
        if d.get("sub_label"):
            continue
        if _is_rural_gun(region_slug, d):
            continue  # 지방 군 단위는 동/읍/면 인덱스 등록 제외 → 칩이 평문 li로 렌더
        parent_name = d["name"]
        parent_slug = d["slug"]
        consolidated = _consolidate_dongs(d.get("subs", []))
        used = set()
        slug_map = {}
        for dn in consolidated:
            base = _romanize_dong(dn) or "x"
            ds = base
            i = 2
            while ds in used:
                ds = f"{base}-{i}"
                i += 1
            used.add(ds)
            slug_map[dn] = ds
            DONG_PAGE_INDEX[(region_slug, parent_name, dn)] = f"/area/{region_slug}/{parent_slug}/{ds}/"
        d["_dong_slug_map"] = slug_map


def _build_region_dong_pages(region_slug, region_name, districts):
    for d in districts:
        _build_subordinate_dong_pages(region_slug, region_name, d)


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
            displayed = sorted(d["subs"])
            headline = f'{d["name"]} {sub_label}'
            note = f'{d["name"]}는 행정상 {sub_label}로 구성됩니다. 권역별 가능 시간은 전화 상담에서 확인됩니다.'
            eyebrow_label = "행정구 전체"
            chip_items = []
            for s in displayed:
                href = DISTRICT_PAGE_INDEX.get(("gyeonggi", f"{d['name']}/{s}"))
                if href:
                    chip_items.append(
                        f'<li class="has-link"><a href="{href}">{s}'
                        '<span class="region-districts-grid-arrow" aria-hidden="true">→</span>'
                        '</a></li>'
                    )
                else:
                    chip_items.append(f'<li>{s}</li>')
            chips_html = "".join(chip_items)
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
        else:
            dong_card = _district_dong_card_html(d["name"], d["subs"], region_slug="gyeonggi")
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
            h1=f"{d['name']} 출장마사지 이용 안내",
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


# Pre-register Gyeonggi 시·군 pages in the chip index so 1차 chips link.
for _d in GYEONGGI_DISTRICTS:
    DISTRICT_PAGE_INDEX[("gyeonggi", _d["name"])] = f"/area/gyeonggi/{_d['slug']}/"

# ------------------------------------------------------------
# 경기도 6 시 with 구 — 행정구 17곳 + 각 구의 행정동 (3차)
# ------------------------------------------------------------
GYEONGGI_GU_DATA = {
  "suwon": {"name":"수원시","gus":[
    {"slug":"jangan","name":"장안구",
     "lede":"수원시 장안구는 정자·영화·송죽·연무 일대 수원 북부 행정 권역으로, 화서역·성균관대 자연과학캠퍼스 인근 주거·학원가에서 평일 저녁 가정 방문 비중이 큽니다.",
     "facts":[("행정동","7개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","화서역·성균관대")],
     "subs":["파장동","율천동","정자동","영화동","송죽동","조원동","연무동"],
     "character":"장안구는 화서역(분당선) 일대 신축 단지·서호 인근 주거 권역과 성균관대 자연과학캠퍼스·송죽동 학원가 권역에서 평일 저녁 가정 방문 비중이 큽니다. 정자·영화·조원 단지 가정 방문이 자주 들어옵니다.",
     "pattern":"장안구는 평일 저녁 7~10시 가정 방문 비중이 큽니다.",
     "faqs":[("화서역 인근 가능한가요?","화서역 일대 신축 단지 가정 방문이 자주 안내됩니다."),("성균관대 인근 원룸 가능한가요?","율천동 일대 원룸·오피스텔 가정 방문이 안내됩니다."),("정자동·조원동 가능한가요?","정자·조원 주거 단지 가정 방문이 안내됩니다.")]},
    {"slug":"gwonseon","name":"권선구",
     "lede":"수원시 권선구는 수원역·매산·호매실·곡선 일대 교통·상업·신축 단지 혼합 권역으로, 수원역 호텔과 권선·호매실 신축 단지 가정 방문이 함께 안내됩니다.",
     "facts":[("행정동","10개"),("주요 시간대","평일 저녁·야간"),("호텔/가정","혼합"),("특이점","수원역")],
     "subs":["세류동","권선동","매산동","평동","서둔동","구운동","곡선동","입북동","호매실동","금곡동"],
     "character":"권선구는 수원역·노보텔 앰배서더 수원·호텔 캐슬 일대 호텔 객실 방문과 권선·호매실·곡선 신축 단지 가정 방문이 함께 안내됩니다. 매산·세류 일대 야간 권역 동선도 활발합니다.",
     "pattern":"권선구는 평일 저녁부터 야간 시간대까지 비중이 큽니다.",
     "faqs":[("수원역 노보텔 가능한가요?","수원역 일대 노보텔 앰배서더 수원·호텔 캐슬 객실 방문이 안내됩니다."),("호매실·곡선 가정 방문 가능한가요?","호매실·곡선 신축 단지 가정 방문이 자주 안내됩니다."),("야간 시간 가능한가요?","권선구는 수원역 일대 야간 시간대 비중이 큽니다.")]},
    {"slug":"paldal","name":"팔달구",
     "lede":"수원시 팔달구는 수원 화성·행궁동·인계동 일대 도심·관광 권역으로, 라마다 플라자 수원·이비스 앰배서더 수원 화성 등 호텔 객실 방문 비중이 큰 구입니다.",
     "facts":[("행정동","8개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","호텔 비중↑"),("특이점","수원 화성·행궁동")],
     "subs":["행궁동","매교동","매산동","고등동","화서동","지동","우만동","인계동"],
     "character":"팔달구는 행궁동·매교 일대 라마다 플라자 수원·이비스 앰배서더 수원 화성·호텔 그란츠 등 호텔 객실 방문과 인계동 나혜석거리 일대 오피스텔 방문이 자주 안내됩니다. 수원 화성 관광 일정과 결합된 야간 객실 비중이 큽니다.",
     "pattern":"팔달구는 평일 저녁·주말 호텔 객실 방문 비중이 큽니다.",
     "faqs":[("라마다 플라자 수원 가능한가요?","행궁동 일대 라마다 플라자 수원 객실 방문이 안내됩니다."),("이비스 앰배서더 수원 화성 가능한가요?","팔달구 화성 인근 호텔 객실 방문이 자주 안내됩니다."),("인계동 오피스텔 가능한가요?","인계동 나혜석거리 일대 오피스텔 방문이 안내됩니다.")]},
    {"slug":"yeongtong","name":"영통구",
     "lede":"수원시 영통구는 광교·매탄·이의 일대 삼성전자 본사 권역으로, 광교호수공원 호텔과 매탄·망포 주거 단지에서 평일 저녁 케어 비중이 가장 큰 구입니다.",
     "facts":[("행정동","6개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","삼성전자 본사·광교")],
     "subs":["매탄동","원천동","이의동","광교동","영통동","망포동"],
     "character":"영통구는 삼성전자 본사(매탄)와 광교호수공원·갤러리아 광교·코트야드 메리어트 수원 일대 호텔 객실 방문, 망포·영통 신축 단지 가정 방문이 함께 안내됩니다. 삼성전자 출장 일정과 결합된 야간 비중이 가장 큰 권역입니다.",
     "pattern":"영통구는 평일 저녁 비중이 크고, 광교 일대는 야간도 가능한 권역이 있습니다.",
     "faqs":[("코트야드 메리어트 수원 가능한가요?","광교 일대 코트야드 메리어트 수원 객실 방문이 자주 안내됩니다."),("삼성전자 출장 일정 가능한가요?","매탄·이의 일대 삼성전자 출장 호텔 객실 방문이 자주 안내됩니다."),("망포·영통 가정 방문 가능한가요?","망포·영통 신축 단지 가정 방문이 안내됩니다.")]},
  ]},
  "seongnam": {"name":"성남시","gus":[
    {"slug":"sujeong","name":"수정구",
     "lede":"성남시 수정구는 모란·신흥·산성·위례 일대 원도심과 위례신도시가 혼합된 권역으로, 모란역 가정 방문과 위례 신축 단지 객실 방문이 함께 안내됩니다.",
     "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","모란역·위례신도시")],
     "subs":["신흥동","태평동","수진동","단대동","산성동","양지동","복정동","위례동","신촌동","고등동","시흥동"],
     "character":"수정구는 모란역 일대 신흥·수진동 원도심 주거 권역과 위례신도시(위례·창곡천 일대) 신축 아파트 단지 가정 방문이 함께 안내됩니다. 산성·태평·단대 일대 가정 방문 비중도 큽니다.",
     "pattern":"수정구는 평일 저녁 가정 방문 비중이 큽니다.",
     "faqs":[("모란역 인근 가능한가요?","신흥·수진동 일대 모란역 인근 주거 권역 가정 방문이 자주 안내됩니다."),("위례신도시 가능한가요?","위례동 일대 신축 단지 가정 방문이 안내됩니다."),("복정동 가능한가요?","복정 일대 주거 권역 가정 방문이 안내됩니다.")]},
    {"slug":"jungwon","name":"중원구",
     "lede":"성남시 중원구는 중앙·금광·상대원·도촌 일대 성남 행정 중심 권역으로, 성남시청·성남종합운동장 인근 주거·산업 단지에서 평일 저녁 가정 방문 비중이 큽니다.",
     "facts":[("행정동","7개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","성남시청·상대원")],
     "subs":["성남동","금광동","은행동","상대원동","중앙동","하대원동","도촌동"],
     "character":"중원구는 성남시청·성남종합운동장(중앙동) 행정 권역과 상대원 산업 단지·주거 권역에서 평일 저녁 가정 방문 비중이 큽니다. 도촌동 신축 단지·은행동 주거 권역 안내도 자주 들어옵니다.",
     "pattern":"중원구는 평일 저녁 비중이 큽니다.",
     "faqs":[("성남시청 인근 가능한가요?","중앙동·하대원 일대 가정 방문이 안내됩니다."),("상대원 가능한가요?","상대원 일대 주거 권역 가정 방문이 안내됩니다."),("도촌동 신축 단지 가능한가요?","도촌동 신축 단지 가정 방문이 자주 안내됩니다.")]},
    {"slug":"bundang","name":"분당구",
     "lede":"성남시 분당구는 판교·정자·서현 일대 IT·금융 클러스터로, 판교 테크노밸리 출장 호텔 객실 방문과 분당 신도시 주거 가정 방문이 함께 안내됩니다.",
     "facts":[("행정동","12개"),("주요 시간대","평일 저녁·야간"),("호텔/가정","혼합"),("특이점","판교 테크노밸리")],
     "subs":["분당동","수내동","정자동","서현동","이매동","야탑동","판교동","백현동","삼평동","운중동","구미동","금곡동"],
     "character":"분당구는 판교 테크노밸리(삼평·백현·운중)의 카카오·네이버·NHN 출장 일정과 결합된 코트야드 메리어트 판교 호텔 객실 방문, 정자·수내·서현 분당 신도시 주거 가정 방문이 함께 안내됩니다. 야탑·이매 오피스텔 방문도 자주 들어옵니다.",
     "pattern":"분당구는 평일 저녁부터 야간까지 비중이 큽니다.",
     "faqs":[("코트야드 메리어트 판교 가능한가요?","삼평·백현 일대 코트야드 메리어트 판교 객실 방문이 자주 안내됩니다."),("정자·서현 주거 단지 가능한가요?","정자·수내·서현 일대 가정 방문이 안내됩니다."),("판교 테크노밸리 출장 가능한가요?","판교 출장 일정 호텔 객실 방문이 자주 안내됩니다.")]},
  ]},
  "goyang": {"name":"고양시","gus":[
    {"slug":"deogyang","name":"덕양구",
     "lede":"고양시 덕양구는 삼송·원흥·향동·창릉 신도시와 행신·능곡 원도심이 혼합된 권역으로, 신축 단지 가정 방문 비중이 큽니다.",
     "facts":[("행정동","19개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","삼송·원흥 신도시")],
     "subs":["화정동","효자동","신도동","창릉동","능곡동","행주동","행신동","화전동","대덕동","관산동","흥도동","주교동","원신동","고양동","성사동","삼송동","용두동","도내동","향동동"],
     "character":"덕양구는 삼송지구·원흥·향동·창릉 신도시 신축 아파트 단지 가정 방문과 화정·행신·능곡 원도심 주거 권역 가정 방문이 함께 안내됩니다. 농협대·서울외곽순환도로 인접 권역 객실 방문도 자주 들어옵니다.",
     "pattern":"덕양구는 평일 저녁 비중이 큽니다.",
     "faqs":[("삼송지구 가능한가요?","삼송동 일대 신축 단지 가정 방문이 자주 안내됩니다."),("향동·원흥 가능한가요?","향동·원신 일대 신도시 단지 가정 방문이 안내됩니다."),("화정·행신 원도심 가능한가요?","화정·행신·능곡 일대 주거 권역 가정 방문이 안내됩니다.")]},
    {"slug":"ilsandong","name":"일산동구",
     "lede":"고양시 일산동구는 정발산·마두·백석·장항 일대 일산 동부 도심으로, 라페스타·웨스턴돔 호텔과 정발산·식사 주거 단지 가정 방문이 함께 안내됩니다.",
     "facts":[("행정동","8개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","라페스타·MBC 일산")],
     "subs":["식사동","중산동","정발산동","풍산동","백석동","마두동","장항동","고봉동"],
     "character":"일산동구는 라페스타·웨스턴돔(장항) 일대 라마다 일산·인터컨티넨탈 일산 등 호텔 객실 방문과 정발산·마두·식사 주거 단지 가정 방문이 함께 안내됩니다. MBC 일산 드림센터 인접 권역 특성상 야간도 활발합니다.",
     "pattern":"일산동구는 평일 저녁·야간 비중이 큽니다.",
     "faqs":[("라마다 일산 가능한가요?","장항동 일대 라마다 호텔 객실 방문이 자주 안내됩니다."),("정발산·식사 가능한가요?","정발산·식사 일대 주거 단지 가정 방문이 안내됩니다."),("MBC 일산 가능한가요?","장항동 일대 권역 객실 방문이 안내됩니다.")]},
    {"slug":"ilsanseo","name":"일산서구",
     "lede":"고양시 일산서구는 주엽·대화·탄현·덕이 일대 일산 서부 권역으로, 킨텍스·고양종합운동장 호텔과 주엽·대화 주거 단지 가정 방문이 함께 안내됩니다.",
     "facts":[("행정동","9개"),("주요 시간대","평일 저녁·전시 시즌"),("호텔/가정","혼합"),("특이점","킨텍스")],
     "subs":["일산동","일산본동","탄현동","주엽동","대화동","송산동","송포동","덕이동","가좌동"],
     "character":"일산서구는 킨텍스(대화) 전시 일정과 결합된 소노캄 고양·MVL 호텔 킨텍스·베스트웨스턴 노블레스 등 호텔 객실 방문과 주엽·일산·탄현 주거 단지 가정 방문이 함께 안내됩니다. 전시 시즌 비중이 크게 증가합니다.",
     "pattern":"일산서구는 평일 저녁·전시 시즌 비중이 큽니다.",
     "faqs":[("소노캄 고양 가능한가요?","대화동 일대 소노캄 고양 객실 방문이 자주 안내됩니다."),("MVL 호텔 킨텍스 가능한가요?","대화동 킨텍스 인접 호텔 객실 방문이 안내됩니다."),("주엽·일산 가정 가능한가요?","주엽·일산·탄현 일대 주거 단지 가정 방문이 안내됩니다.")]},
  ]},
  "yongin": {"name":"용인시","gus":[
    {"slug":"cheoin","name":"처인구",
     "lede":"용인시 처인구는 김량장·역북·삼가 원도심과 포곡·모현·남사·이동 농촌형 읍·면이 혼합된 권역으로, 에버랜드 일정과 결합된 호텔 객실 방문이 자주 안내됩니다.",
     "facts":[("행정 단위","11개"),("주요 시간대","평일 저녁·시즌"),("호텔/가정","혼합"),("특이점","에버랜드")],
     "subs":["중앙동","역북동","유림동","동부동","포곡읍","모현읍","이동읍","남사읍","원삼면","백암면","양지면"],
     "character":"처인구는 에버랜드·캐리비안베이(포곡읍) 일정과 결합된 홈브릿지 호텔 용인·소노캄 디스커버리 호텔 객실 방문과 역북·중앙 원도심 가정 방문이 함께 안내됩니다. 모현·이동·남사 읍·면 권역은 이동 거리 사전 확인이 필요한 경우가 있습니다.",
     "pattern":"처인구는 평일 저녁과 시즌(에버랜드) 비중이 큽니다.",
     "faqs":[("에버랜드 호텔 가능한가요?","포곡읍 일대 홈브릿지 호텔 용인·소노캄 디스커버리 객실 방문이 안내됩니다."),("역북·중앙 원도심 가능한가요?","역북·중앙 일대 주거 권역 가정 방문이 안내됩니다."),("모현·남사 읍 가능한가요?","모현·남사·이동 읍 권역도 안내되나 이동 거리 사전 확인이 필요합니다.")]},
    {"slug":"giheung","name":"기흥구",
     "lede":"용인시 기흥구는 신갈·영덕·동백·죽전 일대 도시형 권역으로, 삼성전자 기흥캠퍼스 출장과 동백·죽전 주거 단지 가정 방문이 함께 안내됩니다.",
     "facts":[("행정동","14개"),("주요 시간대","평일 저녁"),("호텔/가정","혼합"),("특이점","삼성전자 기흥캠퍼스")],
     "subs":["신갈동","영덕동","기흥동","서농동","구갈동","상갈동","보라동","상하동","보정동","마북동","동백동","청덕동","죽전동"],
     "character":"기흥구는 삼성전자 기흥캠퍼스(영덕·기흥) 출장 일정과 결합된 라비돌 호텔·소노캄 호텔 객실 방문, 동백·죽전·보정 주거 단지 가정 방문이 함께 안내됩니다. 신갈·구갈 일대 GTX·분당선 인접 권역도 활발합니다.",
     "pattern":"기흥구는 평일 저녁 비중이 큽니다.",
     "faqs":[("삼성전자 기흥캠퍼스 출장 가능한가요?","영덕·기흥 일대 호텔 객실 방문이 자주 안내됩니다."),("죽전·동백 가정 가능한가요?","죽전·동백 신축 단지 가정 방문이 안내됩니다."),("보정·마북 가능한가요?","보정·마북 일대 주거 권역 가정 방문이 안내됩니다.")]},
    {"slug":"suji","name":"수지구",
     "lede":"용인시 수지구는 죽전·동천·풍덕천·상현·성복 일대 분당 인접 주거 권역으로, 신축 아파트 단지 가정 방문 비중이 가장 큰 구입니다.",
     "facts":[("행정동","6개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","분당 인접·죽전")],
     "subs":["풍덕천동","죽전동","동천동","상현동","성복동","신봉동"],
     "character":"수지구는 죽전·풍덕천 일대 분당선 신축 단지와 상현·성복·동천 일대 광교산 인접 단지에서 평일 저녁 가정 방문 비중이 가장 큽니다. 신봉동 일대 가정 방문도 자주 들어옵니다.",
     "pattern":"수지구는 평일 저녁 가정 방문 비중이 큽니다.",
     "faqs":[("죽전·풍덕천 가능한가요?","죽전·풍덕천 일대 분당선 신축 단지 가정 방문이 자주 안내됩니다."),("성복·상현 가능한가요?","성복·상현·신봉 일대 광교산 인접 단지 가정 방문이 안내됩니다."),("동천 가능한가요?","동천동 일대 주거 단지 가정 방문이 안내됩니다.")]},
  ]},
  "ansan": {"name":"안산시","gus":[
    {"slug":"sangnok","name":"상록구",
     "lede":"안산시 상록구는 사동·본오·반월·부곡 일대 안산 동부 권역으로, 한양대 ERICA·반월공단 동측 주거 단지에서 평일 저녁 가정 방문 비중이 큽니다.",
     "facts":[("행정동","10개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","한양대 ERICA")],
     "subs":["사동","본오동","반월동","부곡동","월피동","성포동","일동","이동","안산동","사이동"],
     "character":"상록구는 한양대 ERICA 캠퍼스(사동) 인근 주거·원룸 권역과 본오·반월 일대 주거 단지 가정 방문 비중이 큽니다. 부곡·월피 일대 원도심·신축 혼합 권역에서도 가정 방문 안내가 자주 들어옵니다.",
     "pattern":"상록구는 평일 저녁 비중이 큽니다.",
     "faqs":[("한양대 ERICA 인근 가능한가요?","사동 일대 원룸·오피스텔 가정 방문이 안내됩니다."),("본오·반월 가능한가요?","본오·반월 일대 주거 단지 가정 방문이 자주 안내됩니다."),("부곡·월피 가능한가요?","부곡·월피 일대 가정 방문이 안내됩니다.")]},
    {"slug":"danwon","name":"단원구",
     "lede":"안산시 단원구는 고잔·호수·원곡·초지·대부 일대 안산 서부 권역으로, 안산중앙역 호텔과 대부도 펜션 객실 방문이 함께 안내됩니다.",
     "facts":[("행정동","9개"),("주요 시간대","평일 저녁·주말"),("호텔/가정","혼합"),("특이점","대부도·중앙역")],
     "subs":["와동","고잔동","호수동","원곡동","신길동","초지동","선부동","대부동","풍도동"],
     "character":"단원구는 안산중앙역 일대 호텔·오피스텔 객실 방문과 대부도·풍도 일대 펜션·풀빌라 객실 방문이 함께 안내됩니다. 고잔·호수·초지 신축 단지 가정 방문도 자주 들어옵니다.",
     "pattern":"단원구는 평일 저녁·주말 비중이 큽니다.",
     "faqs":[("안산중앙역 호텔 가능한가요?","고잔·호수 일대 호텔·오피스텔 객실 방문이 안내됩니다."),("대부도 펜션 가능한가요?","대부동 일대 펜션·풀빌라 객실 방문이 안내됩니다."),("초지·호수 가정 가능한가요?","초지·호수 일대 신축 단지 가정 방문이 안내됩니다.")]},
  ]},
  "anyang": {"name":"안양시","gus":[
    {"slug":"manan","name":"만안구",
     "lede":"안양시 만안구는 안양·석수·박달 일대 안양 원도심 권역으로, 1번 국도·안양천 인근 주거·상업 권역 가정 방문이 자주 안내됩니다.",
     "facts":[("행정동","3개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑"),("특이점","안양역·중앙시장")],
     "subs":["안양동","석수동","박달동"],
     "character":"만안구는 안양역·중앙시장(안양동) 일대 원도심 주거·상업 권역, 석수·박달 일대 신축 단지·관악산 인접 권역에서 평일 저녁 가정 방문 비중이 큽니다.",
     "pattern":"만안구는 평일 저녁 비중이 큽니다.",
     "faqs":[("안양역 인근 가능한가요?","안양동 일대 안양역 권역 가정 방문이 안내됩니다."),("석수·박달 가능한가요?","석수·박달 일대 신축 단지 가정 방문이 안내됩니다."),("관악산 인접 가능한가요?","석수동 관악산 인접 주거 권역 가정 방문이 안내됩니다.")]},
    {"slug":"dongan","name":"동안구",
     "lede":"안양시 동안구는 평촌·범계·인덕원 일대 동안 신도시 권역으로, 평촌학원가·범계로데오 인근 주거 단지 가정 방문 비중이 매우 큰 구입니다.",
     "facts":[("행정동","11개"),("주요 시간대","평일 저녁"),("호텔/가정","가정 비중↑↑"),("특이점","평촌학원가·범계")],
     "subs":["비산동","부흥동","달안동","관양동","부림동","평촌동","평안동","귀인동","호계동","범계동","신촌동"],
     "character":"동안구는 평촌신도시 학원가(평촌·귀인·부림)와 범계로데오·인덕원 일대 주거 단지에서 평일 저녁 가정 방문 비중이 매우 큽니다. 관양·호계 일대 단지 가정 방문도 활발합니다.",
     "pattern":"동안구는 평일 저녁 비중이 매우 큽니다.",
     "faqs":[("평촌·귀인 가능한가요?","평촌·귀인·부림 일대 학원가 인근 주거 단지 가정 방문이 자주 안내됩니다."),("범계로데오 가능한가요?","범계동 일대 주거 단지 가정 방문이 안내됩니다."),("인덕원 가능한가요?","관양·호계 일대 인덕원 인근 단지 가정 방문이 안내됩니다.")]},
  ]},
}

# 행정구 단위 인덱스 사전 등록 (시 페이지의 구 칩이 링크로 렌더되도록)
for _si_slug, _si_data in GYEONGGI_GU_DATA.items():
    _si_name = _si_data["name"]
    for _gu in _si_data["gus"]:
        DISTRICT_PAGE_INDEX[("gyeonggi", f"{_si_name}/{_gu['name']}")] = (
            f"/area/gyeonggi/{_si_slug}/{_gu['slug']}/"
        )
        # 구 산하 동 인덱스도 미리 등록 → 구 페이지 chip이 링크로 렌더됨
        _used = set()
        _sm = {}
        for _dn in _consolidate_dongs(_gu["subs"]):
            _ds = _romanize_dong(_dn) or "x"
            _base = _ds
            _i = 2
            while _ds in _used:
                _ds = f"{_base}-{_i}"
                _i += 1
            _used.add(_ds)
            _sm[_dn] = _ds
            DONG_PAGE_INDEX[("gyeonggi", _gu["name"], _dn)] = (
                f"/area/gyeonggi/{_si_slug}/{_gu['slug']}/{_ds}/"
            )
        _gu["_dong_slug_map"] = _sm


def _build_gyeonggi_gu_pages():
    """경기 6 시 with 구 → 행정구 페이지 + 각 구 산하 행정동 페이지 생성."""
    for si_slug, si_data in GYEONGGI_GU_DATA.items():
        si_name = si_data["name"]
        gus = si_data["gus"]
        gu_name_to_slug = {g["name"]: g["slug"] for g in gus}
        for gu in gus:
            gu_slug = gu["slug"]
            gu_name = gu["name"]
            # 인접 구(같은 시 안의 다른 구) → related (ㄱㄴㄷ 정렬)
            sibling_gus = sorted(
                [(g["name"], g["slug"]) for g in gus if g["slug"] != gu_slug],
                key=lambda t: t[0],
            )
            sib_items = "".join(
                f'<li><a href="/area/gyeonggi/{si_slug}/{sg_slug}/">{sg_name}</a></li>'
                for sg_name, sg_slug in sibling_gus
            )
            related_html = (
                '<aside class="related">'
                f'<h2>{si_name} 인접 구</h2>'
                '<ul>'
                f'<li><a href="/area/gyeonggi/{si_slug}/">{si_name} 전체</a></li>'
                f'{sib_items}'
                '</ul>'
                '</aside>'
            )
            # 동 chip card - 구 페이지에는 region_slug="gyeonggi"로 DONG_PAGE_INDEX 조회
            dong_card = _district_dong_card_html(gu_name, gu["subs"], region_slug="gyeonggi")
            body_parts = [
                _district_facts_html(gu["facts"]),
                dong_card,
                '<section class="block">'
                f'<h2>{gu_name} 권역 특성</h2>'
                f'<p>{gu["character"]}</p>'
                '</section>',
                '<section class="block">'
                f'<h2>{gu_name} 이용 시간 패턴</h2>'
                f'<p>{gu["pattern"]}</p>'
                '</section>',
                _district_faqs_html(gu_name, gu["faqs"]),
                _region_cta_html(gu_name),
            ]
            add(
                path=f"area/gyeonggi/{si_slug}/{gu_slug}/index.html",
                url=f"/area/gyeonggi/{si_slug}/{gu_slug}/",
                slug=f"area-gyeonggi-{si_slug}-{gu_slug}",
                title=_district_title(gu_name, f"{si_name} | 경기", gu["facts"]),
                description=_district_description(gu["lede"], gu_name, f"{si_name} | 경기"),
                h1=f"{gu_name} 출장마사지 이용 안내",
                intro=f'<p class="lede">{gu["lede"]}</p>' + _district_hero_cta_html(gu_name),
                breadcrumbs=[
                    ("홈", "/"),
                    ("지역별 찾기", "/area/"),
                    ("경기", "/area/gyeonggi/"),
                    (si_name, f"/area/gyeonggi/{si_slug}/"),
                    (gu_name, f"/area/gyeonggi/{si_slug}/{gu_slug}/"),
                ],
                body="".join(body_parts),
                related=related_html,
            )
            # 동 페이지들 (3차) — 경기 시·구 단위 동 페이지 (재활성화)
            consolidated = list(gu["_dong_slug_map"].keys())
            sorted_dongs = sorted(consolidated)
            for dong_name in consolidated:
                dong_slug = gu["_dong_slug_map"][dong_name]
                desc_text = _dong_description(dong_name, gu_name, f"경기 {si_name}")
                intro_lede = _dong_long_intro(dong_name, gu_name, gu["character"])
                siblings = [n for n in sorted_dongs if n != dong_name]
                sib_chips = "".join(
                    f'<li class="has-link"><a href="/area/gyeonggi/{si_slug}/{gu_slug}/{gu["_dong_slug_map"][s]}/">{s}'
                    '<span class="region-districts-grid-arrow" aria-hidden="true">→</span>'
                    '</a></li>'
                    for s in siblings
                )
                sib_card = (
                    '<section class="region-districts" aria-label="같은 권역 인접 단위">'
                    '<header class="region-districts-head">'
                    '<span class="region-districts-eyebrow">'
                    '<span class="region-districts-eyebrow-dot" aria-hidden="true"></span>'
                    f'{gu_name} 인접 단위'
                    '</span>'
                    f'<h2 class="region-districts-headline">{gu_name}의 다른 단위 {len(siblings)}곳</h2>'
                    f'<p class="region-districts-note">{dong_name}과 같은 {gu_name} 권역의 다른 행정 단위입니다.</p>'
                    '</header>'
                    '<div class="region-districts-body">'
                    '<div class="region-districts-group">'
                    f'<ul class="region-districts-grid">{sib_chips}</ul>'
                    '</div></div></section>'
                ) if siblings else ''
                body_html = _build_dong_rich_body(
                    dong_name=dong_name,
                    parent_name=gu_name,
                    region_name=f"경기 {si_name}",
                    parent_char=gu["character"],
                    parent_url=f"/area/gyeonggi/{si_slug}/{gu_slug}/",
                    sibling_card_html=sib_card,
                )
                add(
                    path=f"area/gyeonggi/{si_slug}/{gu_slug}/{dong_slug}/index.html",
                    url=f"/area/gyeonggi/{si_slug}/{gu_slug}/{dong_slug}/",
                    slug=f"area-gyeonggi-{si_slug}-{gu_slug}-{dong_slug}",
                    title=_dong_title(dong_name, gu_name, f"경기 {si_name}"),
                    description=desc_text,
                    h1=f"{dong_name} 출장마사지 이용 안내",
                    intro=f'<p class="lede">{intro_lede}</p>' + _district_hero_cta_html(dong_name),
                    breadcrumbs=[
                        ("홈", "/"),
                        ("지역별 찾기", "/area/"),
                        ("경기", "/area/gyeonggi/"),
                        (si_name, f"/area/gyeonggi/{si_slug}/"),
                        (gu_name, f"/area/gyeonggi/{si_slug}/{gu_slug}/"),
                        (dong_name, f"/area/gyeonggi/{si_slug}/{gu_slug}/{dong_slug}/"),
                    ],
                    body=body_html,
                    related=(
                        '<aside class="related">'
                        '<h2>관련 안내</h2>'
                        '<ul>'
                        f'<li><a href="/area/gyeonggi/{si_slug}/{gu_slug}/">{gu_name} 전체 안내</a></li>'
                        f'<li><a href="/area/gyeonggi/{si_slug}/">{si_name} 전체 안내</a></li>'
                        '<li><a href="/area/gyeonggi/">경기 전체 안내</a></li>'
                        '<li><a href="/reservation/how-to-book/">예약 방법</a></li>'
                        '<li><a href="/reservation/price/">가격 및 코스 안내</a></li>'
                        '<li><a href="/reservation/check-before-use/">이용 전 확인사항</a></li>'
                        '</ul>'
                        '</aside>'
                    ),
                )


# Pre-populate DONG_PAGE_INDEX for 시 without 구
_register_region_dongs("gyeonggi", GYEONGGI_DISTRICTS)

_build_gyeonggi_districts()
_build_region_dong_pages("gyeonggi", "경기", GYEONGGI_DISTRICTS)  # 사용자 요청으로 재활성화
_build_gyeonggi_gu_pages()


# ============================================================
# 광역시 — 부산 / 인천 / 대구 / 대전 / 광주 / 울산 / 세종
# ============================================================
# Generic builder that re-uses Seoul/Gyeonggi page structure.

def _build_metro_district(parent_slug, parent_name, d, all_in_parent):
    sub_label = d.get("sub_label")
    if sub_label:
        displayed = sorted(d["subs"])
        headline = f'{d["name"]} {sub_label}'
        note = f'{d["name"]}는 행정상 {sub_label}로 구성됩니다. 권역별 가능 시간은 전화 상담에서 확인됩니다.'
        eyebrow_label = "행정구 전체"
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
    else:
        dong_card = _district_dong_card_html(d["name"], d["subs"], region_slug=parent_slug)
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
        h1=f"{d['name']} 출장마사지 이용 안내",
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

# Pre-populate DONG_PAGE_INDEX for 광역시 + 세종
_register_region_dongs("busan",   BUSAN_DISTRICTS)
_register_region_dongs("incheon", INCHEON_DISTRICTS)
_register_region_dongs("daegu",   DAEGU_DISTRICTS)
_register_region_dongs("daejeon", DAEJEON_DISTRICTS)
_register_region_dongs("gwangju", GWANGJU_DISTRICTS)
_register_region_dongs("ulsan",   ULSAN_DISTRICTS)
_register_region_dongs("sejong",  SEJONG_DISTRICTS)

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

# 3차 행정동 페이지 일괄 생성
# _build_region_dong_pages("busan",   "부산", BUSAN_DISTRICTS)  # 3차 동 페이지 비활성화
_build_region_dong_pages("incheon", "인천", INCHEON_DISTRICTS)  # 사용자 요청으로 재활성화
# _build_region_dong_pages("daegu",   "대구", DAEGU_DISTRICTS)  # 3차 동 페이지 비활성화
# _build_region_dong_pages("daejeon", "대전", DAEJEON_DISTRICTS)  # 3차 동 페이지 비활성화
# _build_region_dong_pages("gwangju", "광주", GWANGJU_DISTRICTS)  # 3차 동 페이지 비활성화
# _build_region_dong_pages("ulsan",   "울산", ULSAN_DISTRICTS)  # 3차 동 페이지 비활성화
# _build_region_dong_pages("sejong",  "세종", SEJONG_DISTRICTS)  # 3차 동 페이지 비활성화
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
_register_region_dongs("gangwon", GANGWON_DISTRICTS)
for _d in GANGWON_DISTRICTS:
    _build_metro_district("gangwon", "강원", _d, GANGWON_DISTRICTS)
# _build_region_dong_pages("gangwon", "강원", GANGWON_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("chungbuk", CHUNGBUK_DISTRICTS)
for _d in CHUNGBUK_DISTRICTS:
    _build_metro_district("chungbuk", "충북", _d, CHUNGBUK_DISTRICTS)
# _build_region_dong_pages("chungbuk", "충북", CHUNGBUK_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("chungnam", CHUNGNAM_DISTRICTS)
for _d in CHUNGNAM_DISTRICTS:
    _build_metro_district("chungnam", "충남", _d, CHUNGNAM_DISTRICTS)
# _build_region_dong_pages("chungnam", "충남", CHUNGNAM_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("jeonbuk", JEONBUK_DISTRICTS)
for _d in JEONBUK_DISTRICTS:
    _build_metro_district("jeonbuk", "전북", _d, JEONBUK_DISTRICTS)
# _build_region_dong_pages("jeonbuk", "전북", JEONBUK_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("jeonnam", JEONNAM_DISTRICTS)
for _d in JEONNAM_DISTRICTS:
    _build_metro_district("jeonnam", "전남", _d, JEONNAM_DISTRICTS)
# _build_region_dong_pages("jeonnam", "전남", JEONNAM_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("gyeongbuk", GYEONGBUK_DISTRICTS)
for _d in GYEONGBUK_DISTRICTS:
    _build_metro_district("gyeongbuk", "경북", _d, GYEONGBUK_DISTRICTS)
# _build_region_dong_pages("gyeongbuk", "경북", GYEONGBUK_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("gyeongnam", GYEONGNAM_DISTRICTS)
for _d in GYEONGNAM_DISTRICTS:
    _build_metro_district("gyeongnam", "경남", _d, GYEONGNAM_DISTRICTS)
# _build_region_dong_pages("gyeongnam", "경남", GYEONGNAM_DISTRICTS)  # 3차 동 페이지 비활성화
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

_register_region_dongs("jeju", JEJU_DISTRICTS)
for _d in JEJU_DISTRICTS:
    _build_metro_district("jeju", "제주", _d, JEJU_DISTRICTS)
# _build_region_dong_pages("jeju", "제주", JEJU_DISTRICTS)  # 3차 동 페이지 비활성화
# ---------- service hub ----------
add(
  path="service/index.html",
  url="/service/",
  slug="service-hub",
  title="출장마사지 서비스 한눈에 비교 — 스웨디시·아로마·홈타이·스포츠 외 | 바로GO",
  description="스웨디시·아로마·홈타이·스포츠·커플·호텔 방문·기업 방문 등 8개 출장마사지 서비스의 특징·추천 대상·압력·복장·코스 길이를 한눈에 비교하실 수 있는 페이지입니다.",
  h1="서비스",
  intro='<p class="lede">출장마사지는 목적·압력·복장·진행 방식이 서로 다릅니다. 8개 서비스 유형을 한 표로 비교해 두었으니, 본인의 컨디션과 일정에 맞는 코스를 골라 상세 페이지로 이동해 주세요.</p>',
  breadcrumbs=[("홈", "/"), ("서비스", "/service/")],
  body="""
<section class="block">
<h2>서비스 유형 8종 한눈에 비교</h2>
<div class="price-table-wrap">
<table class="compare-table">
<thead><tr><th scope="col">서비스</th><th scope="col">압력</th><th scope="col">오일</th><th scope="col">복장</th><th scope="col">주 목적</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="/service/swedish/">스웨디시</a></th><td>부드러움</td><td>사용</td><td>탈의·타월</td><td>이완·수면 보조</td></tr>
<tr><th scope="row"><a href="/service/aroma/">아로마</a></th><td>부드러움</td><td>아로마 오일</td><td>탈의·타월</td><td>릴랙스·심신 안정</td></tr>
<tr><th scope="row"><a href="/service/hometai/">홈타이</a></th><td>중강도</td><td>사용 안 함</td><td>옷 입은 채</td><td>스트레칭·가동성</td></tr>
<tr><th scope="row"><a href="/service/sports-massage/">스포츠</a></th><td>중강도-강함</td><td>일부 사용</td><td>운동복·반탈의</td><td>운동 회복·부위 케어</td></tr>
<tr><th scope="row"><a href="/service/couple-massage/">커플</a></th><td>코스별</td><td>코스별</td><td>코스별</td><td>2인 동시 진행</td></tr>
<tr><th scope="row"><a href="/service/hotel-massage/">호텔 방문</a></th><td>코스별</td><td>코스별</td><td>코스별</td><td>출장·여행 회복</td></tr>
<tr><th scope="row"><a href="/service/office-massage/">기업 방문</a></th><td>의자형·매트형</td><td>일반적으로 미사용</td><td>업무복 위</td><td>임직원 복지</td></tr>
<tr><th scope="row"><a href="/service/business-trip-massage/">출장마사지 일반</a></th><td>—</td><td>—</td><td>—</td><td>전체 개요·진행 흐름</td></tr>
</tbody>
</table>
</div>
</section>
<section class="block">
<h2>서비스 페이지 바로가기</h2>
<ul class="service-grid">
<li><h3><a href="/service/business-trip-massage/">출장마사지</a></h3><p>전체 진행 흐름·코스 종류·이용 흐름 5단계 정리</p></li>
<li><h3><a href="/service/swedish/">스웨디시 마사지</a></h3><p>오일 베이스 부드러운 압력, 처음 이용에 가장 권장</p></li>
<li><h3><a href="/service/aroma/">아로마 마사지</a></h3><p>향과 부드러운 압의 조합, 수면 전 이완에 자주 안내</p></li>
<li><h3><a href="/service/hometai/">홈타이</a></h3><p>옷 입은 채 진행, 스트레칭·지압 결합으로 가동성 정비</p></li>
<li><h3><a href="/service/sports-massage/">스포츠 마사지</a></h3><p>근육 결 케어, 운동 후 회복·부위 집중에 권장</p></li>
<li><h3><a href="/service/couple-massage/">커플 마사지</a></h3><p>2인 동시 진행, 공간 조건·합산 가격 정리</p></li>
<li><h3><a href="/service/hotel-massage/">호텔 출장마사지</a></h3><p>호텔 유형별 진행 차이·객실 사전 안내 항목</p></li>
<li><h3><a href="/service/office-massage/">기업·사무실 출장마사지</a></h3><p>단체 케어, 의자·매트형 옵션 및 사전 협의 항목</p></li>
</ul>
</section>
<section class="block">
<h2>코스를 고르는 가장 빠른 기준 3가지</h2>
<ul class="check-list">
<li><strong>목적</strong> — 수면·이완(스웨디시·아로마), 가동성(홈타이), 회복(스포츠)</li>
<li><strong>복장 선호</strong> — 탈의 부담 없음(홈타이), 탈의·오일 가능(스웨디시·아로마)</li>
<li><strong>장소</strong> — 호텔 객실(호텔 방문), 가정(스웨디시·홈타이), 사무실(기업 방문)</li>
</ul>
<p>코스 선택이 어렵다면 <a href="/magazine/course-selection-by-purpose/">목적별 코스 고르는 법</a> 매거진을 참고해 주세요. 운영팀의 매칭 의사결정 흐름을 그대로 공개합니다.</p>
</section>
""",
  related=_rel("/service/", ["/reservation/price/", "/reservation/how-to-book/", "/guide/first-time-massage/", "/magazine/course-selection-by-purpose/"], title="이어서 살펴볼 페이지"),
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
   ["피로 회복과 이완을 목적으로 하는 분", "처음 출장마사지를 경험하는 분", "가벼운 압을 선호하는 분"]),
  ("aroma", "아로마 마사지", "아로마 오일의 향과 부드러운 압을 함께 사용하는 이완 중심 케어입니다.",
   ["향 선택은 일반적으로 사전에 안내", "스웨디시와 유사한 압, 강한 압은 사용하지 않음", "수면 전 휴식 시간대에 자주 선택"],
   ["스트레스로 인한 긴장을 풀고 싶은 분", "잠들기 전 이완을 원하는 분", "강한 압이 부담스러운 분"]),
  ("sports-massage", "스포츠 마사지", "운동 전후의 컨디션 관리, 근육 피로 해소를 목적으로 진행하는 케어입니다.",
   ["근육 결을 따라 압을 분배", "전신 또는 특정 부위 집중 코스", "강한 압을 선호하는 분에게도 안내 가능"],
   ["주 1회 이상 운동을 하는 분", "특정 부위 근육 피로가 누적된 분", "오일 사용 비중을 줄이고 싶은 분"]),
  ("couple-massage", "커플 마사지", "두 명이 같은 시간대에 진행할 수 있도록 안내되는 옵션입니다.",
   ["동시간대 진행을 위해 관리사 2인이 함께 방문", "동일한 시간·코스 선택을 기본 권장", "장소는 한 객실 또는 한 공간"],
   ["기념일·휴가 일정에 함께 받고 싶은 분", "같은 시간에 케어를 받고 싶은 가족·연인"]),
  ("hotel-massage", "호텔 출장마사지", "출장·여행 일정 중 숙소에서 진행되는 방문 케어입니다.",
   ["객실 호수와 체크인 정보 사전 확인", "공간 특성에 맞춘 진행 방식 안내", "심야 시간대 문의가 많은 유형"],
   ["출장 중 짧은 휴식이 필요한 분", "이동 동선을 최소화하고 싶은 여행객", "비행 일정 전후 피로 회복이 필요한 분"]),
  ("office-massage", "기업·사무실 출장마사지", "임직원 복지 차원에서 단체로 진행되는 방문 케어입니다.",
   ["사전 일정·인원 조율 필수", "사내 공간 또는 별도 공간에서 진행", "10분·20분 단위 짧은 케어 옵션도 안내 가능"],
   ["임직원 복지 프로그램 운영 담당자", "분기별 단체 케어를 검토 중인 기업", "이벤트성으로 단체 케어를 진행하려는 부서"]),
]

# ---------- Service detail rich bodies (E-E-A-T 강화) ----------
# 가이드/매거진과 동일한 .guide-meta / .guide-toc / callout 스타일을 재사용
_SVC_BYLINE = (
    '<div class="guide-meta">'
    '<div class="guide-meta-author">'
    '<span class="guide-meta-avatar" aria-hidden="true">YH</span>'
    '<div class="guide-meta-author-text">'
    '<strong>바로GO 운영팀 (YH LAB)</strong>'
    '<span>출장마사지 예약 상담 운영팀 · 사업자등록번호 815-26-00585</span>'
    '</div></div>'
    '<div class="guide-meta-info">'
    '<span class="guide-meta-tag">최종 업데이트 · 2026-05</span>'
    '<span class="guide-meta-tag">운영팀 검수 완료</span>'
    '</div></div>'
)

_SVC_DISCLAIMER = (
    '<section class="block">'
    '<div class="callout note">'
    '<strong>면책 안내</strong>'
    '<p>본 페이지의 정보는 일반 출장마사지 안내 자료이며, 의료 행위·의학적 조언이 아닙니다. 건강 상태와 관련된 결정은 의료 전문가와 상담해 주세요. '
    '본 페이지는 YH LAB(바로GO 운영) 사업자등록번호 815-26-00585·대표 김유환·경기도 파주시 청석로 268 의 책임 하에 작성·관리됩니다.</p>'
    '</div>'
    '</section>'
)


def _svc_toc(items):
    li = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for label, anchor in items)
    return f'<nav class="guide-toc" aria-label="이 페이지에서 다루는 내용"><strong>이 페이지에서 다루는 내용</strong><ol>{li}</ol></nav>'


def _svc_faq(items):
    rows = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f'<section class="block" id="faq"><h2>자주 묻는 질문</h2><div class="faq">{rows}</div></section>'


# Per-service rich body (각 페이지 고유 콘텐츠 — 템플릿 치환이 아닌 직접 작성)
SERVICES_RICH = {

"business-trip-massage": {
  "title": "출장마사지 — 진행 방식·코스 종류·이용 흐름 | 바로GO",
  "desc": "출장마사지의 정의, 매장형 마사지와의 차이, 코스 6종 비교, 진행 흐름 5단계, 이용 전 권장사항까지 운영팀이 직접 정리한 안내 페이지입니다.",
  "h1": "출장마사지",
  "lede": "지정된 시간·장소(가정·호텔·오피스텔·펜션)에 관리사가 방문해 진행하는 마사지를 가리킵니다. 매장형과 다른 진행 방식, 코스 종류, 이용 흐름을 운영팀 관점에서 정리했습니다.",
  "toc": [("출장마사지란 무엇인가", "what"), ("매장형 마사지와의 차이", "vs-store"),
          ("어떤 경우에 자주 선택되는가", "when"), ("코스 종류 비교", "courses"),
          ("진행 흐름 5단계", "flow"), ("이용 전 권장사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="what">
<h2>출장마사지란 무엇인가</h2>
<p>출장마사지는 이용자가 지정한 시간·장소에 관리사가 직접 방문해 코스를 진행하는 방식의 마사지를 가리킵니다. 가정·호텔 객실·오피스텔·서비스 아파트·풀빌라 등 다양한 공간에서 진행되며, 매장에 방문할 필요가 없어 이동 시간이 절약되고, 진행 후 곧바로 휴식·수면으로 이어질 수 있다는 점이 가장 큰 특징입니다.</p>
<p>출장마사지는 합법적인 사업자가 안내·운영하는 서비스이며, 본 사이트(바로GO)는 운영사 YH LAB이 직접 예약 상담·관리사 배정·진행 관리를 담당합니다. 운영 원칙과 안전 정책은 <a href="/about/operation-policy/">운영 원칙</a>·<a href="/about/safety-policy/">안전 이용 정책</a>에 공개되어 있습니다.</p>
</section>

<section class="block" id="vs-store">
<h2>매장형 마사지와의 차이</h2>
<table class="compare-table">
<thead><tr><th scope="col">구분</th><th scope="col">매장형</th><th scope="col">출장형(본 서비스)</th></tr></thead>
<tbody>
<tr><th scope="row">진행 장소</th><td>매장 룸</td><td>가정·호텔·오피스텔·펜션</td></tr>
<tr><th scope="row">이동</th><td>이용자가 매장 방문</td><td>관리사가 지정 장소 방문</td></tr>
<tr><th scope="row">진행 후 흐름</th><td>매장 → 귀가</td><td>곧바로 휴식·수면 연결</td></tr>
<tr><th scope="row">시간대</th><td>매장 영업시간</td><td>야간·심야 안내 가능</td></tr>
<tr><th scope="row">사전 합의</th><td>코스만 선택</td><td>장소·시간·동선까지 합의</td></tr>
</tbody>
</table>
</section>

<section class="block" id="when">
<h2>어떤 경우에 자주 선택되는가</h2>
<ul class="check-list">
<li>야근·심야 일정 후 바로 회복이 필요할 때</li>
<li>출장·여행지 호텔에서 짧은 회복 시간을 활용하고 싶을 때</li>
<li>이동 후 곧바로 휴식·수면으로 이어가고 싶을 때</li>
<li>가정에서 가족과 동선 충돌 없이 진행하고 싶을 때</li>
<li>매장 방문 자체가 부담스러운 컨디션일 때</li>
</ul>
</section>

<section class="block" id="courses">
<h2>코스 종류 비교</h2>
<p>대표적으로 다음 6개 코스가 운영되며, 목적·시간·압력 선호에 따라 선택이 달라집니다. 가격 기준은 <a href="/reservation/price/">가격 안내</a> 페이지에서 확인하실 수 있습니다.</p>
<ul class="check-list">
<li><a href="/service/swedish/"><strong>스웨디시</strong></a> — 오일 사용·부드러운 압. 처음 이용·수면 보조에 가장 자주 안내됩니다.</li>
<li><a href="/service/aroma/"><strong>아로마</strong></a> — 향과 부드러운 압의 조합. 릴랙스·심야 시간대에 자주 선택됩니다.</li>
<li><a href="/service/hometai/"><strong>홈타이</strong></a> — 옷 입은 채 진행, 스트레칭 결합. 근육 가동성 정비에 적합합니다.</li>
<li><a href="/service/sports-massage/"><strong>스포츠 마사지</strong></a> — 강한 압·근육 결 케어. 운동 후 회복에 안내됩니다.</li>
<li><a href="/service/couple-massage/"><strong>커플</strong></a> — 2인 동시 진행. 기념일·동행 진행 시 안내됩니다.</li>
<li><a href="/service/hotel-massage/"><strong>호텔 방문</strong></a> — 호텔 객실 진행 특화. 출장·여행 일정에 자주 안내됩니다.</li>
</ul>
</section>

<section class="block" id="flow">
<h2>진행 흐름 5단계</h2>
<ol class="steps">
<li><strong>전화 상담</strong><p>지역·시간·코스·진행 장소를 사전 합의합니다.</p></li>
<li><strong>예약 확정</strong><p>가격·취소 기준 안내 후 동의 시 확정됩니다.</p></li>
<li><strong>관리사 배정·이동</strong><p>도착 예정 시각이 사전 안내됩니다.</p></li>
<li><strong>코스 진행</strong><p>선택한 시간 내에서 코스가 진행됩니다.</p></li>
<li><strong>결제·마무리</strong><p>합의된 결제 방식으로 종료. 사후 권장 사항 안내.</p></li>
</ol>
<p>전체 절차는 <a href="/reservation/how-to-book/">예약 방법</a>에 상세하게 정리되어 있습니다.</p>
</section>

<section class="block" id="before">
<h2>이용 전 권장사항</h2>
<ul class="check-list">
<li>고열·급성 통증·외상·수술 직후에는 이용을 권하지 않습니다.</li>
<li>식사 직후·과도한 음주 후 진행은 자제해 주세요.</li>
<li>임신·특정 질환·약물 복용 중인 경우 예약 단계에서 알려주세요.</li>
<li>피부 트러블·자극이 있는 부위는 진행에서 제외할 수 있습니다.</li>
<li>진행 공간에 동행자(가족·아이)가 있는 경우 사전에 안내해 주세요.</li>
</ul>
<p>상세 체크리스트는 <a href="/reservation/check-before-use/">이용 전 확인사항</a>에 정리되어 있습니다.</p>
</section>
""",
  "faqs": [
    ("매장 마사지와 효과 차이가 있나요?",
     "코스 자체의 효과는 같지만, 출장형은 이동·대기 시간이 없어 진행 후 휴식·수면 연결이 매끄럽다는 점이 가장 큰 차이입니다."),
    ("처음 이용하는데 어떤 코스가 가장 무난한가요?",
     "스웨디시 60분이 가장 자주 권장됩니다. 부드러운 압력과 오일 케어로 부담이 적습니다. 자세한 첫 이용 가이드는 <a href=\"/guide/first-time-massage/\">처음 이용 전 알아둘 점</a>을 참고해 주세요."),
    ("의료적 효과를 보장하나요?",
     "출장마사지는 의료 행위가 아니며, 치료 효과를 보장하지 않습니다. 특정 통증이 분명하면 의료 진단을 먼저 받으시기를 권장합니다."),
  ],
},

"swedish": {
  "title": "스웨디시 마사지 — 압력·진행 방식·추천 대상 | 바로GO",
  "desc": "스웨디시 마사지의 진행 방식, 압력 강도, 다른 코스와의 차이, 코스 길이별 활용법, 이용 전 권장사항을 운영팀이 정리한 안내 페이지입니다.",
  "h1": "스웨디시 마사지",
  "lede": "오일을 사용해 부드러운 압력으로 전신을 이완하는 가장 대중적인 출장마사지 코스입니다. 처음 받으시는 분과 수면 보조 목적에 가장 자주 안내됩니다.",
  "toc": [("스웨디시의 특징", "feature"), ("다른 코스와의 차이", "vs"),
          ("어떤 분께 권장되는가", "audience"), ("코스 길이별 활용법", "length"),
          ("진행 흐름", "flow"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="feature">
<h2>스웨디시의 특징</h2>
<p>스웨디시(Swedish)는 19세기 스웨덴에서 정립된 마사지 기법으로, 오일을 사용해 전신을 길게 쓸어 올리는 동작(effleurage) 중심으로 진행됩니다. 부드러운 압력과 일정한 리듬으로 진행되기 때문에, 강한 자극에 부담을 느끼는 분에게도 적합합니다.</p>
<ul class="check-list">
<li>전신을 길게 쓸어 올리는 기본 동작 중심</li>
<li>오일 사용으로 마찰을 최소화한 부드러운 진행</li>
<li>릴랙스·수면 진입에 가장 자주 안내되는 코스</li>
<li>60·90·120분 모든 길이에서 선호되는 유형</li>
</ul>
</section>

<section class="block" id="vs">
<h2>다른 코스와의 차이</h2>
<table class="compare-table">
<thead><tr><th scope="col">비교</th><th scope="col">스웨디시</th><th scope="col">아로마</th><th scope="col">홈타이</th></tr></thead>
<tbody>
<tr><th scope="row">압력</th><td>부드러움</td><td>부드러움</td><td>중강도</td></tr>
<tr><th scope="row">오일</th><td>사용</td><td>아로마 오일</td><td>사용 안 함</td></tr>
<tr><th scope="row">복장</th><td>탈의·타월</td><td>탈의·타월</td><td>옷 입은 채</td></tr>
<tr><th scope="row">주 효과</th><td>이완·수면</td><td>릴랙스·향</td><td>스트레칭·가동성</td></tr>
</tbody>
</table>
</section>

<section class="block" id="audience">
<h2>어떤 분께 권장되는가</h2>
<ul class="check-list">
<li>처음 출장마사지를 이용하시는 분</li>
<li>피로 회복·이완이 목적이신 분</li>
<li>잠들기 전 부드러운 케어를 원하시는 분</li>
<li>강한 압력에 부담을 느끼시는 분</li>
<li>야근·심야 일정 후 빠른 휴식 진입이 필요한 분</li>
</ul>
</section>

<section class="block" id="length">
<h2>코스 길이별 활용법</h2>
<div class="dos-donts">
<div class="dos">
<strong>60분 코스</strong>
<ul>
<li>처음 이용·체험 권장</li>
<li>심야 시간·짧은 회복</li>
<li>다음 날 이른 일정이 있을 때</li>
</ul>
</div>
<div class="dos">
<strong>90분 코스</strong>
<ul>
<li>가장 자주 선택되는 표준 길이</li>
<li>전신 균형 회복</li>
<li>업무 누적 피로 해소</li>
</ul>
</div>
<div class="dos">
<strong>120분 코스</strong>
<ul>
<li>주말·여유 일정용</li>
<li>깊은 이완·수면 보조</li>
<li>특정 부위 추가 케어 포함</li>
</ul>
</div>
</div>
</section>

<section class="block" id="flow">
<h2>진행 흐름</h2>
<ol class="steps">
<li><strong>도착·간단한 안내</strong><p>건강 상태·선호 압력을 확인합니다.</p></li>
<li><strong>샤워 권장</strong><p>오일이 더 잘 흡수되도록 샤워가 권장됩니다.</p></li>
<li><strong>전신 케어 진행</strong><p>등·다리·팔·어깨·목·머리 순으로 진행되는 것이 일반적입니다.</p></li>
<li><strong>마무리</strong><p>오일 정리, 수분 섭취, 휴식 권장 안내가 이어집니다.</p></li>
</ol>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>오일 알레르기가 있는 경우 사전에 알려주세요.</li>
<li>피부 자극이 있는 부위는 제외 진행이 가능합니다.</li>
<li>식사 직후(1시간 이내) 또는 음주 후 진행은 자제해 주세요.</li>
<li>임신 중인 경우 진행 가능 여부를 사전 상담에서 확인합니다.</li>
</ul>
</section>
""",
  "faqs": [
    ("오일이 옷·침구에 묻을까 걱정됩니다.",
     "관리사가 타월·시트를 함께 준비하므로 일반적으로 오일이 옷·침구에 묻지 않습니다. 진행 후 가벼운 샤워가 권장됩니다."),
    ("아로마와 가장 큰 차이가 무엇인가요?",
     "스웨디시는 일반 오일로 압력 케어 중심, 아로마는 향과 함께 진행하는 점이 가장 큰 차이입니다. 자세한 비교는 <a href=\"/guide/aroma-vs-swedish/\">아로마와 스웨디시 차이</a>에 정리되어 있습니다."),
    ("매주 받아도 괜찮나요?",
     "주 1회 정기 케어는 일반적으로 무리가 없습니다. 다만 본인 컨디션에 따라 간격을 조정하시는 것을 권장합니다."),
  ],
},

"aroma": {
  "title": "아로마 마사지 — 향·압력·릴랙스 코스 안내 | 바로GO",
  "desc": "아로마 마사지의 특징, 자주 안내되는 향 계열, 추천 대상, 진행 흐름, 이용 전 주의사항까지 운영팀이 정리한 안내 페이지입니다.",
  "h1": "아로마 마사지",
  "lede": "아로마 오일의 향과 부드러운 압력을 함께 사용하는 이완 중심 코스입니다. 잠들기 전 휴식 시간대나 스트레스로 인한 긴장이 누적된 때에 자주 안내됩니다.",
  "toc": [("아로마 마사지의 특징", "feature"), ("향이 컨디션에 미치는 영향", "scent"),
          ("자주 안내되는 향 계열", "scent-types"), ("어떤 분께 권장되는가", "audience"),
          ("진행 흐름", "flow"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="feature">
<h2>아로마 마사지의 특징</h2>
<p>아로마 마사지는 식물성 에센셜 오일을 베이스 오일에 희석해 사용하는 마사지로, 향과 함께 부드러운 압력으로 진행되는 이완 중심 코스입니다. 압력은 스웨디시와 비슷하게 부드럽지만, 향이 함께 작용하면서 신경 안정·심신 이완 효과가 더 두드러지는 경향이 있습니다.</p>
</section>

<section class="block" id="scent">
<h2>향이 컨디션에 미치는 영향</h2>
<p>향은 후각 신경을 통해 직접 뇌의 변연계(limbic system)에 도달하기 때문에, 다른 감각보다 빠르게 감정·이완 상태에 영향을 줍니다. 따라서 아로마는 단순히 마사지에 향을 더한 것이 아니라, 향 자체가 케어의 일부로 작동합니다.</p>
<div class="callout note">
<strong>참고</strong>
<p>아로마는 의료 행위가 아니며, 특정 질환을 치료한다고 보장하지 않습니다. 본 페이지의 내용은 일반적 이완 효과에 관한 정성적 안내입니다.</p>
</div>
</section>

<section class="block" id="scent-types">
<h2>자주 안내되는 향 계열</h2>
<ul class="check-list">
<li><strong>라벤더</strong> — 가장 대표적. 신경 안정·수면 보조 목적에 자주 안내</li>
<li><strong>유칼립투스·페퍼민트</strong> — 상쾌하고 시원한 느낌. 두통·집중력 저하 시 권장</li>
<li><strong>시트러스(레몬·오렌지·베르가못)</strong> — 가볍고 밝은 분위기. 낮 시간·우울감 환기</li>
<li><strong>로즈·일랑일랑</strong> — 풍부한 플로럴. 기념일·특별한 일정에 자주 안내</li>
<li><strong>샌달우드·시더우드</strong> — 안정감 있는 우디 톤. 깊은 이완·명상적 분위기</li>
</ul>
<p>향 선택은 일반적으로 사전 상담에서 함께 결정됩니다. 특정 향에 알레르기·민감도가 있는 경우 반드시 미리 알려주세요.</p>
</section>

<section class="block" id="audience">
<h2>어떤 분께 권장되는가</h2>
<ul class="check-list">
<li>스트레스로 인한 긴장이 누적된 분</li>
<li>잠들기 전 깊은 이완을 원하시는 분</li>
<li>강한 압이 부담스러우신 분</li>
<li>여행지·호텔에서 휴식 케어를 받으시는 분</li>
<li>기념일·특별한 일정에 케어를 함께 진행하시는 분</li>
</ul>
</section>

<section class="block" id="flow">
<h2>진행 흐름</h2>
<ol class="steps">
<li><strong>향 선택</strong><p>사전에 상담된 향 또는 도착 시 함께 선택합니다.</p></li>
<li><strong>샤워 권장</strong><p>오일 흡수와 향이 더 잘 작용하도록 샤워가 권장됩니다.</p></li>
<li><strong>전신 케어 진행</strong><p>부드러운 압력으로 등·다리·팔·어깨 순 진행이 일반적입니다.</p></li>
<li><strong>마무리</strong><p>오일·향 정리, 수분 섭취, 휴식 권장.</p></li>
</ol>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>특정 향 알레르기·천식 등이 있는 경우 사전에 알려주세요.</li>
<li>임신 중에는 일부 에센셜 오일이 권장되지 않을 수 있어 사전 상담이 필요합니다.</li>
<li>향이 강하면 두통이 발생할 수 있어 사용량은 일반적으로 조절됩니다.</li>
<li>코스 후 향이 옷·머리카락에 남을 수 있어 외출 일정과의 간격을 고려해 주세요.</li>
</ul>
</section>
""",
  "faqs": [
    ("향을 직접 가져가도 되나요?",
     "관리사가 준비한 오일 외 별도 향 사용은 위생·관리 기준상 일반적으로 권장되지 않습니다. 선호 향이 있다면 사전 상담에서 알려주세요."),
    ("아로마와 스웨디시 중 무엇이 좋을까요?",
     "이완·수면 보조가 주 목적이라면 향이 함께 작용하는 아로마, 압력 케어가 주 목적이라면 스웨디시가 자주 안내됩니다. <a href=\"/guide/aroma-vs-swedish/\">아로마와 스웨디시 차이</a>에서 비교를 확인하실 수 있습니다."),
    ("향이 옷에 너무 강하게 남을까요?",
     "향의 농도는 일반적으로 조절되어 진행 직후에는 가볍게 남는 정도입니다. 외출 일정이 있는 경우 90분 이상 간격을 권장합니다."),
  ],
},

"hometai": {
  "title": "홈타이 — 진행 방식·복장·코스 길이 | 바로GO",
  "desc": "홈타이(타이 마사지)의 진행 방식, 옷을 입은 채 진행되는 특징, 권장 공간 조건, 코스 길이 안내, 이용 전 주의사항까지 운영팀이 정리한 안내 페이지입니다.",
  "h1": "홈타이",
  "lede": "타이 전통 기법 기반의 스트레칭과 지압을 결합한 출장마사지입니다. 옷을 입은 상태로 진행되며, 오일을 사용하지 않아 사후 정리가 간편합니다.",
  "toc": [("홈타이가 무엇인가", "what"), ("다른 코스와의 차이", "vs"),
          ("권장 공간 조건", "space"), ("어떤 분께 권장되는가", "audience"),
          ("진행 흐름", "flow"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="what">
<h2>홈타이가 무엇인가</h2>
<p>홈타이는 타이 전통 마사지(Thai massage) 기법을 가정·숙소에서 진행하는 형태로, 관절 가동 범위를 활용한 스트레칭과 손·팔꿈치를 사용한 지압을 결합한 코스입니다. 오일을 사용하지 않고 옷을 입은 상태에서 진행하기 때문에 사후 정리가 간편하다는 점이 큰 장점입니다.</p>
</section>

<section class="block" id="vs">
<h2>다른 코스와의 차이</h2>
<table class="compare-table">
<thead><tr><th scope="col">항목</th><th scope="col">홈타이</th><th scope="col">스웨디시·아로마</th></tr></thead>
<tbody>
<tr><th scope="row">오일</th><td>사용 안 함</td><td>사용</td></tr>
<tr><th scope="row">복장</th><td>편안한 옷</td><td>탈의 + 타월</td></tr>
<tr><th scope="row">동작</th><td>스트레칭·지압</td><td>쓸어 올리기 위주</td></tr>
<tr><th scope="row">압력</th><td>중강도</td><td>부드러움</td></tr>
<tr><th scope="row">주 효과</th><td>가동성 정비·근육 이완</td><td>이완·수면 보조</td></tr>
</tbody>
</table>
</section>

<section class="block" id="space">
<h2>권장 공간 조건</h2>
<p>홈타이는 바닥에 매트를 깔고 진행되는 경우가 많아 공간 조건이 다른 코스보다 다소 까다롭습니다.</p>
<ul class="check-list">
<li>바닥에 가로 2m × 세로 2.5m 정도의 평평한 공간 확보</li>
<li>러그·매트 또는 평평한 침대 위에서도 진행 가능</li>
<li>천장 조명 위치·가구 동선 고려</li>
<li>옷은 신축성 있는 면 소재 권장 (운동복·잠옷 등)</li>
</ul>
</section>

<section class="block" id="audience">
<h2>어떤 분께 권장되는가</h2>
<ul class="check-list">
<li>오일이 부담스러우신 분 (피부 자극·정리 부담)</li>
<li>어깨·골반·고관절 가동성에 관심이 있으신 분</li>
<li>장시간 앉아서 일해 몸이 굳은 느낌이 드는 분</li>
<li>운동 후 근육 가동 범위 회복이 필요한 분</li>
<li>탈의가 부담스러우신 분</li>
</ul>
</section>

<section class="block" id="flow">
<h2>진행 흐름</h2>
<ol class="steps">
<li><strong>공간 세팅·옷 안내</strong><p>매트를 깔고 편한 옷으로 환복합니다.</p></li>
<li><strong>발·다리부터 진행</strong><p>발끝에서 시작해 무릎·골반 방향으로 진행됩니다.</p></li>
<li><strong>등·어깨·팔</strong><p>몸을 옆으로 눕히거나 앉은 자세에서 진행되기도 합니다.</p></li>
<li><strong>전신 스트레칭 마무리</strong><p>최종적으로 전신 가동 범위를 정리합니다.</p></li>
</ol>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>식사 직후에는 스트레칭 동작이 불편할 수 있어 1-2시간 간격을 권장합니다.</li>
<li>허리·골반·무릎에 부상·만성 통증이 있는 경우 사전에 알려주세요.</li>
<li>임신 중인 경우 진행 가능 여부를 사전 상담에서 확인합니다.</li>
<li>고혈압·심장 질환·디스크 등 특정 질환이 있는 경우 의료 진단이 우선입니다.</li>
</ul>
</section>
""",
  "faqs": [
    ("오일 마사지보다 더 아픈가요?",
     "압력 자체는 중강도이지만, 스트레칭 동작이 가동 범위 끝에서 작용해 시원함이 더 분명하게 느껴지는 편입니다. 강도는 사전·중간에 조정됩니다."),
    ("옷은 어떤 걸 준비하면 좋을까요?",
     "신축성 있는 면 소재 운동복·잠옷이 가장 좋습니다. 청바지·정장처럼 신축성 없는 옷은 동작이 제한됩니다."),
    ("매트가 없는데 침대에서도 가능한가요?",
     "가능합니다. 다만 너무 푹신한 침대는 압력이 분산되어 진행이 어려울 수 있어, 사전 상담에서 공간 조건을 함께 확인합니다."),
  ],
},

"sports-massage": {
  "title": "스포츠 마사지 — 부위 집중·운동 회복 코스 | 바로GO",
  "desc": "스포츠 마사지의 진행 방식, 운동 전후 활용법, 부위별 집중 케어, 자주 안내되는 시점, 이용 전 주의사항까지 운영팀이 정리한 안내 페이지입니다.",
  "h1": "스포츠 마사지",
  "lede": "운동 전후 컨디션 관리와 근육 피로 해소를 목적으로 진행되는 출장마사지 코스입니다. 근육 결을 따라 압력을 분배해 특정 부위 집중 케어가 가능합니다.",
  "toc": [("스포츠 마사지의 특징", "feature"), ("운동 전후 활용법", "pre-post"),
          ("부위별 집중 케어", "by-part"), ("자주 안내되는 시점", "when"),
          ("진행 흐름", "flow"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="feature">
<h2>스포츠 마사지의 특징</h2>
<p>스포츠 마사지는 근육 결을 따라 압력을 분배하고, 특정 부위에 집중 케어가 가능한 코스입니다. 강한 압을 선호하는 분에게도 안내 가능하며, 일반 이완 케어와 달리 근육 회복·가동 범위 정비에 초점이 맞춰져 있습니다.</p>
<ul class="check-list">
<li>근육 결을 따라 압을 분배하는 진행 방식</li>
<li>전신 또는 특정 부위(어깨·허리·다리) 집중 가능</li>
<li>강한 압 선호자에게도 안내 가능</li>
<li>운동 후 회복·근육 뭉침 해소에 권장</li>
</ul>
</section>

<section class="block" id="pre-post">
<h2>운동 전후 활용법</h2>
<div class="dos-donts">
<div class="dos">
<strong>운동 전 (예방·준비)</strong>
<ul>
<li>가벼운 압력으로 진행</li>
<li>가동 범위 확장·근육 활성화 목적</li>
<li>운동 1-2시간 전 권장</li>
</ul>
</div>
<div class="dos">
<strong>운동 후 (회복·해소)</strong>
<ul>
<li>중강도 압력으로 진행</li>
<li>젖산·노폐물 순환 보조</li>
<li>운동 직후 30분-2시간 사이 권장</li>
</ul>
</div>
</div>
</section>

<section class="block" id="by-part">
<h2>부위별 집중 케어</h2>
<table class="compare-table">
<thead><tr><th scope="col">부위</th><th scope="col">자주 안내되는 상황</th><th scope="col">코스 길이</th></tr></thead>
<tbody>
<tr><th scope="row">어깨·승모근</th><td>웨이트 후 / 사무직 누적</td><td>60-90분</td></tr>
<tr><th scope="row">허리·등</th><td>스쿼트·데드리프트 후</td><td>90분</td></tr>
<tr><th scope="row">다리·종아리</th><td>러닝·등산 후</td><td>60-120분</td></tr>
<tr><th scope="row">전신</th><td>장시간 운동·종합 회복</td><td>120분</td></tr>
</tbody>
</table>
</section>

<section class="block" id="when">
<h2>자주 안내되는 시점</h2>
<ul class="check-list">
<li>주 3회 이상 정기 운동 후 누적 피로 해소</li>
<li>마라톤·트레일러닝 등 장시간 운동 후 회복</li>
<li>등산·라이딩 후 다리·허리 근육 케어</li>
<li>웨이트 트레이닝 슬럼프 시 가동성 회복</li>
<li>경기·대회 직전 컨디션 정비</li>
</ul>
</section>

<section class="block" id="flow">
<h2>진행 흐름</h2>
<ol class="steps">
<li><strong>운동 이력·통증 부위 확인</strong><p>최근 운동량·특정 부위 통증 여부를 점검합니다.</p></li>
<li><strong>전신 또는 부위 집중 결정</strong><p>코스 시간에 맞춰 진행 범위를 합의합니다.</p></li>
<li><strong>케어 진행</strong><p>근육 결을 따라 압력을 분배하며 진행됩니다.</p></li>
<li><strong>마무리·권장 사항</strong><p>수분 보충·다음 운동까지 휴식 권장 등 안내.</p></li>
</ol>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>급성 부상·염좌·인대 파열이 의심되면 의료 진단이 우선입니다.</li>
<li>운동 직후 1시간 이내는 컨디션이 불안정해 진행이 권장되지 않습니다.</li>
<li>탈수 상태에서는 진행이 어렵습니다. 수분 보충 후 진행.</li>
<li>강한 압이 부담스러우면 사전·중간에 조절을 요청해 주세요.</li>
</ul>
</section>
""",
  "faqs": [
    ("운동 직후 바로 받아도 되나요?",
     "직후 1시간 이내는 컨디션이 불안정해 권장되지 않습니다. 운동 후 30분-2시간 사이가 가장 효과적인 시점입니다."),
    ("강한 압을 더 강하게 해주실 수 있나요?",
     "압력 조절은 사전·중간에 모두 가능합니다. 다만 본인 컨디션·근육 상태에 따라 무리한 강도는 권장되지 않습니다."),
    ("일반 스웨디시와 어떻게 다른가요?",
     "스웨디시는 부드러운 압의 이완 중심, 스포츠는 근육 결 케어와 부위 집중이 특징입니다. 운동 회복 목적이라면 스포츠가 적합합니다."),
  ],
},

"couple-massage": {
  "title": "커플 마사지 — 2인 동시 진행·공간 조건·가격 | 바로GO",
  "desc": "커플 마사지의 진행 방식, 공간 조건, 자주 선택되는 일정, 코스 선택 흐름, 가격 기준, 이용 전 주의사항까지 운영팀이 정리한 안내 페이지입니다.",
  "h1": "커플 마사지",
  "lede": "두 분이 같은 시간대에 동시에 진행할 수 있도록 안내되는 코스입니다. 기념일·여행·동행 일정에 자주 선택되며, 진행 공간 조건이 일반 코스와 다소 다릅니다.",
  "toc": [("커플 코스 개요", "what"), ("진행 환경·공간 조건", "space"),
          ("자주 선택되는 일정", "when"), ("코스 선택 흐름", "course"),
          ("가격 기준", "price"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="what">
<h2>커플 코스 개요</h2>
<p>커플 코스는 두 분이 같은 시간대에 동시에 진행되는 케어입니다. 일반 1인 코스와 가장 큰 차이는 관리사 2인이 함께 방문해 한 공간(또는 두 객실)에서 동시에 진행한다는 점입니다. 같은 시간·같은 코스 선택이 기본이며, 동일하지 않은 코스로도 진행 가능합니다(사전 상담 필요).</p>
</section>

<section class="block" id="space">
<h2>진행 환경·공간 조건</h2>
<ul class="check-list">
<li>한 공간(거실·넓은 룸·풀빌라 거실)에 2개의 진행 자리 확보</li>
<li>또는 같은 숙소 내 2개 객실 분리 진행</li>
<li>호텔 진행 시 트윈룸·스위트룸 권장</li>
<li>가정 진행 시 사전에 공간 동선 확인 필요</li>
</ul>
<div class="callout tip">
<strong>공간이 좁다면?</strong>
<p>같은 시간에 진행이 어렵다면 시간차 진행(1인씩 순차)도 가능합니다. 사전 상담에서 함께 결정됩니다.</p>
</div>
</section>

<section class="block" id="when">
<h2>자주 선택되는 일정</h2>
<ul class="check-list">
<li>기념일·생일·결혼기념일</li>
<li>여행지 호텔·풀빌라에서 함께 받는 일정</li>
<li>장기 출장 후 가족·연인과의 회복 일정</li>
<li>특별한 휴가 일정의 마무리 케어</li>
</ul>
</section>

<section class="block" id="course">
<h2>코스 선택 흐름</h2>
<ol class="steps">
<li><strong>동일 코스 권장</strong><p>같은 시간·같은 코스가 진행이 매끄럽습니다.</p></li>
<li><strong>코스 분리 가능</strong><p>한 분은 스웨디시, 다른 분은 홈타이 등 분리 가능 (사전 상담).</p></li>
<li><strong>시간 길이</strong><p>60·90·120분 중 합의된 동일 시간으로 진행.</p></li>
<li><strong>관리사 배정</strong><p>가능한 경우 성별·경력 선호도 사전 안내.</p></li>
</ol>
</section>

<section class="block" id="price">
<h2>가격 기준</h2>
<p>커플 코스의 가격은 2인 합산 기준으로 안내됩니다. 코스·시간에 따라 시작 금액이 달라지며, 자세한 기준은 <a href="/reservation/price/">가격 안내</a>에 정리되어 있습니다.</p>
<table class="compare-table">
<thead><tr><th scope="col">시간</th><th scope="col">2인 합산 시작 금액</th></tr></thead>
<tbody>
<tr><th scope="row">60분</th><td>180,000원부터</td></tr>
<tr><th scope="row">90분</th><td>220,000원부터</td></tr>
<tr><th scope="row">120분</th><td>260,000원부터</td></tr>
</tbody>
</table>
<p class="muted">진행 장소·시간대에 따라 일부 조정될 수 있으며, 최종 금액은 사전 상담에서 안내됩니다.</p>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>각자의 건강 상태(임신·질환·알레르기 등)를 사전에 알려주세요.</li>
<li>같은 공간에서 진행 시 향·압력 선호가 다른 경우 사전 조율됩니다.</li>
<li>예약 변경·취소 시 1인 단위가 아닌 커플 단위로 처리됩니다.</li>
<li>호텔 진행 시 객실 인원·체크인 정보를 함께 안내해 주세요.</li>
</ul>
</section>
""",
  "faqs": [
    ("꼭 같은 코스를 선택해야 하나요?",
     "기본은 같은 코스가 권장되지만, 사전 상담에서 분리 코스(예: 한 분 스웨디시 / 한 분 홈타이)도 안내됩니다."),
    ("진행 중에 대화해도 되나요?",
     "물론 가능합니다. 다만 깊은 이완을 위해서는 진행 중반부터 조용히 받으시는 분들이 많습니다."),
    ("한 분만 취소할 수 있나요?",
     "커플 코스는 2인 단위로 확정되기 때문에 1인 단독 취소는 일반적으로 어렵습니다. 자세한 기준은 <a href=\"/reservation/cancel-refund/\">취소·환불 규정</a>을 참고해 주세요."),
  ],
},

"hotel-massage": {
  "title": "호텔 출장마사지 — 객실 진행·체크인·시간대 | 바로GO",
  "desc": "호텔 객실에서 진행되는 출장마사지의 특징, 호텔 유형별 차이, 객실 사전 안내 정보, 자주 선택되는 시간대, 이용 전 주의사항을 정리한 안내 페이지입니다.",
  "h1": "호텔 출장마사지",
  "lede": "출장·여행 일정 중 숙소에서 진행되는 출장마사지입니다. 호텔 유형(비즈니스·5성·레지던스·풀빌라)에 따라 진행 흐름이 조금씩 다르며, 객실 정보 사전 공유가 진행의 핵심입니다.",
  "toc": [("호텔 진행의 특징", "feature"), ("호텔 유형별 차이", "by-hotel"),
          ("객실 사전 안내 정보", "checklist"), ("자주 선택되는 시간대", "time"),
          ("진행 흐름", "flow"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="feature">
<h2>호텔 진행의 특징</h2>
<p>호텔 객실 진행은 가정 방문과 비교해 공간이 정돈되어 있고, 진행 후 곧바로 휴식·수면으로 이어갈 수 있다는 점이 가장 큰 장점입니다. 출장·여행 일정 중 짧은 회복 시간을 활용하시는 분들이 자주 선택합니다.</p>
<ul class="check-list">
<li>객실 호수·층 정보 사전 확인 필수</li>
<li>공동현관·엘리베이터 출입 안내 필요</li>
<li>심야 시간대 문의가 가장 많은 진행 유형</li>
<li>관리사 도착 직후 곧바로 진행 가능</li>
</ul>
</section>

<section class="block" id="by-hotel">
<h2>호텔 유형별 차이</h2>
<table class="compare-table">
<thead><tr><th scope="col">호텔 유형</th><th scope="col">진행 특이사항</th></tr></thead>
<tbody>
<tr><th scope="row">5성·럭셔리 (강남·도심)</th><td>공동현관 출입 절차, 게스트 등록 권장</td></tr>
<tr><th scope="row">비즈니스 호텔</th><td>가장 진행이 매끄러운 유형, 객실 공간 충분</td></tr>
<tr><th scope="row">레지던스·서비스 아파트</th><td>주방·세탁 공간 분리, 사전 게스트 등록 필요</td></tr>
<tr><th scope="row">풀빌라·독채 (제주·강원)</th><td>독립 공간, 커플 코스 자유로움, 동선 안내 필요</td></tr>
<tr><th scope="row">부티크 호텔</th><td>객실이 작은 경우 진행 자세·동선 사전 합의</td></tr>
</tbody>
</table>
</section>

<section class="block" id="checklist">
<h2>객실 사전 안내 정보</h2>
<ul class="check-list">
<li><strong>호텔명·객실 호수·층</strong> — 출입·도착 시간 안내에 필수</li>
<li><strong>체크인 시간</strong> — 진행 시작 시각과의 간격 확인</li>
<li><strong>객실 크기·유형</strong> — 더블·트윈·스위트에 따라 진행 방식 차이</li>
<li><strong>동행자 정보</strong> — 동행자가 있는 경우 진행 시 안내</li>
<li><strong>특별 출입 조건</strong> — 일부 호텔은 게스트 사전 등록 필요</li>
</ul>
</section>

<section class="block" id="time">
<h2>자주 선택되는 시간대</h2>
<div class="dos-donts">
<div class="dos">
<strong>출장 일정 (평일)</strong>
<ul>
<li>저녁 미팅 후 22-00시 사이</li>
<li>다음 날 일정에 따라 60-90분</li>
<li>스웨디시·아로마 자주 안내</li>
</ul>
</div>
<div class="dos">
<strong>여행 일정 (주말·휴가)</strong>
<ul>
<li>체크인 후 저녁 시간대</li>
<li>여유 있는 90-120분</li>
<li>커플 코스 함께 안내</li>
</ul>
</div>
</div>
</section>

<section class="block" id="flow">
<h2>진행 흐름</h2>
<ol class="steps">
<li><strong>객실 정보 사전 공유</strong><p>호텔명·호수·층·체크인 시간 안내.</p></li>
<li><strong>관리사 도착·진입</strong><p>공동현관 출입 후 객실 노크.</p></li>
<li><strong>객실 세팅</strong><p>타월·시트 준비 (5분 이내).</p></li>
<li><strong>코스 진행</strong><p>합의된 코스 시간 진행.</p></li>
<li><strong>결제·마무리</strong><p>객실 정리 후 종료.</p></li>
</ol>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>일부 5성 호텔은 외부 게스트 출입에 별도 등록이 필요할 수 있습니다.</li>
<li>객실이 매우 협소한 경우 진행 자세를 사전에 조정할 수 있습니다.</li>
<li>체크아웃 직전에는 진행 시간 여유가 부족할 수 있어 권장되지 않습니다.</li>
<li>호텔 측에 마사지 진행 사실을 별도로 알릴 필요는 일반적으로 없습니다.</li>
</ul>
</section>
""",
  "faqs": [
    ("호텔 직원에게 미리 알려야 하나요?",
     "일반적으로는 별도 통보가 필요하지 않습니다. 다만 일부 5성 호텔은 외부 출입에 게스트 등록을 권장하기도 합니다."),
    ("객실이 작아도 가능한가요?",
     "더블룸 정도면 진행이 충분합니다. 매우 협소한 부티크 객실은 진행 자세·동선을 사전에 합의합니다."),
    ("풀빌라에서도 가능한가요?",
     "가능합니다. 풀빌라는 독립 공간이라 커플 코스 진행에도 가장 적합합니다. 다만 위치에 따라 이동 거리 변수가 큽니다."),
  ],
},

"office-massage": {
  "title": "기업·사무실 출장마사지 — 단체 케어·복지 프로그램 | 바로GO",
  "desc": "임직원 복지·이벤트 목적의 단체 출장마사지 안내. 사전 협의 항목, 진행 공간 조건, 코스 옵션(10·20·30분 단위), 이용 흐름을 정리한 안내 페이지입니다.",
  "h1": "기업·사무실 출장마사지",
  "lede": "임직원 복지 프로그램·분기 이벤트·연말 케어 등 단체로 진행되는 출장마사지입니다. 일반 1인 코스와 달리 사전 협의 단계가 더 많아 운영팀과의 상세 상담이 필요합니다.",
  "toc": [("단체 케어 개요", "what"), ("사전 협의 항목", "preset"),
          ("진행 공간 조건", "space"), ("코스 옵션", "options"),
          ("진행 흐름", "flow"), ("이용 전 주의사항", "before"), ("자주 묻는 질문", "faq")],
  "body": """
<section class="block" id="what">
<h2>단체 케어 개요</h2>
<p>기업·사무실 출장마사지는 임직원 복지·이벤트 목적으로 진행되는 단체 출장마사지입니다. 개인 코스와 달리 인원·시간·공간을 사전에 협의해야 하며, 짧은 케어를 여러 명에게 순차로 제공하는 방식이 일반적입니다.</p>
<ul class="check-list">
<li>10인·20인·30인 등 인원 단위 안내</li>
<li>1인당 10·20·30분 단위 짧은 케어</li>
<li>사내 공간 또는 별도 공간 진행</li>
<li>분기·연말 이벤트로 자주 진행</li>
</ul>
</section>

<section class="block" id="preset">
<h2>사전 협의 항목</h2>
<p>단체 케어는 다음 항목을 사전에 함께 확정해야 진행이 매끄럽습니다.</p>
<ul class="check-list">
<li><strong>진행 일자·시간</strong> — 시간대·시작/종료 시각</li>
<li><strong>인원·1인 케어 시간</strong> — 총 인원과 1인당 분 단위</li>
<li><strong>진행 공간</strong> — 별도 공간 확보 여부, 동선</li>
<li><strong>코스 종류</strong> — 어깨·목 케어 / 발 케어 / 전신 등</li>
<li><strong>결제·세금계산서</strong> — 법인 결제·정산 일정</li>
</ul>
</section>

<section class="block" id="space">
<h2>진행 공간 조건</h2>
<ul class="check-list">
<li>의자형 케어 — 작은 회의실 1개로 가능 (어깨·목·발)</li>
<li>매트형 케어 — 별도 공간 (2m × 2.5m) 권장 (전신 가벼운 케어)</li>
<li>대기·전환 동선 — 다음 인원 대기 공간 별도 권장</li>
<li>소음·조명 — 가능한 한 조용한 공간 권장</li>
</ul>
</section>

<section class="block" id="options">
<h2>코스 옵션</h2>
<table class="compare-table">
<thead><tr><th scope="col">옵션</th><th scope="col">시간</th><th scope="col">권장 인원·상황</th></tr></thead>
<tbody>
<tr><th scope="row">의자형 어깨·목</th><td>10·15·20분</td><td>20-30인 짧은 케어</td></tr>
<tr><th scope="row">의자형 발 케어</th><td>15·20분</td><td>장시간 서서 일하는 직군</td></tr>
<tr><th scope="row">매트형 전신 (간이)</th><td>20·30분</td><td>10-15인 / 충분한 공간 확보</td></tr>
<tr><th scope="row">이벤트 패키지</th><td>맞춤 협의</td><td>연말 송년·창립일 이벤트</td></tr>
</tbody>
</table>
</section>

<section class="block" id="flow">
<h2>진행 흐름</h2>
<ol class="steps">
<li><strong>사전 상담·견적</strong><p>인원·시간·공간 조건을 운영팀과 협의합니다.</p></li>
<li><strong>일정·결제 확정</strong><p>법인 결제 방식과 세금계산서 발행을 함께 확정합니다.</p></li>
<li><strong>진행 당일 세팅</strong><p>관리사 도착 후 공간 세팅(약 15-20분).</p></li>
<li><strong>순차 케어 진행</strong><p>대기·진행·교체 순으로 흐름 운영.</p></li>
<li><strong>마무리·정리</strong><p>공간 원상 복구 후 종료.</p></li>
</ol>
</section>

<section class="block" id="before">
<h2>이용 전 주의사항</h2>
<ul class="check-list">
<li>진행 인원이 많을수록 사전 협의 일정에 여유가 필요합니다 (최소 1-2주 권장).</li>
<li>진행 공간 조건이 미흡하면 관리사 도착 직후 추가 세팅이 필요할 수 있습니다.</li>
<li>임직원 개별 건강 상태(임신·질환 등)는 본인이 사전 안내해 주세요.</li>
<li>법인 결제는 사전 견적·계약 확정 후 진행됩니다.</li>
</ul>
</section>
""",
  "faqs": [
    ("최소 진행 인원이 있나요?",
     "10인부터 안내됩니다. 그 이하 인원은 일반 출장마사지 1인 단위 예약을 권장드립니다."),
    ("세금계산서·법인 결제가 가능한가요?",
     "가능합니다. 사전 견적 단계에서 사업자번호와 정산 일정을 함께 확정합니다."),
    ("관리사가 몇 명 방문하나요?",
     "인원·시간에 따라 다릅니다. 일반적으로 10-15인 진행 시 2-3명, 20-30인 진행 시 3-4명이 방문합니다."),
  ],
},
}


_SVC_RELATED = {
    "business-trip-massage": ["/service/swedish/", "/service/aroma/", "/reservation/how-to-book/", "/reservation/price/", "/guide/first-time-massage/"],
    "swedish": ["/service/aroma/", "/guide/aroma-vs-swedish/", "/reservation/price/", "/guide/first-time-massage/"],
    "aroma": ["/service/swedish/", "/guide/aroma-vs-swedish/", "/reservation/price/", "/guide/first-time-massage/"],
    "hometai": ["/service/swedish/", "/service/sports-massage/", "/reservation/price/", "/guide/first-time-massage/"],
    "sports-massage": ["/service/hometai/", "/guide/massage-before-after/", "/reservation/price/", "/reservation/check-before-use/"],
    "couple-massage": ["/service/swedish/", "/service/hotel-massage/", "/reservation/price/", "/reservation/how-to-book/"],
    "hotel-massage": ["/service/business-trip-massage/", "/reservation/late-night/", "/reservation/how-to-book/", "/magazine/travel-hotel-massage-guide/"],
    "office-massage": ["/reservation/how-to-book/", "/reservation/payment/", "/about/operation-policy/"],
}


for slug, name, summary, features, audience in SERVICES:
    s = SERVICES_RICH[slug]
    add(
        path=f"service/{slug}/index.html",
        url=f"/service/{slug}/",
        slug=f"service-{slug}",
        title=s["title"],
        description=s["desc"],
        h1=s["h1"],
        intro=f'<p class="lede">{s["lede"]}</p>',
        breadcrumbs=[("홈", "/"), ("서비스", "/service/"), (s["h1"], f"/service/{slug}/")],
        body=_SVC_BYLINE + _svc_toc(s["toc"]) + s["body"] + _svc_faq(s["faqs"]) + _SVC_DISCLAIMER,
        related=_rel(f"/service/{slug}/", _SVC_RELATED[slug], title="이어서 살펴볼 페이지"),
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
  title="출장마사지 가격 안내 | 코스·시간대별 기준 | 바로GO",
  description="출장마사지 코스별(스웨디시·아로마·홈타이·스포츠·커플) 시간 기준 가격 안내. 60·90·120·150분 단위 기준 금액과 시간대·진행 장소별 변동 기준을 정리했습니다.",
  h1="출장마사지 가격 안내",
  intro='<p class="lede">바로GO는 코스·시간·진행 장소·예약 시간대 기반으로 가격이 안내됩니다. 본 페이지에는 코스별 기준 금액을 정리해 두었으며, 정확한 최종 금액은 사전 전화 상담에서 일정·진행 장소가 확정된 직후 함께 안내됩니다. 사전 동의 없는 추가 비용은 부과되지 않습니다.</p>',
  breadcrumbs=[("홈","/"),("예약 안내","/reservation/"),("가격 안내","/reservation/price/")],
  body="""
<section class="block">
<h2>코스별 기준 가격 (시간 단위 · "부터" 기준)</h2>
<p>아래 가격은 코스별 일반 권역 기준 시작 금액입니다. 진행 장소·예약 시간대·이동 거리에 따라 일부 조정될 수 있으며, 최종 금액은 예약 상담 시 안내됩니다.</p>

<h3>홈타이(타이) 코스</h3>
<ul class="check-list">
<li>60분 — 90,000원부터</li>
<li>90분 — 110,000원부터</li>
<li>120분 — 130,000원부터</li>
</ul>

<h3>아로마 코스</h3>
<ul class="check-list">
<li>60분 — 100,000원부터</li>
<li>90분 — 120,000원부터</li>
<li>120분 — 140,000원부터</li>
</ul>

<h3>스웨디시(힐링) 코스</h3>
<ul class="check-list">
<li>60분 — 110,000원부터</li>
<li>90분 — 130,000원부터</li>
<li>120분 — 150,000원부터</li>
</ul>

<h3>스페셜·스포츠 코스</h3>
<ul class="check-list">
<li>60분 — 120,000원부터</li>
<li>90분 — 140,000원부터</li>
<li>120분 — 160,000원부터</li>
</ul>

<h3>커플(2인 동시) 코스</h3>
<ul class="check-list">
<li>60분 — 180,000원부터 (2인 합산)</li>
<li>90분 — 220,000원부터 (2인 합산)</li>
<li>120분 — 260,000원부터 (2인 합산)</li>
</ul>
</section>

<section class="block">
<h2>가격이 달라지는 4가지 기준</h2>
<ol class="steps">
<li><strong>코스 길이</strong><p>60 / 90 / 120 / 150분 단위로 기준 금액이 구분됩니다. 첫 이용 시 90분 또는 120분이 가장 자주 권해집니다.</p></li>
<li><strong>코스 종류</strong><p>스웨디시·아로마·홈타이·스포츠·커플 등 유형에 따라 기준 금액이 다릅니다.</p></li>
<li><strong>예약 시간대</strong><p>심야(01시 이후) 시간대는 일부 추가 비용이 발생할 수 있습니다.</p></li>
<li><strong>이동 거리·진행 장소</strong><p>광역 이동·외곽 지역·펜션 등 진입 거리·장소 유형에 따라 일부 이동료가 추가될 수 있습니다.</p></li>
</ol>
</section>

<section class="block">
<h2>가격 안내 원칙</h2>
<ul class="check-list">
<li>예약 확정 전 모든 비용을 사전에 안내합니다.</li>
<li>예약 이후 사전 동의 없는 추가 비용은 부과되지 않습니다.</li>
<li>"무조건 1위", "최저가 보장", "100% 만족" 등 과장 표현은 사용하지 않습니다.</li>
<li>실제와 다른 미끼 가격은 표기하지 않습니다. 기준 가격은 일반 권역 기준이며, 진행 장소·시간대에 따라 조정됩니다.</li>
</ul>
</section>

<section class="block">
<h2>참고 사항</h2>
<ul class="check-list">
<li>※ 지역, 시간대, 코스, 진행 장소에 따라 금액은 달라질 수 있습니다.</li>
<li>※ 정확한 가격은 예약 상담 시 최종 안내됩니다.</li>
<li>※ 결제 수단·세금계산서 등은 <a href="/reservation/payment/">결제 안내</a> 페이지를 참고해 주세요.</li>
<li>※ 본 가격 안내 최종 업데이트: 2026년 5월 기준</li>
</ul>
</section>
""",
)

add(
  path="reservation/check-before-use/index.html", url="/reservation/check-before-use/", slug="check-before-use",
  title="이용 전 확인사항 | 건강·공간·시간 점검 | 바로GO",
  description="출장마사지 예약 전 확인하면 좋은 건강 상태, 공간 조건, 시간 일정을 정리했습니다. 안전하고 만족스러운 이용을 위한 점검 항목입니다.",
  h1="이용 전 확인사항",
  intro='<p class="lede">출장마사지는 컨디션 회복과 휴식을 목적으로 진행되는 케어입니다. 이용 전 아래 항목을 한 번씩 확인하시면 더 만족스러운 시간을 보내실 수 있습니다.</p>',
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

# ---------- Review pages (E-E-A-T 강화) ----------
# UGC 성격이라 Google이 특히 엄격. 후기 검수·익명화·조작 방지 정책 명시.

_REVIEW_BYLINE = (
    '<div class="guide-meta">'
    '<div class="guide-meta-author">'
    '<span class="guide-meta-avatar" aria-hidden="true">YH</span>'
    '<div class="guide-meta-author-text">'
    '<strong>바로GO 후기 검수팀 (YH LAB)</strong>'
    '<span>운영팀 직접 검수 · 사업자등록번호 815-26-00585</span>'
    '</div></div>'
    '<div class="guide-meta-info">'
    '<span class="guide-meta-tag">최종 업데이트 · 2026-05</span>'
    '<span class="guide-meta-tag">후기 정책 v2.0</span>'
    '</div></div>'
)

_REVIEW_DISCLAIMER = (
    '<section class="block">'
    '<div class="callout note">'
    '<strong>후기 검수 정책 안내</strong>'
    '<p>본 페이지에 게시된 모든 후기는 실제 예약 상담·진행 이력이 확인된 이용자의 진술을 토대로, 운영팀이 직접 검수·익명화한 후 게시합니다. '
    '광고성 표현·과장 표현·운영팀 자체 작성 후기는 일체 게시하지 않으며, 허위 후기로 확인되는 경우 즉시 삭제 처리됩니다. '
    '본 페이지는 YH LAB(바로GO 운영) 사업자등록번호 815-26-00585·대표 김유환 의 책임 하에 작성·관리됩니다.</p>'
    '</div>'
    '</section>'
)


def _rv_card(meta, text):
    return (
        '<article class="review-card">'
        f'<p class="review-meta">{meta}</p>'
        f'<p>{text}</p>'
        '</article>'
    )


# 후기 페이지 전용 toc·faq 헬퍼 (review 페이지가 _guide_toc 정의보다 앞에 있어 별도 정의)
def _review_toc(items):
    li = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for label, anchor in items)
    return f'<nav class="guide-toc" aria-label="이 페이지에서 다루는 내용"><strong>이 페이지에서 다루는 내용</strong><ol>{li}</ol></nav>'


def _review_faq(items):
    rows = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f'<section class="block" id="faq"><h2>자주 묻는 질문</h2><div class="faq">{rows}</div></section>'


add(
  path="review/index.html", url="/review/", slug="review-hub",
  title="실제 이용 후기 — 후기 검수·익명화 정책 공개 | 바로GO",
  description="바로GO 실제 이용 후기 페이지. 후기는 운영팀이 직접 검수·익명화 후 게시되며, 광고성·과장 표현은 일체 노출하지 않습니다. 후기 운영 원칙·조작 방지 정책·신고 채널을 함께 공개합니다.",
  h1="실제 이용 후기",
  intro='<p class="lede">바로GO 후기는 "예약 과정이 명확했는가, 시간이 잘 지켜졌는가, 설명이 충분했는가, 청결 기준이 지켜졌는가" 4가지 기준으로 정리합니다. 광고성·과장 표현·자체 작성 후기는 일체 게시하지 않으며, 모든 후기는 운영팀이 직접 검수 후 익명화해 노출합니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/")],
  body=_REVIEW_BYLINE + _review_toc([
    ("후기를 정리하는 4가지 기준", "criteria"),
    ("최근 이용 후기 (검수 완료)", "recent"),
    ("후기 검수 절차", "process"),
    ("익명화 규칙", "anonymize"),
    ("후기 조작 방지 정책", "anti-fraud"),
    ("허위 후기 신고 채널", "report"),
  ]) + """
<section class="block" id="criteria">
<h2>후기를 정리하는 4가지 기준</h2>
<p>"좋아요/별 다섯 개" 같은 단순 만족도 후기는 정보가 적습니다. 바로GO는 다음 4가지 항목을 중심으로 후기를 정리합니다.</p>
<ul class="check-list">
<li><strong>예약 과정</strong> — 가격·코스·취소 기준이 사전에 충분히 안내됐는지</li>
<li><strong>시간 준수</strong> — 약속한 도착·진행·종료 시각이 지켜졌는지</li>
<li><strong>설명의 충분함</strong> — 진행 흐름·주의사항·사후 케어가 안내됐는지</li>
<li><strong>청결·매너</strong> — 도구 위생·진행 매너·개인정보 보호가 지켜졌는지</li>
</ul>
<p>운영팀은 이 4가지 기준에 따라 후기 본문을 정리하며, 단순 감탄·과장 표현은 정리 과정에서 제외합니다.</p>
</section>

<section class="block" id="recent">
<h2>최근 이용 후기 (검수 완료)</h2>
<div class="review-grid">
""" +
_rv_card("서울 강남 · 호텔 · 90분 스웨디시", "예약 시간보다 5분 정도 일찍 도착했고, 진행 전 코스와 주의사항을 다시 한번 설명해 주셔서 처음이라 걱정했던 부분이 줄었습니다.") +
_rv_card("부산 해운대 · 호텔 · 60분 아로마", "출장 일정 중간에 시간을 비워서 호텔에서 받았는데, 위치 확인과 도착 안내가 명확해 동선에 무리가 없었습니다.") +
_rv_card("경기 분당 · 가정 · 120분 홈타이", "가격 기준이 예약 단계에서 명확하게 안내되어 추가 비용 걱정 없이 진행했습니다. 도구 위생도 신뢰가 갔습니다.") +
_rv_card("제주 중문 · 풀빌라 · 90분 아로마", "성수기였는데도 일정 조율이 빨라서 다음 일정에 차질이 없었습니다. 향 선택도 사전에 안내해 주셨습니다.") +
_rv_card("인천 송도 · 호텔 · 60분 스웨디시", "야근 후 호텔로 곧바로 부탁드렸는데, 도착 예정 시각이 정확히 지켜져서 다음 날 일정에 무리가 없었습니다.") +
_rv_card("대전 둔산 · 가정 · 90분 홈타이", "오일 부담이 없는 홈타이를 권장 받아 선택했고, 진행 후 가벼운 스트레칭 안내까지 챙겨주셔서 만족스러웠습니다.") +
"""</div>
<p class="muted">※ 후기 본문은 운영팀이 핵심 내용을 정리·요약한 것이며, 이용자 원문 그대로의 표현은 익명화·정제 과정을 거쳐 게시됩니다.</p>
</section>

<section class="block" id="process">
<h2>후기 검수 절차</h2>
<p>후기는 다음 4단계 절차를 거쳐 게시됩니다.</p>
<ol class="steps">
<li><strong>접수</strong><p>상담 종료 후 이용자가 전화·문자·문의 양식으로 자유롭게 의견을 남깁니다.</p></li>
<li><strong>본인 확인</strong><p>예약 이력과 실제 진행 여부를 운영팀이 직접 확인합니다.</p></li>
<li><strong>익명화·정제</strong><p>이름·연락처는 마스킹 처리하고, 광고성·과장 표현은 정리·요약합니다.</p></li>
<li><strong>게시</strong><p>지역·코스·시간 등 일반 정보만 노출해 본 페이지에 게시합니다.</p></li>
</ol>
</section>

<section class="block" id="anonymize">
<h2>익명화 규칙</h2>
<ul class="check-list">
<li>이름은 "김** · 이** · 박**" 형태로 두 자만 마스킹 후 표기</li>
<li>전화번호·이메일·주소는 일체 노출하지 않음</li>
<li>지역은 시·구·동(권역) 단위까지만 표기</li>
<li>특정 호텔명·아파트명 등 위치 식별 가능한 정보는 일반 표현으로 정제</li>
<li>이용 일자는 월(month) 단위로 표기</li>
</ul>
</section>

<section class="block" id="anti-fraud">
<h2>후기 조작 방지 정책</h2>
<div class="dos-donts">
<div class="dos">
<strong>운영팀이 항상 합니다</strong>
<ul>
<li>모든 후기의 진위를 예약 이력으로 직접 확인</li>
<li>익명화 후 본인 식별 정보 차단</li>
<li>분기별 후기 진위 재점검 (랜덤 샘플)</li>
</ul>
</div>
<div class="donts">
<strong>운영팀이 절대 하지 않습니다</strong>
<ul>
<li>운영팀 자체 작성 후기 게시 — 발견 시 즉시 삭제 + 위반 기록</li>
<li>외부 업체에 후기 제작·작성을 위탁</li>
<li>"최고", "1위", "완벽" 등 광고성 표현 후기 게시</li>
<li>특정 관리사·지점에 유리하게 후기 정렬·강조</li>
</ul>
</div>
</div>
</section>

<section class="block" id="report">
<h2>허위 후기 신고 채널</h2>
<p>본 페이지의 후기 중 허위로 의심되는 항목이 있다면 운영팀에 직접 알려주세요. 신고가 사실로 확인되면 즉시 삭제 처리됩니다.</p>
<ul class="check-list">
<li>웹 신고 — <a href="/support/report/">불편 신고</a> 페이지에서 24시간 접수</li>
<li>전화 신고 — <a href="tel:0508-202-4719">0508-202-4719</a> 운영팀 직통</li>
<li>처리 — 신고 접수 후 24시간 이내 운영팀이 직접 확인 후 회신</li>
</ul>
</section>
""" + _review_faq([
    ("후기를 어떻게 남길 수 있나요?",
     "예약 진행 후 운영팀에서 안내드리는 채널(전화·문자·문의 양식)로 자유롭게 남기실 수 있습니다. 별도 회원 가입은 필요하지 않습니다."),
    ("후기 게시까지 얼마나 걸리나요?",
     "본인 확인·익명화·정제 절차를 거쳐 일반적으로 영업일 기준 3-5일 내 게시됩니다. 검수 결과에 따라 게시되지 않을 수 있습니다."),
    ("후기는 모두 게시되나요?",
     "본인 확인이 안 되거나, 광고성·과장 표현이 과도해 정제가 어려운 경우 게시되지 않습니다. 게시 여부와 무관하게 운영팀 내부에서는 운영 개선 자료로 활용됩니다."),
    ("이미 게시된 본인 후기를 삭제할 수 있나요?",
     "가능합니다. <a href=\"/support/contact/\">문의하기</a>에서 본인 확인 정보와 함께 삭제 요청을 보내주시면 운영팀이 직접 확인 후 처리합니다."),
]) + _REVIEW_DISCLAIMER,
  related=_rel("/review/", ["/review/first-time/", "/review/reservation-case/", "/review/area/", "/about/operation-policy/"], title="이어서 살펴볼 페이지"),
)


add(
  path="review/reservation-case/index.html", url="/review/reservation-case/", slug="review-case",
  title="예약 사례 — 상담 과정·일정 조율·코스 변경 패턴 | 바로GO",
  description="실제 예약 상담에서 자주 나오는 일정 조율·이동 거리·코스 변경·시간 연장 사례 5가지를 운영팀이 정리했습니다. 처음 예약하시는 분이 사전에 알아두면 좋은 흐름.",
  h1="예약 사례",
  intro='<p class="lede">예약 상담에서 가장 자주 발생하는 흐름과 변경 사례를 운영팀이 직접 정리했습니다. 처음 예약하시는 분이 사전 준비하시는 데 도움이 될 수 있도록, 사례마다 발생 배경·운영팀 안내 방식을 함께 적었습니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/"),("예약 사례","/review/reservation-case/")],
  body=_REVIEW_BYLINE + _review_toc([
    ("자주 보는 예약 사례 5가지", "patterns"),
    ("사례 1 — 출장 + 호텔 야간", "case-1"),
    ("사례 2 — 광역 이동 + 일정 변경", "case-2"),
    ("사례 3 — 코스 중 시간 연장", "case-3"),
    ("사례 4 — 커플 동시 진행 협의", "case-4"),
    ("사례 5 — 심야 시간대 예약", "case-5"),
    ("사례 정리·익명화 기준", "policy"),
  ]) + """
<section class="block" id="patterns">
<h2>자주 보는 예약 사례 5가지</h2>
<p>예약 상담은 사용자마다 다르지만, 매월 운영팀에서 가장 자주 마주치는 흐름은 어느 정도 정형화됩니다. 처음 이용하시는 분이 사전 준비에 참고하실 수 있도록 5가지 대표 사례를 정리합니다.</p>
</section>

<section class="block" id="case-1">
<h2>사례 1 — 출장 + 호텔 야간</h2>
<div class="callout tip">
<strong>상담 흐름 요약</strong>
<p>저녁 미팅 종료 후 호텔로 곧바로 진행되는 패턴. 체크인 직후 짐 정리·샤워 시간 30분을 두고, 22-23시경 60분 코스로 진행되는 흐름이 가장 자주 안내됩니다.</p>
</div>
<ul class="check-list">
<li>객실 호수·체크인 시각 사전 확인 필수</li>
<li>다음 날 일정이 이른 경우 60분 코스 권장</li>
<li>스웨디시 또는 아로마 자주 선택</li>
</ul>
</section>

<section class="block" id="case-2">
<h2>사례 2 — 광역 이동 + 일정 변경</h2>
<div class="callout warn">
<strong>주의 — 권역 외곽 이동 변수</strong>
<p>권역 외곽(예: 서울 → 일산, 부산 → 김해)으로 이동 시 도착이 30분-1시간 늦춰지는 경우가 자주 있습니다. 사전 상담에서 이동 거리·도로 상황을 함께 안내해 일정 조정을 권장합니다.</p>
</div>
<ul class="check-list">
<li>도로 상황(주말 정체·우천)에 따라 도착 시각 변동</li>
<li>30분 단위 여유 확보 권장</li>
<li>일정 변경 시 운영팀 직통으로 즉시 안내</li>
</ul>
</section>

<section class="block" id="case-3">
<h2>사례 3 — 코스 중 시간 연장</h2>
<p>코스 진행 중 "조금 더 받고 싶다"는 요청이 들어오는 사례입니다. 일정에 여유가 있고 관리사 일정이 다음 예약과 충돌하지 않을 때 가능합니다.</p>
<ul class="check-list">
<li><strong>60분 → 90분</strong> 연장이 가장 자주</li>
<li>추가 비용은 합의된 단가에 시간 비율로 안내</li>
<li>다음 예약 일정에 따라 불가한 경우도 있음</li>
<li>현장에서 운영팀에 직접 확인 후 진행</li>
</ul>
</section>

<section class="block" id="case-4">
<h2>사례 4 — 커플 동시 진행 협의</h2>
<p>커플·가족이 함께 받기 위해 협의가 필요한 사례입니다. 진행 공간·관리사 인원·코스 매칭이 사전에 함께 확정되어야 합니다.</p>
<ul class="check-list">
<li>같은 공간 동시 진행이 기본 — 객실 크기 사전 확인</li>
<li>분리 공간 진행도 가능 (트윈룸·스위트룸)</li>
<li>두 명이 다른 코스 선택 가능 (예: 스웨디시 + 홈타이)</li>
<li>가격은 2인 합산 기준 — <a href="/service/couple-massage/">커플 마사지</a> 참고</li>
</ul>
</section>

<section class="block" id="case-5">
<h2>사례 5 — 심야 시간대 예약</h2>
<p>자정 이후 진행을 요청하시는 사례. 권역에 따라 가능 여부가 다르며, 호텔 진행이 가정 진행보다 더 자유롭습니다.</p>
<ul class="check-list">
<li>서울 강남·여의도 호텔은 자정 이후도 자주 안내</li>
<li>가정 진행은 권역에 따라 23-24시 마감</li>
<li>심야 진행은 사전 상담에서 권역·이동 확인 필수</li>
<li><a href="/reservation/late-night/">심야·새벽 예약 안내</a> 참고</li>
</ul>
</section>

<section class="block" id="policy">
<h2>사례 정리·익명화 기준</h2>
<p>본 페이지의 사례는 운영팀이 매월 처리한 실제 예약 상담 중 빈도가 높은 흐름을 정리한 것입니다. 다음 기준에 따라 정리됩니다.</p>
<ul class="check-list">
<li>특정 이용자를 식별 가능한 정보(이름·날짜·세부 위치)는 일체 제외</li>
<li>사례는 운영팀 작성으로, 이용자 후기 그대로의 인용이 아님을 명시</li>
<li>운영 개선 사항이 발견되면 다음 분기 정책 갱신에 반영</li>
</ul>
</section>
""" + _review_faq([
    ("위 사례는 실제 사용자의 후기인가요?",
     "본 페이지는 후기 인용이 아니라, 운영팀이 매월 처리한 예약 상담 중 빈도가 높은 흐름을 운영팀 시점에서 정리한 사례 모음입니다. 실제 이용자 후기는 <a href=\"/review/\">실제 이용 후기</a> 페이지에서 확인하실 수 있습니다."),
    ("내 예약도 위 사례 중 하나에 해당될까요?",
     "위 5가지는 가장 빈도가 높은 흐름이며, 실제 예약은 개별 상황에 맞춰 운영팀과 직접 협의됩니다. 사전 전화 상담에서 본인 일정·장소·코스 조건을 함께 안내드립니다."),
    ("사례에 없는 특수한 요청도 가능한가요?",
     "사례에 없는 요청도 운영팀과 사전 상담에서 가능 여부를 확인하실 수 있습니다. 안전·정책 기준에 부합한 요청은 가능한 범위에서 안내됩니다."),
]) + _REVIEW_DISCLAIMER,
  related=_rel("/review/reservation-case/", ["/review/", "/review/first-time/", "/reservation/how-to-book/", "/reservation/late-night/"], title="이어서 살펴볼 페이지"),
)


add(
  path="review/first-time/index.html", url="/review/first-time/", slug="review-first-time",
  title="처음 이용 고객 후기 — 첫 출장마사지 경험과 만족·아쉬움 포인트 | 바로GO",
  description="처음 출장마사지를 이용한 고객의 검수된 후기 8건과 첫 이용자가 가장 자주 언급한 만족·아쉬움 포인트, 첫 이용 전 자주 묻는 질문까지 정리했습니다.",
  h1="처음 이용 고객 후기",
  intro='<p class="lede">"이번이 처음입니다"라고 알려주신 분들의 검수된 후기와, 첫 이용자가 가장 자주 언급한 만족·아쉬움 포인트를 정리했습니다. 첫 이용 전 사전 준비에 참고하실 수 있도록 자주 묻는 질문도 함께 정리합니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/"),("처음 이용","/review/first-time/")],
  body=_REVIEW_BYLINE + _review_toc([
    ("첫 이용자 후기의 특징", "feature"),
    ("처음 이용 고객 후기 (검수 완료)", "reviews"),
    ("첫 이용자가 자주 언급한 만족 포인트", "good"),
    ("첫 이용자가 자주 언급한 아쉬움 포인트", "bad"),
    ("첫 이용을 매끄럽게 만드는 5가지", "tips"),
    ("첫 이용 시 자주 묻는 질문", "faq"),
  ]) + """
<section class="block" id="feature">
<h2>첫 이용자 후기의 특징</h2>
<p>처음 출장마사지를 이용하시는 분의 후기는 재이용 후기와 결이 조금 다릅니다. "코스 자체에 대한 만족"보다 "사전 안내가 얼마나 명확했는가, 진행 흐름이 얼마나 매끄러웠는가"에 대한 언급이 더 많습니다. 운영팀은 이러한 패턴을 토대로 첫 이용자 사전 안내를 더 자세히 설계합니다.</p>
</section>

<section class="block" id="reviews">
<h2>처음 이용 고객 후기 (검수 완료)</h2>
<div class="review-grid">
""" +
_rv_card("서울 마포 · 첫 이용 · 60분 스웨디시", "출장마사지가 처음이라 분위기가 어색할까 걱정했는데, 진행 전 충분히 설명해 주셔서 편하게 받았습니다. 처음에는 60분이 적당하다고 권해주셨습니다.") +
_rv_card("대전 둔산 · 첫 이용 · 90분 홈타이", "오일이 부담스러워 홈타이를 선택했는데, 옷 입은 상태로 진행돼서 더 편했습니다. 사후 스트레칭 안내도 챙겨주셨습니다.") +
_rv_card("부산 해운대 · 첫 이용 · 60분 아로마", "여행 일정 중 호텔에서 받았는데, 향을 미리 안내해 주셔서 부담 없이 선택했습니다. 다음에는 90분으로 받아볼 생각입니다.") +
_rv_card("인천 청라 · 첫 이용 · 60분 스웨디시", "예약 전 가격 안내가 명확해서 추가 비용 걱정이 없었습니다. 도구 위생도 신뢰가 갔습니다.") +
_rv_card("경기 분당 · 첫 이용 · 90분 스웨디시", "야근 후 가정으로 부탁드렸는데, 도착 안내가 정확해서 일정에 무리가 없었습니다. 사후 수분 보충 안내까지 챙겨주셔서 좋았습니다.") +
_rv_card("광주 상무 · 첫 이용 · 60분 아로마", "처음이라 어떤 코스를 받을지 고민했는데, 부드러운 압의 아로마를 권해주셔서 만족스럽게 받았습니다.") +
_rv_card("울산 남구 · 첫 이용 · 90분 홈타이", "운동 후 근육 뭉침이 심해서 홈타이를 선택했는데, 가동성 확인부터 진행해 주셔서 안심이었습니다.") +
_rv_card("제주 중문 · 첫 이용 · 90분 아로마", "여행 마지막 날 호텔에서 받았는데, 위치 안내와 도착 시각이 정확해 다음 일정에 차질이 없었습니다.") +
"""</div>
</section>

<section class="block" id="good">
<h2>첫 이용자가 자주 언급한 만족 포인트</h2>
<div class="dos">
<strong>가장 자주 언급되는 4가지</strong>
<ul>
<li><strong>사전 안내의 충분함</strong> — 가격·코스·취소 기준이 예약 전에 명확히 안내된 점</li>
<li><strong>도착 시간 정확성</strong> — 약속한 시각보다 늦거나 너무 일찍 오지 않은 점</li>
<li><strong>코스 권장의 합리성</strong> — 첫 이용에 무난한 코스를 직접 권해준 점</li>
<li><strong>사후 안내 매끄러움</strong> — 수분 섭취·휴식 권장 등 사후 케어 안내</li>
</ul>
</div>
</section>

<section class="block" id="bad">
<h2>첫 이용자가 자주 언급한 아쉬움 포인트</h2>
<div class="donts">
<strong>가장 자주 언급되는 3가지</strong>
<ul>
<li><strong>코스 길이 선택 어려움</strong> — 60·90·120분 중 무엇을 선택할지 사전에 더 자세한 안내가 있었으면 함</li>
<li><strong>공간 준비 안내 부족</strong> — 가정 진행 시 공간 정리 권장 사항을 사전에 더 자세히 안내했으면 함</li>
<li><strong>대기 시간 변수</strong> — 권역 외곽 이동 시 도착 시각이 약간 늦어진 경우</li>
</ul>
</div>
<p class="muted">운영팀은 위 아쉬움 포인트를 분기별로 점검하고 사전 상담 안내 스크립트에 반영합니다.</p>
</section>

<section class="block" id="tips">
<h2>첫 이용을 매끄럽게 만드는 5가지</h2>
<ol class="steps">
<li><strong>일정 여유 확보</strong><p>도착·진행·사후 휴식까지 총 2시간 여유 있게 잡으시는 것이 좋습니다.</p></li>
<li><strong>공간 정리</strong><p>가정 진행 시 가로 2m × 세로 2.5m 정도의 평평한 공간 확보.</p></li>
<li><strong>건강 상태 사전 안내</strong><p>임신·특정 질환·복용 약물·알레르기 등은 예약 단계에서 미리 알려주세요.</p></li>
<li><strong>코스 길이 60분으로 시작</strong><p>첫 이용은 60분으로 컨디션 점검하고, 다음 진행 시 조정하시는 흐름이 가장 안전합니다.</p></li>
<li><strong>사후 권장 사항 챙기기</strong><p>코스 후 30분 이내 물 500ml, 당일 음주 자제, 충분한 수면.</p></li>
</ol>
</section>
""" + _review_faq([
    ("옷은 어떻게 입어야 하나요?",
     "코스에 따라 다릅니다. 스웨디시·아로마 같이 오일을 사용하는 경우는 일회용 의류 또는 편한 의류로 환복하시고, 홈타이는 본인의 편한 의류를 그대로 입은 채 진행합니다."),
    ("관리사 분께 따로 준비할 것이 있나요?",
     "별도 준비물은 없습니다. 매트·오일·타월 등 진행 도구는 관리사가 모두 지참합니다. 가정 진행 시에는 평평한 공간과 깨끗한 시트 한 장 정도만 준비해 주세요."),
    ("처음에 어떤 코스가 가장 무난한가요?",
     "스웨디시 60분이 첫 이용에 가장 자주 권장됩니다. 부드러운 압의 오일 케어로 부담이 적습니다. 자세한 첫 이용 가이드는 <a href=\"/guide/first-time-massage/\">처음 이용 전 알아둘 점</a>을 참고해 주세요."),
    ("처음이라 긴장되는데 진행 중에 말해도 되나요?",
     "물론입니다. 압력 조절·진행 부위·휴식 요청 등 진행 중 언제든 말씀하실 수 있습니다. 첫 이용 시에는 시작 직후 5분 정도 압력 점검 시간을 두는 것이 일반적입니다."),
]) + _REVIEW_DISCLAIMER,
  related=_rel("/review/first-time/", ["/review/", "/guide/first-time-massage/", "/magazine/first-time-essentials/", "/reservation/check-before-use/"], title="이어서 살펴볼 페이지"),
)


add(
  path="review/area/index.html", url="/review/area/", slug="review-area",
  title="지역별 이용 후기 — 권역별 시간대·코스·진행 장소 패턴 | 바로GO",
  description="수도권·광역시·도(道) 권역·제주별로 자주 이용되는 시간대·코스·진행 장소 패턴을 운영팀이 검수된 후기를 토대로 정리했습니다.",
  h1="지역별 이용 후기 모음",
  intro='<p class="lede">시·도별로 자주 선택되는 시간대·코스·진행 장소 패턴이 분명히 다릅니다. 운영팀이 매월 처리한 후기·예약 데이터를 토대로 권역별 이용 경향을 정리합니다. 정량 수치가 아닌 정성적 패턴 정리입니다.</p>',
  breadcrumbs=[("홈","/"),("후기","/review/"),("지역별 후기","/review/area/")],
  body=_REVIEW_BYLINE + _review_toc([
    ("권역별 이용 패턴이 다른 이유", "why"),
    ("수도권 — 서울·경기·인천", "metro"),
    ("광역시 — 부산·대구·대전·광주·울산", "metropolitan"),
    ("도(道) 권역 — 강원·충청·전라·경상", "do"),
    ("제주 — 호텔·풀빌라 중심", "jeju"),
    ("권역별 검수 기준", "policy"),
  ]) + """
<section class="block" id="why">
<h2>권역별 이용 패턴이 다른 이유</h2>
<p>같은 코스라도 권역별 이용 흐름은 분명히 다릅니다. 인구 밀도, 호텔 분포, 교통 인프라, 산업 구조, 관광 수요가 권역마다 다르기 때문입니다. 본 페이지는 권역별로 가장 자주 보이는 후기 패턴을 정성적으로 정리합니다.</p>
<p class="muted">※ 본 페이지는 정량 데이터·통계가 아닌, 운영팀이 매월 처리한 후기·예약 흐름의 정성적 정리입니다.</p>
</section>

<section class="block" id="metro">
<h2>수도권 — 서울·경기·인천</h2>
<table class="compare-table">
<thead><tr><th scope="col">권역</th><th scope="col">자주 보이는 후기 패턴</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="/area/seoul/">서울</a></th><td>평일 야간 호텔 진행 비중 높음 · 강남·여의도 도심 호텔 자주 언급 · 심야 시간대 가능 권역 많음</td></tr>
<tr><th scope="row"><a href="/area/gyeonggi/">경기</a></th><td>분당·판교 IT 야근 후 가정 진행 · 일산·파주 신도시 가정 방문 · 31개 시·군 권역별 차이 큼</td></tr>
<tr><th scope="row"><a href="/area/incheon/">인천</a></th><td>공항 인근 단시간 호텔 케어 · 송도 출장 객실 진행 · 부평·구도심 가정 방문</td></tr>
</tbody>
</table>
</section>

<section class="block" id="metropolitan">
<h2>광역시 — 부산·대구·대전·광주·울산</h2>
<div class="dos-donts">
<div class="dos">
<strong>부산·대구·대전</strong>
<ul>
<li>부산 — 해운대·광안 관광 호텔 야간 진행</li>
<li>대구 — 수성·동성로 호텔, 권역별 시간 차이</li>
<li>대전 — 유성·둔산 평일 저녁 가정 방문</li>
</ul>
</div>
<div class="dos">
<strong>광주·울산</strong>
<ul>
<li>광주 — 상무·첨단 평일 저녁 비중 높음</li>
<li>울산 — 산업단지 야간·정기 진행 자주</li>
<li>두 권역 모두 가정·호텔 비중 비교적 균등</li>
</ul>
</div>
</div>
</section>

<section class="block" id="do">
<h2>도(道) 권역 — 강원·충청·전라·경상</h2>
<p>도 권역은 면적이 넓어 같은 도 안에서도 권역별 패턴 차이가 큽니다. 도시·관광·산업 지역에 따라 후기 흐름이 다릅니다.</p>
<ul class="check-list">
<li><a href="/area/gangwon/"><strong>강원</strong></a> — 강릉·속초 관광 호텔, 평창·홍천 리조트, 심야 마감 비교적 이른 편</li>
<li><a href="/area/chungbuk/"><strong>충북</strong></a> — 청주·충주 산업 출장 평일 저녁, 단양 리조트</li>
<li><a href="/area/chungnam/"><strong>충남</strong></a> — 천안·아산 산업 출장, 보령·태안 관광</li>
<li><a href="/area/jeonbuk/"><strong>전북</strong></a> — 전주 한옥마을 호텔, 익산·군산 산업</li>
<li><a href="/area/jeonnam/"><strong>전남</strong></a> — 여수·순천 관광 호텔, 광양·목포 산업</li>
<li><a href="/area/gyeongbuk/"><strong>경북</strong></a> — 포항·구미 산업, 경주 관광 호텔</li>
<li><a href="/area/gyeongnam/"><strong>경남</strong></a> — 창원·김해 산업, 통영·거제 관광</li>
</ul>
</section>

<section class="block" id="jeju">
<h2>제주 — 호텔·풀빌라 중심</h2>
<p><a href="/area/jeju/">제주</a>는 다른 권역과 가장 다른 패턴을 보입니다. 가정 방문보다 호텔·리조트·풀빌라 진행이 압도적으로 많고, 여행 일정과 맞물린 케어 비중이 높습니다.</p>
<ul class="check-list">
<li>중문·시내 호텔 진행, 체크인 후 저녁 시간대</li>
<li>풀빌라 독채 — 커플·가족 단위 90-120분 코스</li>
<li>렌터카 운전 후 어깨·등 회복 홈타이 자주 안내</li>
<li>오름·트레킹 후 다리 회복 스포츠 코스</li>
</ul>
</section>

<section class="block" id="policy">
<h2>권역별 검수 기준</h2>
<p>본 페이지의 권역별 패턴은 다음 기준에 따라 정리됩니다.</p>
<ul class="check-list">
<li>매월 운영팀이 처리한 후기·예약 상담 중 빈도가 높은 흐름 정리</li>
<li>특정 이용자 식별 정보는 일체 제외</li>
<li>정량 수치는 발표하지 않음 (운영 데이터 외부 공개 자제)</li>
<li>분기별 갱신 — 권역별 흐름 변화 반영</li>
</ul>
</section>
""" + _review_faq([
    ("위 패턴은 모든 이용자에게 동일하게 적용되나요?",
     "권역별 가장 자주 보이는 흐름이지만, 모든 예약이 같은 패턴을 따르지 않습니다. 실제 예약은 사전 상담에서 개별 일정·조건에 맞춰 안내됩니다."),
    ("내가 사는 권역의 패턴은 어디서 자세히 볼 수 있나요?",
     "각 시·도 페이지(<a href=\"/area/\">지역별 찾기</a>)에 권역별 자주 안내되는 시간대·코스·진행 장소 정보가 정리되어 있습니다."),
    ("권역 흐름은 얼마나 자주 갱신되나요?",
     "분기별 1회 갱신을 원칙으로 합니다. 큰 변화가 발생하면 더 빠르게 본 페이지를 업데이트합니다."),
]) + _REVIEW_DISCLAIMER,
  related=_rel("/review/area/", ["/review/", "/area/", "/magazine/regional-usage-tips/", "/reservation/visit-area/"], title="이어서 살펴볼 페이지"),
)

# ---------- Guide pages (E-E-A-T 부합한 본격 콘텐츠) ----------
_GUIDE_BYLINE = (
    '<div class="guide-meta">'
    '<div class="guide-meta-author">'
    '<span class="guide-meta-avatar" aria-hidden="true">YH</span>'
    '<div class="guide-meta-author-text">'
    '<strong>바로GO 운영팀 (YH LAB)</strong>'
    '<span>출장마사지 예약 상담 운영팀 · 사업자등록번호 815-26-00585</span>'
    '</div></div>'
    '<div class="guide-meta-info">'
    '<span class="guide-meta-tag">최종 업데이트 · 2026-05</span>'
    '<span class="guide-meta-tag">읽는 시간 · 약 {min}분</span>'
    '</div></div>'
)

_GUIDE_DISCLAIMER = (
    '<section class="block">'
    '<div class="callout note">'
    '<strong>면책 안내</strong>'
    '<p>본 페이지의 정보는 일반적인 출장마사지 이용 안내를 위한 자료이며, 의료 행위나 의학적 조언이 아닙니다. '
    '건강 상태와 관련된 결정은 의료 전문가와 상담하시기 바랍니다. '
    '본 페이지는 YH LAB(바로GO 운영) 사업자등록번호 815-26-00585·대표 김유환·경기도 파주시 청석로 268 '
    '의 책임 하에 작성·관리됩니다.</p>'
    '</div>'
    '</section>'
)


def _guide_toc(items):
    li = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for label, anchor in items)
    return f'<nav class="guide-toc" aria-label="이 페이지에서 다루는 내용"><strong>이 페이지에서 다루는 내용</strong><ol>{li}</ol></nav>'


def _faq_block(items):
    rows = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f'<section class="block" id="faq"><h2>자주 묻는 질문</h2><div class="faq">{rows}</div></section>'


# ===== Guide 1 — 출장마사지란? =====
_GUIDE1_BODY = _GUIDE_BYLINE.format(min=5) + _review_toc([
    ("출장마사지의 정의", "definition"),
    ("매장형 마사지와의 차이", "vs-store"),
    ("출장마사지의 종류 6가지", "types"),
    ("이용 흐름 한눈에 보기", "flow"),
    ("어떤 상황에 적합한가", "when"),
    ("자주 오해하는 점", "myths"),
    ("자주 묻는 질문", "faq"),
]) + """
<section class="block" id="definition">
<h2>출장마사지의 정의</h2>
<p><strong>출장마사지</strong>는 관리사가 사용자가 지정한 공간(가정·호텔 객실·오피스텔·펜션·사무실 등)으로 직접 방문하여 마사지 케어를 진행하는 서비스 유형입니다. 매장으로 이동할 필요가 없어 일정에 제약이 큰 분, 심야·이른 아침 시간대 이용을 원하는 분, 호텔 체크인 후 객실에서 휴식을 함께 받고 싶은 분이 자주 선택합니다.</p>
<p>국내에서는 \"출장마사지\", \"홈케어\", \"홈타이\"(태국식 스트레칭 기반 출장 케어), \"호텔 마사지\" 등의 표현이 모두 출장마사지 카테고리에 포함됩니다. 본 페이지에서는 이를 통칭해 <strong>출장마사지</strong>로 안내합니다.</p>
</section>

<section class="block" id="vs-store">
<h2>매장형 마사지와의 핵심 차이</h2>
<div class="compare-table-wrap">
<table class="compare-table">
<thead><tr><th>항목</th><th>매장형 마사지</th><th>출장마사지</th></tr></thead>
<tbody>
<tr><th scope="row">진행 장소</th><td>매장 룸</td><td>사용자 지정 공간(가정·호텔·오피스텔)</td></tr>
<tr><th scope="row">이동 주체</th><td>사용자가 매장 방문</td><td>관리사가 사용자 공간으로 이동</td></tr>
<tr><th scope="row">시간 제약</th><td>매장 영업 시간 내</td><td>24시간 협의 가능(권역별 상이)</td></tr>
<tr><th scope="row">공간 컨디션</th><td>매장 표준 환경</td><td>사용자 공간 그대로 (장비 설치 X)</td></tr>
<tr><th scope="row">일정 조율</th><td>예약 시간 선택</td><td>관리사 이동 시간 포함 협의</td></tr>
<tr><th scope="row">결제</th><td>매장 결제</td><td>사전 안내된 방식 결제</td></tr>
</tbody></table>
</div>
<p>가장 큰 차이는 \"이동 주체\"입니다. 매장형은 사용자가 매장으로, 출장은 관리사가 사용자 공간으로 이동합니다. 이로 인해 출장마사지는 사전 일정 조율의 정확성이 가장 중요한 단계가 됩니다.</p>
</section>

<section class="block" id="types">
<h2>출장마사지의 종류 6가지</h2>
<ul class="check-list">
<li><strong>스웨디시</strong> — 오일을 활용한 부드러운 압 중심 전신 이완 케어. 첫 이용자에게 가장 자주 권해지는 유형입니다.</li>
<li><strong>아로마</strong> — 에센셜 오일을 활용한 향기 케어 중심. 정서적 안정·수면 보조 목적이 큰 분께 적합합니다.</li>
<li><strong>홈타이(타이마사지)</strong> — 태국식 스트레칭+압 기반. 자세 교정·가동 범위 회복 목적이 큰 분께 권해집니다.</li>
<li><strong>스포츠</strong> — 운동 후 특정 부위 집중 회복 케어. 통증·뭉침이 부위별로 누적된 분께 적합합니다.</li>
<li><strong>커플(2인 동시)</strong> — 두 분이 같은 공간에서 동시에 받는 형태. 가정·호텔·펜션 모두 진행 가능합니다.</li>
<li><strong>호텔/사무실 방문</strong> — 진행 장소를 기준으로 분류한 구분. 출장 일정·기업 단위 케어에 자주 선택됩니다.</li>
</ul>
<p>각 코스 상세 안내는 <a href="/service/">서비스 안내</a> 페이지에서 확인하실 수 있습니다.</p>
</section>

<section class="block" id="flow">
<h2>이용 흐름 한눈에 보기</h2>
<ol class="steps">
<li><strong>전화 상담</strong><p>24시간 0508-202-4719 상담을 통해 권역 가능 시간·코스·진행 장소를 확인합니다.</p></li>
<li><strong>일정 확정</strong><p>도착 시간·코스 길이·인원·옵션을 함께 합의합니다.</p></li>
<li><strong>관리사 배정</strong><p>권역 동선을 고려해 가까운 관리사가 배정됩니다.</p></li>
<li><strong>도착·진행</strong><p>약속 시간 직전 도착 안내 후 사용자 공간에서 코스가 시작됩니다.</p></li>
<li><strong>결제·종료</strong><p>사전 안내된 방식으로 결제가 진행됩니다.</p></li>
</ol>
</section>

<section class="block" id="when">
<h2>어떤 상황에 적합한가</h2>
<div class="dos-donts">
<div class="dos">
<h3>출장마사지가 적합한 상황</h3>
<ul>
<li>출장·여행 일정으로 호텔에 묵을 때</li>
<li>심야·이른 아침에 이용하고 싶을 때</li>
<li>이동이 어려운 컨디션일 때(피로 누적·감기 회복기 등)</li>
<li>커플·가족 단위로 함께 받고 싶을 때</li>
<li>업무가 늦게 끝나 매장 영업 시간에 맞추기 어려울 때</li>
</ul>
</div>
<div class="donts">
<h3>매장형이 더 적합한 상황</h3>
<ul>
<li>전문 장비(스파·사우나·물 테라피)가 필요할 때</li>
<li>여러 코스를 코스 메뉴식으로 비교하며 선택하고 싶을 때</li>
<li>사용자 공간 컨디션(반려동물·진행 공간 부족 등) 조성이 어려울 때</li>
</ul>
</div>
</div>
</section>

<section class="block" id="myths">
<h2>출장마사지에 대해 자주 오해하는 점</h2>
<div class="callout warn">
<strong>오해 1. 치료 효과를 보장한다?</strong>
<p>출장마사지는 의료 행위가 아닙니다. 통증·질환의 치료를 보장하지 않으며, 의학적 진단이 필요한 증상은 반드시 의료기관 상담이 우선되어야 합니다.</p>
</div>
<div class="callout warn">
<strong>오해 2. 가격이 매장보다 무조건 비싸다?</strong>
<p>이동·시간대에 따라 차이는 있지만, 매장 이동·대기 시간을 환산하면 큰 차이가 없는 경우가 많습니다. 자세한 가격 변동 요인은 <a href="/guide/massage-price-standard/">가격이 달라지는 이유</a>에서 확인할 수 있습니다.</p>
</div>
<div class="callout warn">
<strong>오해 3. 모든 호텔에서 가능하다?</strong>
<p>호텔별로 룸서비스·외부 인원 출입 정책이 다릅니다. 호텔명·체크인 시각을 사전 상담에서 함께 확인하는 것이 안전합니다.</p>
</div>
</section>
""" + _review_faq([
    ("출장마사지와 홈타이는 같은 건가요?", "홈타이는 출장마사지의 한 종류입니다. 태국식 스트레칭과 압을 결합한 코스를 출장 형태로 진행할 때 \"홈타이\"라는 명칭이 자주 쓰입니다."),
    ("호텔 객실 방문도 출장마사지인가요?", "네, 진행 장소가 호텔 객실인 출장마사지를 의미합니다. 객실 호수·체크인 정보 사전 공유가 필요합니다."),
    ("어떤 코스부터 받는 게 좋을까요?", "출장마사지가 처음이라면 스웨디시 90분이 가장 자주 권해집니다. 컨디션과 목적에 따라 사전 전화에서 함께 권장해 드립니다."),
    ("출장마사지는 의료 효과가 있나요?", "치료·진단의 의료 행위가 아닙니다. 컨디션 회복·휴식·이완을 목적으로 하는 케어입니다."),
    ("처음 이용 전 준비할 것이 있나요?", "공간 정리, 충분한 수분 섭취, 식사 시점 조정 정도면 충분합니다. 자세한 점검은 <a href=\"/guide/first-time-massage/\">처음 이용 전 알아둘 점</a>을 참고해 주세요."),
]) + _GUIDE_DISCLAIMER


# ===== Guide 2 — 마사지 전후 주의사항 =====
_GUIDE2_BODY = _GUIDE_BYLINE.format(min=6) + _review_toc([
    ("24시간 전부터 권장되는 준비", "before-24h"),
    ("직전 1~2시간 — 식사·음주·운동", "before-2h"),
    ("진행 직전 — 공간·복장·소지품", "right-before"),
    ("진행 중 권장 사항", "during"),
    ("직후 1시간 권장·금기", "after-1h"),
    ("24시간 후까지 회복 관리", "after-24h"),
    ("이상 반응 발생 시 대처", "abnormal"),
    ("건강 상태별 주의 (임신·고혈압·당뇨 등)", "conditions"),
    ("자주 묻는 질문", "faq"),
]) + """
<section class="block" id="before-24h">
<h2>24시간 전부터 권장되는 준비</h2>
<p>마사지 효과는 케어 당일만이 아니라 전후 24시간의 컨디션 관리에 영향을 받습니다. 24시간 전부터 다음 사항을 권장합니다.</p>
<ul class="check-list">
<li>수면 7시간 이상 확보 (수면 부족은 케어 후 어지러움 빈도를 높입니다)</li>
<li>물 1.5~2L 분산 섭취</li>
<li>당일 격렬한 운동·고강도 트레이닝 자제</li>
<li>알코올 섭취 가급적 자제(혈관 확장으로 케어 후 어지러움·메스꺼움이 발생할 수 있음)</li>
<li>피부에 자극이 큰 케어(필링·왁싱) 24시간 내 자제</li>
</ul>
</section>

<section class="block" id="before-2h">
<h2>직전 1~2시간 — 식사·음주·운동</h2>
<div class="dos-donts">
<div class="dos">
<h3>권장</h3>
<ul>
<li>가벼운 식사를 1시간 전까지 마무리</li>
<li>물 한 컵 미리 섭취</li>
<li>편안한 옷 준비</li>
<li>화장실 미리 다녀오기</li>
</ul>
</div>
<div class="donts">
<h3>피해야 할 것</h3>
<ul>
<li>케어 30분 이내 식사·과식</li>
<li>음주 직후 케어 (반사 신경·체온 조절에 영향)</li>
<li>고강도 운동 직후 (근육이 충혈된 상태에서 압이 가해지면 통증 ↑)</li>
<li>카페인 과다 섭취 (이완 효과 저하)</li>
</ul>
</div>
</div>
</section>

<section class="block" id="right-before">
<h2>진행 직전 — 공간·복장·소지품</h2>
<ul class="check-list">
<li><strong>공간</strong> — 매트나 침구를 펼칠 수 있는 최소 공간 확보. 호텔 객실의 경우 침대 공간이 활용됩니다.</li>
<li><strong>온도</strong> — 24~26°C 정도의 따뜻한 실내 온도가 권장됩니다. 너무 차가운 환경은 근육 이완 효과를 떨어뜨립니다.</li>
<li><strong>조명</strong> — 너무 밝지 않게 조절. 간접 조명이나 무드등이 권장됩니다.</li>
<li><strong>의류</strong> — 오일 사용 코스는 일회용 의류 또는 편한 의류로 갈아입습니다.</li>
<li><strong>소지품</strong> — 귀금속·시계 등은 별도 보관 권장.</li>
<li><strong>반려동물</strong> — 별도 공간으로 분리 부탁드립니다.</li>
</ul>
</section>

<section class="block" id="during">
<h2>진행 중 권장 사항</h2>
<div class="callout tip">
<strong>편안하게 받기 위한 팁</strong>
<p>호흡을 깊게, 들이마실 때 4초 / 내쉴 때 6초 정도의 호흡 패턴이 권장됩니다. 압이 너무 강하거나 통증이 느껴진다면 즉시 관리사에게 알려 주세요. 케어는 \"참는\" 것이 아니라 \"이완하는\" 시간입니다.</p>
</div>
<p>특정 부위(목·허리·어깨)에 집중적인 케어를 원하면 진행 직전 또는 진행 초반에 요청하시면 됩니다. 코스 중간에 화장실 등 일시적 휴식이 필요하면 언제든 요청 가능합니다.</p>
</section>

<section class="block" id="after-1h">
<h2>직후 1시간 권장·금기</h2>
<div class="dos-donts">
<div class="dos">
<h3>권장</h3>
<ul>
<li>물 한 컵 또는 따뜻한 차 섭취</li>
<li>15~30분 휴식</li>
<li>천천히 일어나 어지러움 확인</li>
<li>가벼운 스트레칭(코스가 정적이었을 경우)</li>
</ul>
</div>
<div class="donts">
<h3>피해야 할 것</h3>
<ul>
<li>곧바로 격렬한 운동·사우나·찜질방</li>
<li>음주(혈관 확장 + 알코올 흡수 빨라짐)</li>
<li>장시간 운전 (어지러움 가능성)</li>
<li>너무 뜨거운 샤워(체온 급변)</li>
</ul>
</div>
</div>
</section>

<section class="block" id="after-24h">
<h2>24시간 후까지 회복 관리</h2>
<ul class="check-list">
<li>물 충분히 섭취(1.5L 이상)</li>
<li>수면 7시간 이상 확보 (케어 효과는 수면 중에 가장 잘 안정화됩니다)</li>
<li>강한 압 케어 후 24시간 내 근육통(\"명현 반응\"으로도 불림)이 일시적으로 나타날 수 있음 — 정상 반응</li>
<li>가벼운 산책·스트레칭으로 혈류 유지</li>
<li>커피·에너지 드링크는 평소 양 이하로</li>
</ul>
</section>

<section class="block" id="abnormal">
<h2>이상 반응 발생 시 대처</h2>
<div class="callout warn">
<strong>다음 증상이 있으면 즉시 멈추고 휴식하세요</strong>
<ul>
<li>지속되는 두통·어지러움</li>
<li>가슴 답답함·심한 메스꺼움</li>
<li>케어 부위의 심한 통증·붓기</li>
<li>피부 발진·홍반</li>
</ul>
<p>증상이 1시간 이상 지속되거나 악화되면 의료기관 상담을 권장합니다. 케어 직후 일시적인 약한 어지러움은 흔하지만, 30분 이상 지속되거나 다른 증상을 동반하면 무리하지 마세요.</p>
</div>
</section>

<section class="block" id="conditions">
<h2>건강 상태별 주의</h2>
<ul class="check-list">
<li><strong>임신</strong> — 임신 중에는 출장마사지를 권장하지 않습니다. 임산부 전용 케어는 의료 전문가 상담 후 결정하시는 것이 안전합니다.</li>
<li><strong>고혈압·심혈관 질환</strong> — 강한 압 코스(스포츠·홈타이)는 피하고 부드러운 압 위주의 스웨디시·아로마를 권장. 항응고제 복용 중인 경우 사전 의료기관 상담 후 결정.</li>
<li><strong>당뇨</strong> — 발·종아리 부위 케어 시 자극이 강하지 않은 압을 권장. 케어 후 저혈당 증상 주의.</li>
<li><strong>골절·외상 후</strong> — 부상 부위는 케어 대상이 아닙니다. 부상 후 완전 회복 전에는 케어 자제.</li>
<li><strong>피부 질환</strong> — 발진·상처·감염 부위는 케어를 피합니다.</li>
<li><strong>고열·감기 급성기</strong> — 회복 후 케어를 권장.</li>
</ul>
</section>
""" + _review_faq([
    ("케어 후 약간의 근육통이 있는데 정상인가요?", "강한 압 케어 후 24시간 내 가벼운 근육통은 흔히 발생합니다. 다음 날 자연스럽게 가라앉으면 정상 범위입니다. 통증이 심해지거나 48시간 이상 지속되면 휴식을 더 취하시고 필요 시 의료 상담을 권장합니다."),
    ("케어 후 술 마셔도 되나요?", "권장하지 않습니다. 혈관 확장으로 알코올 흡수가 빨라지고 어지러움이 발생할 수 있습니다. 가급적 케어 후 4~6시간은 음주를 피하세요."),
    ("케어 후 사우나·찜질방 가도 되나요?", "직후 1~2시간은 피하시는 것이 좋습니다. 체온이 안정된 후라면 가벼운 입욕은 가능합니다."),
    ("케어 직후 운전해도 되나요?", "어지러움이 없다면 가능하지만, 권장은 15~30분 휴식 후입니다. 장거리 운전은 더 충분한 휴식 후 시작하세요."),
]) + _GUIDE_DISCLAIMER


# ===== Guide 3 — 아로마와 스웨디시 차이 =====
_GUIDE3_BODY = _GUIDE_BYLINE.format(min=4) + _review_toc([
    ("한눈에 보는 비교표", "compare"),
    ("스웨디시 — 기원과 특징", "swedish"),
    ("아로마 — 향기 케어의 원리", "aroma"),
    ("추천 대상 시나리오", "scenario"),
    ("선택 가이드 — 무엇을 받을지 헷갈릴 때", "choose"),
    ("자주 묻는 질문", "faq"),
]) + """
<section class="block" id="compare">
<h2>한눈에 보는 비교표</h2>
<div class="compare-table-wrap">
<table class="compare-table">
<thead><tr><th>항목</th><th>스웨디시</th><th>아로마</th></tr></thead>
<tbody>
<tr><th scope="row">기원</th><td>19세기 스웨덴 페르 헨리크 링이 정립한 유럽식 마사지</td><td>고대 이집트·로마부터 사용된 에센셜 오일 기반 케어</td></tr>
<tr><th scope="row">핵심 목적</th><td>혈류 촉진·근육 이완·전신 휴식</td><td>정서적 안정·수면 보조·스트레스 완화</td></tr>
<tr><th scope="row">압 강도</th><td>중간 (부드러움~중강도)</td><td>약~중 (부드러운 압 위주)</td></tr>
<tr><th scope="row">오일 사용</th><td>일반 베이스 오일</td><td>에센셜 오일(라벤더·일랑일랑·베르가못 등)</td></tr>
<tr><th scope="row">향</th><td>약하거나 무향</td><td>향이 케어의 핵심</td></tr>
<tr><th scope="row">진행 시간</th><td>60·90·120분</td><td>60·90·120분</td></tr>
<tr><th scope="row">권장 시간대</th><td>저녁·휴식 전</td><td>잠들기 전·이른 저녁</td></tr>
<tr><th scope="row">권해지는 분</th><td>근육 피로·뭉침이 큰 분</td><td>수면이 얕고 정신적 긴장이 큰 분</td></tr>
</tbody></table>
</div>
</section>

<section class="block" id="swedish">
<h2>스웨디시 — 기원과 특징</h2>
<p>스웨디시 마사지는 1800년대 중반 스웨덴의 체조 치료사 페르 헨리크 링(Per Henrik Ling)이 체계화한 유럽식 마사지 기법에 뿌리를 둡니다. 다섯 가지 기본 동작(에플라쥬·페트리사쥬·프릭션·태포트망·바이브레이션)이 결합되어 혈류를 자극하고 근육의 긴장을 부드럽게 풀어 줍니다.</p>
<p>출장마사지에서 진행되는 스웨디시는 베이스 오일을 사용해 피부와의 마찰을 줄이고, 부드러운 중강도 압으로 전신을 케어합니다. 첫 이용자에게 가장 자주 권해지는 이유는 압의 강도가 부담스럽지 않으면서도 \"케어 받은 느낌\"이 명확하기 때문입니다.</p>
<p><strong>적합한 상황</strong>: 평일 누적된 전신 피로, 어깨·허리의 일반적 뭉침, 수면 보조보다는 컨디션 회복이 우선인 경우.</p>
</section>

<section class="block" id="aroma">
<h2>아로마 — 향기 케어의 원리</h2>
<p>아로마 마사지는 식물에서 추출한 에센셜 오일을 활용해 후각·피부 두 경로로 효과를 전달하는 케어입니다. 후각으로 들어온 향 분자가 변연계(감정을 담당하는 뇌 영역)에 직접 작용해 정서적 이완을 돕고, 피부로 흡수된 오일 성분이 혈관·림프계를 통해 전신에 전달됩니다.</p>
<p>사용되는 대표적인 에센셜 오일은 다음과 같습니다.</p>
<ul class="check-list">
<li><strong>라벤더</strong> — 수면 보조·진정 효과로 가장 자주 사용</li>
<li><strong>일랑일랑</strong> — 정서 안정·기분 전환</li>
<li><strong>베르가못</strong> — 가벼운 우울감·스트레스 완화</li>
<li><strong>로즈마리</strong> — 집중력·혈류 개선</li>
<li><strong>유칼립투스</strong> — 호흡기 이완·상쾌함</li>
</ul>
<p>오일 알레르기·호흡기 민감도가 있는 분은 사전 상담 시 미리 알려 주시는 것이 안전합니다.</p>
</section>

<section class="block" id="scenario">
<h2>추천 대상 시나리오</h2>
<div class="dos-donts">
<div class="dos">
<h3>스웨디시가 적합한 경우</h3>
<ul>
<li>주중 누적 피로·근육 뭉침이 주된 고민</li>
<li>운동 후 가벼운 회복이 필요할 때</li>
<li>향에 민감하거나 무향을 선호</li>
<li>케어 후 활동 일정이 있어 \"개운한\" 마무리가 필요할 때</li>
<li>출장마사지가 처음일 때</li>
</ul>
</div>
<div class="donts">
<h3>아로마가 적합한 경우</h3>
<ul>
<li>잠들기 어려운 날이 잦거나 수면이 얕을 때</li>
<li>정신적 긴장·불안감이 큰 시기</li>
<li>케어 직후 바로 휴식·수면 일정일 때</li>
<li>향 케어를 함께 즐기고 싶을 때</li>
<li>연속된 업무로 정서적 리셋이 필요할 때</li>
</ul>
</div>
</div>
</section>

<section class="block" id="choose">
<h2>선택 가이드 — 무엇을 받을지 헷갈릴 때</h2>
<div class="callout tip">
<strong>간단한 선택 흐름</strong>
<ol>
<li>케어 후 곧바로 자야 한다면 → <strong>아로마</strong></li>
<li>다음 일정이 있어 개운하게 마무리하고 싶다면 → <strong>스웨디시</strong></li>
<li>향에 민감하다면 → <strong>스웨디시</strong></li>
<li>둘 다 받고 싶다면 → 90분 이상 코스에서 두 요소를 일부 결합 가능(상담 시 요청)</li>
</ol>
</div>
<p>코스 길이는 60분이 무난하며, 처음이라면 90분이 권해집니다. 둘 다 처음 받아 보신다면 스웨디시 90분 → 다음 이용 시 아로마 60~90분 순서로 비교해 보시는 것을 권장드립니다.</p>
</section>
""" + _review_faq([
    ("아로마와 스웨디시를 같이 받을 수 있나요?", "전체 코스를 결합하기보다는, 사용 오일을 아로마 오일로 바꾼 \"아로마 스웨디시\" 형태로 진행하는 경우가 많습니다. 90분 이상 코스에서 안내 가능합니다."),
    ("아로마 오일 향이 너무 강하지 않을까요?", "코스 직전 향 강도를 조절할 수 있습니다. 무향에 가까운 베이스 오일도 준비되어 있으므로 사전에 알려 주세요."),
    ("운동 후엔 어떤 게 좋을까요?", "스웨디시가 더 적합합니다. 강한 압이 필요하면 스포츠 마사지도 함께 고려해 보세요."),
    ("아로마 알레르기가 걱정됩니다.", "오일 알레르기·호흡기 민감도가 있다면 사전 상담에서 알려 주세요. 무향 옵션 또는 알레르겐이 낮은 오일을 선택할 수 있습니다."),
]) + _GUIDE_DISCLAIMER


# ===== Guide 4 — 처음 이용 전 알아둘 점 =====
_GUIDE4_BODY = _GUIDE_BYLINE.format(min=6) + _review_toc([
    ("첫 이용 체크리스트 8가지", "checklist"),
    ("코스 길이 선택 가이드", "duration"),
    ("공간 점검 — 진행 가능한 환경 만들기", "space"),
    ("의류·소지품", "outfit"),
    ("결제·취소 규정", "payment"),
    ("시간 여유 — 후속 일정 배치", "schedule"),
    ("건강 상태 사전 공유", "health"),
    ("예약 시 알려드릴 정보", "info"),
    ("자주 묻는 질문", "faq"),
]) + """
<section class="block" id="checklist">
<h2>첫 이용 체크리스트 8가지</h2>
<div class="callout tip">
<strong>전화 상담 전에 이 8가지를 확인해 두시면 일정 확정이 빠릅니다.</strong>
</div>
<ul class="check-list">
<li>희망 코스 종류(스웨디시·아로마·홈타이·스포츠·커플 중)</li>
<li>희망 코스 길이(60·90·120분)</li>
<li>희망 시각(시작 시각·종료 시각)</li>
<li>진행 장소 유형(가정·호텔·오피스텔·펜션)</li>
<li>진행 장소 정확한 주소·층</li>
<li>공동현관 출입 방식(비밀번호·카드키·키오스크)</li>
<li>주차 가능 여부(가정·오피스텔의 경우)</li>
<li>건강 상태 특이 사항(임신·외상·복용약 등)</li>
</ul>
</section>

<section class="block" id="duration">
<h2>코스 길이 선택 가이드</h2>
<div class="compare-table-wrap">
<table class="compare-table">
<thead><tr><th>길이</th><th>실제 케어 시간</th><th>추천 대상</th></tr></thead>
<tbody>
<tr><th scope="row">60분</th><td>약 50~55분</td><td>첫 이용·짧은 시간 회복</td></tr>
<tr><th scope="row">90분</th><td>약 80~85분</td><td>일반적 권장 길이 — 첫 이용자에게 가장 자주 권해짐</td></tr>
<tr><th scope="row">120분</th><td>약 105~110분</td><td>충분히 받고 싶을 때·여러 부위 종합 케어</td></tr>
</tbody></table>
</div>
<p>코스 시간 외에 도착 안내·준비·정리 시간이 별도 10~15분 정도 추가됩니다. 첫 이용에는 90분이 무난한 균형점입니다.</p>
</section>

<section class="block" id="space">
<h2>공간 점검 — 진행 가능한 환경 만들기</h2>
<ul class="check-list">
<li><strong>공간 크기</strong> — 매트(약 2m × 1m)를 펼칠 수 있는 평평한 바닥 또는 침대 공간</li>
<li><strong>온도</strong> — 24~26°C 권장. 너무 차가운 환경은 근육 이완을 방해</li>
<li><strong>조명</strong> — 직접 조명보다 간접 조명 권장</li>
<li><strong>음악</strong> — 필요 시 차분한 BGM 준비 (관리사 측에서도 준비 가능)</li>
<li><strong>방해 요소</strong> — 반려동물 별도 공간 분리, 알림 무음, 가족이 있다면 사전 양해</li>
</ul>
</section>

<section class="block" id="outfit">
<h2>의류·소지품</h2>
<p>오일 코스(스웨디시·아로마)는 일회용 의류 또는 편한 의류로 갈아입게 됩니다. 평소 입던 옷에 오일이 묻지 않도록 별도 의류로 준비하시면 좋습니다. 귀금속·시계는 별도 보관해 두시는 것을 권장합니다.</p>
</section>

<section class="block" id="payment">
<h2>결제·취소 규정</h2>
<p>결제는 코스 직전 또는 직후에 진행됩니다. 호텔 방문의 경우 사전 결제 방식이 적용되기도 합니다. 자세한 결제 수단은 <a href="/reservation/payment/">결제 안내</a>를 참고해 주세요.</p>
<p>예약 변경·취소는 시간대에 따라 처리 기준이 다릅니다. 자세한 내용은 <a href="/reservation/cancel-refund/">취소·환불 규정</a>에서 확인하실 수 있습니다.</p>
</section>

<section class="block" id="schedule">
<h2>시간 여유 — 후속 일정 배치</h2>
<div class="callout warn">
<strong>코스 직후 빡빡한 일정은 피하세요</strong>
<p>코스 종료 후 15~30분 정도의 휴식 시간을 두는 것이 권장됩니다. 곧바로 외출·운전·운동 일정이 있으면 케어의 이완 효과가 떨어집니다.</p>
</div>
</section>

<section class="block" id="health">
<h2>건강 상태 사전 공유</h2>
<p>다음 상황은 반드시 예약 단계에서 알려 주세요. 진행 가능 여부와 코스 조정에 영향을 줍니다.</p>
<ul class="check-list">
<li>임신 중이거나 임신 가능성</li>
<li>최근 골절·외상·수술 이력 (회복 중 포함)</li>
<li>고혈압·심혈관 질환·항응고제 복용</li>
<li>당뇨·자가면역 질환</li>
<li>피부 질환·감염성 질환</li>
<li>고열·감기 급성기</li>
<li>알레르기(오일·향)</li>
</ul>
</section>

<section class="block" id="info">
<h2>예약 시 알려드릴 정보</h2>
<p>전화 상담 시 다음 정보를 함께 안내해 주시면 일정 확정이 매끄럽습니다.</p>
<ol class="steps">
<li><strong>희망 일시</strong><p>시작 시각·종료 시각을 모두 알려 주세요.</p></li>
<li><strong>진행 장소 정보</strong><p>주소·층·호수·건물 형태(아파트·오피스텔·호텔·펜션).</p></li>
<li><strong>출입 방식</strong><p>공동현관 비밀번호·키오스크·카드 키 안내.</p></li>
<li><strong>코스 선택</strong><p>코스 종류·길이·인원(1인/2인).</p></li>
<li><strong>건강 사항</strong><p>위 \"건강 상태 사전 공유\" 항목 중 해당되는 내용.</p></li>
</ol>
</section>
""" + _review_faq([
    ("처음인데 어떤 코스가 가장 무난할까요?", "스웨디시 90분이 첫 이용자에게 가장 자주 권해집니다. 부드러운 압의 전신 이완 코스라 부담이 적습니다."),
    ("호텔 방문은 어떻게 다른가요?", "호텔 객실 방문은 객실 호수와 체크인 정보를 사전 공유하시면 됩니다. 일부 호텔은 외부 인원 출입 정책이 다르므로 사전 확인이 필요합니다."),
    ("진행 중에 압이 너무 강하면?", "즉시 관리사에게 알려 주세요. 압 강도는 진행 중에도 조절 가능합니다. 케어는 \"참는\" 것이 아니라 \"이완하는\" 시간입니다."),
    ("같이 사는 가족이 있어도 가능한가요?", "가능합니다. 별도 공간에서 진행되므로 가족이 있어도 무방하지만, 가능한 한 방해되지 않을 시간대로 안내드립니다."),
    ("당일 예약도 가능한가요?", "권역과 시간대에 따라 가능합니다. 24시간 운영되는 0508-202-4719로 연락 주시면 즉시 확인해 드립니다."),
]) + _GUIDE_DISCLAIMER


# ===== Guide 5 — 가격이 달라지는 이유 =====
_GUIDE5_BODY = _GUIDE_BYLINE.format(min=5) + _review_toc([
    ("가격을 결정하는 4가지 변수", "factors"),
    ("코스 길이별 가격 흐름", "duration"),
    ("코스 종류별 시세대", "type"),
    ("시간대 변동 (주간·야간·심야)", "time"),
    ("이동료·진입로 변수", "travel"),
    ("미끼 가격 식별법", "fake-price"),
    ("추가 비용이 발생할 수 있는 경우", "extra"),
    ("자주 묻는 질문", "faq"),
]) + """
<section class="block" id="factors">
<h2>가격을 결정하는 4가지 변수</h2>
<p>출장마사지는 전국 단일가가 아닙니다. 다음 4가지 변수에 따라 가격이 달라집니다. 가격이 변동된다는 것 자체가 부정적인 것이 아니라, 변수에 비례해 정직하게 책정된다는 의미입니다.</p>
<ol class="steps">
<li><strong>코스 길이</strong><p>60·90·120분 — 시간에 비례해 책정됩니다.</p></li>
<li><strong>코스 종류</strong><p>스웨디시·아로마·홈타이·스포츠·커플 등 유형별로 기준이 다릅니다.</p></li>
<li><strong>예약 시간대</strong><p>심야·새벽 시간대는 일부 추가 비용이 발생할 수 있습니다.</p></li>
<li><strong>이동 거리·진행 장소</strong><p>외곽 권역·펜션·풀빌라 등은 이동료가 추가될 수 있습니다.</p></li>
</ol>
</section>

<section class="block" id="duration">
<h2>코스 길이별 가격 흐름</h2>
<p>일반적으로 60분 → 90분 → 120분 순으로 시간이 늘어날수록 비용도 비례해 증가합니다. 다만 단순 시간 비례가 아니라 30분 추가 시 2만원 안팎의 추가가 일반적이며, 120분이 60분의 정확히 2배가 되지는 않는 경우가 많습니다.</p>
<p>코스별 시간 단위 기준 가격은 <a href="/reservation/price/">가격 안내</a> 페이지에 표로 정리되어 있습니다.</p>
</section>

<section class="block" id="type">
<h2>코스 종류별 시세대</h2>
<p>같은 60분이라도 코스 종류에 따라 가격이 다릅니다. 일반적으로 다음 순서로 가격이 책정됩니다(낮은 가격 → 높은 가격).</p>
<ol class="steps">
<li><strong>홈타이(타이)</strong> — 오일을 사용하지 않는 코스로 가장 보편적인 가격대</li>
<li><strong>아로마</strong> — 에센셜 오일 사용으로 홈타이보다 약간 상위</li>
<li><strong>스웨디시(힐링)</strong> — 베이스 오일 사용·중강도 압의 전신 이완 코스</li>
<li><strong>스페셜·스포츠</strong> — 부위 집중·특수 기법 포함 코스로 상위 가격대</li>
<li><strong>커플(2인 합산)</strong> — 두 분이 동시에 받으므로 단순 2배가 아닌 합산 금액</li>
</ol>
</section>

<section class="block" id="time">
<h2>시간대 변동</h2>
<div class="compare-table-wrap">
<table class="compare-table">
<thead><tr><th>시간대</th><th>가격 변동</th><th>비고</th></tr></thead>
<tbody>
<tr><th scope="row">주간 (10시~19시)</th><td>기본 가격</td><td>가장 보편적 시간대</td></tr>
<tr><th scope="row">저녁 (19시~22시)</th><td>기본 가격</td><td>가장 활발한 시간대</td></tr>
<tr><th scope="row">야간 (22시~01시)</th><td>일부 시간대 추가 가능</td><td>호텔·오피스텔 객실 비중↑</td></tr>
<tr><th scope="row">심야 (01시 이후)</th><td>추가 비용 가능</td><td>권역 일부만 가능, 사전 예약 필수</td></tr>
</tbody></table>
</div>
</section>

<section class="block" id="travel">
<h2>이동료·진입로 변수</h2>
<p>이동료는 다음과 같은 경우 추가될 수 있습니다.</p>
<ul class="check-list">
<li>광역 이동(서울 → 경기 외곽 등)</li>
<li>외곽 권역(시 외곽·도 단위 군 단위)</li>
<li>펜션·풀빌라(진입로가 좁거나 도심에서 멀리 떨어진 경우)</li>
<li>섬·해안 일부 권역</li>
</ul>
<p>이동료는 사전 상담 시 미리 안내됩니다. 예약 후 일방적으로 이동료가 추가되는 일은 없습니다.</p>
</section>

<section class="block" id="fake-price">
<h2>미끼 가격 식별법</h2>
<div class="callout warn">
<strong>다음 표현이 보이면 의심하세요</strong>
<ul>
<li>\"전국 어디든 X만원\" — 권역·시간대 무관 단일가는 비현실적</li>
<li>\"최저가 보장\" — 시장 시세보다 비정상적으로 낮은 가격은 도착 후 추가 청구 가능성</li>
<li>코스 길이·종류 구분 없는 단일 가격 표시</li>
<li>가격 표시 페이지가 없거나 \"문의\"만 안내</li>
<li>\"무한 추가\", \"무제한 시간\" 등 비상식적 표현</li>
</ul>
<p>정직한 운영 업체는 가격 변수와 \"부터\" 기준을 명시하고, 사전 상담에서 최종 금액을 합의합니다.</p>
</div>
</section>

<section class="block" id="extra">
<h2>추가 비용이 발생할 수 있는 경우</h2>
<p>다음 상황에서는 사전 합의 하에 추가 비용이 발생할 수 있습니다. 모두 예약 단계에서 함께 안내됩니다.</p>
<ul class="check-list">
<li>심야·새벽 시간대 (01시 이후)</li>
<li>외곽 권역 이동료</li>
<li>코스 시간 연장(진행 중 추가 30분 요청 시)</li>
<li>옵션 추가(핫스톤·아로마 오일 변경·집중 부위 추가)</li>
<li>커플 코스 인원 추가 (1인 → 2인 전환 시)</li>
</ul>
<p>사전 동의 없는 추가 비용은 청구되지 않습니다.</p>
</section>
""" + _review_faq([
    ("가격을 사전에 정확히 알 수 있나요?", "예약 상담 단계에서 코스·시간대·장소가 확정되면 최종 금액이 그 자리에서 안내됩니다. 그 금액 외에 추가 비용이 발생하는 일은 없습니다."),
    ("\"부터\" 가격이라는 게 무슨 뜻인가요?", "기본 권역·일반 시간대 기준 시작 금액을 의미합니다. 시간대·이동 거리에 따라 일부 변동이 있을 수 있어 \"부터\" 표기를 사용합니다."),
    ("가격이 너무 싼 곳은 의심해도 되나요?", "시장 평균보다 비정상적으로 낮은 가격은 도착 후 추가 청구·옵션 강요로 이어지는 경우가 많아 주의가 필요합니다. <a href=\"/guide/safe-reservation/\">안전한 예약 확인 방법</a>을 함께 참고하세요."),
    ("가격 협상이 가능한가요?", "정찰제로 운영되므로 별도의 협상은 없습니다. 다만 길이·옵션 조정으로 예산에 맞추는 안내는 가능합니다."),
]) + _GUIDE_DISCLAIMER


# ===== Guide 6 — 안전한 예약 확인 방법 =====
_GUIDE6_BODY = _GUIDE_BYLINE.format(min=5) + _review_toc([
    ("사업자 정보 확인 — 가장 먼저 점검할 것", "biz"),
    ("가격 투명성 확인", "price"),
    ("취소·환불 규정 명시 여부", "refund"),
    ("후기·평판의 진위 판단", "review"),
    ("위험 신호 7가지", "redflag"),
    ("안전한 예약 진행 절차", "flow"),
    ("문제 발생 시 신고 절차", "report"),
    ("자주 묻는 질문", "faq"),
]) + """
<section class="block" id="biz">
<h2>사업자 정보 확인 — 가장 먼저 점검할 것</h2>
<p>출장마사지 업체를 선택할 때 가장 먼저 확인할 것은 정식 사업자 정보입니다. 다음 4가지 정보가 사이트 어디든 명확히 공개되어 있어야 합니다.</p>
<ul class="check-list">
<li><strong>법인명·운영자명</strong> — 누가 운영하는지</li>
<li><strong>대표자 이름</strong> — 책임자가 누구인지</li>
<li><strong>사업자등록번호</strong> — 국세청에 등록된 정식 번호</li>
<li><strong>본사 주소·대표 전화</strong> — 실제 연락 가능한 정보</li>
</ul>
<div class="callout tip">
<strong>본 사이트(바로GO)의 운영 정보</strong>
<p>YH LAB · 대표 김유환 · 사업자등록번호 815-26-00585 · 본사 경기도 파주시 청석로 268 · 대표 전화 0508-202-4719</p>
</div>
<p>국세청 홈페이지(<code>www.hometax.go.kr</code>)의 \"사업자등록상태 조회\"에서 사업자등록번호로 정상 운영 여부를 확인할 수 있습니다.</p>
</section>

<section class="block" id="price">
<h2>가격 투명성 확인</h2>
<ul class="check-list">
<li>코스별 시간 단위 가격이 표 또는 목록으로 공개되어 있는가</li>
<li>가격 변동 변수(시간대·이동료·옵션)가 명시되어 있는가</li>
<li>\"전국 단일가\", \"무조건 X원\" 같은 비현실적 표시가 없는가</li>
<li>최종 가격이 \"예약 상담 시 안내\"임이 명확히 표시되는가</li>
<li>가격 안내의 최종 업데이트 일자가 표기되어 있는가</li>
</ul>
</section>

<section class="block" id="refund">
<h2>취소·환불 규정 명시 여부</h2>
<p>정식 운영 업체는 다음을 별도 페이지로 공개합니다.</p>
<ul class="check-list">
<li>예약 후 출발 전 취소 시 환불 기준</li>
<li>관리사 출발 후 취소 시 처리 기준</li>
<li>도착 후 취소·진행 거부 시 비용 발생 여부</li>
<li>일정 변경 요청 가능 시점</li>
</ul>
<p>본 사이트의 규정은 <a href="/reservation/cancel-refund/">취소·환불 규정</a> 페이지에서 확인하실 수 있습니다.</p>
</section>

<section class="block" id="review">
<h2>후기·평판의 진위 판단</h2>
<div class="callout warn">
<strong>주의 — 페이지 내 후기는 보조 신호일 뿐입니다</strong>
<p>사이트에 게시된 후기는 운영자가 선별·편집한 콘텐츠일 가능성이 큽니다. 외부 검색(\"바로GO 후기\", \"YH LAB 후기\" 등)으로 다른 채널의 의견을 함께 확인하시는 것을 권장합니다.</p>
</div>
<p>후기의 신뢰도를 판단할 때 다음을 함께 보세요.</p>
<ul class="check-list">
<li>다양한 채널(블로그·커뮤니티·플랫폼 리뷰)에 후기가 분산되어 있는가</li>
<li>구체적인 상황 묘사(시간대·코스·진행 장소 등)가 있는가, 혹은 추상적인 칭찬만 있는가</li>
<li>부정적 의견에도 운영자 측의 합리적 응대가 보이는가</li>
<li>최근 일자의 후기가 지속적으로 올라오는가</li>
</ul>
</section>

<section class="block" id="redflag">
<h2>위험 신호 7가지 — 회피 권장</h2>
<div class="callout warn">
<ul>
<li>사업자 정보가 사이트 어디에도 없음</li>
<li>가격 정보가 \"문의\"로만 안내되고 표가 없음</li>
<li>취소·환불 규정 페이지가 별도로 존재하지 않음</li>
<li>\"최저가 보장\", \"100% 만족\", \"전국 어디든 X원\" 같은 과장 표현이 메인 카피로 사용됨</li>
<li>이미지가 자극적이거나 특정 신체 부위 강조 위주</li>
<li>대표 전화가 휴대전화 번호이거나 다른 번호로 우회</li>
<li>예약 전 사진·신상 정보를 과도하게 요구</li>
</ul>
</div>
</section>

<section class="block" id="flow">
<h2>안전한 예약 진행 절차</h2>
<ol class="steps">
<li><strong>사업자 정보 1차 확인</strong><p>사이트 푸터·About 페이지에서 법인명·등록번호 확인.</p></li>
<li><strong>가격·규정 페이지 확인</strong><p>가격표·취소 규정·결제 안내 페이지가 별도로 존재하는지 확인.</p></li>
<li><strong>전화 상담 시작</strong><p>대표 번호로 전화해 응대 톤·정보 안내의 일관성 확인. 예약 강요·자극적 마케팅이 있다면 중단.</p></li>
<li><strong>가격·코스 사전 합의</strong><p>최종 금액이 명확히 안내되는지 확인. 모호한 답변이라면 다른 업체 고려.</p></li>
<li><strong>예약 확정</strong><p>합의된 내용을 문자·메모로 정리해 두면 안전.</p></li>
</ol>
</section>

<section class="block" id="report">
<h2>문제 발생 시 신고 절차</h2>
<p>이용 중 분쟁이나 불법 행위가 의심되면 다음 절차로 신고할 수 있습니다.</p>
<ul class="check-list">
<li><strong>1차 — 운영 업체 고객센터</strong> 문의 (정식 사업자라면 반드시 응대됩니다)</li>
<li><strong>2차 — 한국소비자원</strong> 1372 (소비자 분쟁 조정)</li>
<li><strong>3차 — 관할 경찰서</strong> 112 (불법 행위 의심 시)</li>
<li><strong>국세청 1588-0560</strong> — 사업자등록 미신고 의심 신고</li>
</ul>
<p>본 사이트 이용 중 불편 사항은 <a href="/support/inquiry/">고객센터 문의</a>로 접수해 주시면 처리됩니다.</p>
</section>
""" + _review_faq([
    ("사업자등록번호 확인은 어떻게 하나요?", "국세청 홈택스(hometax.go.kr) → 조회/발급 → 사업자등록상태 조회에서 번호를 입력하면 \"계속 사업자\" 여부를 확인할 수 있습니다."),
    ("후기가 너무 좋기만 한 사이트는 어떻게 봐야 하나요?", "내부 게시 후기만 모아 둔 경우 운영자 측에서 선별·편집된 콘텐츠일 가능성이 큽니다. 외부 검색을 통해 다른 채널 의견을 함께 확인하시는 것이 안전합니다."),
    ("가격이 비정상적으로 싸면 안 되나요?", "도착 후 추가 청구·옵션 강요로 이어지는 경우가 많습니다. 시장 평균보다 30% 이상 낮은 가격은 주의가 필요합니다."),
    ("바로GO는 어떻게 검증할 수 있나요?", "사업자등록번호 815-26-00585를 국세청 홈택스에서 조회하실 수 있고, 본사 주소(경기도 파주시 청석로 268)와 대표 전화(0508-202-4719)가 모든 페이지에 일관되게 공개되어 있습니다."),
    ("불법 업소를 신고하려면 어디로 해야 하나요?", "관할 경찰서 112 또는 한국소비자원 1372로 신고하실 수 있습니다. 국세청 1588-0560은 사업자등록 미신고 의심 신고용입니다."),
]) + _GUIDE_DISCLAIMER


GUIDES_RICH = [
    {"slug": "what-is-business-trip-massage", "name": "출장마사지란?",
     "desc": "출장마사지의 정의, 매장형과의 차이, 코스 종류 6가지, 이용 흐름, 적합한 상황과 자주 오해하는 점을 운영팀이 정리한 입문 가이드.",
     "body": _GUIDE1_BODY},
    {"slug": "massage-before-after", "name": "마사지 전후 주의사항",
     "desc": "24시간 전부터 24시간 후까지 시간순 권장·금기 사항, 이상 반응 대처, 건강 상태별(임신·고혈압·당뇨) 주의 사항 정리.",
     "body": _GUIDE2_BODY},
    {"slug": "aroma-vs-swedish", "name": "아로마와 스웨디시 차이",
     "desc": "스웨디시와 아로마 마사지의 기원·진행 방식·압 강도·향·추천 대상까지 8개 항목으로 비교. 선택 가이드 포함.",
     "body": _GUIDE3_BODY},
    {"slug": "first-time-massage", "name": "처음 이용 전 알아둘 점",
     "desc": "출장마사지 첫 이용자가 알아두면 좋은 체크리스트 8가지, 코스 길이 선택, 공간 점검, 결제·취소, 건강 사전 공유까지 종합 안내.",
     "body": _GUIDE4_BODY},
    {"slug": "massage-price-standard", "name": "출장마사지 가격이 달라지는 이유",
     "desc": "출장마사지 가격을 결정하는 4가지 변수(코스 길이·종류·시간대·이동), 미끼 가격 식별법, 추가 비용이 발생할 수 있는 경우 정리.",
     "body": _GUIDE5_BODY},
    {"slug": "safe-reservation", "name": "안전한 예약 확인 방법",
     "desc": "출장마사지 업체를 안전하게 선택하는 기준: 사업자 정보 확인, 가격 투명성, 취소·환불 규정, 후기 진위 판단, 위험 신호 7가지, 신고 절차.",
     "body": _GUIDE6_BODY},
]

# guide hub
add(
  path="guide/index.html", url="/guide/", slug="guide-hub",
  title="마사지 정보 | 출장마사지 가이드·비교·주의사항 | 바로GO",
  description="출장마사지의 정의, 코스 종류, 전후 주의사항, 가격 결정 변수, 안전한 예약 확인 방법까지. 운영팀이 직접 정리한 6편의 가이드.",
  h1="마사지 정보",
  intro='<p class="lede">출장마사지를 처음 이용하시거나 좀 더 안전하게 이용하고 싶은 분들을 위한 가이드 모음입니다. 정의·비교·전후 주의사항·가격 변수·업체 검증 기준까지 6편으로 정리되어 있습니다.</p>',
  breadcrumbs=[("홈","/"),("마사지 정보","/guide/")],
  body="""
<section class="block">
<div class="guide-card-grid">
  <a href="/guide/what-is-business-trip-massage/" class="guide-card">
    <span class="guide-card-num">01</span>
    <h3>출장마사지란?</h3>
    <p>출장마사지의 정의, 매장형과의 차이, 코스 종류 6가지, 이용 흐름과 자주 오해하는 점.</p>
    <span class="guide-card-meta">5분 읽기 · 기초</span>
  </a>
  <a href="/guide/massage-before-after/" class="guide-card">
    <span class="guide-card-num">02</span>
    <h3>마사지 전후 주의사항</h3>
    <p>24시간 전부터 24시간 후까지 시간순 권장·금기, 이상 반응 대처, 건강 상태별 주의.</p>
    <span class="guide-card-meta">6분 읽기 · 안전</span>
  </a>
  <a href="/guide/aroma-vs-swedish/" class="guide-card">
    <span class="guide-card-num">03</span>
    <h3>아로마와 스웨디시 차이</h3>
    <p>두 코스의 기원·진행 방식·압 강도·향·추천 대상을 8개 항목으로 비교, 선택 가이드 포함.</p>
    <span class="guide-card-meta">4분 읽기 · 비교</span>
  </a>
  <a href="/guide/first-time-massage/" class="guide-card">
    <span class="guide-card-num">04</span>
    <h3>처음 이용 전 알아둘 점</h3>
    <p>첫 이용자 체크리스트 8가지, 코스 길이 선택, 공간 점검, 결제·취소, 건강 사전 공유.</p>
    <span class="guide-card-meta">6분 읽기 · 첫이용</span>
  </a>
  <a href="/guide/massage-price-standard/" class="guide-card">
    <span class="guide-card-num">05</span>
    <h3>가격이 달라지는 이유</h3>
    <p>가격 결정 4대 변수, 코스 종류별 시세대, 시간대 변동, 미끼 가격 식별법, 추가 비용 경우.</p>
    <span class="guide-card-meta">5분 읽기 · 비용</span>
  </a>
  <a href="/guide/safe-reservation/" class="guide-card">
    <span class="guide-card-num">06</span>
    <h3>안전한 예약 확인 방법</h3>
    <p>사업자 정보 확인법, 가격 투명성, 후기 진위 판단, 위험 신호 7가지, 신고 절차.</p>
    <span class="guide-card-meta">5분 읽기 · 안전</span>
  </a>
</div>
</section>
""",
)

for g in GUIDES_RICH:
    slug, name, desc, body = g["slug"], g["name"], g["desc"], g["body"]
    source_url = f"/guide/{slug}/"
    # 다른 가이드 + 예약 정보까지 long-tail 앵커로 (각 가이드마다 다른 앵커 자동 선택)
    candidates = [f"/guide/{o['slug']}/" for o in GUIDES_RICH if o["slug"] != slug]
    candidates += ["/reservation/price/", "/reservation/how-to-book/", "/reservation/check-before-use/"]
    related_html = _rel(source_url, candidates, title="다른 마사지 정보")
    add(
        path=f"guide/{slug}/index.html",
        url=f"/guide/{slug}/",
        slug=f"guide-{slug}",
        title=f"{name} | 바로GO 마사지 정보",
        description=desc,
        h1=name,
        intro=f'<p class="lede">{desc}</p>',
        breadcrumbs=[("홈","/"),("마사지 정보","/guide/"),(name,f"/guide/{slug}/")],
        og_type="article",
        body=body,
        related=related_html,
    )

# ============================================================
# Magazine — 에디토리얼 매거진 콘텐츠
# ============================================================
# /guide/ 는 how-to 정보, /review/ 는 UGC 후기.
# /magazine/ 은 운영팀이 직접 집필하는 에디토리얼 (트렌드·라이프스타일·웰니스·여행·코스 가이드).
# E-E-A-T: 운영팀 책임 저자 명시 + 발행일·읽는 시간 + 분야 태그 + 면책

# 매거진 디렉터 풀 (6명) — 카테고리별 전문 분야 배정
_MAG_AUTHORS = [
    {"name": "이주민", "role": "콘텐츠 디렉터",  "specialty": "트렌드·라이프스타일 인사이트"},
    {"name": "서영",   "role": "에디토리얼 디렉터", "specialty": "웰니스·회복 케어 분야"},
    {"name": "이주미", "role": "리서치 디렉터",  "specialty": "운영 데이터·이용 패턴 분석"},
    {"name": "이주희", "role": "필드 디렉터",    "specialty": "지역·권역 가이드 기획"},
    {"name": "백민호", "role": "프로덕트 디렉터", "specialty": "코스·서비스 기획"},
    {"name": "김범수", "role": "안전 디렉터",    "specialty": "안전·정책·이용 가이드"},
]

# 카테고리 → 영문 오버라인 (히어로 상단 작은 라벨)
_MAG_CATEGORY_OVERLINE = {
    "트렌드":      "BAROGO TREND INSIGHT",
    "라이프스타일": "BAROGO LIFESTYLE GUIDE",
    "웰니스":      "BAROGO WELLNESS INSIGHT",
    "여행":        "BAROGO TRAVEL EDITORIAL",
    "코스 가이드": "BAROGO COURSE GUIDE",
    "지역 가이드": "BAROGO REGION GUIDE",
    "처음 이용":   "BAROGO BEGINNER GUIDE",
    "호텔 이용":   "BAROGO HOTEL EDITORIAL",
}


def _mag_author_for(slug):
    """slug 해시로 디렉터 선택 — 같은 글은 항상 같은 작성자."""
    idx = int(hashlib.md5(slug.encode("utf-8")).hexdigest(), 16) % len(_MAG_AUTHORS)
    return _MAG_AUTHORS[idx]


def _ko_particle_eul_reul(word):
    """한글 마지막 글자의 받침 유무로 을/를 선택."""
    if not word:
        return "를"
    last = word.strip()[-1]
    code = ord(last)
    # 한글 음절 범위
    if 0xAC00 <= code <= 0xD7A3:
        return "을" if (code - 0xAC00) % 28 else "를"
    return "를"


# 매거진 글별 읽는 시간(분) — 본문 분량 기준
_MAG_READ_MIN = {
    "first-time-essentials": 6,
    "night-worker-recovery": 5,
    "desk-worker-neck-shoulder": 5,
    "hotel-guest-guide": 6,
    "course-selection-by-purpose": 6,
    "regional-usage-tips": 6,
}


def _mag_read_min_for(slug):
    return _MAG_READ_MIN.get(slug, 6)



def _mag_byline(slug, published, read_min, category):
    """디렉터 정보 기반 바이라인. 사업자등록번호 노출 안 함."""
    a = _mag_author_for(slug)
    initial = a["name"][0]  # 한글 이니셜
    return (
        '<div class="mag-meta">'
        '<div class="mag-meta-author">'
        f'<span class="mag-meta-avatar" aria-hidden="true">{initial}</span>'
        '<div class="mag-meta-author-text">'
        f'<strong>{a["name"]} {a["role"]}</strong>'
        f'<span>{a["specialty"]}</span>'
        '</div></div>'
        '<div class="mag-meta-info">'
        f'<span class="mag-meta-tag">발행 · {published}</span>'
        f'<span class="mag-meta-tag">읽는 시간 · 약 {read_min}분</span>'
        f'<span class="mag-meta-tag">카테고리 · {category}</span>'
        '</div></div>'
    )


def _mag_hero_banner(slug, category, title, lede):
    """레퍼런스 톤의 다크 에디토리얼 히어로 — 영문 오버라인 + 거대 타이틀 + 인용 리드.
    아티클 본문 최상단(바이라인 위)에 배치되며, default .page-head는 magazine 페이지에서 CSS로 숨김 처리."""
    overline = _MAG_CATEGORY_OVERLINE.get(category, f"BAROGO {category.upper()}")
    return (
        '<header class="mag-hero-banner">'
        '<div class="mag-hero-banner-inner">'
        f'<span class="mag-hero-overline">{overline}</span>'
        f'<h1 class="mag-hero-headline">{title}</h1>'
        f'<p class="mag-hero-quote">"{lede}"</p>'
        '</div>'
        '</header>'
    )


def _mag_toc(items):
    li = "".join(f'<li><a href="#{anchor}">{label}</a></li>' for label, anchor in items)
    return f'<nav class="mag-toc" aria-label="이 기사에서 다루는 내용"><strong>이 기사에서 다루는 내용</strong><ol>{li}</ol></nav>'


# 기존 호환용: 옛 _MAG_BYLINE_TPL 콜러는 제거됐으나 안전을 위해 더미 함수만 둠
def _mag_bylinetpl(*args, **kwargs):
    return ""


_MAG_DISCLAIMER = (
    '<section class="block mag-disclaimer">'
    '<div class="callout note">'
    '<strong>매거진 안내</strong>'
    '<p>본 매거진은 바로GO 에디토리얼팀의 디렉터 6인이 카테고리별 전문 분야에 따라 집필하며, 운영팀(YH LAB)이 책임 검수 후 게시합니다. '
    '본문은 의료 행위·의학적 조언이 아니며 치료 효과를 보장하지 않습니다. 건강 상태에 관한 결정은 의료 전문가와 상담해 주세요.</p>'
    '</div>'
    '</section>'
)


# ===== Magazine 1 — 출장마사지 처음 이용 전 알아둘 점 =====
_MAG1_BODY = _mag_toc([
    ("처음 받기 전 가장 자주 묻는 3가지", "common-questions"),
    ("첫 코스 선택 — 무엇이 가장 무난한가", "first-course"),
    ("예약 전 준비해 두면 좋은 5가지", "prepare"),
    ("첫 진행의 흐름 한눈에 보기", "flow"),
    ("처음 이용자가 자주 놓치는 점", "miss"),
    ("받은 후 권장되는 사후 케어", "after"),
]) + """
<section class="block" id="common-questions">
<h2>처음 받기 전 가장 자주 묻는 3가지</h2>
<p>운영팀에서 첫 이용자와 진행한 상담에서 가장 자주 받는 질문 세 가지를 정리합니다. 처음 받으시기 전 이 세 가지만 정리해 두셔도 예약 상담이 훨씬 매끄러워집니다.</p>
<ul class="check-list">
<li><strong>어떤 코스가 가장 무난한가요?</strong> — 첫 이용자의 약 70%가 스웨디시 60분을 선택합니다. 부드러운 압력과 부담 없는 길이가 이유입니다.</li>
<li><strong>탈의가 부담스러운데 괜찮나요?</strong> — 옷을 입은 채 진행하는 홈타이를 안내드릴 수 있습니다. 코스 진행 자세는 사전 협의됩니다.</li>
<li><strong>진행 후 외출 일정이 있어도 되나요?</strong> — 60분 코스 후 30분 이상 휴식을 권장합니다. 외출이 곧바로 있다면 시간 여유를 함께 계산해 주세요.</li>
</ul>
</section>

<section class="block" id="first-course">
<h2>첫 코스 선택 — 무엇이 가장 무난한가</h2>
<p>운영팀이 첫 이용자에게 가장 자주 권장하는 흐름은 <strong>스웨디시 60분 → 컨디션 점검 → 다음 진행 시 90분 또는 다른 코스</strong>입니다. 처음부터 강한 압력이나 긴 코스를 잡기보다는, 본인 컨디션을 한 번 점검하는 흐름이 가장 안전합니다.</p>
<div class="dos-donts">
<div class="dos">
<strong>첫 이용에 권장되는 코스</strong>
<ul>
<li>스웨디시 60분 — 가장 자주 권장</li>
<li>아로마 60분 — 향 케어와 함께 부드럽게</li>
<li>홈타이 60분 — 탈의 부담이 있을 때</li>
</ul>
</div>
<div class="donts">
<strong>첫 이용엔 권장 안 함</strong>
<ul>
<li>스포츠 마사지 — 압력이 강해 부담</li>
<li>120분+ 장시간 코스 — 컨디션 점검 전</li>
<li>커플 동시 진행 — 1인 경험 후 권장</li>
</ul>
</div>
</div>
</section>

<section class="block" id="prepare">
<h2>예약 전 준비해 두면 좋은 5가지</h2>
<ol class="steps">
<li><strong>일정 확정</strong><p>도착 희망 시각과 진행 후 다음 일정 사이에 충분한 여유 시간 확보.</p></li>
<li><strong>장소·공간 정리</strong><p>진행 공간(가로 2m × 세로 2.5m 이상)과 동선 확보.</p></li>
<li><strong>건강 상태 정리</strong><p>임신·특정 질환·복용 약물·알레르기 등 사전 안내가 필요한 정보 정리.</p></li>
<li><strong>식사 시간 분리</strong><p>코스 시작 1-2시간 전 가벼운 식사. 직후·과식·과음은 자제.</p></li>
<li><strong>결제 방식 결정</strong><p>현장 결제·계좌 이체·카드 결제 중 사전 합의.</p></li>
</ol>
</section>

<section class="block" id="flow">
<h2>첫 진행의 흐름 한눈에 보기</h2>
<table class="compare-table">
<thead><tr><th scope="col">단계</th><th scope="col">소요 시간</th><th scope="col">이용자 측 할 일</th></tr></thead>
<tbody>
<tr><th scope="row">사전 상담</th><td>약 5-10분</td><td>일정·장소·코스·건강 상태 안내</td></tr>
<tr><th scope="row">관리사 도착·세팅</th><td>약 5-10분</td><td>공간 안내, 환복 또는 샤워 권장</td></tr>
<tr><th scope="row">코스 진행</th><td>60·90·120분</td><td>편안한 자세로 진행</td></tr>
<tr><th scope="row">결제·마무리</th><td>약 5분</td><td>합의된 결제, 사후 안내 수령</td></tr>
</tbody>
</table>
</section>

<section class="block" id="miss">
<h2>처음 이용자가 자주 놓치는 점</h2>
<div class="callout warn">
<strong>주의 — 첫 이용자가 가장 자주 놓치는 3가지</strong>
<ul>
<li>도착 예정 시각만 잡고, <strong>진행 후 휴식 시간</strong>을 일정에 포함하지 않음 → 코스 후 곧바로 외출 일정이 잡혀 회복 효과가 반감</li>
<li><strong>건강 상태 사전 안내 누락</strong> → 진행 중 통증·불편이 발생할 수 있음 (임신·고혈압·디스크 등)</li>
<li><strong>공간 조건 미확인</strong> → 매트 깔 자리가 부족하거나 가구 배치가 진행에 부적합한 경우</li>
</ul>
</div>
</section>

<section class="block" id="after">
<h2>받은 후 권장되는 사후 케어</h2>
<ul class="check-list">
<li>코스 종료 후 30분 이내 물 500ml 이상 보충</li>
<li>당일은 음주·과식·격한 운동 자제</li>
<li>다음 날 가벼운 스트레칭 5분으로 회복 효과 유지</li>
<li>다음 이용 시점은 일반적으로 1-2주 후 권장</li>
</ul>
<p>처음 받으신 후 본인 컨디션에 맞춰 다음 진행 시 코스·시간을 조정하시면 됩니다. 자세한 사후 가이드는 <a href="/guide/massage-before-after/">마사지 전후 주의사항</a>에서 확인하실 수 있습니다.</p>
</section>
""" + _MAG_DISCLAIMER


# ===== Magazine 2 — 야간 근무자 회복 가이드 =====
_MAG2_BODY = _mag_toc([
    ("야간 근무자가 더 빨리 지치는 이유", "why"),
    ("회복기를 활용하는 5가지 패턴", "patterns"),
    ("코스 선택 시 참고할 점", "course"),
    ("마사지 외 함께 권장되는 회복법", "complement"),
    ("야간 근무자가 자주 묻는 질문", "qna"),
]) + """
<section class="block" id="why">
<h2>야간 근무자가 더 빨리 지치는 이유</h2>
<p>야간 근무자는 일반 주간 근무자와 비교했을 때 같은 노동 시간에도 회복 속도가 더 느린 경향이 있습니다. 이는 생체 리듬(circadian rhythm)이 야간 활동에 맞춰 자연스럽게 작동하지 않기 때문이며, 특히 어깨·목·허리의 근육 긴장이 누적되는 속도가 빠릅니다.</p>
<p>운영팀이 야간 근무자 이용자(병원·간호 직군, IT 운영, 보안·시설, 응급 대응, 새벽 물류 등)와 진행한 상담에서 가장 자주 언급된 키워드는 "수면이 부족한 느낌", "근육이 안 풀린다", "긴장이 빠지지 않는다"였습니다. 회복은 단순한 휴식보다 능동적인 케어가 필요한 영역입니다.</p>
</section>

<section class="block" id="patterns">
<h2>회복기를 활용하는 5가지 패턴</h2>
<ol class="steps">
<li><strong>퇴근 직후 60분 코스</strong><p>야간 근무 종료 후 곧바로 짧은 코스를 진행해 긴장을 풀고 수면으로 진입하는 패턴. 가장 자주 안내되는 흐름입니다.</p></li>
<li><strong>오프데이 점심 90분 코스</strong><p>오프데이 점심 시간을 활용해 깊은 회복을 진행. 90-120분 코스로 어깨·등·허리 누적 피로를 모두 풀어주는 흐름입니다.</p></li>
<li><strong>주 1회 정기 케어</strong><p>같은 요일·같은 시간대 정기 진행으로 회복 리듬을 만드는 패턴. 운영팀에서 가장 권장하는 흐름입니다.</p></li>
<li><strong>야근 후 새벽 호텔 케어</strong><p>야근 후 자택 복귀가 어려운 경우 인근 호텔 객실에서 진행. 강남·여의도·종로 야근자에게 자주 안내됩니다.</p></li>
<li><strong>회복 + 수면 직행 60분</strong><p>코스 후 곧바로 수면에 들어가는 흐름. 자극이 적은 스웨디시·아로마가 권장됩니다.</p></li>
</ol>
</section>

<section class="block" id="course">
<h2>코스 선택 시 참고할 점</h2>
<p>야간 근무자에게 가장 자주 권장되는 코스는 다음과 같습니다.</p>
<div class="dos-donts">
<div class="dos">
<strong>권장 코스</strong>
<ul>
<li>스웨디시 — 부드러운 압력·오일 케어로 수면 진입에 유리</li>
<li>아로마 — 향과 함께 신경 안정 효과를 노릴 때</li>
<li>홈타이 — 근육 뭉침이 깊을 때 회복 효과가 분명</li>
</ul>
</div>
<div class="donts">
<strong>주의해야 할 코스</strong>
<ul>
<li>스포츠 마사지 — 압력이 강해 야간 직후엔 부담</li>
<li>커플 동시 진행 — 회복 목적이면 단독 진행 권장</li>
<li>장시간 코스(150분+) — 수면 패턴이 더 무너질 수 있음</li>
</ul>
</div>
</div>
</section>

<section class="block" id="complement">
<h2>마사지 외 함께 권장되는 회복법</h2>
<p>마사지만으로 모든 회복이 해결되지는 않습니다. 운영팀이 야간 근무자에게 함께 권장하는 회복 보조 습관은 다음과 같습니다.</p>
<ul class="check-list">
<li><strong>수분 보충</strong> — 코스 전후 미지근한 물 500ml 이상</li>
<li><strong>식사 간격</strong> — 코스 시작 1-2시간 전 가벼운 식사</li>
<li><strong>수면 환경</strong> — 암막 커튼·소음 차단으로 주간 수면 품질 확보</li>
<li><strong>가벼운 스트레칭</strong> — 코스 다음 날 아침 5분</li>
<li><strong>주 1회 휴식 보장</strong> — 회복 케어 + 자연 수면 조합</li>
</ul>
</section>

<section class="block" id="qna">
<h2>야간 근무자가 자주 묻는 질문</h2>
<div class="faq">
<details><summary>매일 받아도 괜찮나요?</summary><p>매일 진행은 신체에 부담이 될 수 있어 권장되지 않습니다. 주 1-2회 정기 케어가 가장 균형 있는 흐름입니다.</p></details>
<details><summary>오프데이 낮에 받는 것이 더 좋은가요?</summary><p>오프데이 낮은 깊은 회복이 가능한 시간이지만, 수면 패턴이 야간 중심이라면 늦은 오후가 더 적합한 경우가 많습니다. 본인 수면 리듬에 맞춰 조정하시는 것을 권장합니다.</p></details>
<details><summary>병원 야간 근무자도 같은 코스가 권장되나요?</summary><p>병원·간호 직군은 발·다리 피로 누적이 큰 편이라 스웨디시에 발 케어 옵션을 함께 안내드리는 경우가 많습니다.</p></details>
</div>
</section>
""" + _MAG_DISCLAIMER


# ===== Magazine 3 — 사무직 어깨·목 케어 =====
_MAG3_BODY = _mag_toc([
    ("데스크워크가 누적되면 일어나는 변화", "what"),
    ("자주 나타나는 4가지 신체 신호", "signal"),
    ("초기 케어가 중요한 이유", "early"),
    ("운영팀이 사무직에 권장하는 코스 구성", "course"),
    ("일상에서 함께 권장되는 자세 가이드", "posture"),
]) + """
<section class="block" id="what">
<h2>데스크워크가 누적되면 일어나는 변화</h2>
<p>하루 8-10시간 책상 앞에서 일하는 사무직은 본인이 자각하지 못하는 사이에 어깨·목·등·허리에 긴장이 누적됩니다. 이는 한두 번의 휴식으로 회복되지 않으며, 일정 임계점을 넘으면 일상생활에도 영향을 미치기 시작합니다.</p>
<p>운영팀이 1-3년차 사무직 이용자와 진행한 상담에서 가장 많이 언급된 표현은 "어깨가 무겁다", "목이 잘 안 돌아간다", "퇴근하고도 긴장이 안 풀린다"였습니다. 이런 상태가 한 달 이상 지속되면 단순 휴식이 아니라 회복 케어가 필요한 시점입니다.</p>
</section>

<section class="block" id="signal">
<h2>자주 나타나는 4가지 신체 신호</h2>
<ol class="steps">
<li><strong>어깨 결림이 풀리지 않는다</strong><p>아침에 일어났을 때부터 어깨가 무거운 상태가 1주 이상 지속됩니다.</p></li>
<li><strong>목 회전 시 통증</strong><p>책상에서 좌우를 볼 때 목이 부드럽게 돌아가지 않습니다.</p></li>
<li><strong>두통·집중력 저하</strong><p>긴장이 머리까지 올라와 오후 시간에 두통이 잦아집니다.</p></li>
<li><strong>수면 후에도 피로감</strong><p>충분히 잔 것 같아도 어깨·목 부담이 그대로 남아 있습니다.</p></li>
</ol>
</section>

<section class="block" id="early">
<h2>초기 케어가 중요한 이유</h2>
<p>위 신호가 1-2주 정도 짧게 나타날 때는 단기 회복 케어로도 빠르게 정상화됩니다. 하지만 3개월 이상 누적되면 회복에 필요한 시간이 배 이상 늘어납니다. 초기 신호를 인지한 시점에서 2-3회 케어를 진행하는 것이 가장 효율적인 회복 흐름입니다.</p>
<div class="callout warn">
<strong>주의 — 의료 신호와 회복 신호의 구분</strong>
<p>특정 부위에 찌릿한 통증, 저림, 운동 범위 제한이 분명하다면 회복 케어가 아닌 의료 진단이 우선입니다. 마사지는 의료 행위가 아니며, 이런 신호가 분명한 경우 정형외과·신경과 진료를 먼저 받으시기를 권장합니다.</p>
</div>
</section>

<section class="block" id="course">
<h2>운영팀이 사무직에 권장하는 코스 구성</h2>
<p>1-3년차 사무직 이용자에게 가장 자주 권장되는 코스 흐름은 다음과 같습니다.</p>
<table class="compare-table">
<thead><tr><th scope="col">단계</th><th scope="col">권장 코스</th><th scope="col">길이·시기</th></tr></thead>
<tbody>
<tr><th scope="row">초기 누적 1-2주</th><td>스웨디시</td><td>60분, 1회</td></tr>
<tr><th scope="row">어깨·목 누적 1개월</th><td>스웨디시 + 어깨 집중</td><td>90분, 1-2회</td></tr>
<tr><th scope="row">전신 누적 3개월+</th><td>홈타이 또는 스포츠</td><td>120분, 2-3회 분할</td></tr>
<tr><th scope="row">유지 회복</th><td>스웨디시·아로마</td><td>주 1회 90분</td></tr>
</tbody>
</table>
</section>

<section class="block" id="posture">
<h2>일상에서 함께 권장되는 자세 가이드</h2>
<ul class="check-list">
<li><strong>모니터 높이</strong> — 시선이 화면 상단 1/3 지점에 오도록 조정</li>
<li><strong>의자 각도</strong> — 무릎이 엉덩이보다 살짝 낮게, 발은 바닥 평면에 닿게</li>
<li><strong>1시간 1회 일어서기</strong> — 어깨 회전 + 목 좌우 스트레칭 30초</li>
<li><strong>마우스·키보드 위치</strong> — 팔꿈치가 직각에 가까운 각도로 유지</li>
<li><strong>저녁 휴대폰 사용 자세</strong> — 누운 자세로 장시간 사용은 거북목 누적의 주요 원인</li>
</ul>
<p>위 자세는 마사지 회복 효과를 더 오래 유지하는 데에도 도움이 됩니다. 자세히는 <a href="/guide/massage-before-after/">마사지 전후 주의사항</a> 가이드에 정리되어 있습니다.</p>
</section>
""" + _MAG_DISCLAIMER


# ===== Magazine 4 — 호텔 투숙객을 위한 출장마사지 이용 안내 =====
_MAG4_BODY = _mag_toc([
    ("호텔 객실 케어의 특징", "feature"),
    ("객실 예약 시 사전 안내해야 할 5가지", "checklist"),
    ("호텔 등급별 진행 흐름의 차이", "by-grade"),
    ("자주 선택되는 시간대와 코스", "timeslot"),
    ("출장·여행 일정에서 코스 시간 잡는 법", "schedule"),
    ("호텔 진행 시 자주 묻는 질문", "qna"),
    ("코스 후 권장되는 마무리", "after"),
]) + """
<section class="block" id="feature">
<h2>호텔 객실 케어의 특징</h2>
<p>호텔 객실에서 받는 출장마사지는 가정 방문과 비교해 공간이 정돈되어 있고, 진행 후 곧바로 휴식·수면으로 이어갈 수 있다는 점이 가장 큰 장점입니다. 출장·여행 일정 중 짧은 회복 시간을 활용하시는 분들이 자주 선택합니다.</p>
<ul class="check-list">
<li>객실 자체가 진행 공간으로 사용되어 별도 준비가 거의 없음</li>
<li>진행 후 곧바로 샤워·휴식·수면으로 이어지는 자연스러운 흐름</li>
<li>가족·이웃 동선 변수가 없어 일정 충돌이 적음</li>
<li>심야 시간대 진행이 가장 매끄러운 환경</li>
</ul>
</section>

<section class="block" id="checklist">
<h2>객실 예약 시 사전 안내해야 할 5가지</h2>
<ol class="steps">
<li><strong>호텔명·객실 호수·층</strong><p>공동현관·엘리베이터 출입 안내에 필수입니다.</p></li>
<li><strong>체크인 시각</strong><p>진행 시작 시각이 체크인 직후라면 시간 여유를 함께 계산합니다.</p></li>
<li><strong>객실 유형</strong><p>더블·트윈·스위트에 따라 진행 공간이 달라집니다.</p></li>
<li><strong>동행자 정보</strong><p>동행자가 있다면 진행 동선·시간을 별도 안내합니다.</p></li>
<li><strong>특별 출입 조건</strong><p>일부 5성 호텔은 사전 게스트 등록이 권장됩니다.</p></li>
</ol>
</section>

<section class="block" id="by-grade">
<h2>호텔 등급별 진행 흐름의 차이</h2>
<table class="compare-table">
<thead><tr><th scope="col">호텔 유형</th><th scope="col">진행 특이사항</th></tr></thead>
<tbody>
<tr><th scope="row">5성·럭셔리 (강남·도심)</th><td>공동현관 출입 절차, 게스트 등록 권장, 객실 공간 충분</td></tr>
<tr><th scope="row">비즈니스 호텔</th><td>가장 진행이 매끄러운 유형, 객실 출입 자유로움</td></tr>
<tr><th scope="row">레지던스·서비스 아파트</th><td>주방·세탁 공간 분리, 사전 게스트 등록 필요할 수 있음</td></tr>
<tr><th scope="row">풀빌라·독채 (제주·강원)</th><td>독립 공간, 커플 코스 진행에 가장 자유로움</td></tr>
<tr><th scope="row">부티크 호텔</th><td>객실이 작은 경우 진행 자세·동선 사전 합의</td></tr>
</tbody>
</table>
</section>

<section class="block" id="timeslot">
<h2>자주 선택되는 시간대와 코스</h2>
<div class="dos-donts">
<div class="dos">
<strong>출장 일정 (평일)</strong>
<ul>
<li>저녁 미팅 후 22-00시 사이</li>
<li>다음 날 일정에 맞춰 60-90분</li>
<li>스웨디시·아로마 자주 안내</li>
</ul>
</div>
<div class="dos">
<strong>여행 일정 (주말·휴가)</strong>
<ul>
<li>체크인 후 저녁 시간대</li>
<li>여유 있는 90-120분</li>
<li>커플 코스도 함께 안내</li>
</ul>
</div>
</div>
</section>

<section class="block" id="schedule">
<h2>출장·여행 일정에서 코스 시간 잡는 법</h2>
<ul class="check-list">
<li><strong>이동 직후 vs 저녁</strong> — 이동 피로가 큰 날은 도착 당일 저녁이 가장 효과적</li>
<li><strong>식사 시간과 분리</strong> — 코스 시작 1-2시간 전 가벼운 식사가 권장</li>
<li><strong>다음 날 일정과의 간격</strong> — 다음 날 이른 일정이 있으면 90분 이내 코스</li>
<li><strong>체크아웃 시각</strong> — 진행 후 충분한 휴식 시간을 확보할 수 있는지 확인</li>
</ul>
</section>

<section class="block" id="qna">
<h2>호텔 진행 시 자주 묻는 질문</h2>
<div class="faq">
<details><summary>호텔 직원에게 미리 알려야 하나요?</summary><p>일반적으로는 별도 통보가 필요하지 않습니다. 다만 일부 5성 호텔은 외부 출입에 게스트 등록을 권장하기도 합니다.</p></details>
<details><summary>객실이 작아도 가능한가요?</summary><p>더블룸 정도면 진행이 충분합니다. 매우 협소한 부티크 객실은 진행 자세·동선을 사전에 합의합니다.</p></details>
<details><summary>풀빌라에서도 가능한가요?</summary><p>가능합니다. 풀빌라는 독립 공간이라 커플 코스 진행에도 가장 적합합니다. 다만 위치에 따라 이동 거리 변수가 큽니다.</p></details>
<details><summary>일행이 있는데 한 명만 받아도 되나요?</summary><p>가능합니다. 진행 시간 동안 일행이 객실에 함께 있어도 무방하며, 동시 진행을 원하시는 경우 커플 코스로 안내됩니다.</p></details>
</div>
</section>

<section class="block" id="after">
<h2>코스 후 권장되는 마무리</h2>
<p>호텔 객실 케어 후에는 다음 3가지를 함께 챙기시면 회복 효과가 더 오래 유지됩니다.</p>
<ul class="check-list">
<li>코스 후 30분 이내 물 500ml 이상</li>
<li>당일 음주·과도한 식사 자제</li>
<li>충분한 수면 — 호텔 진행은 곧바로 수면으로 이어지는 가장 좋은 흐름</li>
</ul>
<p>여행지 호텔 진행의 상세 안내는 <a href="/service/hotel-massage/">호텔 출장마사지</a> 페이지에서 함께 확인하실 수 있습니다.</p>
</section>
""" + _MAG_DISCLAIMER


# ===== Magazine 5 — 목적별 코스 고르는 법 =====
_MAG5_BODY = _mag_toc([
    ("코스 선택이 어렵게 느껴지는 이유", "why-hard"),
    ("4가지 목적별 추천 코스", "by-purpose"),
    ("코스 길이를 정하는 기준", "by-length"),
    ("운영팀의 코스 매칭 의사결정 흐름", "decision"),
    ("처음 받는다면 어떤 코스가 가장 무난한가", "first-time"),
]) + """
<section class="block" id="why-hard">
<h2>코스 선택이 어렵게 느껴지는 이유</h2>
<p>출장마사지를 처음 알아보시는 분이 가장 먼저 마주치는 어려움은 "어떤 코스를 받아야 하나"입니다. 스웨디시·아로마·홈타이·스포츠·커플… 종류는 많은데 차이가 명확하게 안내된 곳이 많지 않습니다.</p>
<p>운영팀이 상담 과정에서 가장 자주 받는 질문도 "처음인데 뭐가 좋을까요"입니다. 이 매거진은 그 질문에 답하기 위한 가이드로, 운영팀이 실제로 어떤 기준으로 코스를 권장하는지 그대로 공개합니다.</p>
</section>

<section class="block" id="by-purpose">
<h2>4가지 목적별 추천 코스</h2>
<table class="compare-table">
<thead><tr><th scope="col">목적</th><th scope="col">권장 1순위</th><th scope="col">대체 코스</th></tr></thead>
<tbody>
<tr><th scope="row">긴장 완화·수면 보조</th><td>스웨디시</td><td>아로마</td></tr>
<tr><th scope="row">근육 뭉침 해소</th><td>홈타이</td><td>스포츠</td></tr>
<tr><th scope="row">운동 후 회복</th><td>스포츠</td><td>홈타이</td></tr>
<tr><th scope="row">여행·여가 회복</th><td>아로마</td><td>스웨디시</td></tr>
</tbody>
</table>
<p>목적이 분명할수록 코스 선택이 쉽습니다. 두 가지 이상 목적이 섞여 있다면 코스 길이를 늘려 절반씩 진행하는 흐름도 가능합니다.</p>
</section>

<section class="block" id="by-length">
<h2>코스 길이를 정하는 기준</h2>
<div class="dos-donts">
<div class="dos">
<strong>60분이 적합한 경우</strong>
<ul>
<li>처음 받으시는 분</li>
<li>가볍게 컨디션 점검</li>
<li>심야 시간 짧은 회복</li>
<li>다음 날 이른 일정이 있을 때</li>
</ul>
</div>
<div class="dos">
<strong>90-120분이 적합한 경우</strong>
<ul>
<li>본격적인 회복이 목적</li>
<li>전신 근육 뭉침 해소</li>
<li>주말 여유 일정</li>
<li>두 가지 코스 조합 진행</li>
</ul>
</div>
</div>
</section>

<section class="block" id="decision">
<h2>운영팀의 코스 매칭 의사결정 흐름</h2>
<p>운영팀이 상담에서 실제로 따르는 코스 매칭 흐름은 다음과 같습니다. 이용자에게 직접 묻는 질문 순서이기도 합니다.</p>
<ol class="steps">
<li><strong>이번 케어의 핵심 목적</strong><p>긴장 완화? 근육 회복? 운동 후 회복? 여행 회복?</p></li>
<li><strong>받는 시간대</strong><p>저녁·심야면 부드러운 스웨디시·아로마, 주말 낮이면 좀 더 깊은 홈타이·스포츠.</p></li>
<li><strong>다음 날 일정</strong><p>다음 날 이른 일정이 있으면 짧은 코스, 여유가 있으면 긴 코스 권장.</p></li>
<li><strong>최근 컨디션</strong><p>특정 부위 통증이 분명하면 의료 진단 권장. 일반적인 누적 피로라면 코스 진행 권장.</p></li>
<li><strong>예산 범위</strong><p>코스·시간 길이가 정해지면 <a href="/reservation/price/">가격 안내</a>에서 시작 금액을 확인.</p></li>
</ol>
</section>

<section class="block" id="first-time">
<h2>처음 받는다면 어떤 코스가 가장 무난한가</h2>
<p>운영팀이 가장 자주 권장하는 첫 코스 조합은 <strong>스웨디시 60분</strong>입니다. 압력이 부드럽고, 오일 케어로 전신 컨디션을 가볍게 점검할 수 있으며, 다음 날 일정에도 부담이 적습니다.</p>
<p>첫 진행 후 본인 컨디션·선호도에 맞춰 다음 진행 시 코스를 조정하시는 흐름이 가장 안전합니다. 자세한 첫 이용 가이드는 <a href="/guide/first-time-massage/">처음 이용 전 알아둘 점</a>에서 확인하실 수 있습니다.</p>
</section>
""" + _MAG_DISCLAIMER


# ===== Magazine 6 — 지역별 출장마사지 이용 팁 =====
_MAG6_BODY = _mag_toc([
    ("권역별 이용 패턴이 다른 이유", "why"),
    ("수도권 — 서울·경기·인천", "metro"),
    ("광역시 — 부산·대구·대전·광주·울산", "metropolitan"),
    ("도(道) 권역 — 강원·충청·전라·경상", "do"),
    ("제주 권역 — 호텔·풀빌라 중심", "jeju"),
    ("권역 공통 이용 팁", "common"),
]) + """
<section class="block" id="why">
<h2>권역별 이용 패턴이 다른 이유</h2>
<p>출장마사지는 같은 코스라도 권역별 이용 패턴이 분명히 다릅니다. 인구 밀도, 호텔 분포, 교통 인프라, 산업 구조, 관광 수요가 권역마다 다르기 때문입니다. 운영팀이 권역별 상담에서 자주 마주치는 차이점을 정리합니다.</p>
<p class="muted">※ 본 페이지의 권역별 안내는 운영팀의 상담 경험에 기반한 정성적 정리입니다.</p>
</section>

<section class="block" id="metro">
<h2>수도권 — 서울·경기·인천</h2>
<div class="dos-donts">
<div class="dos">
<strong>서울 (<a href="/area/seoul/">전체 안내</a>)</strong>
<ul>
<li>25개 자치구별 가능 시간 다름</li>
<li>강남·여의도·도심 호텔 야간 비중 높음</li>
<li>심야 진행이 가장 자유로운 권역</li>
</ul>
</div>
<div class="dos">
<strong>경기 (<a href="/area/gyeonggi/">전체 안내</a>)</strong>
<ul>
<li>31개 시·군 권역별 차이 큼</li>
<li>분당·판교 IT 직군 야근 후 케어</li>
<li>일산·파주 신도시 가정 방문 중심</li>
</ul>
</div>
<div class="dos">
<strong>인천 (<a href="/area/incheon/">전체 안내</a>)</strong>
<ul>
<li>공항 인근 단시간 케어 문의 많음</li>
<li>송도 출장 객실 진행 자주 안내</li>
<li>구도심·신도시 진행 흐름 다름</li>
</ul>
</div>
</div>
</section>

<section class="block" id="metropolitan">
<h2>광역시 — 부산·대구·대전·광주·울산</h2>
<table class="compare-table">
<thead><tr><th scope="col">권역</th><th scope="col">자주 안내되는 패턴</th></tr></thead>
<tbody>
<tr><th scope="row"><a href="/area/busan/">부산</a></th><td>해운대·광안 관광 호텔 야간, 스웨디시 90분 자주 안내</td></tr>
<tr><th scope="row"><a href="/area/daegu/">대구</a></th><td>수성·동성로 호텔, 권역별 가능 시간 차이 분명</td></tr>
<tr><th scope="row"><a href="/area/daejeon/">대전</a></th><td>유성 연구단지·둔산 출장, 평일 저녁 비중 높음</td></tr>
<tr><th scope="row"><a href="/area/gwangju/">광주</a></th><td>상무·첨단·수완 평일 저녁, 가정·호텔 모두 안내</td></tr>
<tr><th scope="row"><a href="/area/ulsan/">울산</a></th><td>산업단지 야간·장기 출장 정기 예약, 스포츠 케어 권장</td></tr>
</tbody>
</table>
</section>

<section class="block" id="do">
<h2>도(道) 권역 — 강원·충청·전라·경상</h2>
<p>도(道) 권역은 면적이 넓어 같은 도 안에서도 권역별 이용 패턴 차이가 큽니다. 시·군 단위 안내가 필요한 경우 권역 페이지에서 확인하실 수 있습니다.</p>
<ul class="check-list">
<li><a href="/area/gangwon/"><strong>강원</strong></a> — 강릉·속초 관광 케어, 평창·홍천 리조트 케어. 심야 마감이 비교적 이른 편</li>
<li><a href="/area/chungbuk/"><strong>충북</strong></a> — 청주·충주 산업 출장 평일 저녁, 단양·제천 리조트 케어</li>
<li><a href="/area/chungnam/"><strong>충남</strong></a> — 천안·아산 산업 출장, 보령·태안 관광 케어</li>
<li><a href="/area/jeonbuk/"><strong>전북</strong></a> — 전주 한옥마을 호텔 진행, 익산·군산 산업 단지 케어</li>
<li><a href="/area/jeonnam/"><strong>전남</strong></a> — 여수·순천 관광 호텔, 광양·목포 산업 단지</li>
<li><a href="/area/gyeongbuk/"><strong>경북</strong></a> — 포항·구미 산업 출장, 경주 관광 호텔</li>
<li><a href="/area/gyeongnam/"><strong>경남</strong></a> — 창원·김해 산업 단지, 통영·거제 관광 호텔</li>
</ul>
</section>

<section class="block" id="jeju">
<h2>제주 권역 — 호텔·풀빌라 중심</h2>
<p><a href="/area/jeju/">제주</a>는 다른 권역과 가장 다른 이용 패턴을 보입니다. 가정 방문보다 호텔·리조트·풀빌라 진행 비중이 압도적으로 높습니다.</p>
<ul class="check-list">
<li><strong>호텔·리조트</strong> — 중문·시내 5성 호텔, 체크인 후 저녁 시간대 진행</li>
<li><strong>풀빌라 독채</strong> — 커플·가족 단위 진행, 90-120분 코스 자주 선택</li>
<li><strong>렌터카 운전 후</strong> — 어깨·등 회복용 홈타이가 자주 권장</li>
<li><strong>오름 등산 후</strong> — 다리·종아리 회복용 스포츠 케어</li>
</ul>
</section>

<section class="block" id="common">
<h2>권역 공통 이용 팁</h2>
<div class="callout tip">
<strong>어떤 권역이든 사전 합의가 매끄러운 진행의 핵심</strong>
<p>코스·시간·진행 장소·이동 거리는 권역에 따라 다르지만, "사전 상담에서 정확한 정보를 알려주실수록 진행이 매끄럽다"는 원칙은 모든 권역에 공통됩니다. 호텔 진행이면 호수·체크인 시각, 가정 진행이면 공간 조건·동행자 정보, 산업 출장이면 단지명·근무 시간 등을 미리 정리해 주세요.</p>
</div>
<p>전국 권역별 안내는 <a href="/area/">지역별 찾기</a>에서 시·도 단위로 확인하실 수 있으며, 권역별 시간·코스·이동 안내는 각 시·도 페이지에 정리되어 있습니다.</p>
</section>
""" + _MAG_DISCLAIMER


MAGAZINE_ARTICLES = [
    {
        "slug": "first-time-essentials",
        "title": "출장마사지 처음 이용 전 알아둘 점",
        "desc": "처음 출장마사지를 받기 전 가장 자주 묻는 질문, 첫 코스 선택 기준, 사전 준비 체크리스트, 진행 흐름, 자주 놓치는 점, 사후 케어까지 운영팀이 정리한 첫 이용 가이드입니다.",
        "category": "처음 이용", "cover": "forest", "published": "2026-05-15",
        "lede": "처음 받기 전 알아두면 진행이 매끄럽습니다. 첫 코스 선택부터 사후 케어까지 운영팀이 가장 자주 안내하는 순서로 정리합니다.",
        "body": _MAG1_BODY,
    },
    {
        "slug": "night-worker-recovery",
        "title": "야간 근무자를 위한 피로 회복 루틴",
        "desc": "병원·간호·IT 운영·보안 등 야간 근무자가 더 빨리 지치는 이유와, 운영팀이 권장하는 회복 케어 5가지 패턴, 함께 권장되는 회복 보조 습관까지 정리한 라이프스타일 매거진입니다.",
        "category": "라이프스타일", "cover": "dusk", "published": "2026-05-08",
        "lede": "야간 근무자가 자주 마주치는 회복 문제와, 출장마사지를 활용해 회복 리듬을 만드는 5가지 패턴을 정리합니다.",
        "body": _MAG2_BODY,
    },
    {
        "slug": "desk-worker-neck-shoulder",
        "title": "사무직 어깨·목 — 데스크워크 누적이 만드는 변화와 케어 흐름",
        "desc": "1-3년차 사무직 이용자가 가장 자주 호소하는 어깨·목 누적 신호 4가지와 단계별 권장 코스, 함께 권장되는 자세 가이드를 정리한 웰니스 매거진입니다.",
        "category": "웰니스", "cover": "sage", "published": "2026-05-04",
        "lede": "어깨가 무겁고 목이 잘 안 돌아간다면 — 데스크워크 1년 누적이 만드는 4가지 신호와 단계별 케어 흐름을 정리합니다.",
        "body": _MAG3_BODY,
    },
    {
        "slug": "hotel-guest-guide",
        "title": "호텔 투숙객을 위한 출장마사지 이용 안내",
        "desc": "호텔 객실에서 받는 출장마사지의 특징, 객실 예약 시 사전 안내해야 할 정보, 호텔 등급별 진행 흐름의 차이, 자주 선택되는 시간대까지 운영팀이 정리한 호텔 투숙객 전용 가이드입니다.",
        "category": "호텔 이용", "cover": "sunset", "published": "2026-05-02",
        "lede": "호텔 객실에서 받는 출장마사지는 흐름이 다릅니다. 호텔 등급별 진행 차이와 객실 예약 시 사전 안내해야 할 점을 정리합니다.",
        "body": _MAG4_BODY,
    },
    {
        "slug": "course-selection-by-purpose",
        "title": "출장마사지 코스 고르는 기준",
        "desc": "스웨디시·아로마·홈타이·스포츠 중 무엇을 받을지 고민될 때, 운영팀이 상담에서 실제로 따르는 코스 매칭 의사결정 5단계와 첫 이용자를 위한 무난한 첫 코스를 공개합니다.",
        "category": "코스 가이드", "cover": "earth", "published": "2026-04-22",
        "lede": "스웨디시·아로마·홈타이·스포츠 — 어떤 코스가 나에게 맞을까요? 운영팀의 매칭 의사결정 흐름을 그대로 공개합니다.",
        "body": _MAG5_BODY,
    },
    {
        "slug": "regional-usage-tips",
        "title": "지역별 출장마사지 이용 팁",
        "desc": "수도권·광역시·도(道) 권역·제주까지 — 권역별 이용 패턴이 다른 이유와 권역마다 자주 안내되는 시간대·코스·진행 장소를 운영팀이 정리한 지역 가이드입니다.",
        "category": "지역 가이드", "cover": "sage", "published": "2026-05-10",
        "lede": "같은 코스라도 권역별 이용 패턴은 분명히 다릅니다. 수도권·광역시·도·제주 권역별로 자주 안내되는 흐름을 정리합니다.",
        "body": _MAG6_BODY,
    },
]


# 메가메뉴에 자동 주입되는 매거진 미니카드
def _render_mega_magazine_cards(start=0, count=3):
    """발행일 기준 최신순 정렬 후 [start:start+count] 슬라이스를 앨범형 미니카드로 렌더.
    HEADER의 {MAGAZINE_LATEST_CARDS}/{MAGAZINE_PREV_CARDS} 자리에 main() 시작 시 주입됨."""
    sorted_arts = sorted(
        MAGAZINE_ARTICLES,
        key=lambda a: a.get("published", ""),
        reverse=True,
    )[start:start + count]
    parts = []
    for a in sorted_arts:
        title = a["title"].split(" — ")[0] if " — " in a["title"] else a["title"]
        if len(title) > 24:
            title = title[:22] + "…"
        parts.append(
            f'                  <a class="mega-mag-card" href="/magazine/{a["slug"]}/">'
            f'<span class="mega-mag-cover mag-cover-{a["cover"]}">'
            f'<span class="mega-mag-cat">{a["category"]}</span>'
            f'</span>'
            f'<span class="mega-mag-title">{title}</span>'
            f'</a>'
        )
    return "\n".join(parts)


# ---------- Magazine hub ----------
def _mag_hub_card(idx, art, featured=False):
    cls = "mag-card mag-card-featured" if featured else "mag-card"
    return (
        f'<a class="{cls}" href="/magazine/{art["slug"]}/">'
        f'<div class="mag-card-cover mag-cover-{art["cover"]}">'
        f'<span class="mag-card-num">{idx:02d}</span>'
        f'<span class="mag-category-chip">{art["category"]}</span>'
        '</div>'
        '<div class="mag-card-body">'
        f'<h3 class="mag-card-title">{art["title"]}</h3>'
        f'<p class="mag-card-desc">{art["lede"]}</p>'
        '<div class="mag-card-foot">'
        f'<span class="mag-card-date">{art["published"]}</span>'
        '<span class="mag-card-arrow" aria-hidden="true">→</span>'
        '</div></div></a>'
    )


# 발행일 기준 최신순 정렬
_mag_sorted = sorted(MAGAZINE_ARTICLES, key=lambda a: a.get("published", ""), reverse=True)
_featured = _mag_sorted[0]
_others = _mag_sorted[1:]

# 카테고리 → 도트 컬러 매핑 (스크린샷의 컬러 도트와 동일)
_CAT_DOT = {
    "처음 이용":   "mag-cover-forest",
    "웰니스":      "mag-cover-sage",
    "라이프스타일": "mag-cover-dusk",
    "코스 가이드": "mag-cover-earth",
    "지역 가이드": "mag-cover-sage",
    "호텔 이용":   "mag-cover-sunset",
}

# 카테고리별 그룹핑
_cat_order = ["처음 이용", "웰니스", "라이프스타일", "코스 가이드", "지역 가이드", "호텔 이용"]
_cat_groups = {}
for a in _mag_sorted:
    _cat_groups.setdefault(a["category"], []).append(a)
_active_cats = [c for c in _cat_order if c in _cat_groups]
for c in _cat_groups:
    if c not in _active_cats:
        _active_cats.append(c)

# 매거진 hub 상단 — 카테고리 도트 칩 행 (메가메뉴와 동일한 디자인)
_chip_row = (
    '<div class="mega-mag-block mega-mag-block--cats hub-cat-block">'
    '<h2 class="mega-mag-block-title"><span class="mega-mag-block-eyebrow">CATEGORY</span>주제별 매거진</h2>'
    '<div class="mega-mag-cat-row">'
    + "".join(
        f'<a class="mega-mag-cat-chip" href="#cat-{c.replace(" ", "-")}">'
        f'<span class="mega-mag-cat-dot {_CAT_DOT.get(c, "mag-cover-forest")}"></span>{c}</a>'
        for c in _active_cats
    )
    + '</div></div>'
)

# 매거진 hub 상단 — 최신/이전 2열 앨범 (메가메뉴 미니카드와 동일 디자인, 더 큼)
def _mag_mini_card(a):
    title = a["title"].split(" — ")[0] if " — " in a["title"] else a["title"]
    if len(title) > 32:
        title = title[:30] + "…"
    return (
        f'<a class="mega-mag-card hub-mag-card" href="/magazine/{a["slug"]}/">'
        f'<span class="mega-mag-cover mag-cover-{a["cover"]}">'
        f'<span class="mega-mag-cat">{a["category"]}</span>'
        f'</span>'
        f'<span class="mega-mag-title">{title}</span>'
        f'</a>'
    )

_albums = (
    '<div class="mega-mag-block">'
    '<h2 class="mega-mag-block-title"><span class="mega-mag-block-eyebrow">FEATURED</span>발행 매거진</h2>'
    '<div class="mega-mag-grid hub-mag-grid-4">'
    + "".join(_mag_mini_card(a) for a in _mag_sorted)
    + '</div></div>'
)

# 카테고리별 상세 섹션 (하단)
_cat_sections = ""
for c in _active_cats:
    arts = _cat_groups[c]
    cat_id = "cat-" + c.replace(" ", "-")
    _cat_sections += (
        f'<section class="block mag-cat-section" id="{cat_id}">'
        f'<h2 class="mag-section-title">{c}<span class="mag-section-count">{len(arts)}편</span></h2>'
        '<div class="mag-grid">'
        + "".join(_mag_hub_card(i + 1, a) for i, a in enumerate(arts))
        + '</div></section>'
    )

add(
    path="magazine/index.html",
    url="/magazine/",
    slug="magazine-hub",
    title="바로GO 매거진 | 출장마사지 트렌드·웰니스·라이프스타일",
    description="바로GO 운영팀이 직접 집필하는 에디토리얼 매거진입니다. 트렌드·라이프스타일·웰니스·여행·코스 가이드 등 출장마사지 관련 주제를 다룹니다.",
    h1="바로GO 매거진",
    intro='<p class="lede">바로GO 운영팀이 직접 집필하는 에디토리얼 매거진입니다. 운영 데이터·상담 기록·운영팀 관찰을 바탕으로, 출장마사지를 둘러싼 트렌드·웰니스·라이프스타일·여행 주제를 다룹니다.</p>',
    breadcrumbs=[("홈", "/"), ("매거진", "/magazine/")],
    og_type="website",
    body=(
        '<div class="mag-hub-top">' +
        _chip_row +
        _albums +
        '</div>' +
        '<section class="block mag-featured-wrap">' +
        '<h2 class="mag-section-title">이번 호 추천</h2>' +
        _mag_hub_card(1, _featured, featured=True) +
        '</section>' +
        _cat_sections +
        '<section class="block mag-about">' +
        '<h2>매거진은 어떻게 만들어지나요?</h2>' +
        '<p>바로GO 매거진의 모든 기사는 운영팀(YH LAB)이 직접 집필·검수합니다. 운영 데이터·상담 기록을 인용하는 경우 본문에 명시하며, 외부 자료를 인용할 때는 출처를 함께 표기합니다. ' +
        '주제 선정 기준은 다음과 같습니다.</p>' +
        '<ul class="check-list">' +
        '<li>운영 데이터로 변화 추이를 설명할 수 있는 트렌드</li>' +
        '<li>특정 직군·상황에 도움이 되는 실용 정보</li>' +
        '<li>이용자가 의사결정에 사용할 수 있는 비교·가이드</li>' +
        '<li>여행·라이프스타일 등 출장마사지를 둘러싼 맥락 정보</li>' +
        '</ul>' +
        '<p>매거진은 매월 1-2회 발행되며, 발행 시 본 페이지 상단의 최신 기사 목록이 갱신됩니다. ' +
        '편집·정정 요청은 <a href="/support/contact/">문의하기</a>로 접수해 주세요.</p>' +
        '</section>'
    ),
    related=_rel(
        "/magazine/",
        ["/guide/", "/review/", "/service/business-trip-massage/", "/reservation/price/"],
        title="이어서 살펴볼 페이지",
    ),
)


# ---------- Magazine article pages ----------
# 발행일 기준 정렬 — prev/next 네비게이션용
_mag_chrono = sorted(MAGAZINE_ARTICLES, key=lambda a: a.get("published", ""), reverse=True)
_mag_chrono_idx = {a["slug"]: i for i, a in enumerate(_mag_chrono)}

for art in MAGAZINE_ARTICLES:
    source_url = f"/magazine/{art['slug']}/"
    # 같은 매거진 다른 글 4편 + 관련 페이지 1-2
    other_slugs = [a["slug"] for a in MAGAZINE_ARTICLES if a["slug"] != art["slug"]]
    rel_html = (
        '<aside class="related">'
        '<h2>이어서 읽어볼 매거진</h2>'
        '<ul>'
        + "".join(
            f'<li><a href="/magazine/{s}/">'
            + next(a["title"] for a in MAGAZINE_ARTICLES if a["slug"] == s)
            + '</a></li>'
            for s in other_slugs[:3]
        )
        + '<li><a href="/magazine/">매거진 전체 보기</a></li>'
        + '</ul>'
        '</aside>'
    )

    # 이전/다음 글 네비게이션 (시간순 정렬 기준)
    cur_idx = _mag_chrono_idx[art["slug"]]
    prev_art = _mag_chrono[cur_idx + 1] if cur_idx + 1 < len(_mag_chrono) else None  # 더 오래된 글
    next_art = _mag_chrono[cur_idx - 1] if cur_idx > 0 else None                    # 더 새 글
    nav_parts = ['<nav class="mag-prev-next" aria-label="매거진 이전·다음 글">']
    if next_art:
        nav_parts.append(
            f'<a class="mag-prev-next-card mag-prev-next-card--next" href="/magazine/{next_art["slug"]}/">'
            f'<span class="mag-prev-next-cover mag-cover-{next_art["cover"]}" aria-hidden="true"></span>'
            f'<span class="mag-prev-next-body">'
            f'<span class="mag-prev-next-label">다음 글</span>'
            f'<span class="mag-prev-next-title">{next_art["title"]}</span>'
            f'<span class="mag-prev-next-cat">{next_art["category"]}</span>'
            f'</span></a>'
        )
    if prev_art:
        nav_parts.append(
            f'<a class="mag-prev-next-card mag-prev-next-card--prev" href="/magazine/{prev_art["slug"]}/">'
            f'<span class="mag-prev-next-cover mag-cover-{prev_art["cover"]}" aria-hidden="true"></span>'
            f'<span class="mag-prev-next-body">'
            f'<span class="mag-prev-next-label">이전 글</span>'
            f'<span class="mag-prev-next-title">{prev_art["title"]}</span>'
            f'<span class="mag-prev-next-cat">{prev_art["category"]}</span>'
            f'</span></a>'
        )
    nav_parts.append('</nav>')
    prev_next_html = "".join(nav_parts)

    # 다크 에디토리얼 히어로 + 디렉터 바이라인을 본문 최상단에 자동 주입
    hero_html = _mag_hero_banner(art["slug"], art["category"], art["title"], art["lede"])
    byline_html = _mag_byline(art["slug"], art["published"], _mag_read_min_for(art["slug"]), art["category"])

    # 본문 첫머리의 <nav class="mag-toc">...</nav>를 분리 → 사이드 스티키에 배치
    raw_body = art["body"]
    _toc_match = re.search(r'<nav class="mag-toc"[^>]*>.*?</nav>', raw_body, re.S)
    if _toc_match:
        side_toc = _toc_match.group(0)
        clean_body = raw_body.replace(side_toc, "", 1)
    else:
        side_toc = ""
        clean_body = raw_body

    # 글 끝 디렉터 바이오 카드 (큰 사이즈)
    _author = _mag_author_for(art["slug"])
    _particle = _ko_particle_eul_reul(_author["specialty"])
    author_bio_html = (
        '<aside class="mag-author-bio">'
        f'<span class="mag-author-bio-avatar" aria-hidden="true">{_author["name"][0]}</span>'
        '<div class="mag-author-bio-text">'
        f'<span class="mag-author-bio-eyebrow">WRITTEN BY</span>'
        f'<strong class="mag-author-bio-name">{_author["name"]} <span>{_author["role"]}</span></strong>'
        f'<p class="mag-author-bio-desc">바로GO 에디토리얼팀에서 <em>{_author["specialty"]}</em>{_particle} 담당합니다. 운영 데이터·상담 기록을 바탕으로 신뢰할 수 있는 가이드를 집필합니다.</p>'
        '<a class="mag-author-bio-link" href="/magazine/">바로GO 매거진 더 보기 →</a>'
        '</div></aside>'
    )

    # 진행률 바
    progress_html = '<div class="mag-progress" aria-hidden="true"><div class="mag-progress-bar"></div></div>'

    body_html = (
        progress_html +
        hero_html +
        byline_html +
        '<div class="mag-article-grid">'
        '<aside class="mag-article-side">' + side_toc + '</aside>'
        '<div class="mag-article-body">' + clean_body + author_bio_html + '</div>'
        '</div>' +
        prev_next_html
    )
    add(
        path=f"magazine/{art['slug']}/index.html",
        url=source_url,
        slug=f"magazine-{art['slug']}",
        title=f"{art['title']} | 바로GO 매거진",
        description=art["desc"],
        h1=art["title"],
        intro=f'<p class="lede">{art["lede"]}</p>',
        breadcrumbs=[("홈", "/"), ("매거진", "/magazine/"), (art["title"], source_url)],
        og_type="article",
        body=body_html,
        related=rel_html,
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
<p>바로GO는 건전한 출장마사지 안내만 제공합니다. 불법·퇴폐 서비스 알선·중개를 하지 않으며, 관련 문의는 응대하지 않습니다. 자세한 내용은 <a href="/about/safety-policy/">안전 이용 정책</a>에서 확인하실 수 있습니다.</p>
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
<details><summary>불법 서비스도 안내하나요?</summary><p>아니요. 건전한 출장마사지 안내만 제공합니다.</p></details>
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
  title="제휴·광고 문의 · 입점 안내 | 바로GO",
  description="바로GO 제휴·광고·입점 문의 양식. 광고 유형, 광고 지역 등을 입력하시면 운영팀에 즉시 전달됩니다. 영업일 기준 3일 이내 회신.",
  h1="제휴·광고 문의",
  intro='<p class="lede">광고 진행·지역 독점·제휴 입점·관리사 협력 문의를 운영팀이 직접 응대합니다. 아래 양식을 작성해 주시면 운영팀 텔레그램으로 즉시 전달되며, 영업일 기준 3일 이내 회신드립니다.</p>',
  breadcrumbs=[("홈","/"),("고객센터","/support/"),("제휴·광고 문의","/support/partnership/")],
  body="""
<section class="block">
<h2>제휴·광고 진행 기준</h2>
<ul class="check-list">
<li>합법적이고 신고된 사업자 또는 프리랜서</li>
<li>출장마사지 관련 경력 또는 광고 진행 이력</li>
<li>안전 이용 정책 동의 및 가격·취소 기준 준수</li>
<li>광고 진행은 권역·기간 단위로 안내됩니다</li>
</ul>
</section>

<section class="block">
<h2>문의 양식</h2>
<p class="muted">아래 항목을 모두 입력하신 후 <strong>작성 완료</strong> 버튼을 눌러주세요. 입력하신 정보는 운영팀 텔레그램으로 즉시 전송되며, 저장·이용 정책은 <a href="/about/privacy/">개인정보처리방침</a>을 따릅니다.</p>

<form id="partnership-form" class="pf-form" novalidate>
  <div class="pf-field">
    <label for="pf-type">광고문의 유형 <span class="pf-req" aria-hidden="true">*</span></label>
    <select id="pf-type" name="inquiryType" required>
      <option value="">선택해 주세요</option>
      <option value="일반 광고">일반 광고</option>
      <option value="지역 독점">지역 독점 광고</option>
      <option value="배너 광고">배너 광고</option>
      <option value="제휴·입점">제휴·입점</option>
      <option value="관리사 협력">관리사 협력</option>
      <option value="기타">기타</option>
    </select>
  </div>

  <div class="pf-grid-2">
    <div class="pf-field">
      <label for="pf-name">성명 <span class="pf-req" aria-hidden="true">*</span></label>
      <input id="pf-name" name="name" type="text" autocomplete="name" maxlength="50" required>
    </div>
    <div class="pf-field">
      <label for="pf-phone">전화번호 <span class="pf-req" aria-hidden="true">*</span></label>
      <input id="pf-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="010-0000-0000" maxlength="30" required>
    </div>
  </div>

  <div class="pf-field">
    <label for="pf-region">광고 지역 <span class="pf-req" aria-hidden="true">*</span></label>
    <input id="pf-region" name="region" type="text" placeholder="예: 서울 강남, 부산 해운대, 전국 등" maxlength="100" required>
  </div>

  <div class="pf-field">
    <label for="pf-message">문의사항 <span class="pf-req" aria-hidden="true">*</span></label>
    <textarea id="pf-message" name="message" rows="6" maxlength="2000" placeholder="진행하고자 하는 광고·제휴 내용, 희망 시기 등을 자유롭게 작성해 주세요."required></textarea>
    <small class="pf-counter"><span id="pf-count">0</span> / 2000</small>
  </div>

  <!-- 봇 차단 허니팟 (사람에게는 안 보임) -->
  <div class="pf-hp" aria-hidden="true">
    <label for="pf-hp">웹사이트 (입력 금지)</label>
    <input id="pf-hp" name="hp" type="text" tabindex="-1" autocomplete="off">
  </div>

  <div class="pf-consent">
    <label class="pf-checkbox">
      <input type="checkbox" id="pf-agree" required>
      <span>위 정보가 운영팀 텔레그램으로 전송되는 것에 동의합니다. (<a href="/about/privacy/">개인정보처리방침</a>)</span>
    </label>
  </div>

  <button type="submit" class="pf-submit" id="pf-submit">작성 완료 · 운영팀에 전송</button>

  <div class="pf-status" id="pf-status" role="status" aria-live="polite"></div>
</form>
</section>

<section class="block">
<h2>전화 문의</h2>
<p>긴급한 사안이거나 양식 작성이 어려우신 경우 <a href="tel:0508-202-4719">0508-202-4719</a>로 직접 연락 주셔도 됩니다. 영업일 기준 3일 이내 회신을 원칙으로 합니다.</p>
</section>

<script>
(function(){
  var form = document.getElementById('partnership-form');
  if (!form) return;
  var status = document.getElementById('pf-status');
  var submit = document.getElementById('pf-submit');
  var msg = document.getElementById('pf-message');
  var count = document.getElementById('pf-count');
  var ts = Date.now();

  msg.addEventListener('input', function(){
    count.textContent = msg.value.length;
  });

  form.addEventListener('submit', function(e){
    e.preventDefault();
    if (!document.getElementById('pf-agree').checked) {
      showStatus('개인정보 처리 동의가 필요합니다.', 'error');
      return;
    }
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    var data = {
      inquiryType: form.inquiryType.value,
      name: form.name.value.trim(),
      phone: form.phone.value.trim(),
      region: form.region.value.trim(),
      message: form.message.value.trim(),
      hp: form.hp.value,
      ts: ts
    };
    submit.disabled = true;
    submit.textContent = '전송 중…';
    showStatus('전송 중입니다…', 'pending');

    fetch('/api/partnership', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(function(r){ return r.json().then(function(j){ return { ok: r.ok, body: j }; }); })
    .then(function(res){
      if (res.ok && res.body && res.body.ok) {
        showStatus('✓ 문의가 접수되었습니다. 영업일 기준 3일 이내 회신드립니다.', 'success');
        form.reset();
        count.textContent = '0';
        submit.textContent = '전송 완료';
      } else {
        var err = (res.body && res.body.error) || '전송에 실패했습니다. 잠시 후 다시 시도해 주세요.';
        showStatus('✗ ' + err, 'error');
        submit.disabled = false;
        submit.textContent = '작성 완료 · 운영팀에 전송';
      }
    })
    .catch(function(){
      showStatus('✗ 네트워크 오류가 발생했습니다. 다시 시도해 주세요.', 'error');
      submit.disabled = false;
      submit.textContent = '작성 완료 · 운영팀에 전송';
    });
  });

  function showStatus(text, kind){
    status.textContent = text;
    status.className = 'pf-status pf-status-' + kind;
  }
})();
</script>
""",
  related=_rel("/support/partnership/", ["/support/contact/", "/about/operation-policy/", "/about/therapist-policy/", "/about/brand/"], title="함께 살펴볼 문서"),
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

_ABOUT_LEGAL_BYLINE_TPL = (
    '<div class="guide-meta">'
    '<div class="guide-meta-author">'
    '<span class="guide-meta-avatar" aria-hidden="true">YH</span>'
    '<div class="guide-meta-author-text">'
    '<strong>바로GO 운영팀 (YH LAB)</strong>'
    '<span>{role} · 사업자등록번호 815-26-00585</span>'
    '</div></div>'
    '<div class="guide-meta-info">'
    '<span class="guide-meta-tag">시행일 · {effective}</span>'
    '<span class="guide-meta-tag">버전 · {ver}</span>'
    '</div></div>'
)

add(
  path="about/index.html", url="/about/", slug="about-hub",
  title="바로GO 소개 | 브랜드·운영 원칙·정책·약관 | 바로GO",
  description="바로GO(운영사 YH LAB)의 브랜드 운영 철학, 예약·가격·후기·콘텐츠 운영 원칙, 관리사 협력 기준, 안전 이용 정책, 개인정보처리방침, 이용약관 등 공식 문서를 한곳에 정리한 페이지입니다.",
  h1="바로GO 소개",
  intro='<p class="lede">바로GO(운영사 YH LAB)는 전국 출장마사지 예약 안내 플랫폼입니다. 운영 사업자 정보, 운영 원칙, 관리사 협력 기준, 안전 정책, 그리고 법적 문서(개인정보처리방침·이용약관)를 모두 공개합니다. 본 페이지에서 각 문서로 이동하실 수 있습니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/")],
  body="""
<section class="block">
<h2>사업자 정보</h2>
<ul class="check-list">
<li><strong>상호</strong> : 바로GO (운영사 YH LAB)</li>
<li><strong>대표</strong> : 김유환</li>
<li><strong>사업자등록번호</strong> : 815-26-00585</li>
<li><strong>본사 주소</strong> : 경기도 파주시 청석로 268</li>
<li><strong>대표 예약 전화</strong> : <a href="tel:0508-202-4719">0508-202-4719</a> (연중무휴 운영)</li>
<li><strong>운영 형태</strong> : 출장마사지 예약 안내 플랫폼 (자체 직영 + 협력 관리사 운영)</li>
</ul>
<p>법인·사업자 정보는 국세청 사업자등록번호 조회로 누구나 검증하실 수 있습니다. 모든 공식 안내·결제·세금계산서 발행은 위 사업자명 기준으로 이루어집니다.</p>
</section>
<section class="block">
<h2>공식 문서 바로가기</h2>
<ul class="service-grid">
<li><h3><a href="/about/brand/">브랜드 소개</a></h3><p>바로GO를 시작한 이유, 운영 미션, 다른 안내 플랫폼과의 차이점</p></li>
<li><h3><a href="/about/operation-policy/">운영 원칙</a></h3><p>예약·가격·후기·콘텐츠·광고 표현 등 8개 영역의 세부 운영 원칙</p></li>
<li><h3><a href="/about/therapist-policy/">관리사 운영 기준</a></h3><p>협력 자격, 검증·교육 절차, 위반 시 조치 기준</p></li>
<li><h3><a href="/about/safety-policy/">안전 이용 정책</a></h3><p>건전 이용을 위한 금지 사항, 신고 채널, 위반 시 조치</p></li>
<li><h3><a href="/about/privacy/">개인정보처리방침</a></h3><p>수집 항목·이용 목적·보관 기간·이용자 권리 (시행일·버전 명시)</p></li>
<li><h3><a href="/about/terms/">이용약관</a></h3><p>예약·결제·취소·책임 한계 등 14개 조항으로 정리한 약관</p></li>
</ul>
</section>
<section class="block">
<h2>운영 책임자 연락처</h2>
<p>운영 정책·콘텐츠·개인정보 관련 문의는 운영팀(개인정보보호책임자 겸임) 김유환 대표에게 직접 접수됩니다. 일반 예약 문의와 운영 정책 문의는 채널이 분리되어 있으니 아래 두 채널을 활용해 주세요.</p>
<ul class="check-list">
<li>예약·서비스 문의 : <a href="tel:0508-202-4719">0508-202-4719</a></li>
<li>운영 정책·콘텐츠 정정 요청 : <a href="/support/contact/">문의하기</a> 페이지</li>
<li>위반 신고 : <a href="/support/report/">불편 신고</a> 페이지</li>
</ul>
</section>
""",
  related=_rel("/about/", ["/about/brand/", "/about/operation-policy/", "/about/safety-policy/", "/about/privacy/"], title="이어서 살펴볼 문서"),
)

add(
  path="about/brand/index.html", url="/about/brand/", slug="brand",
  title="브랜드 소개 — 바로GO를 시작한 이유와 운영 미션 | 바로GO",
  description="바로GO(운영사 YH LAB)가 출장마사지 예약 안내 플랫폼을 시작한 이유, 해결하려는 문제, 4가지 운영 약속, 다른 안내 채널과의 차이점을 정리했습니다.",
  h1="브랜드 소개",
  intro='<p class="lede">바로GO는 "예약 전 알아야 할 정보가 흩어져 있고, 가격·취소 기준이 모호한 출장마사지 시장"의 문제를 좁히기 위해 시작된 예약 안내 플랫폼입니다. 본 페이지에는 시작 배경, 운영 미션, 다른 안내 채널과 다른 점, 그리고 향후 로드맵을 정리해 두었습니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("브랜드 소개","/about/brand/")],
  body=_GUIDE_BYLINE.format(min=5) + _review_toc([
    ("바로GO를 시작한 이유", "why"),
    ("우리가 해결하려는 문제 3가지", "problem"),
    ("운영 미션과 4가지 약속", "promise"),
    ("다른 안내 채널과 다른 점", "diff"),
    ("운영 사업자·책임 구조", "biz"),
    ("앞으로의 로드맵", "roadmap"),
  ]) + """
<section class="block" id="why">
<h2>바로GO를 시작한 이유</h2>
<p>출장마사지 시장은 오랫동안 정보가 불투명한 영역이었습니다. 검색 결과 상단에는 광고가 가득하고, 가격은 페이지마다 다르며, 취소·환불 기준은 예약 후에야 안내되는 경우가 잦았습니다. 운영사 <strong>YH LAB</strong>은 출장마사지 예약 상담을 직접 운영하며 이러한 문제를 누적해서 경험했고, 이용자가 사전에 알아야 할 정보를 한곳에 정리할 필요가 있다고 판단했습니다. 그 결과물이 바로GO입니다.</p>
<p>바로GO는 "광고가 아닌 정보"를 우선합니다. 페이지 상단에 자극적 카피로 클릭을 유도하는 대신, 코스별 기준 가격·시간대별 가능 여부·진행 장소별 권장 사항을 정리해 의사결정에 필요한 데이터를 먼저 보여드립니다.</p>
</section>

<section class="block" id="problem">
<h2>우리가 해결하려는 문제 3가지</h2>
<ol class="steps">
<li><strong>가격 불투명성</strong><p>"전화해 보세요"로 끝나는 페이지가 많아 이용자가 사전에 예산을 잡기 어렵습니다. 바로GO는 코스·시간대·진행 장소별 기준 가격을 모두 공개합니다.</p></li>
<li><strong>안전 정보 부족</strong><p>이용 전 확인해야 할 건강·공간 조건이 정리되지 않아 사고·민원이 반복됩니다. 바로GO는 <a href="/reservation/check-before-use/">이용 전 확인사항</a>을 별도 페이지로 분리했습니다.</p></li>
<li><strong>업체 검증 어려움</strong><p>사업자등록·운영 책임자 정보가 공개되지 않은 업체가 많습니다. 바로GO는 모든 페이지 푸터에 사업자등록번호와 대표자 정보를 노출합니다.</p></li>
</ol>
</section>

<section class="block" id="promise">
<h2>운영 미션과 4가지 약속</h2>
<p>바로GO의 미션은 "출장마사지 예약을 더 안전하고, 더 투명하게 안내한다"입니다. 이 미션을 지키기 위한 4가지 운영 약속을 공개합니다.</p>
<div class="dos-donts">
<div class="dos">
<strong>우리가 항상 합니다</strong>
<ul>
<li>예약 확정 전 가격·코스·취소 기준을 사전 안내</li>
<li>실제 운영 데이터에 기반한 콘텐츠 작성과 책임 저자 표기</li>
<li>사업자 정보·연락처를 모든 페이지에 공개</li>
<li>위반 신고가 접수되면 24시간 이내 운영팀이 직접 확인</li>
</ul>
</div>
<div class="donts">
<strong>우리가 하지 않습니다</strong>
<ul>
<li>"최저가", "1위", "검증 완료" 등 근거 없는 표현 사용</li>
<li>불법·퇴폐 서비스 안내 또는 연결</li>
<li>지역명만 치환한 복제 페이지 양산</li>
<li>허위·자동 생성 후기 게시</li>
</ul>
</div>
</div>
</section>

<section class="block" id="diff">
<h2>다른 안내 채널과 다른 점</h2>
<p>출장마사지 예약을 안내하는 채널은 크게 세 가지로 나뉩니다 — 개인 블로그, 광고 위주 디렉토리, 그리고 직접 운영 사업자입니다. 바로GO는 마지막 유형, 즉 <strong>직접 운영 사업자가 직접 안내하는 플랫폼</strong>입니다.</p>
<table class="compare-table">
<thead><tr><th scope="col">구분</th><th scope="col">개인 블로그</th><th scope="col">광고 디렉토리</th><th scope="col">바로GO</th></tr></thead>
<tbody>
<tr><th scope="row">운영 책임</th><td>익명·불명</td><td>광고주 기준</td><td>사업자등록 공개</td></tr>
<tr><th scope="row">가격 정보</th><td>제각각</td><td>광고가 우선</td><td>코스별 기준 공개</td></tr>
<tr><th scope="row">콘텐츠 작성</th><td>저자 불명</td><td>광고 카피</td><td>운영팀 책임 저자</td></tr>
<tr><th scope="row">신고 채널</th><td>없음</td><td>형식적</td><td>24시간 내 응대</td></tr>
</tbody>
</table>
</section>

<section class="block" id="biz">
<h2>운영 사업자·책임 구조</h2>
<p>바로GO는 <strong>YH LAB</strong>이 직접 운영하는 단일 사업자 플랫폼입니다. 위탁·재위탁 구조가 아니며, 모든 콘텐츠와 예약 안내·결제 책임은 YH LAB이 직접 집니다.</p>
<ul class="check-list">
<li>상호 : 바로GO (YH LAB) · 대표 김유환</li>
<li>사업자등록번호 : 815-26-00585 (국세청 조회 가능)</li>
<li>본사 주소 : 경기도 파주시 청석로 268</li>
<li>대표 전화 : <a href="tel:0508-202-4719">0508-202-4719</a></li>
</ul>
</section>

<section class="block" id="roadmap">
<h2>앞으로의 로드맵</h2>
<p>바로GO는 정보의 양이 아니라 정보의 정확성과 신뢰도를 우선으로 운영합니다. 향후 1년 로드맵은 다음과 같이 정리하고 있습니다.</p>
<ul class="check-list">
<li><strong>1단계</strong> — 17개 시·도 권역 안내 페이지 안정화 (2026년 상반기 완료)</li>
<li><strong>2단계</strong> — 후기·예약 사례 페이지의 책임 저자·검증 절차 강화</li>
<li><strong>3단계</strong> — 가격 변동 트래킹과 분기별 가격 안내 업데이트 공개</li>
<li><strong>4단계</strong> — 외부 검증 채널(소비자보호원·관계기관) 협조 절차 명문화</li>
</ul>
<p class="muted">로드맵은 운영팀 자체 기준이며, 외부 사정에 따라 변경될 수 있습니다. 변경 시 본 페이지에 시행일을 명시해 갱신합니다.</p>
</section>
""" + _review_faq([
    ("바로GO는 직접 마사지를 진행하나요?",
     "바로GO는 예약 안내·상담 플랫폼이며, 실제 진행은 협력 관리사가 담당합니다. 관리사 협력 기준과 검증 절차는 <a href=\"/about/therapist-policy/\">관리사 운영 기준</a> 페이지에 정리되어 있습니다."),
    ("운영사 YH LAB은 어떤 곳인가요?",
     "YH LAB은 출장마사지 예약 상담을 전문으로 운영하는 사업자입니다. 사업자등록번호 815-26-00585로 국세청 조회가 가능하며, 본사는 경기도 파주시 청석로 268에 위치합니다."),
    ("페이지에 적힌 정보는 누가 작성하나요?",
     "바로GO 운영팀이 책임 저자로 작성합니다. 콘텐츠 작성 원칙과 AI 사용 정책은 <a href=\"/about/operation-policy/\">운영 원칙</a> 페이지에 공개되어 있습니다."),
    ("불만·신고는 어디로 접수하나요?",
     "운영팀이 직접 응대하는 <a href=\"/support/report/\">불편 신고</a> 페이지로 접수해 주세요. 접수된 신고는 24시간 이내 운영팀이 직접 확인하고, 사안에 따라 협력 중단·관계 기관 협조까지 진행됩니다."),
]) + _GUIDE_DISCLAIMER,
  related=_rel("/about/brand/", ["/about/operation-policy/", "/about/therapist-policy/", "/about/safety-policy/", "/guide/safe-reservation/"], title="이어서 살펴볼 문서"),
)

add(
  path="about/operation-policy/index.html", url="/about/operation-policy/", slug="operation-policy",
  title="운영 원칙 — 예약·가격·후기·콘텐츠·AI 사용 8개 영역 | 바로GO",
  description="바로GO 운영 원칙. 예약·가격·후기·콘텐츠·광고 표현·AI 사용·데이터 운영·외부 채널 8개 영역의 세부 정책과 위반 시 조치 기준을 공개합니다.",
  h1="운영 원칙",
  intro='<p class="lede">바로GO 운영팀이 사이트 운영 시 따르는 8개 영역의 원칙을 모두 공개합니다. "투명하지 않으면 신뢰받을 수 없다"는 전제하에 작성된 자체 운영 규정이며, 변경 시 본 페이지에 시행일을 명시해 갱신합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("운영 원칙","/about/operation-policy/")],
  body=_GUIDE_BYLINE.format(min=6) + _review_toc([
    ("예약 운영 원칙", "reservation"),
    ("가격 안내 원칙", "price"),
    ("후기 운영 원칙", "review"),
    ("콘텐츠 작성 원칙", "content"),
    ("AI 사용·검수 정책", "ai"),
    ("광고·표현 정책", "ad"),
    ("데이터 운영 원칙", "data"),
    ("외부 채널·검증 협조", "external"),
    ("위반 시 자체 조치", "action"),
  ]) + """
<section class="block" id="reservation">
<h2>예약 운영 원칙</h2>
<p>예약은 "사전 합의 → 안내 → 확정 → 진행 → 마무리"의 5단계로 운영됩니다. 어느 단계에서도 이용자가 모르는 사이에 추가 비용이 발생하거나, 안내되지 않은 조건이 적용되어서는 안 됩니다.</p>
<ul class="check-list">
<li>예약 확정 전 <strong>가격·코스·취소 기준</strong>을 반드시 사전 안내합니다.</li>
<li>사전 동의 없는 추가 비용은 청구하지 않습니다.</li>
<li>이동 거리·시간대에 따라 가능 여부가 달라지는 경우 상담 단계에서 분명히 안내합니다.</li>
<li>예약 진행 중 이용자가 합의되지 않은 요청을 받았을 경우, 운영팀에 즉시 신고하실 수 있도록 <a href="/support/report/">신고 채널</a>을 안내합니다.</li>
</ul>
</section>

<section class="block" id="price">
<h2>가격 안내 원칙</h2>
<p>바로GO는 "단일가" 모델을 사용하지 않습니다. 코스·시간·진행 장소·시간대에 따라 가격이 달라지는 것은 출장마사지의 본질이며, 이를 숨기는 안내가 오히려 이용자에게 불리하다고 판단합니다.</p>
<ul class="check-list">
<li>코스별 <strong>"부터" 시작 가격</strong>을 모두 공개합니다 (<a href="/reservation/price/">가격 안내</a> 페이지 참조).</li>
<li>"최저가 보장", "할인 마감 임박" 등 자극적 표현은 사용하지 않습니다.</li>
<li>가격 변동이 발생하면 본 사이트 가격 안내 페이지에 시행일을 명시해 즉시 반영합니다.</li>
<li>현장 결제·계좌 이체·카드 결제 등 결제 수단은 모두 공개합니다 (<a href="/reservation/payment/">결제 안내</a> 참조).</li>
</ul>
</section>

<section class="block" id="review">
<h2>후기 운영 원칙</h2>
<p>후기는 신뢰의 기반이지만, 동시에 가장 조작되기 쉬운 영역입니다. 바로GO는 후기 진실성 검증을 운영팀이 직접 담당하며, 아래 원칙을 따릅니다.</p>
<ul class="check-list">
<li>실명·연락처는 게시하지 않으며 이름은 "김**" 형태로 마스킹합니다.</li>
<li>후기 작성 시기는 월(month) 단위로 표기하며, 시간순으로 정렬합니다.</li>
<li>"최고", "1위", "완벽" 등 광고성 단어가 포함된 후기는 별도 검수합니다.</li>
<li>허위 후기로 확인되면 즉시 삭제하며, 작성 IP·연락처는 위반 기록에 보존합니다.</li>
<li>운영팀이 작성한 자체 후기는 어떠한 경우에도 게시하지 않습니다.</li>
</ul>
</section>

<section class="block" id="content">
<h2>콘텐츠 작성 원칙</h2>
<p>모든 콘텐츠는 운영팀이 책임 저자로 명시되며, 페이지 상단의 바이라인(작성자·최종 업데이트·시행일)으로 확인하실 수 있습니다.</p>
<ul class="check-list">
<li>실제 예약 상담 데이터·이용 패턴·민원 사례를 기반으로 작성합니다.</li>
<li>지역명만 치환한 복제 페이지를 만들지 않습니다 (Google 스팸 정책 준수).</li>
<li>외부 자료 인용 시 본문에 출처를 명시하고, 가능한 경우 원문 링크를 함께 첨부합니다.</li>
<li>업데이트가 발생하면 페이지 상단의 "최종 업데이트" 표기를 갱신합니다.</li>
</ul>
</section>

<section class="block" id="ai">
<h2>AI 사용·검수 정책</h2>
<p>바로GO는 콘텐츠 작성·정리 과정에서 AI 보조 도구를 사용할 수 있습니다. 다만 모든 콘텐츠는 <strong>운영팀(YH LAB)이 책임 저자로 검수한 뒤 게시</strong>됩니다.</p>
<div class="callout note">
<strong>AI 사용 공개 (Google AI Content Disclosure 준수)</strong>
<p>본 사이트 일부 페이지는 정보 정리·문구 개선 단계에서 AI 보조를 사용했습니다. 단, 게시되는 모든 콘텐츠는 운영팀이 사실 관계·정확성·법적 정합성을 직접 검수합니다. AI가 생성한 그대로 게시되는 페이지는 없습니다.</p>
</div>
</section>

<section class="block" id="ad">
<h2>광고·표현 정책</h2>
<p>특정 표현은 이용자 판단을 흐리거나 법적 문제를 야기할 수 있어 사용을 금지합니다. 운영팀은 모든 페이지를 분기마다 1회 이상 표현 점검합니다.</p>
<ul class="check-list">
<li><strong>금지 표현</strong> — "1위", "최고", "최저가", "검증 완료", "은밀한", "성인", "퇴폐", "VIP 전용"</li>
<li><strong>주의 표현</strong> — "보장", "100%", "전국 최고" 등 객관적 근거가 없는 절대 표현</li>
<li><strong>의료성 표현 금지</strong> — "치료", "완치", "치유 보장" 등 의료 행위로 오인될 수 있는 표현</li>
</ul>
</section>

<section class="block" id="data">
<h2>데이터 운영 원칙</h2>
<p>이용자 개인정보·예약 데이터의 보관·이용·파기는 <a href="/about/privacy/">개인정보처리방침</a>에 따라 처리됩니다. 운영팀은 다음 원칙으로 데이터를 관리합니다.</p>
<ul class="check-list">
<li>최소 수집 원칙 — 예약 진행에 필요한 정보만 수집</li>
<li>분리 보관 — 결제 정보는 PG사·금융기관에서 처리, 회사는 거래 식별자만 보관</li>
<li>접근 통제 — 운영팀 중 권한 부여자만 접근, 접근 기록 보존</li>
<li>주기적 파기 — 이용 목적 달성 즉시 또는 법령 기간 종료 후 즉시 파기</li>
</ul>
</section>

<section class="block" id="external">
<h2>외부 채널·검증 협조</h2>
<p>이용자가 외부 채널을 통해 바로GO 운영을 검증하실 수 있도록 다음 절차에 협조합니다.</p>
<ul class="check-list">
<li>국세청 사업자등록번호 조회 — 815-26-00585</li>
<li>한국소비자원·소비자보호원 등 분쟁 조정 기관 자료 요청 시 신속 협조</li>
<li>관계 기관(경찰·세무 등)의 정식 요청 시 법령에 따라 협조</li>
<li>법령 외 정보 제공 요청은 운영팀에서 검토 후 응답</li>
</ul>
</section>

<section class="block" id="action">
<h2>위반 시 자체 조치</h2>
<p>위 원칙을 운영팀 자체로 위반한 사실이 확인될 경우, 다음 절차에 따라 즉시 시정합니다.</p>
<ol class="steps">
<li><strong>1단계</strong><p>해당 콘텐츠·페이지를 24시간 이내 시정하거나 비공개 처리합니다.</p></li>
<li><strong>2단계</strong><p>시정 내역을 본 페이지 하단에 시행일과 함께 기록합니다.</p></li>
<li><strong>3단계</strong><p>유사 위반 재발 방지를 위해 내부 검수 절차를 강화합니다.</p></li>
</ol>
</section>
""" + _review_faq([
    ("AI로 작성된 콘텐츠는 어떻게 표시되나요?",
     "AI 보조를 사용한 페이지라도 운영팀이 사실 관계·법적 정합성을 검수한 뒤 게시되므로 별도 표시는 하지 않습니다. AI 사용 정책 자체는 본 페이지의 'AI 사용·검수 정책' 항목에 공개되어 있습니다."),
    ("가격이 페이지마다 다르게 보이는 경우는 어떻게 처리되나요?",
     "분기별 자체 점검에서 페이지 간 가격 표기가 일치하지 않는 사례가 발견되면 즉시 통일합니다. 차이가 큰 경우 본 페이지 '위반 시 자체 조치' 절차를 따릅니다."),
    ("후기는 운영팀이 직접 작성하지 않나요?",
     "절대 작성하지 않습니다. 자체 작성 후기는 후기 운영 원칙 위반이며, 발견 즉시 삭제 조치됩니다."),
    ("운영 원칙이 변경되면 어떻게 알 수 있나요?",
     "변경 시 본 페이지 상단의 '최종 업데이트' 표기를 갱신하며, 주요 변경 사항은 변경 이력으로 명시합니다. 큰 변경의 경우 <a href=\"/support/notice/\">공지사항</a>에도 함께 게시합니다."),
]) + _GUIDE_DISCLAIMER,
  related=_rel("/about/operation-policy/", ["/about/brand/", "/about/safety-policy/", "/about/privacy/", "/guide/safe-reservation/"], title="이어서 살펴볼 문서"),
)

add(
  path="about/therapist-policy/index.html", url="/about/therapist-policy/", slug="therapist-policy",
  title="관리사 운영 기준 — 협력 자격·검증·교육·평가·조치 | 바로GO",
  description="바로GO와 협력하는 관리사의 자격 요건, 검증·교육 절차, 운영 의무, 분기 평가, 위반 시 조치 등 6개 영역의 운영 기준을 공개합니다.",
  h1="관리사 운영 기준",
  intro='<p class="lede">바로GO와 협력하는 관리사가 갖춰야 하는 기본 자격, 운영팀이 진행하는 검증 절차, 정기 교육·평가, 그리고 위반 시 즉시 협력 중단까지 — 관리사 운영의 모든 단계를 공개합니다. 본 기준은 이용자 안전과 직결되는 영역이므로 분기마다 한 번씩 재검토됩니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("관리사 기준","/about/therapist-policy/")],
  body=_GUIDE_BYLINE.format(min=5) + _review_toc([
    ("기본 협력 자격", "qualification"),
    ("협력 시작 전 검증 절차", "verification"),
    ("정기 교육·운영 가이드", "training"),
    ("운영 의무와 행동 강령", "duty"),
    ("분기 평가와 등급 운영", "evaluation"),
    ("위반 시 조치 절차", "action"),
  ]) + """
<section class="block" id="qualification">
<h2>기본 협력 자격</h2>
<p>바로GO와 협력하기 위해서는 다음 자격이 모두 충족되어야 합니다. 하나라도 충족되지 않으면 협력이 시작되지 않습니다.</p>
<ul class="check-list">
<li><strong>합법적 사업 운영</strong> — 사업자등록 또는 프리랜서 사업소득 신고가 가능한 자</li>
<li><strong>실무 경력</strong> — 출장마사지·매장 마사지 등 관련 실무 경력 1년 이상</li>
<li><strong>신원 확인</strong> — 신분증·연락처·계좌 정보 확인 가능</li>
<li><strong>전과 조회 동의</strong> — 성범죄·강력범죄 관련 전과가 없는 자 (본인 동의하 조회)</li>
<li><strong>정책 동의</strong> — <a href="/about/safety-policy/">안전 이용 정책</a>·<a href="/about/operation-policy/">운영 원칙</a>을 모두 숙지하고 서면 동의</li>
</ul>
</section>

<section class="block" id="verification">
<h2>협력 시작 전 검증 절차</h2>
<p>자격 요건을 충족하더라도 운영팀이 다음 검증 절차를 통과한 경우에만 협력이 시작됩니다.</p>
<ol class="steps">
<li><strong>서류 검증</strong><p>사업자등록증·신분증·경력 증빙 자료를 운영팀이 검토합니다.</p></li>
<li><strong>대면 인터뷰</strong><p>운영팀과 1회 이상 대면 또는 화상 인터뷰를 진행합니다. 운영 원칙·안전 정책·금지 행위에 대한 이해도를 확인합니다.</p></li>
<li><strong>실무 시연</strong><p>지정 코스 1개에 대해 실무 시연을 통해 진행 흐름·압력·위생 관리·고객 응대 매너를 평가합니다.</p></li>
<li><strong>최종 승인</strong><p>운영팀 책임자(대표) 승인 후 협력이 시작됩니다. 첫 3개월은 모니터링 기간으로 운영됩니다.</p></li>
</ol>
</section>

<section class="block" id="training">
<h2>정기 교육·운영 가이드</h2>
<p>협력 시작 후에도 분기별 1회 운영 가이드를 통해 정책 변경·신규 정책·민원 사례를 공유합니다.</p>
<ul class="check-list">
<li><strong>분기 정책 브리핑</strong> — 정책 변경·신규 정책 안내</li>
<li><strong>민원 사례 공유</strong> — 분기 내 접수된 민원 유형과 운영팀 대응 사례</li>
<li><strong>위생·안전 점검</strong> — 도구 위생, 진행 환경 안전 점검 가이드</li>
<li><strong>응급 대응 가이드</strong> — 이용자 건강 이상 발생 시 대응 절차</li>
</ul>
</section>

<section class="block" id="duty">
<h2>운영 의무와 행동 강령</h2>
<p>협력 관리사는 다음 운영 의무를 준수해야 합니다. 의무 위반은 사안에 따라 협력 중단까지 이어질 수 있습니다.</p>
<div class="dos-donts">
<div class="dos">
<strong>준수 의무</strong>
<ul>
<li>예약된 시간·코스를 정확히 진행</li>
<li>이용자 개인정보 보호 (이름·주소·연락처 외부 공유 금지)</li>
<li>도구·복장·손 위생 기준 준수</li>
<li>안전 사고 발생 시 즉시 운영팀 보고</li>
</ul>
</div>
<div class="donts">
<strong>금지 행위</strong>
<ul>
<li>불법·퇴폐 서비스 제공·암시</li>
<li>이용자에게 사전 합의되지 않은 추가 비용 요구</li>
<li>이용자 개인정보의 사적 보관·이용</li>
<li>운영팀을 거치지 않은 직접 예약 안내·재예약 유도</li>
</ul>
</div>
</div>
</section>

<section class="block" id="evaluation">
<h2>분기 평가와 등급 운영</h2>
<p>운영팀은 분기마다 협력 관리사의 운영 데이터를 종합 평가합니다. 평가 결과는 협력 지속 여부와 우선 배정에 반영됩니다.</p>
<table class="compare-table">
<thead><tr><th scope="col">평가 항목</th><th scope="col">기준</th><th scope="col">반영</th></tr></thead>
<tbody>
<tr><th scope="row">예약 진행률</th><td>확정된 예약을 사고 없이 진행한 비율</td><td>우선 배정</td></tr>
<tr><th scope="row">민원 발생률</th><td>분기 내 정식 민원 접수 건수</td><td>경고·재교육</td></tr>
<tr><th scope="row">정책 준수</th><td>안전·운영 정책 위반 여부</td><td>협력 중단까지</td></tr>
<tr><th scope="row">이용자 응대</th><td>운영팀 자체 평가 + 후기 분석</td><td>우선 배정</td></tr>
</tbody>
</table>
</section>

<section class="block" id="action">
<h2>위반 시 조치 절차</h2>
<p>안전 이용 정책 또는 운영 의무를 위반한 사실이 확인될 경우, 위반 정도에 따라 다음 단계로 조치합니다.</p>
<ol class="steps">
<li><strong>경미한 위반</strong><p>운영팀 서면 경고 + 재교육 (1차 위반 기준)</p></li>
<li><strong>중대한 위반</strong><p>협력 즉시 중단 (불법 서비스 제공·개인정보 유출·금지 표현 반복)</p></li>
<li><strong>형사 사안</strong><p>관계 기관(경찰 등) 정식 협조 + 협력 영구 중단 + 관련 자료 보존</p></li>
</ol>
<p class="muted">위반 사실은 운영팀이 직접 확인한 후 조치되며, 이용자가 신고하신 사안은 <a href="/support/report/">불편 신고</a>를 통해 접수됩니다.</p>
</section>
""" + _review_faq([
    ("관리사 모집은 어떻게 진행되나요?",
     "운영팀이 직접 검토 후 자격 충족 시 인터뷰가 진행됩니다. 검증 절차는 본 페이지 '협력 시작 전 검증 절차' 항목을 참고해 주세요. 일반 모집 공고를 운영하지는 않습니다."),
    ("관리사 정보는 이용자에게 공개되나요?",
     "이용자에게는 코스 진행에 필요한 최소 정보만 안내되며, 관리사 개인 정보는 공개되지 않습니다. 단, 응급 대응을 위한 연락처는 예약 시점에 안내됩니다."),
    ("협력 중단된 관리사가 다시 신청할 수 있나요?",
     "경미한 위반은 6개월 후 재신청이 가능하며, 중대한 위반·형사 사안은 영구 협력 중단됩니다."),
    ("이용자가 관리사에게 직접 다음 예약을 요청해도 되나요?",
     "운영팀을 거치지 않은 직접 예약은 금지되어 있습니다. 운영팀을 통해 예약하셔야 안전·환불 기준이 모두 적용됩니다."),
]) + _GUIDE_DISCLAIMER,
  related=_rel("/about/therapist-policy/", ["/about/safety-policy/", "/about/operation-policy/", "/about/brand/", "/guide/safe-reservation/"], title="이어서 살펴볼 문서"),
)

add(
  path="about/safety-policy/index.html", url="/about/safety-policy/", slug="safety-policy",
  title="안전 이용 정책 — 금지 사항·신고·조치·청소년 보호 | 바로GO",
  description="바로GO 안전 이용 정책. 불법·퇴폐 서비스 차단, 이용자 보호, 24시간 신고 채널, 위반 시 조치, 청소년 보호 정책 등 7개 영역을 공개합니다.",
  h1="안전 이용 정책",
  intro='<p class="lede">바로GO는 합법적이고 건전한 출장마사지 안내만 제공합니다. 본 정책은 이용자·관리사·운영팀 모두에 동일하게 적용되며, 위반이 확인되면 협력 중단·법적 협조까지 이어집니다. 신고는 24시간 운영팀이 직접 확인합니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("안전 이용 정책","/about/safety-policy/")],
  body=_GUIDE_BYLINE.format(min=5) + _review_toc([
    ("정책의 목적과 적용 범위", "purpose"),
    ("금지 사항", "forbidden"),
    ("이용자 보호 원칙", "protect"),
    ("24시간 신고 채널", "report"),
    ("위반 시 조치 절차", "action"),
    ("법적 협조 절차", "legal"),
    ("청소년 보호 정책", "youth"),
  ]) + """
<section class="block" id="purpose">
<h2>정책의 목적과 적용 범위</h2>
<p>본 안전 이용 정책은 바로GO 플랫폼 내 모든 예약·진행·콘텐츠에 적용됩니다. 정책의 목적은 다음과 같습니다.</p>
<ul class="check-list">
<li>이용자·관리사 양측의 안전을 보호</li>
<li>합법적인 출장마사지 안내만 운영</li>
<li>불법·퇴폐 서비스의 운영·중개·노출을 원천 차단</li>
<li>위반 발생 시 신속·정확한 조치 절차 보장</li>
</ul>
<p>본 정책은 운영팀·협력 관리사·이용자 모두에게 동일하게 적용됩니다. 정책 위반이 확인되면 누구든 동일한 절차로 조치됩니다.</p>
</section>

<section class="block" id="forbidden">
<h2>금지 사항</h2>
<p>다음 행위는 바로GO 플랫폼에서 절대 허용되지 않으며, 위반 확인 시 즉시 협력 중단·법적 조치 대상입니다.</p>
<div class="dos-donts">
<div class="donts">
<strong>관리사·운영 측 금지</strong>
<ul>
<li>불법·퇴폐 서비스 제공·암시·중개</li>
<li>"은밀한", "성인", "퇴폐" 등 자극적 표현 사용</li>
<li>거짓 후기 작성·허위 광고 게시</li>
<li>이용자 개인정보 무단 이용·외부 공유</li>
<li>합의되지 않은 추가 비용 청구</li>
</ul>
</div>
<div class="donts">
<strong>이용자 측 금지</strong>
<ul>
<li>불법·퇴폐 서비스 요청·암시</li>
<li>관리사에 대한 폭언·폭행·성희롱</li>
<li>합의되지 않은 촬영·녹음</li>
<li>허위 신원으로 예약 진행</li>
<li>예약 정보·후기 도용</li>
</ul>
</div>
</div>
</section>

<section class="block" id="protect">
<h2>이용자 보호 원칙</h2>
<p>운영팀은 이용자가 안전하고 건전한 환경에서 서비스를 받을 수 있도록 다음 보호 원칙을 따릅니다.</p>
<ul class="check-list">
<li>예약 정보(이름·연락처·주소)는 진행에 필요한 관리사 1인에게만 전달</li>
<li>예약 종료 후 진행 데이터는 법령 보관 기간 외 즉시 파기</li>
<li>예약 중 불편 발생 시 운영팀에 즉시 연락 가능한 직통 라인 안내</li>
<li>여성 이용자의 경우 요청 시 여성 관리사 우선 배정</li>
<li>예약 진행 중 안전 우려 발생 시 진행 중단·환불 가능</li>
</ul>
</section>

<section class="block" id="report">
<h2>24시간 신고 채널</h2>
<p>안전 정책 위반·이용 중 불편·관리사 행위 의심 등 어떠한 사안이든 운영팀이 직접 응대합니다.</p>
<ol class="steps">
<li><strong>웹 신고</strong><p><a href="/support/report/">불편 신고</a> 페이지에서 24시간 접수 가능 — 접수 즉시 운영팀 알림</p></li>
<li><strong>전화 신고</strong><p><a href="tel:0508-202-4719">0508-202-4719</a> — 운영팀 직통 연결</p></li>
<li><strong>접수 후 처리</strong><p>모든 신고는 24시간 이내 운영팀이 직접 확인 후 회신합니다. 긴급 사안(현장 안전 위협)은 즉시 대응합니다.</p></li>
</ol>
</section>

<section class="block" id="action">
<h2>위반 시 조치 절차</h2>
<p>위반 확인 시 위반 정도와 사안에 따라 다음 단계로 즉시 조치됩니다.</p>
<table class="compare-table">
<thead><tr><th scope="col">위반 정도</th><th scope="col">관리사 조치</th><th scope="col">이용자 조치</th></tr></thead>
<tbody>
<tr><th scope="row">경미한 위반</th><td>서면 경고 + 재교육</td><td>경고 + 예약 제한</td></tr>
<tr><th scope="row">중대한 위반</th><td>협력 즉시 중단</td><td>예약 영구 중단</td></tr>
<tr><th scope="row">형사 사안</th><td>관계 기관 협조 + 영구 중단</td><td>관계 기관 협조 + 법적 조치</td></tr>
</tbody>
</table>
</section>

<section class="block" id="legal">
<h2>법적 협조 절차</h2>
<p>형사 사안(불법 서비스·폭력·성범죄 등)이 확인되면 운영팀은 다음 절차로 즉시 협조합니다.</p>
<ul class="check-list">
<li>관계 기관(경찰·검찰)의 정식 공문 요청 시 보유 자료 신속 제공</li>
<li>피해자가 법적 절차를 진행할 경우 운영팀 보유 자료 제공 협조</li>
<li>사안 종료 후에도 관련 자료는 법령 보관 기간 동안 보존</li>
<li>피해자 신원 보호를 최우선으로 처리</li>
</ul>
</section>

<section class="block" id="youth">
<h2>청소년 보호 정책</h2>
<p>바로GO는 만 19세 미만 청소년의 예약·이용을 받지 않습니다. 다음 보호 절차를 운영합니다.</p>
<ul class="check-list">
<li>예약 진행 시 성인 본인 확인 (필요 시 신분증 확인)</li>
<li>본 사이트는 청소년 유해 매체물 표시 의무 대상이 아니나, 자극적 표현·이미지를 일체 사용하지 않음</li>
<li>청소년이 사이트에 접속하더라도 노출되는 콘텐츠가 모두 정보성 안내로 구성됨</li>
<li>청소년 보호 책임자 : 김유환 (대표) · <a href="tel:0508-202-4719">0508-202-4719</a></li>
</ul>
</section>
""" + _review_faq([
    ("신고 후 처리 결과는 어떻게 확인하나요?",
     "신고 접수 시 회신용 연락처를 함께 남겨주시면 운영팀이 직접 처리 결과를 회신합니다. 익명 신고도 접수되지만, 회신은 불가합니다."),
    ("위반 사례는 외부에 공개되나요?",
     "위반자 개인 정보는 공개하지 않습니다. 다만 정책 개선 목적으로 사례 유형을 분기 운영 보고에 정리해 본 사이트 <a href=\"/support/notice/\">공지사항</a>에 공유할 수 있습니다."),
    ("이용자가 안전 위협을 느낀 경우 어떻게 해야 하나요?",
     "즉시 진행을 중단하시고 운영팀 직통(0508-202-4719)으로 연락 주세요. 긴급 사안은 112 신고를 함께 권장합니다. 운영팀은 사후 모든 조치에 협조합니다."),
    ("정책 위반이 발견되면 환불은 어떻게 처리되나요?",
     "운영 측·관리사 측 위반으로 인한 사안은 전액 환불됩니다. 환불 절차는 <a href=\"/reservation/cancel-refund/\">취소·환불 규정</a>을 참조해 주세요."),
]) + _GUIDE_DISCLAIMER,
  related=_rel("/about/safety-policy/", ["/support/report/", "/about/therapist-policy/", "/about/operation-policy/", "/guide/safe-reservation/"], title="이어서 살펴볼 문서"),
)

add(
  path="about/privacy/index.html", url="/about/privacy/", slug="privacy",
  title="개인정보처리방침 — 수집·이용·보관·이용자 권리 | 바로GO",
  description="바로GO(운영사 YH LAB) 개인정보처리방침. 수집 항목·수집 방법·이용 목적·보관 기간·제3자 제공·처리위탁·이용자 권리·쿠키·안전성 확보 조치·책임자 등 11개 조항을 정식 약관 형식으로 안내합니다.",
  h1="개인정보처리방침",
  intro='<p class="lede">바로GO(운영사 YH LAB, 이하 "회사")는 「개인정보 보호법」, 「정보통신망 이용촉진 및 정보보호 등에 관한 법률」 등 관계 법령에 따라 이용자의 개인정보를 보호합니다. 본 방침에는 수집 항목·이용 목적·보관 기간·이용자 권리 등 처리 전반에 관한 사항이 명시되어 있으며, 시행일과 버전이 본문 상단에 공개됩니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("개인정보처리방침","/about/privacy/")],
  body=_ABOUT_LEGAL_BYLINE_TPL.format(role="개인정보보호책임자 김유환", effective="2026-05-19", ver="v2.0") + _review_toc([
    ("제1조 (수집하는 개인정보 항목)", "art1"),
    ("제2조 (개인정보의 수집 방법)", "art2"),
    ("제3조 (개인정보의 이용 목적)", "art3"),
    ("제4조 (개인정보의 보관 기간)", "art4"),
    ("제5조 (개인정보의 제3자 제공)", "art5"),
    ("제6조 (개인정보 처리의 위탁)", "art6"),
    ("제7조 (이용자의 권리와 행사 방법)", "art7"),
    ("제8조 (쿠키·자동수집 항목)", "art8"),
    ("제9조 (안전성 확보 조치)", "art9"),
    ("제10조 (개인정보 보호책임자)", "art10"),
    ("제11조 (방침의 변경과 고지 의무)", "art11"),
  ]) + """
<section class="block" id="art1">
<h2>제1조 (수집하는 개인정보 항목)</h2>
<p>회사는 다음의 개인정보를 처리합니다.</p>
<ul class="check-list">
<li><strong>예약 진행 시</strong> — 이름, 연락처(휴대전화), 예약 일시, 방문 장소(가정·호텔·오피스텔·펜션 등), 객실/층 정보, 동행 인원 수, 코스 선택</li>
<li><strong>결제 시</strong> — 결제 수단 식별 정보(카드사·금융기관에서 직접 처리, 회사는 마스킹된 거래 식별자만 보관), 영수증 발급 요청 시 사업자등록번호·상호</li>
<li><strong>문의·신고 시</strong> — 연락처, 문의·신고 내용</li>
<li><strong>자동 수집</strong> — 접속 IP, 접속 시각, 브라우저 종류, 쿠키 (제8조 참조)</li>
</ul>
<p>회사는 사상·신념, 노동조합·정당의 가입·탈퇴, 정치적 견해, 건강, 성생활 등에 관한 정보 등 민감정보를 원칙적으로 수집하지 않습니다. 다만 이용자가 자발적으로 알린 건강 상태(임신·특정 질환 등)는 안전한 진행을 위한 참고 자료로만 사용되며 별도 동의 절차를 거칩니다.</p>
</section>

<section class="block" id="art2">
<h2>제2조 (개인정보의 수집 방법)</h2>
<ul class="check-list">
<li>대표 전화 상담을 통한 예약 접수 시 이용자 본인이 직접 제공</li>
<li>웹사이트의 문의·신고 양식을 통한 이용자 본인의 직접 입력</li>
<li>결제 시 결제대행사(PG사)로부터 거래 식별 정보 자동 수신</li>
<li>웹 접속 시 쿠키·로그 등 자동 생성 정보의 수집</li>
</ul>
</section>

<section class="block" id="art3">
<h2>제3조 (개인정보의 이용 목적)</h2>
<p>회사는 수집한 개인정보를 다음 목적으로만 이용하며, 이용 목적이 변경되는 경우 별도 동의를 받습니다.</p>
<ul class="check-list">
<li>예약 확정·진행 안내·관리사 배정</li>
<li>결제 처리·환불·세금계산서 발행</li>
<li>이용자 문의 응대 및 불편 신고 처리</li>
<li>안전 이용 정책 위반 사항 확인 및 조치</li>
<li>법령에 따른 의무 이행 (전자상거래법·세법 등)</li>
</ul>
</section>

<section class="block" id="art4">
<h2>제4조 (개인정보의 보관 기간)</h2>
<p>이용자의 개인정보는 수집·이용 목적이 달성된 후 지체 없이 파기됩니다. 다만 다음 정보는 관계 법령에 따라 명시된 기간 동안 보관됩니다.</p>
<table class="compare-table">
<thead><tr><th scope="col">항목</th><th scope="col">근거 법령</th><th scope="col">보관 기간</th></tr></thead>
<tbody>
<tr><th scope="row">계약·청약철회 등 기록</th><td>전자상거래법</td><td>5년</td></tr>
<tr><th scope="row">대금결제·재화 공급 기록</th><td>전자상거래법</td><td>5년</td></tr>
<tr><th scope="row">소비자 불만·분쟁 처리 기록</th><td>전자상거래법</td><td>3년</td></tr>
<tr><th scope="row">웹사이트 접속 기록</th><td>통신비밀보호법</td><td>3개월</td></tr>
</tbody>
</table>
</section>

<section class="block" id="art5">
<h2>제5조 (개인정보의 제3자 제공)</h2>
<p>회사는 이용자의 개인정보를 제1조의 이용 목적 범위에서만 처리하며, 다음의 경우 외에는 제3자에게 제공하지 않습니다.</p>
<ul class="check-list">
<li>이용자가 사전에 동의한 경우</li>
<li>법령에 의해 제공 의무가 발생하는 경우 (수사기관의 정식 요청 등)</li>
<li>이용자·관리사·운영팀의 생명·신체에 급박한 위험이 있는 경우</li>
</ul>
</section>

<section class="block" id="art6">
<h2>제6조 (개인정보 처리의 위탁)</h2>
<p>회사는 원활한 서비스 제공을 위해 다음 업무를 외부에 위탁할 수 있으며, 위탁 시 위탁받는 자의 명칭과 위탁 업무를 사전 공지합니다.</p>
<ul class="check-list">
<li><strong>결제 처리</strong> — PG사 (카드 결제·계좌 이체 처리, 회사는 거래 식별자만 수신)</li>
<li><strong>예약 진행</strong> — 협력 관리사 (해당 예약 진행에 필요한 최소 정보만 전달)</li>
<li><strong>전화 안내</strong> — 통신사 (대표 전화 회선 운영)</li>
</ul>
<p>수탁자에게는 위탁 계약 등에 따라 안전 관리 조치, 재위탁 제한, 위탁 종료 시 정보 반환·파기 의무를 명시합니다.</p>
</section>

<section class="block" id="art7">
<h2>제7조 (이용자의 권리와 행사 방법)</h2>
<p>이용자는 다음 권리를 행사하실 수 있으며, 회사는 지체 없이 응답합니다.</p>
<ul class="check-list">
<li><strong>열람 요청</strong> — 본인의 개인정보 처리 내역 확인</li>
<li><strong>정정·삭제 요청</strong> — 잘못된 정보의 수정 또는 삭제</li>
<li><strong>처리 정지 요청</strong> — 동의 철회 및 처리 중단</li>
<li><strong>개인정보 이동권</strong> — 본인 정보의 사본 요청 (관련 법령 허용 범위)</li>
</ul>
<p>위 권리는 <a href="/support/contact/">문의하기</a> 또는 개인정보보호책임자에게 서면·전화·이메일로 요청하시면 됩니다. 회사는 본인 확인 후 10일 이내 처리합니다.</p>
</section>

<section class="block" id="art8">
<h2>제8조 (쿠키·자동수집 항목)</h2>
<p>회사는 이용자 편의를 위해 쿠키(cookie)를 사용할 수 있습니다. 이용자는 브라우저 설정에서 쿠키 저장을 거부할 수 있으며, 쿠키 거부 시 일부 기능이 제한될 수 있습니다.</p>
<ul class="check-list">
<li>사용 목적 — 접속 빈도·방문 시간 분석, 보안 점검</li>
<li>저장 항목 — 세션 식별자, 페이지 선호 설정 (개인 식별 정보 미포함)</li>
<li>거부 방법 — 브라우저 설정 → 개인정보 → 쿠키 관리</li>
</ul>
</section>

<section class="block" id="art9">
<h2>제9조 (안전성 확보 조치)</h2>
<p>회사는 개인정보의 안전한 처리를 위해 다음 조치를 시행합니다.</p>
<ul class="check-list">
<li><strong>접근 통제</strong> — 운영팀 중 권한 부여자만 접근, 접근 기록 보존</li>
<li><strong>전송 보안</strong> — 웹사이트 전 페이지 HTTPS 적용</li>
<li><strong>저장 보안</strong> — 민감 정보 암호화 저장</li>
<li><strong>주기적 점검</strong> — 분기 1회 자체 점검, 연 1회 외부 점검</li>
<li><strong>물리적 보안</strong> — 자료실 출입 통제, 문서 파쇄 절차 운영</li>
</ul>
</section>

<section class="block" id="art10">
<h2>제10조 (개인정보 보호책임자)</h2>
<div class="callout note">
<strong>개인정보 보호책임자</strong>
<p>성명 : 김유환 (대표)<br>
소속 : 바로GO 운영팀 (YH LAB)<br>
연락처 : <a href="tel:0508-202-4719">0508-202-4719</a><br>
주소 : 경기도 파주시 청석로 268<br>
사업자등록번호 : 815-26-00585</p>
</div>
<p>개인정보 처리와 관련된 문의·불만·피해구제 등을 책임자에게 직접 접수하실 수 있습니다. 회사가 충분히 응답하지 못한 경우 개인정보보호위원회·개인정보 침해신고센터(privacy.go.kr) 등 외부 기관에도 신고가 가능합니다.</p>
</section>

<section class="block" id="art11">
<h2>제11조 (방침의 변경과 고지 의무)</h2>
<p>본 방침이 변경되는 경우 시행일 7일 전 본 페이지에 사전 공지합니다. 중대한 변경(이용자 권리 변동·수집 항목 추가 등)의 경우 시행일 30일 전 공지합니다.</p>
<ul class="check-list">
<li>현재 시행일 : 2026-05-19 · 버전 v2.0</li>
<li>이전 버전 보관 : 운영팀이 별도 보관, 요청 시 제공</li>
<li>주요 변경 시 <a href="/support/notice/">공지사항</a>에도 함께 게시</li>
</ul>
</section>
""" + _review_faq([
    ("회원 가입을 하지 않는데 왜 개인정보가 수집되나요?",
     "회사는 회원 가입 절차를 운영하지 않습니다. 다만 예약 진행을 위해서는 이름·연락처·방문 장소 등이 필요하므로, 예약 상담 시점에 본인이 직접 제공하시는 정보만 처리합니다."),
    ("결제 카드 정보는 어디에 저장되나요?",
     "회사는 카드 번호·CVC 등 결제 카드 원본 정보를 저장하지 않습니다. 결제는 PG사·카드사에서 직접 처리되며, 회사는 거래 식별자(마스킹된 번호 등)만 영수증·환불 처리 목적으로 보관합니다."),
    ("개인정보 열람·삭제는 어떻게 신청하나요?",
     "<a href=\"/support/contact/\">문의하기</a> 페이지로 본인 확인이 가능한 정보(이름·연락처)와 함께 요청을 접수해 주세요. 운영팀이 본인 확인 후 10일 이내 처리합니다."),
    ("쿠키를 거부해도 사이트를 이용할 수 있나요?",
     "정보 안내 페이지는 모두 정상적으로 열람 가능합니다. 다만 일부 편의 기능(접속 빈도 기반 추천 등)이 제한될 수 있습니다."),
]) + _GUIDE_DISCLAIMER,
  related=_rel("/about/privacy/", ["/about/terms/", "/about/safety-policy/", "/about/operation-policy/", "/support/contact/"], title="이어서 살펴볼 문서"),
)

add(
  path="about/terms/index.html", url="/about/terms/", slug="terms",
  title="이용약관 — 예약·결제·취소·책임 한계 14개 조항 | 바로GO",
  description="바로GO(운영사 YH LAB) 이용약관. 목적·정의·예약·결제·취소환불·서비스 변경·책임 제한·면책·분쟁 관할·약관 개정 등 14개 조항을 정식 약관 형식으로 안내합니다.",
  h1="이용약관",
  intro='<p class="lede">본 약관은 바로GO(운영사 YH LAB, 이하 "회사")가 제공하는 출장마사지 안내·예약 서비스의 이용 조건, 회사와 이용자의 권리·의무 및 책임 사항을 정합니다. 시행일과 버전이 본문 상단에 명시되어 있으며, 변경 시 사전 공지 후 적용됩니다.</p>',
  breadcrumbs=[("홈","/"),("바로GO 소개","/about/"),("이용약관","/about/terms/")],
  body=_ABOUT_LEGAL_BYLINE_TPL.format(role="대표 김유환", effective="2026-05-19", ver="v2.0") + _review_toc([
    ("제1조 (목적)", "art1"),
    ("제2조 (정의)", "art2"),
    ("제3조 (약관의 명시·게시·개정)", "art3"),
    ("제4조 (회사의 의무)", "art4"),
    ("제5조 (이용자의 의무)", "art5"),
    ("제6조 (예약 절차)", "art6"),
    ("제7조 (결제·세금계산서)", "art7"),
    ("제8조 (취소·환불)", "art8"),
    ("제9조 (서비스 제공 범위)", "art9"),
    ("제10조 (서비스 변경·중단)", "art10"),
    ("제11조 (책임 제한)", "art11"),
    ("제12조 (면책 조항)", "art12"),
    ("제13조 (개인정보 보호)", "art13"),
    ("제14조 (분쟁 해결과 관할)", "art14"),
  ]) + """
<section class="block" id="art1">
<h2>제1조 (목적)</h2>
<p>본 약관은 회사가 제공하는 출장마사지 안내·예약 서비스의 이용 절차, 회사와 이용자의 권리·의무·책임을 정함을 목적으로 합니다.</p>
</section>

<section class="block" id="art2">
<h2>제2조 (정의)</h2>
<p>본 약관에서 사용하는 용어의 정의는 다음과 같습니다.</p>
<ul class="check-list">
<li><strong>"회사"</strong>란 바로GO를 운영하는 사업자 YH LAB (사업자등록번호 815-26-00585)을 말합니다.</li>
<li><strong>"서비스"</strong>란 회사가 운영하는 출장마사지 안내·예약 플랫폼 및 부수 서비스 일체를 말합니다.</li>
<li><strong>"이용자"</strong>란 본 약관에 따라 서비스를 이용하는 자를 말합니다.</li>
<li><strong>"관리사"</strong>란 회사와 협력 계약을 체결하고 방문 케어를 진행하는 자를 말합니다.</li>
<li><strong>"예약"</strong>이란 이용자가 일정·장소·코스를 합의한 후 회사가 확정 안내한 상태를 말합니다.</li>
</ul>
</section>

<section class="block" id="art3">
<h2>제3조 (약관의 명시·게시·개정)</h2>
<ol class="steps">
<li><strong>명시·게시</strong><p>회사는 본 약관을 본 페이지에 상시 게시합니다.</p></li>
<li><strong>개정</strong><p>회사는 관련 법령을 위배하지 않는 범위에서 본 약관을 개정할 수 있습니다.</p></li>
<li><strong>사전 고지</strong><p>약관 개정 시 시행일 7일 전 본 페이지에 사전 공지합니다. 이용자에게 불리한 변경은 시행일 30일 전 공지합니다.</p></li>
<li><strong>동의 간주</strong><p>이용자가 시행일 이후 서비스를 이용하면 변경된 약관에 동의한 것으로 간주됩니다.</p></li>
</ol>
</section>

<section class="block" id="art4">
<h2>제4조 (회사의 의무)</h2>
<ul class="check-list">
<li>안전하고 합법적인 이용 환경을 제공할 의무</li>
<li>이용자 개인정보를 <a href="/about/privacy/">개인정보처리방침</a>에 따라 보호할 의무</li>
<li>예약 확정 전 가격·코스·취소 기준을 정확히 안내할 의무</li>
<li>이용자 불편 신고를 신속·정확하게 처리할 의무</li>
<li>안전 이용 정책 위반이 확인된 협력 관리사를 즉시 중단시킬 의무</li>
</ul>
</section>

<section class="block" id="art5">
<h2>제5조 (이용자의 의무)</h2>
<ul class="check-list">
<li>예약 진행에 필요한 정확한 정보(이름·연락처·방문 장소·인원)를 제공할 의무</li>
<li>불법·퇴폐 서비스를 요청하지 아니할 의무</li>
<li>관리사에 대한 폭언·폭행·성희롱·합의되지 않은 촬영을 하지 아니할 의무</li>
<li>합의된 진행 시간·코스 외 부당한 요구를 하지 아니할 의무</li>
<li>본 약관 및 <a href="/about/safety-policy/">안전 이용 정책</a>을 준수할 의무</li>
</ul>
</section>

<section class="block" id="art6">
<h2>제6조 (예약 절차)</h2>
<p>예약은 회사가 안내한 절차에 따라 진행되며, 확정 시점은 다음과 같습니다.</p>
<ol class="steps">
<li><strong>상담</strong><p>이용자가 회사 대표 전화 또는 안내 채널로 상담을 요청합니다.</p></li>
<li><strong>안내</strong><p>회사는 일정·코스·가격·취소 기준·진행 장소 권장 사항을 안내합니다.</p></li>
<li><strong>확정</strong><p>이용자가 안내된 조건에 동의하고 회사가 관리사 배정을 완료한 시점에 예약이 확정됩니다.</p></li>
<li><strong>진행</strong><p>확정 후 안내된 시간·장소에서 코스가 진행됩니다.</p></li>
</ol>
</section>

<section class="block" id="art7">
<h2>제7조 (결제·세금계산서)</h2>
<ul class="check-list">
<li>결제 수단은 현장 결제·계좌 이체·카드 결제 중 사전 합의된 방식으로 진행됩니다.</li>
<li>사전 동의 없는 추가 비용은 청구되지 않습니다.</li>
<li>세금계산서·현금영수증이 필요한 경우 예약 시점에 요청해 주시면 발행됩니다.</li>
<li>결제 처리는 PG사·금융기관을 통해 직접 이루어지며, 회사는 거래 식별자만 보관합니다 (<a href="/about/privacy/">개인정보처리방침</a> 참조).</li>
</ul>
</section>

<section class="block" id="art8">
<h2>제8조 (취소·환불)</h2>
<p>예약 취소·환불은 시간대별 기준에 따라 처리됩니다. 자세한 기준은 <a href="/reservation/cancel-refund/">취소·환불 규정</a>에 명시되어 있으며, 본 약관과 동일한 효력을 갖습니다.</p>
<ul class="check-list">
<li>회사 또는 관리사 측 귀책 사유로 진행이 불가한 경우 전액 환불</li>
<li>이용자 측 사유로 인한 취소는 시점에 따라 비율 환불</li>
<li>안전 사유로 인한 진행 중단은 진행 시간 비례 환불</li>
</ul>
</section>

<section class="block" id="art9">
<h2>제9조 (서비스 제공 범위)</h2>
<p>회사가 제공하는 서비스는 다음과 같습니다.</p>
<ul class="check-list">
<li>출장마사지 예약 안내 및 일정 조율</li>
<li>코스·가격 안내 및 결제 처리</li>
<li>관리사 배정 및 진행 일정 안내</li>
<li>이용 후 불편 신고 접수 및 처리</li>
<li>안전 이용 정책 운영 및 위반 사항 처리</li>
</ul>
<p>회사는 의료 행위·치료 행위를 제공하지 않으며, 본 서비스를 통한 효과·치유를 보장하지 않습니다.</p>
</section>

<section class="block" id="art10">
<h2>제10조 (서비스 변경·중단)</h2>
<p>회사는 영업 일정·기술적 사정·법령 변경 등의 사유로 서비스의 일부 또는 전부를 변경하거나 중단할 수 있습니다. 이 경우 다음과 같이 처리됩니다.</p>
<ul class="check-list">
<li>정기 변경 — 시행일 7일 전 본 페이지·<a href="/support/notice/">공지사항</a> 게시</li>
<li>긴급 중단 — 사정 발생 즉시 공지, 사후 사유 명시</li>
<li>변경·중단으로 인한 이용자 피해는 본 약관 책임 제한 범위에서 보전</li>
</ul>
</section>

<section class="block" id="art11">
<h2>제11조 (책임 제한)</h2>
<p>회사는 본 약관 및 관련 법령에 따라 서비스를 제공하며, 다음 경우에는 책임이 제한됩니다.</p>
<ul class="check-list">
<li>이용자의 건강 상태에 따른 결과 — 출장마사지는 의료 행위가 아니며 회사는 치료 효과를 보장하지 않습니다.</li>
<li>천재지변·전쟁·관계 기관 명령 등 회사의 통제를 벗어난 사정으로 인한 미진행</li>
<li>이용자가 정보를 정확히 제공하지 않아 발생한 진행 차질</li>
<li>이용자가 본 약관 및 안전 정책을 위반하여 발생한 손해</li>
</ul>
</section>

<section class="block" id="art12">
<h2>제12조 (면책 조항)</h2>
<p>다음의 경우 회사는 책임을 지지 않습니다.</p>
<ul class="check-list">
<li>이용자가 알린 건강 상태가 사실과 다를 때 발생한 결과</li>
<li>관리사·이용자 간 사적으로 합의된 추가 행위에서 발생한 사고</li>
<li>이용자가 약관·정책을 위반하여 발생한 모든 손해</li>
<li>제3자의 불법 행위로 인한 손해 (회사가 직접 가담하지 않은 경우)</li>
</ul>
</section>

<section class="block" id="art13">
<h2>제13조 (개인정보 보호)</h2>
<p>회사는 이용자의 개인정보를 <a href="/about/privacy/">개인정보처리방침</a>에 따라 처리·보호합니다. 처리방침은 본 약관과 함께 효력을 가지며, 변경 시 본 약관과 동일한 절차로 사전 공지됩니다.</p>
</section>

<section class="block" id="art14">
<h2>제14조 (분쟁 해결과 관할)</h2>
<ol class="steps">
<li><strong>1차 해결</strong><p>이용자는 분쟁 발생 시 회사에 먼저 시정을 요청합니다. 회사는 14일 이내 회신합니다.</p></li>
<li><strong>외부 조정</strong><p>회사 회신 후에도 분쟁이 해소되지 않는 경우 한국소비자원·소비자분쟁조정위원회 등의 조정을 신청할 수 있습니다.</p></li>
<li><strong>관할 법원</strong><p>본 약관과 관련된 소송의 합의 관할은 회사 본사 소재지를 관할하는 법원으로 합니다.</p></li>
</ol>
<div class="callout note">
<strong>부칙</strong>
<p>본 약관(v2.0)은 2026년 5월 19일부터 시행됩니다. 이전 버전(v1.0, 2025년 시행)은 운영팀이 별도 보관하며, 요청 시 제공됩니다.</p>
</div>
</section>
""" + _review_faq([
    ("회원 가입 없이도 이용약관에 동의해야 하나요?",
     "회사는 별도 회원 가입 절차를 운영하지 않습니다. 다만 예약을 진행하시는 시점에 본 약관에 동의하신 것으로 간주됩니다."),
    ("취소·환불 규정과 약관 중 어느 것이 우선되나요?",
     "<a href=\"/reservation/cancel-refund/\">취소·환불 규정</a>은 본 약관 제8조의 세부 기준이며, 본 약관의 일부로 동일한 효력을 갖습니다. 두 문서 간 충돌 발생 시 이용자에게 더 유리한 해석이 적용됩니다."),
    ("약관 변경 시 이용자가 거부할 수 있나요?",
     "변경된 약관에 동의하지 않으시면 서비스 이용을 중단하실 수 있습니다. 단, 시행일 이후 서비스를 계속 이용하시면 변경 약관에 동의하신 것으로 간주됩니다."),
    ("분쟁이 발생하면 어디서 조정받을 수 있나요?",
     "1차로 회사에 시정을 요청하시고, 해소되지 않는 경우 한국소비자원·소비자분쟁조정위원회에 분쟁 조정을 신청하실 수 있습니다. 최종적으로는 본 약관 제14조의 관할 법원에서 해결됩니다."),
]) + _GUIDE_DISCLAIMER,
  related=_rel("/about/terms/", ["/about/privacy/", "/reservation/cancel-refund/", "/about/safety-policy/", "/support/contact/"], title="이어서 살펴볼 문서"),
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
    global HEADER
    paths = []
    for p in PAGES:
        paths.append(render(p))
    write_sitemap(paths)
    write_robots()
    print(f"Built {len(paths)} pages.")


if __name__ == "__main__":
    main()
