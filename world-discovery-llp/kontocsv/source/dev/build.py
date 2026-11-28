"""Build a reproducible Dify plugin ZIP without transient or sensitive files."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"src"
BASENAME="kontocsv-0.1.0.difypkg"

def build(repo_url: str) -> Path:
    out=ROOT/BASENAME
    included=[]
    with ZipFile(out,"w") as z:
        for p in sorted(SOURCE.rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts or p.suffix in {".pyc",".log",".pyo"}:
                continue
            rel=p.relative_to(SOURCE).as_posix()
            data=p.read_bytes()
            if rel=="manifest.yaml":
                text=data.decode("utf-8")
                old="repo: https://github.com/world-discovery-llp/dify-plugins"
                assert text.count(old)==1
                data=text.replace(old,"repo: "+repo_url).encode("utf-8")
            elif rel=="README.md":
                text=data.decode("utf-8")
                old="Public source: https://github.com/world-discovery-llp/dify-plugins"
                assert text.count(old)==1
                data=text.replace(old,"Public source: "+repo_url).encode("utf-8")
            info=ZipInfo(rel,(2026,11,28,12,0,0))
            info.compress_type=ZIP_DEFLATED
            info.create_system=3
            info.external_attr=0o100644<<16
            z.writestr(info,data,compresslevel=9)
            included.append(rel)
    with ZipFile(out) as z:
        assert z.testzip() is None
        assert z.namelist()==included
    print(json.dumps({"file":str(out),"bytes":out.stat().st_size,
        "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "source_url":repo_url,"files":len(included)},indent=2))
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-url",default="https://github.com/world-discovery-llp/dify-plugins")
    a=p.parse_args()
    build(a.source_url)
