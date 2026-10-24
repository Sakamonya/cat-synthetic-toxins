#!/usr/bin/env python3
"""联网任务前置检查：代理端口、出口 IP、目标站点可达性。

用法: python scripts/preflight.py [额外URL ...]
退出码 0 = 可以开跑，1 = 有硬性依赖不可用。
"""
from __future__ import annotations

import os
import socket
import sys
import urllib.error
import urllib.request

PROXY = os.environ.get("RESEARCH_PROXY", "http://127.0.0.1:7890")
TARGETS = [
    ("GitHub", "https://github.com"),
    ("DashScope", "https://dashscope.aliyuncs.com"),
    ("Pet Poison Helpline", "https://www.petpoisonhelpline.com/poison/acetaminophen/"),
    ("MSD Vet Manual", "https://www.msdvetmanual.com/toxicology"),
]
UA = "cat-toxins-preflight/0.2"


def opener(proxy: str | None):
    handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy}) if proxy else urllib.request.ProxyHandler({})
    op = urllib.request.build_opener(handler)
    op.addheaders = [("User-Agent", UA)]
    return op


def probe(op, url: str, timeout: int = 15) -> tuple[bool, str]:
    try:
        with op.open(url, timeout=timeout) as r:
            return True, str(r.status)
    except urllib.error.HTTPError as exc:
        # 4xx 说明服务器有响应，视为可达
        return exc.code < 500, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).split("\n")[0][:70]
        return False, msg


def proxy_port() -> tuple[str, int]:
    rest = PROXY.split("://", 1)[-1]
    host, _, port = rest.partition(":")
    return host or "127.0.0.1", int(port or 0)


def main() -> int:
    host, port = proxy_port()
    print(f"proxy target : {PROXY}")

    reachable = False
    try:
        with socket.create_connection((host, port), timeout=3):
            reachable = True
        print(f"proxy port   : open ({host}:{port})")
    except OSError as exc:
        print(f"proxy port   : CLOSED ({exc})")

    direct = opener(None)
    via = opener(PROXY)

    for label, op in (("direct", direct), ("proxy", via)):
        ok, info = probe(op, "https://ipinfo.io/ip")
        print(f"egress {label:6}: {'ok' if ok else 'FAIL'} {info[:40]}")

    failures = 0
    print("\ntargets (direct / proxy):")
    for name, url in TARGETS + [(u, u) for u in sys.argv[1:]]:
        okd, md = probe(direct, url, 20)
        okp, mp = probe(via, url, 20)
        mark = "OK " if (okd or okp) else "FAIL"
        if not (okd or okp):
            failures += 1
        print(f"  [{mark}] {name:22} direct={'y' if okd else 'n'}({md[:18]})  proxy={'y' if okp else 'n'}({mp[:18]})")

    print()
    if not reachable:
        print("结论: 代理端口未监听 —— 需要先启动梯子。")
        return 1
    if failures:
        print(f"结论: {failures} 个目标在两条路径上都不可达。")
        return 1
    print("结论: 可以通过（至少一条路径可达）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
