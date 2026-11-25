"""Prompt Efficiently API client and on-device estimator.

Mirrors the PE browser extension and developer packages:
- estimate math runs locally; only a random request id goes to PE to count usage
  (Free: 5 estimates a day, Pro: unlimited) so the server enforces the account quota.
- AI rewrite sends the prompt text to PE only when the user confirmed they are 18+
  and agree to that processing (the confirm_adult_consent credential).
"""
import json
import re
import urllib.error
import urllib.request
import uuid

from .pe_platforms import PLATFORMS

ORIGIN = "https://promptefficiently.com"
USER_AGENT = "PromptEfficiently-DifyPlugin/0.1.0"

CAP_ESTIMATES = {"small": [1, 2], "medium": [2, 5], "big": [5, 12]}
CAP_PER_TYPE = {"question": [1, 2], "edit": [1, 2], "feature": [2, 5], "app": [5, 12], "general": [1, 3]}
SIZES = {"small": "A single task or question", "medium": "A small project or feature", "big": "A big build, many steps"}

TASK_TYPES = [
    ("question", "a question or explanation", re.compile(r"^(what|how|why|when|where|who|explain|summari[sz]e|write|draft|is |are |can |does|do )\b|\?\s*$", re.I)),
    ("edit", "a small edit", re.compile(r"\b(fix|change|update|remove|rename|tweak|adjust|move|make the)\b", re.I)),
    ("app", "a full build", re.compile(r"\b(app|website|marketplace|platform|dashboard|clone|system)\b", re.I)),
    ("feature", "a feature or page", re.compile(r"\b(auth|login|sign ?up|form|page|section|component|table|checkout|search|filter|landing)\b", re.I)),
]

UNIT_NOUN = {"credits": "credits", "tokens": "tokens", "dollars": "dollars", "messages": "messages"}

# JavaScript Math.round rounds halves up; Python round() is banker's rounding.
def js_round(x):
    import math
    return math.floor(x + 0.5)


class PEError(Exception):
    """User-facing PE error."""


class SessionExpired(PEError):
    """The cached session token is no longer accepted."""


