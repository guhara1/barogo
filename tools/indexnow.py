#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IndexNow 일괄/개별 색인 통보 — 빙·네이버·얀덱스에 URL 변경을 즉시 알린다.

IndexNow 는 한 번의 호출로 참여 검색엔진(Bing·Naver·Yandex·Seznam) 전체에
URL 변경을 통보하는 프로토콜이다. 새 글을 올리거나 페이지를 수정한 뒤
이 스크립트를 실행하면 해당 검색엔진들이 빠르게 재크롤링한다.

사용법
------
  # 1) 사이트맵의 모든 URL 을 일괄 통보 (도메인 이전·최초 등록 시)
  python tools/indexnow.py

  # 2) 특정 글만 통보 (글 하나 올렸을 때 — 가장 흔한 사용)
  python tools/indexnow.py /magazine/new-article/ /magazine/

  # 3) 실제 전송 없이 무엇을 보낼지 미리보기
  python tools/indexnow.py --dry-run

키·도메인은 build.py(SITE_ORIGIN·INDEXNOW_KEY)에서 자동으로 읽으므로
도메인을 바꾸면 이 스크립트도 자동으로 따라간다.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD_PY = ROOT / "build.py"
SITEMAP = ROOT / "sitemap.xml"

# IndexNow 통합 엔드포인트 — 참여 검색엔진 전체로 분배된다.
ENDPOINT = "https://api.indexnow.org/indexnow"
# 한 요청당 최대 URL 수 (프로토콜 권장 상한)
BATCH_SIZE = 10000


def _read_const(name: str) -> str:
    """build.py 에서 따옴표로 둘러싼 상수 값을 추출한다 (무거운 import 회피)."""
    text = BUILD_PY.read_text(encoding="utf-8")
    m = re.search(rf'^{name}\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not m:
        sys.exit(f"build.py 에서 {name} 를 찾지 못했습니다.")
    return m.group(1)


def _sitemap_urls() -> list[str]:
    """sitemap.xml 의 모든 <loc> 절대 URL 을 반환한다."""
    if not SITEMAP.exists():
        sys.exit("sitemap.xml 이 없습니다. 먼저 `python build.py` 를 실행하세요.")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(SITEMAP)
    return [el.text.strip() for el in tree.getroot().findall(".//s:loc", ns) if el.text]


def _normalize(arg: str, origin: str) -> str:
    """CLI 인자를 절대 URL 로 만든다 (전체 URL 또는 / 경로 모두 허용)."""
    if arg.startswith("http://") or arg.startswith("https://"):
        return arg
    return origin.rstrip("/") + "/" + arg.lstrip("/")


def submit(urls: list[str], host: str, key: str, key_location: str) -> None:
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        payload = json.dumps(
            {
                "host": host,
                "key": key,
                "keyLocation": key_location,
                "urlList": batch,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            ENDPOINT,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                code = resp.getcode()
            # 200=즉시 수락, 202=수락(검증 대기). 둘 다 정상.
            print(f"  [{code}] {len(batch)}개 URL 통보 완료")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            print(f"  [HTTP {e.code}] 실패: {body}")
            if e.code == 403:
                print("  → 키 파일이 사이트에 게시됐는지 확인하세요: " + key_location)
        except urllib.error.URLError as e:
            print(f"  [네트워크 오류] {e.reason}")


def main(argv: list[str]) -> None:
    dry = "--dry-run" in argv
    args = [a for a in argv if not a.startswith("--")]

    origin = _read_const("SITE_ORIGIN")                  # https://barogo-1eb.pages.dev
    key = _read_const("INDEXNOW_KEY")
    host = re.sub(r"^https?://", "", origin).strip("/")
    key_location = f"{origin}/{key}.txt"

    if args:
        urls = [_normalize(a, origin) for a in args]
    else:
        urls = _sitemap_urls()

    print(f"도메인 : {host}")
    print(f"키 위치 : {key_location}")
    print(f"대상    : {len(urls)}개 URL")
    if dry:
        for u in urls[:50]:
            print("  ·", u)
        if len(urls) > 50:
            print(f"  … 외 {len(urls) - 50}개")
        print("(--dry-run: 실제 전송하지 않음)")
        return

    submit(urls, host, key, key_location)
    print("완료. 빙·네이버·얀덱스가 곧 재크롤링합니다.")


if __name__ == "__main__":
    main(sys.argv[1:])
