"""
从 Router 两个站点的 /v1/models 生成插件里的模型清单，打包前跑一次：

    python scripts/sync_models.py          # 重写 models/llm/*.yaml、_position.yaml、models/catalog.json
    python scripts/sync_models.py --check  # 只比对，清单过期就 exit 1（给 CI / 发版前自检用）

为什么要生成而不是运行时拉：Dify 只认插件包里的 YAML 作为「预置模型」，安装时就定死了
（官方 OpenRouter 插件也是手写 133 个 YAML）。所以清单在打包时从 Router 同步，
包发出去之后 Router 再上新模型，用户在 Dify 里「添加模型」只填模型名即可，
上下文长度、工具调用、视觉这些能力插件运行时从 /v1/models 自动查，不用手填。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.router_client import CLIENT_HEADERS, SITES  # noqa: E402
from models.schema import model_filename, model_yaml  # noqa: E402

LLM_DIR = ROOT / "models" / "llm"
CATALOG = ROOT / "models" / "catalog.json"


def fetch(site: str) -> list[dict]:
    resp = requests.get(f"{SITES[site]}/models", headers=CLIENT_HEADERS, timeout=30)
    resp.raise_for_status()
    return [m for m in resp.json()["data"] if m.get("category", "chat") == "chat"]


def build(by_site: dict[str, list[dict]]) -> tuple[dict[str, str], list[str], dict]:
    """返回 (文件名→YAML 文本, 排序后的模型 id, catalog)。排序：各站推荐模型在前，国内站在前。"""
    files: dict[str, str] = {}
    catalog: dict[str, dict] = {}
    featured, rest = [], []
    for site, models in by_site.items():
        for m in models:
            if m["id"] in catalog:
                continue
            catalog[m["id"]] = {
                "site": site,
                "owned_by": m.get("owned_by", ""),
                "context_length": int(m.get("context_length") or 32768),
                "capabilities": m.get("capabilities") or [],
            }
            files[model_filename(m["id"])] = yaml.safe_dump(
                model_yaml(m, site), allow_unicode=True, sort_keys=False
            )
            (featured if m.get("featured") else rest).append(m["id"])
    order = featured + rest
    files["_position.yaml"] = yaml.safe_dump(order, allow_unicode=True)
    return files, order, {"models": catalog}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比对，不写文件")
    args = ap.parse_args()

    files, order, catalog = build({site: fetch(site) for site in SITES})
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"

    current = {p.name: p.read_text(encoding="utf-8") for p in LLM_DIR.glob("*.yaml")}
    stale = sorted(set(current) - set(files))
    changed = sorted(n for n, t in files.items() if current.get(n) != t)
    catalog_changed = not CATALOG.exists() or CATALOG.read_text(encoding="utf-8") != catalog_text

    if args.check:
        if stale or changed or catalog_changed:
            print(f"模型清单已过期：新增/变更 {len(changed)}，下线 {len(stale)}，跑 python scripts/sync_models.py 更新")
            for n in changed:
                print("  ~", n)
            for n in stale:
                print("  -", n)
            return 1
        print(f"模型清单是最新的（{len(order)} 个模型）")
        return 0

    for n in stale:
        (LLM_DIR / n).unlink()
    for n, text in files.items():
        (LLM_DIR / n).write_text(text, encoding="utf-8")
    CATALOG.write_text(catalog_text, encoding="utf-8")
    print(f"已同步 {len(order)} 个模型（变更 {len(changed)}，下线 {len(stale)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