def _request(path, token=None, data=None, timeout=25):
    headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(ORIGIN + path, data=body, headers=headers, method="GET" if data is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as e:
        try:
            payload = json.load(e)
        except Exception:
            payload = {}
        return e.code, payload
    except urllib.error.URLError as e:
        raise PEError("Could not reach promptefficiently.com (%s). Try again shortly." % getattr(e, "reason", e)) from None


def send_code(email):
    status, payload = _request("/api/send-code", data={"email": email})
    if status != 200:
        raise PEError("PE would not send a sign-in code to that email (%s)." % (payload.get("error") or status))


def verify_code(email, code):
    status, payload = _request("/api/verify-code", data={"email": email, "code": code})
    if status != 200 or not payload.get("ok") or not payload.get("token"):
        raise PEError("That sign-in code was not accepted. Codes expire after 10 minutes; save with an empty code field to get a fresh one.")
    return payload["token"]


def check_session(token):
    status, _ = _request("/api/session", token=token)
    return status == 200


def consume_usage(token):
    """Count one estimate against the PE account. Returns (pro, remaining)."""
    status, payload = _request("/api/usage", token=token, data={"requestId": str(uuid.uuid4())})
    if status == 401:
        raise SessionExpired("PE session expired. Save the plugin credentials again with a fresh sign-in code.")
    if status == 429:
        raise PEError("The 5 free estimates for today are used. Upgrade to Pro at https://promptefficiently.com/app for unlimited estimates.")
    if status != 200 or not isinstance(payload.get("pro"), bool):
        raise PEError("PE quota check failed (%s). No estimate was counted." % (payload.get("error") or status))
    return payload["pro"], payload.get("remaining")


def ai_rewrite(token, text, mode):
    status, payload = _request(
        "/api/rewrite",
        token=token,
        data={"requestId": str(uuid.uuid4()), "text": text, "consent": True, "adult": True, "mode": mode},
    )
    if status == 401:
        raise SessionExpired("PE session expired. Save the plugin credentials again with a fresh sign-in code.")
    if status == 429:
        raise PEError("The free AI rewrites are used on this PE account. Upgrade to Pro at https://promptefficiently.com/app for more.")
    if status != 200:
        raise PEError("PE rewrite failed (%s)." % (payload.get("error") or status))
    return payload


def platform_by_id(pid):
    for p in PLATFORMS:
        if p["id"] == pid:
            return p
    return None


def plan_by_id(platform, plan_id):
    if not plan_id:
        return None
    for plan in platform.get("plans", []):
        if plan["id"] == plan_id:
            return plan
    return None


def estimate_tokens(text):
    words = len([w for w in text.strip().split() if w])
    return js_round(words * 1.3)


def detect_task_type(text):
    t = (text or "").strip()
    if not t:
        return None, None
    for key, label, rx in TASK_TYPES:
        if rx.search(t):
            return key, label
    return "general", "a general task"


def _fmt(n):
    if n >= 1000000:
        return "%dM" % (n // 1000000) if n % 1000000 == 0 else "%.1fM" % (n / 1000000.0)
    if n >= 1000:
        return "%dK" % js_round(n / 1000)
    return "%d" % n if float(n).is_integer() else "%.1f" % n


# Rough per-size output-token ranges for API (per-token) platforms. Documented as a rough guide.
API_OUTPUT_TOKENS = {"small": (50, 300), "medium": (300, 1500), "big": (1500, 6000)}


def _money(x):
    if x < 0.001:
        return "$%.4f" % x
    if x < 0.1:
        return "$%.3f" % x
    return "$%.2f" % x


def compute_api_estimate(platform, size, input_tokens):
    """Per-token estimate for API model platforms (Dify LLM nodes etc.)."""
    if not platform["inRate"] and not platform["outRate"]:
        return {
            "rangeText": "$0 per call",
            "subText": platform["modelNote"],
            "pct": None,
            "verdict": "fits",
            "verdictText": "Free, runs on your own machine.",
        }
    out_lo, out_hi = API_OUTPUT_TOKENS[size]
    low = input_tokens * platform["inRate"] / 1e6 + out_lo * platform["outRate"] / 1e6
    high = input_tokens * platform["inRate"] / 1e6 + out_hi * platform["outRate"] / 1e6
    notable = high >= 0.05
    return {
        "rangeText": "%s\u2013%s per call" % (_money(low), _money(high)),
        "subText": platform["modelNote"] + ", plus %s\u2013%s output tokens" % (_fmt(out_lo), _fmt(out_hi)),
        "pct": None,
        "verdict": "tight" if notable else "fits",
        "verdictText": "Notable per-call cost. A shorter prompt cuts the input side." if notable else "Cheap per call.",
    }


def compute_estimate(platform, size, plan, type_key):
    """Faithful port of computeEstimate() from the PE extension estimator.js."""
    plan_label = plan["label"] if plan else "Free"
    if platform["kind"] == "caps":
        lo, hi = CAP_PER_TYPE.get(type_key) or CAP_ESTIMATES[size]
        return {
            "rangeText": "%d\u2013%d messages" % (lo, hi),
            "subText": "on %s. Windows are not published, so no exact percentage is possible." % plan_label,
            "pct": None,
            "verdict": "tight" if size == "big" else "fits",
            "verdictText": "Big builds can hit a message window fast. Split it into steps." if size == "big" else "Should fit in a normal window.",
        }
    use_credits = plan and plan.get("unit") == "credits" and platform.get("creditPerTask")
    if use_credits:
        lo, hi = platform["creditPerTask"][size]
    elif type_key and platform.get("perType") and platform["perType"].get(type_key):
        lo, hi = platform["perType"][type_key]
    else:
        lo, hi = platform["perTask"][size]
    range_unit = (plan and plan.get("unit")) or platform["unit"]
    allowance = plan and plan.get("allowance")
    period = plan and plan.get("period")
    pct_lo = pct_hi = None
    verdict, verdict_text = "fits", "Fits comfortably."
    if allowance:
        pct_lo = lo / allowance * 100
        pct_hi = hi / allowance * 100
        unit_noun = "messages" if range_unit == "messages" else range_unit
        if pct_hi >= 100:
            verdict, verdict_text = "over", "Likely blows your %s for the %s on %s." % (unit_noun, period, plan_label)
        elif pct_hi >= 50:
            verdict, verdict_text = "tight", "Tight: up to about %d%% of your %s\u2019s allowance." % (js_round(pct_hi), period)
        else:
            verdict, verdict_text = "fits", "Fits: about %d\u2013%d%% of your %s\u2019s allowance." % (max(1, js_round(pct_lo)), max(1, js_round(pct_hi)), period)
    money = range_unit == "dollars"
    range_text = ("$%.2f\u2013$%.2f" % (lo, hi)) if money else ("%s\u2013%s %s" % (_fmt(lo), _fmt(hi), "messages" if range_unit == "messages" else range_unit))
    sub_text = ("against %s %s on %s each %s" % (_fmt(allowance) if allowance >= 1000000 else "{:,}".format(allowance), "messages" if range_unit == "messages" else range_unit, plan_label, period)) if allowance else ("on %s" % plan_label)
    return {"rangeText": range_text, "subText": sub_text, "pct": min(100, pct_hi) if pct_hi else None, "verdict": verdict, "verdictText": verdict_text}


def cheapest_free_fit(size, type_key):
    best = None
    for p in PLATFORMS:
        if p["kind"] != "credits" or not p.get("freeAllowance"):
            continue
        r = (p.get("perType", {}).get(type_key) if type_key else None) or p.get("perTask", {}).get(size)
        if not r or r[0] + r[1] <= 0:
            continue
        mid = (r[0] + r[1]) / 2
        headroom = p["freeAllowance"] / mid
        if not best or headroom > best["headroom"]:
            best = {"platform": p["name"], "headroom": headroom, "rangeText": "%s\u2013%s %s" % (_fmt(r[0]), _fmt(r[1]), p["freeUnit"])}
    return best


def full_estimate(text, platform_id, size, plan_id):
    platform = platform_by_id(platform_id)
    if not platform:
        raise PEError("Unknown platform '%s'." % platform_id)
    plan = plan_by_id(platform, plan_id)
    if plan_id and not plan:
        raise PEError("Unknown plan '%s' for %s." % (plan_id, platform["name"]))
    type_key, type_label = detect_task_type(text)
    if platform["kind"] == "tokens":
        est = compute_api_estimate(platform, size, estimate_tokens(text))
    else:
        est = compute_estimate(platform, size, plan, type_key)
    result = {
        "platform": platform["name"],
        "plan": "Pay per use" if platform["kind"] == "tokens" else (plan or {}).get("label", "Free"),
        "size": size,
        "sizeMeaning": SIZES[size],
        "taskType": type_label,
        "roughInputTokens": estimate_tokens(text),
        "estimate": est["rangeText"],
        "detail": est["subText"],
        "verdict": est["verdict"],
        "verdictText": est["verdictText"],
        "confidence": platform.get("confidence") or platform.get("unverified") or "Rough estimate, not a quote.",
    }
    if platform["kind"] != "tokens":
        fit = cheapest_free_fit(size, type_key)
        if fit:
            fit = {"platform": fit["platform"], "rangeText": fit["rangeText"], "headroom": fit["headroom"]}
            result["cheapestFreeFit"] = fit
    return result
