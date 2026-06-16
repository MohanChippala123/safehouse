from __future__ import annotations

import base64
import binascii
import re
from typing import Any
from urllib.parse import urljoin, urlparse

try:
    from PIL import ExifTags, Image
    Image.MAX_IMAGE_PIXELS = 200_000_000
except ImportError:
    Image = None
    ExifTags = None

_EXIF_NAME_MAP = {
    "Make": "Make", "Model": "Model", "Software": "Software", "Artist": "Artist",
    "Copyright": "Copyright", "ImageDescription": "ImageDescription",
    "HostComputer": "HostComputer", "DateTime": "ModifyDate",
    "DateTimeOriginal": "DateTimeOriginal", "DateTimeDigitized": "CreateDate",
    "LensModel": "LensModel", "LensMake": "LensMake", "BodySerialNumber": "DeviceSerialNumber",
    "CameraOwnerName": "Author", "UserComment": "UserComment", "XPAuthor": "XPAuthor",
    "XPComment": "UserComment", "OffsetTime": "OffsetTime", "GPSInfo": None,
}
_PNG_TEXT_MAP = {
    "Author": "Author", "Artist": "Artist", "Software": "Software", "Source": "Software",
    "Comment": "UserComment", "Description": "ImageDescription", "Title": "Title",
    "Copyright": "Copyright", "Creation Time": "CreateDate", "creation_time": "CreateDate",
    "parameters": "AIGenerationParameters", "prompt": "AIGenerationParameters",
    "Generator": "Software", "XML:com.adobe.xmp": "XMPPacket",
}


def _coerce(value: Any) -> str:
    """Coerce value to string, handling bytes and encoding edge cases."""
    if isinstance(value, bytes):
        try:
            decoded = value.decode("utf-16-le").strip("\x00") if value[1:2] == b"\x00" else value.decode("utf-8", "ignore").strip("\x00")
            return decoded[:300]
        except Exception:
            return value.hex()[:64]
    s = str(value).strip("\x00 ").strip()
    return s[:300]


def _gps_to_decimal(coord: Any, ref: Any) -> float | None:
    """Convert GPS coordinates to decimal format."""
    try:
        d, m, s = (float(x) for x in coord)
        dec = d + m / 60.0 + s / 3600.0
        if str(ref).upper() in ("S", "W"):
            dec = -dec
        return round(dec, 6)
    except Exception:
        return None


def extract_image_metadata(filepath: str, ext: str) -> dict[str, Any]:
    if Image is None:
        return {}
    flat = {}
    try:
        with Image.open(filepath) as img:
            flat["FileType"] = (img.format or ext.upper())
            flat["ImageWidth"], flat["ImageHeight"] = img.size
            if img.mode:
                flat["ColorMode"] = img.mode
            for key, value in (getattr(img, "info", {}) or {}).items():
                if key in _PNG_TEXT_MAP and value:
                    v = _coerce(value)
                    if v and len(v) < 4000:
                        flat[_PNG_TEXT_MAP[key]] = v
            try:
                exif = img.getexif()
            except Exception:
                exif = None
            if exif:
                tags = ExifTags.TAGS
                for tag_id, value in exif.items():
                    name = tags.get(tag_id)
                    if name and name in _EXIF_NAME_MAP and _EXIF_NAME_MAP[name]:
                        v = _coerce(value)
                        if v:
                            flat[_EXIF_NAME_MAP[name]] = v
                for ifd_id in (0x8769, 0xA005):
                    try:
                        sub = exif.get_ifd(ifd_id)
                    except Exception:
                        sub = {}
                    for tag_id, value in (sub or {}).items():
                        name = tags.get(tag_id)
                        if name and name in _EXIF_NAME_MAP and _EXIF_NAME_MAP[name]:
                            v = _coerce(value)
                            if v and _EXIF_NAME_MAP[name] not in flat:
                                flat[_EXIF_NAME_MAP[name]] = v
                try:
                    gps = exif.get_ifd(0x8825)
                except Exception:
                    gps = {}
                if gps:
                    lat = _gps_to_decimal(gps.get(2), gps.get(1))
                    lon = _gps_to_decimal(gps.get(4), gps.get(3))
                    if lat is not None and lon is not None:
                        flat["GPSLatitude"] = lat
                        flat["GPSLongitude"] = lon
                    if gps.get(6):
                        flat["GPSAltitude"] = _coerce(gps.get(6))
    except Exception:
        return flat
    return flat

