# tools — 색인(인덱싱) 자동화

도메인: **https://barogo-1eb.pages.dev**

## 검색엔진 색인 구성 한눈에

| 채널 | 방식 | 상태 |
|------|------|------|
| **빙·네이버·얀덱스** | IndexNow (즉시 통보) | ✅ `tools/indexnow.py` |
| 전 검색엔진 | `sitemap.xml` + `rss.xml` (절대 URL·우선순위·lastmod) | ✅ build.py 자동 생성 |
| 크롤 허용 | `robots.txt` (봇별 명시 허용 + Host 힌트) | ✅ build.py 자동 생성 |
| 소유확인 | 메인 페이지 `naver-site-verification` / `google-site-verification` 메타 | ✅ |

## IndexNow — 빙·네이버에 즉시 색인 통보

키 파일은 build.py 가 자동 게시한다: `/<key>.txt` 와 `/.well-known/IndexNow`.
키·도메인은 `build.py` 의 `SITE_ORIGIN`·`INDEXNOW_KEY` 에서 자동으로 읽으므로
도메인을 바꾸면 도구도 자동으로 따라간다.

```bash
# 도메인 이전·최초 등록 시 — 사이트맵의 모든 URL 일괄 통보
python tools/indexnow.py

# 글 하나 올렸을 때 — 해당 글만 통보 (가장 흔한 사용)
python tools/indexnow.py /magazine/new-article/ /magazine/

# 미리보기 (실제 전송 안 함)
python tools/indexnow.py --dry-run
```

**새 글 올릴 때 절차**
1. `build.py` 의 `MAGAZINE_ARTICLES` 에 글 추가
2. `python build.py` — 페이지·사이트맵·RSS 재생성
3. `python tools/indexnow.py /magazine/<slug>/ /magazine/` — 빙·네이버에 즉시 통보

## 구글은? (IndexNow 미참여)

구글은 IndexNow 에 참여하지 않는다. 구글 색인은 아래로 처리한다.

- **Search Console 에 사이트 등록 + 사이트맵 제출** — `sitemap.xml` 한 번 제출하면
  구글이 `lastmod` 기준으로 변경분을 재크롤링한다. (메인 페이지의
  `google-site-verification` 메타는 새 도메인용 코드로 교체 필요)
- **Indexing API** 는 공식적으로 `JobPosting`·`BroadcastEvent` 전용이라
  일반 콘텐츠 페이지에는 권장되지 않는다. 일반 페이지는 사이트맵 + 자연 크롤링이 정석.
- **sitemap ping**(`google.com/ping?sitemap=`)은 2023년 구글이,
  빙도 이후 **폐지**했다. 더는 동작하지 않으므로 사용하지 않는다.
  → 구글=Search Console 사이트맵, 빙·네이버=IndexNow 로 역할이 갈린다.
