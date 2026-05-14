# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Shared HTML helpers for VaultGate challenge pages."""
from __future__ import annotations

_STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:system-ui,-apple-system,sans-serif;padding:32px;max-width:840px;margin:0 auto}
h1{font-size:1.35rem;margin-bottom:6px;color:#26c6da}
h2{font-size:.95rem;color:#26c6da;margin-bottom:8px}
.meta{color:#8b949e;font-size:.82rem;margin-bottom:20px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:16px}
.card h2{font-size:.88rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px}
p{color:#8b949e;font-size:.88rem;line-height:1.55;margin-bottom:8px}
code{background:#0d1117;border:1px solid #30363d;border-radius:3px;padding:1px 5px;font-size:.82rem;font-family:'SF Mono',Consolas,monospace;color:#e6edf3}
pre{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:14px;font-size:.8rem;font-family:'SF Mono',Consolas,monospace;overflow-x:auto;white-space:pre;margin-bottom:0;color:#e6edf3}
.token-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:.83rem}
.token-label{color:#8b949e;min-width:60px}
.token-val{font-family:monospace;color:#26c6da;font-size:.8rem;word-break:break-all}
input,textarea{background:#21262d;border:1px solid #30363d;color:#e6edf3;padding:8px 10px;border-radius:4px;font-size:.83rem;font-family:monospace;width:100%;margin-top:4px}
button{background:#26c6da;color:#0d1117;border:none;padding:8px 18px;border-radius:4px;cursor:pointer;font-weight:700;margin-top:10px;font-size:.83rem}
button:hover{background:#00acc1}
.result{margin-top:10px;padding:12px;background:#0d1117;border:1px solid #30363d;border-radius:6px;font-family:monospace;font-size:.78rem;min-height:40px;white-space:pre-wrap;color:#8b949e}
.result.ok{color:#3fb950}
.result.err{color:#f85149}
a.back{display:inline-block;margin-top:24px;font-size:.82rem;color:#8b949e;text-decoration:none}
a.back:hover{color:#e6edf3}
.tier-badge{display:inline-block;font-size:.68rem;font-weight:700;padding:2px 8px;border-radius:8px;color:#fff;vertical-align:middle;margin-left:6px}
table{width:100%;border-collapse:collapse;font-size:.82rem}
td,th{padding:7px 10px;border-bottom:1px solid #30363d;text-align:left}
th{color:#8b949e;font-weight:600;font-size:.75rem;text-transform:uppercase}
label{font-size:.8rem;color:#8b949e;display:block;margin-top:10px}
</style>
"""

_TIER_COLORS = {
    1: "#26c6da", 2: "#42a5f5", 3: "#66bb6a",
    4: "#ef5350", 5: "#ff7043", 6: "#ab47bc",
    7: "#ffa726", 8: "#ec407a",
}

_TIER_NAMES = {
    1: "Horizontal IDOR", 2: "Obfuscated IDs", 3: "Body / Param IDOR",
    4: "Vertical IDOR",   5: "Method Bypass",  6: "Param Pollution",
    7: "Mass Assignment", 8: "JWT Tampering",
}


def page(title: str, body: str) -> str:
    return (f"<!DOCTYPE html><html lang='en'>"
            f"<head><meta charset='utf-8'>"
            f"<title>VaultGate — {title}</title>"
            f"{_STYLE}</head><body>{body}"
            f"<br><a class='back' href='/'>&#8592; Back to challenges</a>"
            f"</body></html>")


def tier_badge(tier: int) -> str:
    c = _TIER_COLORS.get(tier, "#555")
    n = _TIER_NAMES.get(tier, f"Tier {tier}")
    return f'<span class="tier-badge" style="background:{c}">{n}</span>'
