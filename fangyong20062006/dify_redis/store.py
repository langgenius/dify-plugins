"""
内置键值存储引擎，模拟 Redis SET / GET / DEL / EXISTS 语义。

存储结构：
  _store: { key -> {"value": str, "expire_at": float|None} }

持久化：
  pickle 序列化到 STORE_PATH，插件容器重启后自动恢复。
  多线程写入由 threading.Lock 保护。

TTL 语义：
  expire_at = None  → 永不过期（等同 Redis 不设 EX）
  expire_at = float → Unix 时间戳，GET/EXISTS 时检查是否已过期
"""

import os
import pickle
import time
import threading
from typing import Any

STORE_PATH = "/tmp/dify_redis_store.pkl"
_lock = threading.Lock()
_store: dict[str, dict] = {}


def _load() -> None:
    global _store
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "rb") as f:
                _store = pickle.load(f)
        except Exception:
            _store = {}


def _save() -> None:
    with open(STORE_PATH, "wb") as f:
        pickle.dump(_store, f)


# 启动时加载一次
_load()


def _is_expired(entry: dict) -> bool:
    ea = entry.get("expire_at")
    return ea is not None and time.time() > ea


# ── 公开 API ──────────────────────────────────────────

def redis_set(key: str, value: str, ttl_seconds: int | None = None) -> None:
    """写入 key，可选 TTL（秒）。"""
    expire_at = (time.time() + ttl_seconds) if ttl_seconds and ttl_seconds > 0 else None
    with _lock:
        _store[key] = {"value": value, "expire_at": expire_at}
        _save()


def redis_get(key: str) -> str | None:
    """读取 key，不存在或已过期返回 None。"""
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        if _is_expired(entry):
            del _store[key]
            _save()
            return None
        return entry["value"]


def redis_delete(key: str) -> bool:
    """删除 key，返回是否存在过。"""
    with _lock:
        existed = key in _store
        if existed:
            del _store[key]
            _save()
        return existed


def redis_exists(key: str) -> bool:
    """检查 key 是否存在且未过期。"""
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return False
        if _is_expired(entry):
            del _store[key]
            _save()
            return False
        return True


def redis_ttl(key: str) -> int:
    """返回 key 的剩余秒数；-1 表示永不过期；-2 表示不存在或已过期。"""
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return -2
        if _is_expired(entry):
            del _store[key]
            _save()
            return -2
        ea = entry.get("expire_at")
        if ea is None:
            return -1
        return max(0, int(ea - time.time()))


def redis_info() -> dict[str, Any]:
    """返回存储统计信息。"""
    with _lock:
        now = time.time()
        total = len(_store)
        expired = sum(1 for e in _store.values() if e.get("expire_at") and now > e["expire_at"])
        return {
            "total_keys": total,
            "active_keys": total - expired,
            "expired_keys": expired,
            "store_path": STORE_PATH,
            "store_size_bytes": os.path.getsize(STORE_PATH) if os.path.exists(STORE_PATH) else 0,
        }
