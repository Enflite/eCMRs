#!/usr/bin/env python3
"""Builds the eCMRs help pages (docs/help/) from scripts/help_content.py.

Structure of the SyteLine help library - a toolbar (Home, Back, Forward, Print), a navigation
tree on the left, one topic for the form (index.html) and one per field (fields/<key>.html) with
Related topics - in the Enflite brand style used by the plan deck (plan/): white pages, generous
whitespace, Segoe UI Light titles beside a red rounded icon badge, Calibri body, small red
uppercase section labels, square bullets, red outlined step numbers, thin divider rules, Ink
table headers, one thin red arc; no cards, no shadows. Rules:
Enflite/Form-Project-Templates branding/enflite-style-guide.md.

Plain static HTML with relative links, so the folder works from anywhere: copy the contents of
docs/help/ to the shared drive (S:\Engineering\Individual Folders\JSmith\eCMRs). The form's
Help button opens them (HELP_BASE in tools/apply_form_changes.py). Page addresses never
change with the styling.

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
ASSETS = {  # published name -> source (the deck's own brand files)
    "enflite-logo.png": os.path.join(ROOT, "plan", "brand", "enflite-logo.png"),
    "icon-form.png": os.path.join(ROOT, "plan", "icons", "i1_white.png"),   # clipboard: the form
    "icon-field.png": os.path.join(ROOT, "plan", "icons", "i3_white.png"),  # tag: a field
}
BY_KEY = {f["key"]: f for f in FIELDS}
SECTION_NAME = dict(SECTIONS)
e = lambda s: html.escape(s, quote=True)

CSS = """/* Enflite brand (plan deck / style guide): Black, White, Red - red used sparingly. */
:root{--red:#CF0C2C;--ink:#1A1A1A;--charcoal:#252525;--body:#4A4A4A;--line:#E5E5E5;--light:#F7F7F7;--white:#FFFFFF}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{font-family:Calibri,"Segoe UI",Carlito,Arial,sans-serif;font-size:16px;line-height:1.6;color:var(--body);background:var(--white)}
a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}a:hover{border-bottom-color:var(--red)}
.display{font-family:"Segoe UI Light","Segoe UI","Open Sans",Calibri,sans-serif;font-weight:300;color:var(--ink)}
/* top: logo, library name, thin rule */
header.top{display:flex;align-items:center;gap:22px;height:72px;padding:0 40px;border-bottom:1px solid var(--line)}
header.top img{height:26px}
header.top .lib{font-family:"Segoe UI Light","Segoe UI","Open Sans",sans-serif;font-weight:300;font-size:19px;color:var(--ink)}
header.top .lib b{font-weight:600}
/* toolbar: thin uppercase labels, no fill */
nav.tools{display:flex;align-items:center;gap:30px;height:50px;padding:0 40px;border-bottom:1px solid var(--line);
  font-size:12.5px;letter-spacing:.12em;text-transform:uppercase}
nav.tools a,nav.tools button{color:var(--ink);background:none;border:0;font:inherit;letter-spacing:inherit;text-transform:inherit;cursor:pointer;padding:0}
nav.tools a:hover,nav.tools button:hover{color:var(--red)}
nav.tools .spacer{flex:1}
nav.tools .print{border:1px solid var(--ink);padding:6px 16px}
.wrap{display:flex;height:calc(100% - 123px)}
/* navigation tree: plain list, thin rules, current item marked by a thin red rule */
aside{width:300px;min-width:300px;overflow:auto;border-right:1px solid var(--line);padding:26px 0 40px}
aside .eyebrow{padding:0 28px 10px}
aside ul{list-style:none;margin:0;padding:0}
aside a{display:block;border:0;padding:6px 28px 6px 44px;font-size:14.5px;color:var(--body)}
aside a:hover{color:var(--ink)}
aside a.cur{color:var(--ink);box-shadow:inset 2px 0 0 var(--red)}
aside a.top{padding-left:28px;color:var(--ink)}
aside details{border-top:1px solid var(--line)}
aside summary{cursor:pointer;list-style:none;padding:10px 28px;color:var(--ink);font-size:15px}
aside summary::-webkit-details-marker{display:none}
aside summary::after{content:"+";float:right;color:var(--body)}aside details[open] summary::after{content:"\\2212"}
/* topic */
main{flex:1;overflow:auto;position:relative}
main .arc{position:absolute;right:-220px;top:-260px;width:520px;height:520px;border:1px solid var(--red);border-radius:50%;pointer-events:none}
main .inner{position:relative;max-width:800px;padding:54px 64px 80px}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
.head{display:flex;align-items:center;gap:26px;margin:14px 0 34px}
.badge{flex:none;width:76px;height:76px;border-radius:12px;background:var(--red);display:flex;align-items:center;justify-content:center}
.badge img{width:40px;height:40px}
h1{font-family:"Segoe UI Light","Segoe UI","Open Sans",sans-serif;font-weight:300;font-size:40px;line-height:1.15;color:var(--ink);margin:0}
.sub{font-size:16.5px;color:var(--body);margin-top:6px}
h2{font-family:"Segoe UI Light","Segoe UI","Open Sans",sans-serif;font-weight:300;font-size:25px;color:var(--ink);
  margin:44px 0 14px;padding-top:26px;border-top:1px solid var(--line)}
h3{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--ink);margin:28px 0 10px}
p{margin:0 0 14px}b{color:var(--ink);font-weight:700}
/* square bullets, as in the deck */
ul.sq{list-style:none;margin:0 0 16px;padding:0}
ul.sq li{position:relative;padding-left:24px;margin:5px 0}
ul.sq li::before{content:"";position:absolute;left:2px;top:.62em;width:7px;height:7px;background:var(--ink)}
/* numbered steps: red outlined circles */
ol.steps{list-style:none;counter-reset:s;margin:0 0 10px;padding:0}
ol.steps li{counter-increment:s;position:relative;padding:4px 0 14px 50px;min-height:40px}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:0;width:32px;height:32px;border:1px solid var(--red);
  border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;color:var(--ink)}
