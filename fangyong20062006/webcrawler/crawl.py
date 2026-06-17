"""
Web Crawler Tool
使用 requests + BeautifulSoup 实现递归网页爬取，返回结构化 JSON。
避免 Scrapy/Twisted reactor 与 Dify 运行时的冲突。
爬取结果同时以 JSON 文件形式输出到 files 变量，支持直接下载。
"""

import json
import logging
from collections import deque
from collections.abc import Generator
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)

_h2t = html2text.HTML2Text()
_h2t.ignore_links = False
_h2t.ignore_images = True
_h2t.body_width = 0

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _fetch_page(session: requests.Session, url: str, timeout: int = 15) -> dict:
    """抓取单个页面，返回解析后的数据。"""
    try:
        resp = session.get(url, headers=_HEADERS, timeout=timeout, verify=False, allow_redirects=True)
        resp.encoding = resp.apparent_encoding or "utf-8"
        html = resp.text
        status_code = resp.status_code
    except Exception as exc:
        logger.warning("fetch failed: %s — %s", url, exc)
        return {
            "url": url,
            "title": "",
            "text": "",
            "links": [],
            "meta_desc": "",
            "status_code": 0,
            "depth": 0,
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "error": str(exc),
        }

    soup = BeautifulSoup(html, "lxml")

    # 标题
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""

    # 正文（优先语义标签）
    body_el = (
        soup.find("article")
        or soup.find("main")
        or soup.find(class_="content")
        or soup.find(id="content")
        or soup.find("body")
    )
    text = _h2t.handle(str(body_el)).strip() if body_el else ""

    # meta description
    meta_desc = ""
    m = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if m and m.get("content"):
        meta_desc = m["content"].strip()

    # 提取所有链接（绝对 URL，去重）
    links: list[str] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        abs_url = urljoin(url, a["href"])
        parsed = urlparse(abs_url)
        if parsed.scheme in ("http", "https") and abs_url not in seen:
            seen.add(abs_url)
            links.append(abs_url)

    return {
        "url": url,
        "title": title,
        "text": text[:8000],
        "links": links[:50],
        "meta_desc": meta_desc,
        "status_code": status_code,
        "depth": 0,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
    }


def _crawl(
    start_url: str,
    max_depth: int,
    max_pages: int,
    same_domain_only: bool,
    include_pattern: str | None,
) -> tuple[list[dict], str | None]:
    """BFS 递归爬取。返回 (pages, optional_warning)。"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    start_domain = urlparse(start_url).netloc
    visited: set[str] = set()
    pages: list[dict] = []

    queue: deque[tuple[str, int]] = deque([(start_url, 0)])

    with requests.Session() as session:
        while queue and len(pages) < max_pages:
            url, depth = queue.popleft()

            if url in visited:
                continue
            visited.add(url)

            page = _fetch_page(session, url)
            page["depth"] = depth
            pages.append(page)

            if depth < max_depth and len(pages) < max_pages:
                for link in page.get("links", []):
                    if link in visited:
                        continue
                    parsed = urlparse(link)
                    if parsed.scheme not in ("http", "https"):
                        continue
                    if same_domain_only and parsed.netloc != start_domain:
                        continue
                    if include_pattern and include_pattern not in link:
                        continue
                    queue.append((link, depth + 1))

    return pages, None


class CrawlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url          = (tool_parameters.get("url") or "").strip()
        depth        = int(tool_parameters.get("depth") or 1)
        max_pages    = int(tool_parameters.get("max_pages") or 20)
        same_domain  = bool(tool_parameters.get("same_domain_only", True))
        incl_pattern = (tool_parameters.get("include_pattern") or "").strip() or None

        if not url:
            raise ValueError("url 不能为空")
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        depth     = max(0, min(depth, 3))
        max_pages = max(1, min(max_pages, 100))

        pages, warning = _crawl(url, depth, max_pages, same_domain, incl_pattern)

        output: dict[str, Any] = {
            "total_pages": len(pages),
            "start_url":   url,
            "depth":       depth,
            "pages":       pages,
        }
        if warning:
            output["warning"] = warning

        # ── 1. text 输出：摘要信息 ──────────────────────────────────────────
        yield self.create_text_message(
            f"爬取完成：共 {len(pages)} 个页面，起始 URL：{url}，深度：{depth}"
        )

        # ── 2. json 输出：结构化数据（供工作流后续节点引用） ───────────────
        yield self.create_json_message(output)

        # ── 3. files 输出：JSON 文件，可直接点击下载 ───────────────────────
        # 生成友好的文件名：crawl_<domain>_<timestamp>.json
        domain_slug = urlparse(url).netloc.replace(".", "_").replace(":", "_") or "result"
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"crawl_{domain_slug}_{ts}.json"

        json_bytes = json.dumps(output, ensure_ascii=False, indent=2).encode("utf-8")

        yield self.create_blob_message(
            blob=json_bytes,
            meta={
                "mime_type": "application/json",
                "filename":  filename,
            },
        )
