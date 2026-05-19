"""
PNG/JPG → WebP 일괄 변환 스크립트.

사용법:
    python3 scripts/convert_webp.py             # assets/img 아래 전체 변환
    python3 scripts/convert_webp.py --force     # 기존 .webp 덮어쓰기
    python3 scripts/convert_webp.py --dir path  # 디렉토리 지정

기본 정책:
- 알파 채널이 있는 이미지(로고 등) → method=6, quality=92, lossless 비교 후 더 작은 쪽 채택
- 알파 없는 사진/카드 이미지 → quality=82 lossy
- 원본 PNG/JPG는 유지(소셜 크롤러 호환·점진적 도입)
- 동일 stem의 .webp가 이미 있고 원본보다 신선하면 스킵

의존성: Pillow (pip install Pillow)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("Pillow가 필요합니다. 설치: pip3 install Pillow\n")
    sys.exit(1)

SUPPORTED_SRC = {".png", ".jpg", ".jpeg"}
DEFAULT_DIR = Path("assets/img")


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}TB"


def encode_with_alpha(src: Path, dst: Path) -> int:
    """알파 채널 이미지: lossless와 quality=92 lossy 중 작은 쪽 채택."""
    im = Image.open(src).convert("RGBA")

    lossless_path = dst.with_suffix(".webp.lossless.tmp")
    lossy_path = dst.with_suffix(".webp.lossy.tmp")
    im.save(lossless_path, "WEBP", lossless=True, method=6)
    im.save(lossy_path, "WEBP", quality=92, method=6, alpha_quality=100)

    lossless_size = lossless_path.stat().st_size
    lossy_size = lossy_path.stat().st_size

    if lossless_size <= lossy_size:
        lossless_path.replace(dst)
        lossy_path.unlink(missing_ok=True)
        mode = "lossless"
    else:
        lossy_path.replace(dst)
        lossless_path.unlink(missing_ok=True)
        mode = "q92"

    return dst.stat().st_size, mode


def encode_solid(src: Path, dst: Path) -> tuple[int, str]:
    """불투명 사진/카드 이미지: quality=82 lossy."""
    im = Image.open(src).convert("RGB")
    im.save(dst, "WEBP", quality=82, method=6)
    return dst.stat().st_size, "q82"


def convert_one(src: Path, force: bool) -> tuple[str, int, int] | None:
    dst = src.with_suffix(".webp")
    if dst.exists() and not force:
        if dst.stat().st_mtime >= src.stat().st_mtime:
            return None  # 최신 상태

    im = Image.open(src)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im.close()

    if has_alpha:
        new_size, mode = encode_with_alpha(src, dst)
    else:
        new_size, mode = encode_solid(src, dst)

    src_size = src.stat().st_size
    return (mode, src_size, new_size)


def main() -> int:
    parser = argparse.ArgumentParser(description="PNG/JPG → WebP 변환")
    parser.add_argument("--dir", default=str(DEFAULT_DIR), help="변환 대상 디렉토리")
    parser.add_argument("--force", action="store_true", help="기존 .webp 덮어쓰기")
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.is_dir():
        sys.stderr.write(f"디렉토리 없음: {root}\n")
        return 1

    files = sorted(p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_SRC)
    if not files:
        print(f"변환할 이미지가 없습니다: {root}")
        return 0

    total_src = total_dst = 0
    converted = skipped = 0

    for src in files:
        result = convert_one(src, args.force)
        if result is None:
            skipped += 1
            print(f"  skip  {src} (이미 최신)")
            continue
        mode, src_size, dst_size = result
        total_src += src_size
        total_dst += dst_size
        converted += 1
        ratio = (1 - dst_size / src_size) * 100 if src_size else 0
        print(
            f"  ok    {src.name:40s} "
            f"{human_size(src_size):>9s} -> {human_size(dst_size):>9s}  "
            f"({ratio:+.1f}%, {mode})"
        )

    print()
    print(f"변환 {converted}개 / 스킵 {skipped}개")
    if converted:
        total_ratio = (1 - total_dst / total_src) * 100
        print(
            f"총 용량: {human_size(total_src)} -> {human_size(total_dst)} "
            f"({total_ratio:+.1f}%)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