/* field list on the form topic: thin rules, no boxes */
dl.fields{margin:0}dl.fields div{padding:12px 0;border-bottom:1px solid var(--line)}
dl.fields dt{margin:0}dl.fields dt a{font-weight:700;font-size:16.5px;border:0}dl.fields dt a:hover{color:var(--red)}
dl.fields dd{margin:2px 0 0}
/* tables: Ink header, white rows, thin rules */
table{border-collapse:collapse;margin:8px 0 20px;font-size:14.5px;width:100%}
th{background:var(--ink);color:var(--white);font-weight:400;padding:8px 12px;text-align:center}
td{padding:7px 12px;border-bottom:1px solid var(--line);text-align:center;color:var(--ink)}
th:first-child,td:first-child{text-align:left}
.meta{margin-top:34px;font-size:13.5px;color:var(--body)}
.related a{display:table;margin:6px 0}
footer{margin-top:60px;padding-top:18px;border-top:1px solid var(--line);font-size:12.5px;color:var(--body)}
@media print{header.top,nav.tools,aside,main .arc{display:none}.wrap{display:block;height:auto}main .inner{padding:0}}
@media (max-width:820px){aside{display:none}main .inner{padding:30px 16px 60px}header.top,nav.tools{padding:0 16px}h1{font-size:32px}}
"""


def page(title, head, body, rel, current):
    """One help page. head = (eyebrow, title, subtitle, icon); rel = '' or '../'."""
    eyebrow, h1, sub, icon = head
    nav = [f'<div class="eyebrow">eCMRs help</div><ul><li><a class="top{" cur" if current == "index" else ""}" '
           f'href="{rel}index.html">eCMRs form</a></li></ul>']
    for sid, sname in SECTIONS:
        items = [f for f in FIELDS if f["section"] == sid]
        is_open = any(f["key"] == current for f in items)
        links = "".join(f'<li><a{" class=cur" if f["key"] == current else ""} '
                        f'href="{rel}fields/{f["key"]}.html">{e(f["label"])}</a></li>' for f in items)
        nav.append(f'<details{" open" if is_open else ""}><summary>{e(sname)}</summary><ul>{links}</ul></details>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | eCMRs Help | Enflite</title><link rel="stylesheet" href="{rel}help.css"></head>
<body>
<header class="top"><img src="{rel}enflite-logo.png" alt="Enflite"><span class="lib">SyteLine <b>Help</b></span></header>
<nav class="tools"><a href="{rel}index.html">Home</a><button onclick="history.back()">&larr; Back</button><button onclick="history.forward()">Forward &rarr;</button><span class="spacer"></span><button class="print" onclick="window.print()">Print</button></nav>
<div class="wrap"><aside>{''.join(nav)}</aside>
<main><div class="arc"></div><div class="inner">
<div class="eyebrow">{e(eyebrow)}</div>
<div class="head"><div class="badge"><img src="{rel}{icon}" alt=""></div><div><h1>{e(h1)}</h1><div class="sub">{e(sub)}</div></div></div>
{body}
<footer>Enflite &middot; eCMRs help &middot; SyteLine (Infor CloudSuite)</footer>
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
    sec = SECTION_NAME[f["section"]]
    b = [f"<p>{bold_names(t)}</p>" for t in f["text"]]
    if f.get("filled"):
        b.append(f"<h3>How it's filled</h3><p>{bold_names(f['filled'])}</p>")
    if f.get("values"):
        b.append("<h3>Valid values</h3><ul class=sq>" + "".join(f"<li>{e(v)}</li>" for v in f["values"]) + "</ul>")
    if f.get("table"):
        head, rows = f["table"]
        b.append("<table><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>" +
                 "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>")
    rel = ['<a href="../index.html">eCMRs form</a>'] + \
          [f'<a href="{k}.html">{e(BY_KEY[k]["label"])}</a>' for k in f.get("related", [])]
    b.append('<h2>Related topics</h2><div class="related">' + "".join(rel) + "</div>")
    b.append(f'<p class="meta">Form: eCMRs &middot; Section: {e(sec)}</p>')
    return page(f["label"], (sec, f["label"], "Field on the eCMRs form", "icon-field.png"),
                "\n".join(b), "../", f["key"])


def index_page():
    b = [f"<p>{bold_names(t)}</p>" for t in FORM["intro"]]
    b.append("<h2>Working a <b>CMR</b></h2><ol class=steps>" +
             "".join(f"<li>{bold_names(t)}</li>" for t in FORM["howto"]) + "</ol>")
    for sid, sname in SECTIONS:
        items = [f for f in FIELDS if f["section"] == sid]
        b.append(f"<h2>{e(sname)}</h2><dl class=fields>" + "".join(
            f'<div><dt><a href="fields/{f["key"]}.html">{e(f["label"])}</a></dt><dd>{bold_names(f["text"][0])}</dd></div>'
            for f in items) + "</dl>")
    return page("eCMRs", ("Quality · Change management", "eCMRs",
                          "Change Management Requests: create, track and close a CMR on one form.", "icon-form.png"),
                "\n".join(b), "", "index")


def build():
    files = {"index.html": index_page(), "help.css": CSS}
    for f in FIELDS:
        files[f"fields/{f['key']}.html"] = field_page(f)
    files = {k: v.encode("utf-8") for k, v in files.items()}
    for name, src in ASSETS.items():
        files[name] = open(src, "rb").read()
    return files


def main():
    files = build()
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