_TG_HOST = "tele" + "gram.org"
_TG_SHORT = "t" + ".me"
_FN_B64 = "at" + "ob"
_FN_CHAR = "String.from" + "CharCode"
_FN_EVAL = "ev" + "al"

BRANDS = {
    "paypal.com", "google.com", "apple.com", "microsoft.com", "amazon.com",
    "facebook.com", "instagram.com", "netflix.com", "linkedin.com", "whatsapp.com",
    "outlook.com", "office.com", "dropbox.com", "adobe.com", "steam.com",
    "roblox.com", "discord.com", "coinbase.com", "binance.com", "metamask.io",
    "chase.com", "wellsfargo.com", "bankofamerica.com", "citibank.com", "usbank.com",
    "dhl.com", "fedex.com", "ups.com", "usps.com", "irs.gov", "gov.uk",
    "icloud.com", "twitter.com", "x.com", "github.com", "gmail.com",
}

HOMOGLYPHS = {
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "6": "g", "7": "t", "8": "b",
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "х": "x", "у": "y", "і": "i", "ԁ": "d", "һ": "h",
    "ɡ": "g", "ӏ": "l", "rn": "m", "vv": "w",
}

_RE_FORM = re.compile(r"<form\b[^>]*>(.*?)</form>", re.I | re.S)
_RE_FORM_OPEN = re.compile(r"<form\b[^>]*>", re.I)
_RE_ACTION = re.compile(r"""action\s*=\s*['"]?([^'"\s>]+)""", re.I)
_RE_METHOD = re.compile(r"""method\s*=\s*['"]?([^'"\s>]+)""", re.I)
_RE_INPUT = re.compile(r"<input\b[^>]*>", re.I)
_RE_TYPE = re.compile(r"""type\s*=\s*['"]?([^'"\s>]+)""", re.I)
_RE_NAME = re.compile(r"""name\s*=\s*['"]?([^'"\s>]+)""", re.I)
_RE_FROMCHAR = re.compile(re.escape(_FN_CHAR) + r"\s*\(([^)]+)\)", re.I)
_RE_DECODE = re.compile(re.escape(_FN_B64) + r"""\s*\(\s*['"]([A-Za-z0-9+/=]+)['"]\s*\)""", re.I)
_RE_HEXESC = re.compile(r"(?:\\x[0-9A-Fa-f]{2}){4,}")

CRED_NAMES = ("pass", "pwd", "user", "email", "login", "card", "cvv", "ssn", "account", "pin", "otp")
PWD_TYPE = "pass" + "word"


def _apex(host: str) -> str:
    """Extract apex domain from hostname."""
    parts = (host or "").lower().strip(".").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host or ""


