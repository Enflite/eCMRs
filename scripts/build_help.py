#!/usr/bin/env python3
"""Builds the eCMRs help pages (docs/help/) from scripts/help_content.py.

Laid out like the SyteLine help library: a top bar, a toolbar (Home, Back, Forward, Print), a
navigation tree on the left and the topic on the right - one topic for the form (index.html)
and one per field (fields/<key>.html), with Related topics. Enflite-branded, plain static HTML
with relative links, so the folder works from any web host (SharePoint, intranet, GitHub
Pages). The form's right-click -> Help opens these pages once HELP_BASE is set in
tools/apply_form_changes.py.

Run: python3 scripts/build_help.py          (writes docs/help/)
     python3 scripts/build_help.py --check  (fails if docs/help/ is out of date)
"""
import html
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from help_content import FIELDS, FORM, SECTIONS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "help")
LOGO_SRC = os.path.join(ROOT, "plan", "brand", "enflite-logo.png")
BY_KEY = {f["key"]: f for f in FIELDS}
e = lambda s: html.escape(s, quote=True)

CSS = """:root{--ink:#1A1A1A;--body:#3c3c3c;--muted:#6b6b6b;--line:#e1e1e1;--bar:#f1f2f4;--link:#0a5ca8;--red:#CF0C2C}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{font-family:"Segoe UI",Arial,Helvetica,sans-serif;color:var(--body);background:#fff;font-size:15px;line-height:1.55}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
header.top{display:flex;align-items:center;gap:18px;height:60px;padding:0 18px;border-bottom:1px solid var(--line)}
header.top img{height:26px}header.top .lib{font-size:17px;color:var(--ink)}header.top .sep{color:#bbb}
header.top .mod{font-size:17px;color:var(--ink)}
nav.tools{display:flex;align-items:center;gap:22px;height:58px;padding:0 22px;background:var(--bar);font-size:14.5px;color:var(--ink)}
nav.tools a,nav.tools button{color:var(--ink);background:none;border:0;font:inherit;cursor:pointer;padding:0}
nav.tools .spacer{flex:1}
.wrap{display:flex;height:calc(100% - 118px)}
aside{width:330px;min-width:330px;overflow:auto;border-right:1px solid var(--line);padding:14px 0}
aside .grp{padding:9px 22px;font-weight:600;color:var(--ink);border-bottom:1px solid var(--line)}
aside ul{list-style:none;margin:0;padding:0}aside li a{display:block;padding:6px 22px 6px 40px;color:var(--ink);border-bottom:1px solid #f0f0f0;font-size:14px}
aside li a.cur{background:#eef3f9;font-weight:600}
aside details summary{cursor:pointer;padding:8px 22px;color:var(--ink);border-bottom:1px solid var(--line);list-style:none}
aside details summary::before{content:"+ ";color:var(--muted)}aside details[open] summary::before{content:"\\2212  "}
main{flex:1;overflow:auto;padding:40px 60px 60px}
main .inner{max-width:760px}
h1{font-weight:400;font-size:26px;color:var(--ink);margin:18px 0 26px}
h2{font-weight:400;font-size:19px;color:var(--ink);margin:26px 0 8px}
p{margin:0 0 12px}
.meta{color:var(--muted);font-size:13.5px;margin-bottom:22px}
table{border-collapse:collapse;margin:6px 0 16px;font-size:14px}th,td{border:1px solid var(--line);padding:5px 10px;text-align:center}
th:first-child,td:first-child{text-align:left}th{background:var(--bar);font-weight:600;color:var(--ink)}
ul.plain{margin:0 0 12px 18px;padding:0}ol{margin:0 0 12px 18px;padding:0}
.related a{display:block;margin:2px 0 2px 10px}
.fieldlist dt{font-weight:600;color:var(--ink);margin-top:10px}.fieldlist dd{margin:0 0 4px 0}
@media print{header.top,nav.tools,aside{display:none}.wrap{display:block;height:auto}main{padding:0}}
@media (max-width:760px){aside{display:none}main{padding:24px 16px}}
"""


