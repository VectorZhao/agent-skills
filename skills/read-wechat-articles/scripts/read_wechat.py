#!/usr/bin/env python3
"""Read a public WeChat article with a Camoufox-first, stdlib-fallback workflow."""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
        "MicroMessenger/8.0.50"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://servicewechat.com/",
}


class TextExtractor(HTMLParser):
    BLOCKS = {"article", "blockquote", "br", "div", "h1", "h2", "h3", "li", "ol", "p", "pre", "section", "ul"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1
        elif not self.skip and tag in self.BLOCKS:
            self.parts.append("\n- " if tag == "li" else "\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1
        elif not self.skip and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def text(self) -> str:
        lines = [re.sub(r"[ \t]+", " ", x).strip() for x in "".join(self.parts).replace("\xa0", " ").splitlines()]
        return "\n".join(x for x in lines if x)


def emit(payload: dict, code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


def extract_div(raw: str, element_id: str) -> str | None:
    match = re.search(rf'<div[^>]+\bid=["\']{re.escape(element_id)}["\'][^>]*>', raw, re.I)
    if not match:
        return None
    depth = 1
    for tag in re.finditer(r"<(/?)div\b[^>]*>", raw[match.end():], re.I):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            return raw[match.end():match.end() + tag.start()].strip()
    return None


def meta(raw: str, key: str) -> str | None:
    patterns = (
        rf'<meta\b[^>]*(?:property|name)=["\']{re.escape(key)}["\'][^>]*content=["\'](.*?)["\']',
        rf'<meta\b[^>]*content=["\'](.*?)["\'][^>]*(?:property|name)=["\']{re.escape(key)}["\']',
    )
    for pattern in patterns:
        found = re.search(pattern, raw, re.I | re.S)
        if found:
            return html.unescape(re.sub(r"\s+", " ", found.group(1))).strip()
    return None


def parse_html(raw: str, source: str, output: Path) -> dict:
    low = raw.lower()
    if "site unavailable" in low or "unable to access this site" in low:
        return {"status": "blocked", "method": "mobile-fallback", "reason": "network_gateway_denied", "source": source}
    if ("环境异常" in raw and "验证" in raw) or ("verify" in low and "weixin" in low):
        return {"status": "blocked", "method": "mobile-fallback", "reason": "wechat_verification", "source": source}
    body = extract_div(raw, "js_content")
    if not body:
        return {"status": "blocked", "method": "mobile-fallback", "reason": "article_body_missing", "source": source}
    parser = TextExtractor()
    parser.feed(body)
    text = parser.text()
    if not text:
        return {"status": "blocked", "method": "mobile-fallback", "reason": "article_body_empty", "source": source}
    title = meta(raw, "og:title") or "wechat-article"
    author = meta(raw, "author") or ""
    safe = re.sub(r'[/\\?%*:|"<>]', "_", title)[:80]
    output.mkdir(parents=True, exist_ok=True)
    md_path = output / f"{safe}.md"
    md_path.write_text(f"# {title}\n\n作者：{author}\n\n来源：{source}\n\n{text}\n", encoding="utf-8")
    return {"status": "ok", "method": "mobile-fallback", "title": title, "author": author, "source": source, "markdown_path": str(md_path.resolve())}


def proxy_fetch(url: str, output: Path) -> tuple[dict | None, str]:
    """Fetch public article Markdown through the open-source Website2Markdown service."""
    endpoint = f"https://md.genedai.me/{url}?raw=true"
    request = urllib.request.Request(
        endpoint,
        headers={
            "Accept": "text/markdown",
            "User-Agent": "read-wechat-articles/1.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=75) as response:
            markdown = response.read().decode("utf-8", errors="replace").strip()
            method = response.headers.get("X-Markdown-Method", "website2markdown")
    except Exception as exc:
        return None, f"proxy_failed: {exc}"

    low = markdown.lower()
    invalid_markers = (
        '"error":"unauthorized"',
        "site unavailable",
        "unable to access this site",
        "环境异常",
    )
    if len(markdown) < 300 or any(marker in low for marker in invalid_markers):
        return None, "proxy_returned_blocked_or_incomplete_content"

    title_match = re.search(r"^#\s+(.+)$", markdown, re.M)
    title = title_match.group(1).strip() if title_match else "wechat-article"
    safe = re.sub(r'[/\\?%*:|"<>]', "_", title)[:80]
    output.mkdir(parents=True, exist_ok=True)
    md_path = output / f"{safe}.md"
    md_path.write_text(markdown + "\n", encoding="utf-8")
    return {
        "status": "ok",
        "method": f"website2markdown:{method}",
        "title": title,
        "source": url,
        "markdown_path": str(md_path.resolve()),
    }, ""


def camoufox_fetch(url: str, output: Path) -> tuple[dict | None, str]:
    uvx = shutil.which("uvx")
    if not uvx:
        return None, "uvx_not_available"
    env = os.environ.copy()
    temp_root = Path(tempfile.gettempdir()) / "read-wechat-articles"
    env.setdefault("UV_CACHE_DIR", str(temp_root / "cache"))
    env.setdefault("UV_TOOL_DIR", str(temp_root / "tools"))
    env.setdefault("UV_TOOL_BIN_DIR", str(temp_root / "bin"))
    try:
        run = subprocess.run(
            [uvx, "wechat-article-to-markdown", url, "-o", str(output)],
            text=True,
            capture_output=True,
            timeout=180,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return None, "camoufox_timeout"
    if run.returncode != 0:
        detail = (run.stderr or run.stdout).strip()[-1000:]
        return None, f"camoufox_failed: {detail}"
    files = sorted(output.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None, "camoufox_returned_no_markdown"
    return {"status": "ok", "method": "camoufox", "source": url, "markdown_path": str(files[0].resolve())}, ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--from-file", action="store_true")
    parser.add_argument("--output", type=Path, default=Path.cwd() / "wechat-output")
    args = parser.parse_args()

    if args.from_file:
        path = Path(args.source)
        try:
            return emit(parse_html(path.read_text(encoding="utf-8", errors="replace"), str(path.resolve()), args.output))
        except OSError as exc:
            return emit({"status": "error", "reason": str(exc)}, 1)

    if not re.match(r"^https://mp\.weixin\.qq\.com/", args.source):
        return emit({"status": "error", "reason": "not_a_public_wechat_article_url"}, 2)

    primary, proxy_error = proxy_fetch(args.source, args.output)
    if primary:
        return emit(primary)

    primary, camoufox_error = camoufox_fetch(args.source, args.output)
    primary_error = f"{proxy_error}; {camoufox_error}"
    if primary:
        return emit(primary)

    try:
        request = urllib.request.Request(args.source, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        result = parse_html(raw, args.source, args.output)
    except Exception as exc:
        result = {"status": "blocked", "method": "mobile-fallback", "reason": f"request_failed: {exc}", "source": args.source}
    result["primary_error"] = primary_error
    return emit(result, 0 if result.get("status") == "ok" else 1)


if __name__ == "__main__":
    sys.exit(main())