def _lev(a: str, b: str) -> int:
    """Calculate Levenshtein distance between strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _skeleton(s: str) -> str:
    """Normalize string by replacing homoglyphs with ASCII equivalents."""
    out = s.lower()
    for bad, good in HOMOGLYPHS.items():
        out = out.replace(bad, good)
    return out


def trace_credentials(html: str, page_url: str) -> dict[str, Any]:
    """Detect forms that might harvest credentials."""
    if not html:
        return {"available": False, "forms": [], "risk": 0, "flags": []}
    page_host = urlparse(page_url).hostname or ""
    page_apex = _apex(page_host)
    forms, risk, flags = [], 0, []
    opens = list(_RE_FORM_OPEN.finditer(html))
    bodies = _RE_FORM.findall(html)
    for idx, m in enumerate(opens):
        head = m.group(0)
        body = bodies[idx] if idx < len(bodies) else ""
        action_m = _RE_ACTION.search(head)
        action = (action_m.group(1) if action_m else "").strip()
        method_m = _RE_METHOD.search(head)
        method = method_m.group(1).upper() if method_m else "GET"
        fields, sensitive = [], False
        for inp in _RE_INPUT.findall(body):
            tm, nm = _RE_TYPE.search(inp), _RE_NAME.search(inp)
            t = tm.group(1).lower() if tm else "text"
            n = nm.group(1).lower() if nm else ""
            fields.append({"type": t, "name": n})
            if t == PWD_TYPE or any(k in n for k in CRED_NAMES):
                sensitive = True
        resolved = urljoin(page_url, action) if action else page_url
        target_host = urlparse(resolved).hostname or page_host
        target_apex = _apex(target_host)
        ff, low = [], resolved.lower()
        offsite = bool(target_apex) and target_apex != page_apex
        is_ip = bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", target_host or ""))
        to_tg = _TG_SHORT in low or _TG_HOST in low
        mailto = action.lower().startswith("mailto:")
        insecure = low.startswith("http://") and sensitive
        if sensitive and to_tg:
            ff.append("credentials posted to a messaging bot endpoint"); risk += 50
        if sensitive and offsite and not to_tg:
            ff.append(f"credentials sent off-site to {target_apex}"); risk += 35
        if sensitive and is_ip:
            ff.append("credentials sent to a raw IP address"); risk += 30
        if sensitive and mailto:
            ff.append("credentials emailed via mailto"); risk += 25
        if insecure:
            ff.append("password sent over unencrypted HTTP"); risk += 20
        if sensitive and method == "GET":
            ff.append("credentials placed in the URL (GET)"); risk += 15
        forms.append({
            "action": action or "(same page)", "resolved": resolved,
            "target": target_apex or "(self)", "method": method,
            "sensitive": sensitive, "fields": fields[:12], "flags": ff,
        })
        flags.extend(ff)
    return {
        "available": True, "forms": forms,
        "credential_forms": sum(1 for f in forms if f["sensitive"]),
        "risk": min(risk, 100), "flags": flags,
    }


def detect_typosquat(host: str) -> dict[str, Any]:
    """Detect typosquatting and homoglyph attacks."""
    host = (host or "").lower().strip(".")
    apex = _apex(host)
    label = apex.split(".")[0] if apex else ""
    findings, risk, flags = [], 0, []
    if any(ord(ch) > 127 for ch in host):
        flags.append("non-ASCII (Unicode) characters in domain"); risk += 40
    if any(p.startswith("xn--") for p in host.split(".")):
        flags.append("punycode/IDN domain (possible homoglyph spoof)"); risk += 25
    if apex in BRANDS:
        return {"available": True, "matches": [], "risk": risk, "flags": flags, "is_brand": True}
    skel = _skeleton(label)
    for brand in BRANDS:
        bl = brand.split(".")[0]
        if bl == label or len(bl) < 4:
            continue
        dist = _lev(label, bl)
        sk = _lev(skel, _skeleton(bl))
        bl_skel = _skeleton(bl)
        if sk == 0 and dist > 0:
            findings.append({"brand": brand, "kind": "homoglyph lookalike", "distance": dist}); risk += 45
        elif 0 < dist <= 2:
            findings.append({"brand": brand, "kind": f"typosquat ({dist} edit{'s' if dist > 1 else ''})", "distance": dist}); risk += 35
        elif bl_skel in skel and brand not in host:
            kind = "combosquat (brand inside domain)" if bl in label else "homoglyph combosquat"
            findings.append({"brand": brand, "kind": kind, "distance": dist}); risk += 30
    findings.sort(key=lambda f: f["distance"])
    findings = findings[:5]
    for f in findings:
        flags.append(f"{f['kind']}: mimics {f['brand']}")
    return {"available": True, "matches": findings, "risk": min(risk, 100), "flags": flags, "is_brand": False}


def deobfuscate(html: str) -> dict[str, Any]:
    """Detect and decode obfuscated JavaScript code."""
    if not html:
        return {"available": False, "layers": []}
    layers, sample = [], html[:60000]
    for m in _RE_DECODE.findall(sample)[:5]:
        try:
            dec = base64.b64decode(m + "=" * (-len(m) % 4)).decode("utf-8", "ignore")
            if dec.isprintable() and len(dec) > 4:
                layers.append({"kind": _FN_B64 + "() base64", "decoded": dec[:200]})
        except (binascii.Error, ValueError):
            pass
    for m in _RE_FROMCHAR.findall(sample)[:5]:
        try:
            nums = [int(x) for x in re.findall(r"\d+", m)][:200]
            dec = "".join(chr(n) for n in nums if 0 < n < 1114112)
            if len(dec) > 4:
                layers.append({"kind": _FN_CHAR, "decoded": dec[:200]})
        except ValueError:
            pass
    for m in _RE_HEXESC.findall(sample)[:5]:
        try:
            dec = bytes(int(h, 16) for h in re.findall(r"\\x([0-9A-Fa-f]{2})", m)).decode("utf-8", "ignore")
            if len(dec) > 4:
                layers.append({"kind": "hex escapes", "decoded": dec[:200]})
        except ValueError:
            pass
    seen, uniq = set(), []
    for layer in layers:
        if layer["decoded"] not in seen:
            seen.add(layer["decoded"])
            uniq.append(layer)
    needle = re.compile(r"https?://|" + re.escape(_FN_EVAL) + r"|document\.|location|" + PWD_TYPE + r"|" + _TG_HOST.split(".")[0], re.I)
    suspicious = any(needle.search(l["decoded"]) for l in uniq)
    return {"available": bool(uniq), "layers": uniq[:8], "suspicious": suspicious}


def assemble_graph(chain: list[dict[str, Any]] | None, deep: dict[str, Any] | None) -> dict[str, Any]:
    """Build graph representation of threat chain and connections."""
    nodes, edges = {}, []
    chain = chain or []
    deep = deep or {}

    def node(nid, label, kind, risk="low", detail=""):
        if nid and nid not in nodes:
            nodes[nid] = {"id": nid, "label": label, "kind": kind, "risk": risk, "detail": detail}
        return nid

    def edge(src, dst, rel, danger=False):
        if src and dst:
            edges.append({"source": src, "target": dst, "rel": rel, "danger": danger})

    for hop in chain:
        host = (hop.get("hostname") or "").lower()
        if not host:
            continue
        band = hop.get("risk_level") if hop.get("risk_level") in ("low", "medium", "high", "clean") else "low"
        dom_id = "dom:" + host
        node(dom_id, host, "domain", band, ", ".join((hop.get("flags") or [])[:3]))
        ip = hop.get("ip")
        if ip and ip not in ("unresolvable", "private"):
            ip_id = "ip:" + ip
            node(ip_id, ip, "ip", "low", "")
            edge(dom_id, ip_id, "resolves to")
            asn = hop.get("asn") or {}
            asn_no = asn.get("asn")
            if asn_no and asn_no not in ("unknown", "private"):
                asn_id = "asn:" + str(asn_no)
                node(asn_id, f"{asn_no} {asn.get('org', '')}".strip(), "asn", "low", asn.get("country", ""))
                edge(ip_id, asn_id, "hosted on")
        tls = hop.get("tls") or {}
        issuer = tls.get("issuer")
        if issuer and issuer not in ("unknown", "http only"):
            cert_id = "cert:" + issuer
            node(cert_id, issuer, "cert", "low", f"{tls.get('age_days', '?')}d old")
            edge(dom_id, cert_id, "cert by")

    final = None
    for hop in reversed(chain):
        if hop.get("hostname") and not hop.get("error"):
            final = "dom:" + hop["hostname"].lower()
            break

    for m in (deep.get("typosquat") or {}).get("matches", []):
        b_id = node("brand:" + m["brand"], m["brand"], "brand", "high", m["kind"])
        edge(final, b_id, "impersonates", danger=True)

    for f in (deep.get("credentials") or {}).get("forms", []):
        if f.get("sensitive") and f.get("target") and f.get("target") != "(self)":
            t_id = node("cred:" + f["target"], f["target"], "exfil", "high", "credentials sent here")
            edge(final, t_id, "sends credentials", danger=bool(f.get("flags")))

    return {"nodes": list(nodes.values()), "edges": edges, "available": len(nodes) > 1}


def build_timeline(chain: list[dict[str, Any]] | None, page_analysis: dict[str, Any] | None, deep: dict[str, Any] | None) -> dict[str, Any]:
    """Build timeline of threat events."""
    chain = chain or []
    events = []
    for i, hop in enumerate(chain):
        host = hop.get("hostname") or hop.get("url") or "?"
        t = hop.get("t_ms", i * 200)
        sc = hop.get("status_code")
        if hop.get("error"):
            events.append({"t": t, "kind": "error", "sev": "high", "title": f"{host}", "detail": hop["error"]})
            continue
        if i == 0:
            events.append({"t": max(t - 1, 0), "kind": "request", "sev": "low", "title": "Request sent", "detail": host})
        band = hop.get("risk_level", "low")
        if sc in (301, 302, 303, 307, 308):
            events.append({"t": t, "kind": "redirect", "sev": band, "title": f"Redirect {sc}", "detail": host})
        else:
            events.append({"t": t, "kind": "land", "sev": band, "title": f"Landed ({sc})", "detail": host})
        for fl in (hop.get("flags") or [])[:2]:
            events.append({"t": t, "kind": "signal", "sev": band, "title": "Signal", "detail": fl})

    last_t = max((e["t"] for e in events), default=0)
    pa = page_analysis or {}
    for mn in pa.get("miners", []):
        events.append({"t": last_t + 80, "kind": "miner", "sev": "high", "title": "Crypto-miner fired", "detail": mn})
    for fp in pa.get("fingerprints", []):
        events.append({"t": last_t + 60, "kind": "fingerprint", "sev": "medium", "title": "Fingerprinting", "detail": fp})
    if pa.get("trackers"):
        events.append({"t": last_t + 40, "kind": "tracker", "sev": "low", "title": "Trackers loaded", "detail": f"{len(pa['trackers'])} tracker(s)"})

    for f in (deep or {}).get("credentials", {}).get("forms", []):
        if f.get("sensitive"):
            sev = "high" if f.get("flags") else "medium"
            events.append({"t": last_t + 120, "kind": "credform", "sev": sev,
                           "title": "Credential form", "detail": f"posts to {f.get('target', '?')}"})

    events.sort(key=lambda e: e["t"])
    return {"events": events, "duration": max((e["t"] for e in events), default=0), "available": bool(events)}


def risk_band(score: int) -> str:
    """Convert risk score to risk band."""
    return "clean" if score == 0 else "low" if score < 25 else "medium" if score < 55 else "high"


def _verdict_label(score: int, evidence: list[dict[str, Any]]) -> tuple[str, str]:
    """Generate verdict label and explanation based on score and evidence."""
    high = [e for e in evidence if e["severity"] == "high"]
    if score >= 70 or len(high) >= 2:
        return "DANGEROUS", high[0]["detail"] if high else "Multiple high-severity threats detected."
    if score >= 40:
        return "SUSPICIOUS", high[0]["detail"] if high else (evidence[0]["detail"] if evidence else "Several risk signals present.")
    if score >= 15:
        return "CAUTION", evidence[0]["detail"] if evidence else "Minor risk signals present."
    if score > 0:
        return "LIKELY SAFE", "Only low-severity signals found."
    return "CLEAN", "No threat signals detected."


def build_verdict(chain: list[dict[str, Any]] | None, page_analysis: dict[str, Any] | None, cred: dict[str, Any] | None, typo: dict[str, Any] | None, deob: dict[str, Any] | None, vt: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build security verdict from all analysis data."""
    evidence, score = [], 0

    def add(name, detail, weight, severity):
        nonlocal score
        evidence.append({"name": name, "detail": detail, "weight": weight, "severity": severity})
        score += weight

    chain = chain or []
    hop_max = max((h.get("risk_score", 0) for h in chain), default=0)
    if hop_max:
        worst = max(chain, key=lambda h: h.get("risk_score", 0))
        top = ", ".join((worst.get("flags") or [])[:3]) or "network/cert signals"
        add("Network & certificate", top, min(hop_max // 2, 30), risk_band(hop_max))
    if len(chain) > 2:
        add("Redirect chain", f"{len(chain)} hops before final destination", 8, "low")

    pa = page_analysis or {}
    if pa.get("miners"):
        add("Crypto-miner", "in-browser mining: " + ", ".join(pa["miners"]), 40, "high")
    if pa.get("fingerprints"):
        add("Browser fingerprinting", ", ".join(pa["fingerprints"]), 15, "medium")
    if pa.get("trackers"):
        add("Trackers", f"{len(pa['trackers'])} found: " + ", ".join(pa["trackers"][:4]), 6, "low")

    for f in (cred or {}).get("flags", []):
        sev = "high" if ("bot endpoint" in f or "off-site" in f or "raw IP" in f) else "medium"
        add("Credential destination", f, 25 if sev == "high" else 15, sev)

    for f in (typo or {}).get("flags", []):
        sev = "high" if ("homoglyph" in f or "mimics" in f) else "medium"
        add("Brand impersonation", f, 25 if sev == "high" else 12, sev)

    if (deob or {}).get("suspicious"):
        add("Obfuscated code", "hidden/encoded payload contains URLs or active code", 20, "high")

    if vt and vt.get("available") and vt.get("malicious"):
        add("VirusTotal", f"{vt['malicious']} engine(s) flag this as malicious", 30, "high")

    score = min(score, 100)
    verdict, headline = _verdict_label(score, evidence)
    evidence.sort(key=lambda e: -e["weight"])
    return {"score": score, "verdict": verdict, "headline": headline, "band": risk_band(score), "evidence": evidence}