def page(title, body, rel, current):
    """One help page. rel = path prefix back to the help root ('' or '../')."""
    nav = []
    nav.append(f'<div class="grp">eCMRs</div><ul><li><a href="{rel}index.html"'
               f'{" class=cur" if current == "index" else ""}>eCMRs form</a></li></ul>')
    for sid, sname in SECTIONS:
        items = [f for f in FIELDS if f["section"] == sid]
        is_open = any(f["key"] == current for f in items)
        links = "".join(f'<li><a href="{rel}fields/{f["key"]}.html"'
                        f'{" class=cur" if f["key"] == current else ""}>{e(f["label"])}</a></li>'
                        for f in items)
        nav.append(f'<details{" open" if is_open else ""}><summary>{e(sname)}</summary><ul>{links}</ul></details>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} - eCMRs Help</title><link rel="stylesheet" href="{rel}help.css"></head>
<body>
<header class="top"><img src="{rel}enflite-logo.png" alt="Enflite"><span class="lib">SyteLine User Help (Enflite forms)</span><span class="sep">|</span><span class="mod">eCMRs</span></header>
<nav class="tools"><a href="{rel}index.html">&#8962; Home</a><button onclick="history.back()">&larr; Back</button><button onclick="history.forward()">Forward &rarr;</button><span class="spacer"></span><button onclick="window.print()">Print</button></nav>
<div class="wrap"><aside>{''.join(nav)}</aside>
<main><div class="inner">
{body}
</div></main></div>
</body></html>
"""


def bold_names(text):
    """Bold the names of fields and forms in running text, like the SyteLine help does."""
    names = sorted({f["label"] for f in FIELDS if len(f["label"]) < 30} |
                   {"New", "Create Change Request", "Change Request Management", "QC CMRs", "QC MRRs",
                    "Requirement checkboxes", "Item Desc", "Dept Description", "WC Description",
                    "Next Assy Desc", "Vendor Name", "Reviewer ID", "Close Date", "Closed By"},
                   key=len, reverse=True)
    out, i = [], 0
    s = e(text)
    while i < len(s):
        for n in names:
            en = e(n)
            before = s[i - 1] if i else " "
            after = s[i + len(en)] if i + len(en) < len(s) else " "
            if s.startswith(en, i) and not before.isalnum() and not after.isalnum():
                out.append(f"<b>{en}</b>")
                i += len(en)
                break
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def field_page(f):
    b = [f"<h1>{e(f['label'])}</h1>"]
    for t in f["text"]:
        b.append(f"<p>{bold_names(t)}</p>")
    if f.get("filled"):
        b.append(f"<p>{bold_names(f['filled'])}</p>")
    if f.get("values"):
        b.append("<p>Valid values:</p><ul class=plain>" +
                 "".join(f"<li>{e(v)}</li>" for v in f["values"]) + "</ul>")
    if f.get("table"):
        head, rows = f["table"]
        b.append("<table><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>" +
                 "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>")
    sec = dict(SECTIONS)[f["section"]]
    b.append(f'<p class="meta">Form: <a href="../index.html">eCMRs</a> &middot; Section: {e(sec)}</p>')
    rel = [f'<a href="../index.html">eCMRs form</a>'] + \
          [f'<a href="{k}.html">{e(BY_KEY[k]["label"])}</a>' for k in f.get("related", [])]
    b.append('<h2>Related topics</h2><div class="related">' + "".join(rel) + "</div>")
    return page(f["label"], "\n".join(b), "../", f["key"])


def index_page():
    b = [f"<h1>{e(FORM['title'])}</h1>"]
    b += [f"<p>{bold_names(t)}</p>" for t in FORM["intro"]]
    b.append("<h2>Working a CMR</h2><ol>" + "".join(f"<li>{bold_names(t)}</li>" for t in FORM["howto"]) + "</ol>")
    for sid, sname in SECTIONS:
        items = [f for f in FIELDS if f["section"] == sid]
        b.append(f"<h2>{e(sname)}</h2><dl class=fieldlist>" + "".join(
            f'<dt><a href="fields/{f["key"]}.html">{e(f["label"])}</a></dt><dd>{bold_names(f["text"][0])}</dd>'
            for f in items) + "</dl>")
    b.append('<h2>Related topics</h2><div class="related"><span>Enflite/eCMRs (GitHub): implementation plan and troubleshooting</span></div>')
    return page("eCMRs", "\n".join(b), "", "index")


def build():
    files = {"index.html": index_page(), "help.css": CSS}
    for f in FIELDS:
        files[f"fields/{f['key']}.html"] = field_page(f)
    return {k: v.encode("utf-8") for k, v in files.items()}


def main():
    files = build()
    logo = open(LOGO_SRC, "rb").read()
    files["enflite-logo.png"] = logo
    if "--check" in sys.argv:
        stale = [k for k, v in files.items()
                 if not os.path.exists(os.path.join(OUT, k)) or open(os.path.join(OUT, k), "rb").read() != v]
        extra = []
        if os.path.isdir(os.path.join(OUT, "fields")):
            want = {k for k in files if k.startswith("fields/")}
            extra = [f"fields/{n}" for n in os.listdir(os.path.join(OUT, "fields")) if f"fields/{n}" not in want]
        if stale or extra:
            raise SystemExit(f"docs/help out of date: {', '.join(stale + extra)} - re-run without --check")
        print(f"OK: docs/help is up to date ({len(FIELDS)} field pages)")
        return
    if os.path.isdir(os.path.join(OUT, "fields")):
        shutil.rmtree(os.path.join(OUT, "fields"))
    for k, v in files.items():
        p = os.path.join(OUT, k)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(v)
    print(f"Wrote docs/help/: index.html + {len(FIELDS)} field pages")


if __name__ == "__main__":
    main()
