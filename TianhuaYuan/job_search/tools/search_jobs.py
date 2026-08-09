from __future__ import annotations

import sys
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
# NOTE: import dify_plugin before requests. dify_plugin patches ssl/gevent at
# import time; importing requests first would break ssl on some runtimes.
import requests

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs"
REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

REQUEST_TIMEOUT = 20
MAX_COUNT = 50
# Remotive serves its responses behind Cloudflare; a plain curl/bot UA can
# get challenged, so send a recognizable UA string.
BROWSER_UA = "Mozilla/5.0 (job-search-dify-plugin/0.0.1)"


class SearchJobsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        source = (tool_parameters.get("source") or "jobicy").strip().lower()
        query = (tool_parameters.get("query") or "").strip()
        location = (tool_parameters.get("location") or "").strip()
        category = (tool_parameters.get("category") or "").strip()
        job_type = (tool_parameters.get("job_type") or "").strip()

        try:
            count = max(1, min(int(tool_parameters.get("count") or 10), MAX_COUNT))
        except (TypeError, ValueError):
            count = 10

        print(
            f"[job_search] invoke source={source!r} query={query!r} "
            f"location={location!r} category={category!r} job_type={job_type!r} "
            f"count={count}",
            file=sys.stderr,
            flush=True,
        )

        try:
            if source == "remotive":
                jobs = self._search_remotive(query, location, category, job_type, count)
            else:
                jobs = self._search_jobicy(query, location, category, job_type, count)
        except requests.RequestException as exc:
            print(f"[job_search] request error: {exc}", file=sys.stderr, flush=True)
            yield self.create_text_message(f"Job search request failed: {exc}")
            return

        print(f"[job_search] matched {len(jobs)} jobs", file=sys.stderr, flush=True)
        if not jobs:
            yield self.create_text_message("No jobs found matching your criteria.")
            return

        yield self.create_json_message({"source": source, "count": len(jobs), "jobs": jobs})

        lines = [f"Found {len(jobs)} jobs from {source}:", ""]
        for job in jobs:
            lines.append(f"* {job['title']} @ {job['company']}")
            if job.get("location"):
                lines.append(f"  Location: {job['location']}")
            if job.get("salary"):
                lines.append(f"  Salary: {job['salary']}")
            if job.get("url"):
                lines.append(f"  Link: {job['url']}")
            lines.append("")
        yield self.create_text_message("\n".join(lines))

    def _search_jobicy(
        self,
        query: str,
        location: str,
        category: str,
        job_type: str,
        count: int,
    ):
        # Fetch a larger pool than the requested count, then filter locally.
        # Otherwise keyword/location filters would only see the first `count`
        # results and often return nothing.
        params: dict[str, Any] = {"count": max(count, 50)}
        if category:
            params["tag"] = category

        resp = requests.get(JOBICY_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        jobs = (resp.json() or {}).get("jobs", []) or []

        results: list = []
        for job in jobs:
            title = job.get("jobTitle") or ""
            company = job.get("companyName") or ""
            geo = job.get("jobGeo") or ""
            types = [str(t) for t in (job.get("jobType") or [])]

            if query and query.lower() not in (title + " " + company).lower():
                continue
            if location and location.lower() not in geo.lower():
                continue
            if job_type and not any(
                job_type.lower() in (t or "").lower() for t in types
            ):
                continue

            results.append(
                {
                    "id": job.get("id"),
                    "title": title,
                    "company": company,
                    "location": geo,
                    "job_type": ", ".join(types),
                    "salary": None,
                    "url": job.get("url"),
                    "source": "jobicy",
                    "description_excerpt": job.get("jobExcerpt"),
                }
            )
        return results[:count]

    def _search_remotive(
        self,
        query: str,
        location: str,
        category: str,
        job_type: str,
        count: int,
    ):
        # Remotive's public endpoint ignores most filters server-side; fetch
        # the feed once and filter locally so the result is predictable.
        resp = requests.get(
            REMOTIVE_URL, headers={"User-Agent": BROWSER_UA}, timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        jobs = (resp.json() or {}).get("jobs", []) or []

        results: list = []
        for job in jobs:
            title = job.get("title") or ""
            company = job.get("company_name") or ""
            geo = job.get("candidate_required_location") or ""
            types = str(job.get("job_type") or "")
            cats = str(job.get("category") or "")

            if query and query.lower() not in (title + " " + company).lower():
                continue
            if location and location.lower() not in geo.lower():
                continue
            if category and category.lower() not in cats.lower():
                continue
            if job_type and job_type.lower() not in types.lower():
                continue

            results.append(
                {
                    "id": job.get("id"),
                    "title": title,
                    "company": company,
                    "location": geo,
                    "job_type": types,
                    "salary": job.get("salary") or None,
                    "url": job.get("url"),
                    "source": "remotive",
                    "category": cats,
                    "description_excerpt": None,
                }
            )
        return results[:count]
