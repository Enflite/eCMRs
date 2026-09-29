#!/usr/bin/env python3
"""Builds the eCMRs help pages (docs/help/) from scripts/help_content.py.

Structure of the SyteLine help library - a toolbar (Home, Back, Forward, Print), a navigation
tree on the left, one topic for the form (index.html), one per field (fields/<key>.html) with
Related topics, and the updated quality procedures (procedures/, from scripts/procedures_content.py) - in the Enflite brand style used by the plan deck (plan/): white pages, generous
whitespace, Segoe UI Light titles beside a red rounded icon badge, Calibri body, small red
uppercase section labels, square bullets, red outlined step numbers, thin divider rules, Ink
table headers, one thin red arc; no cards, no shadows. Rules:
Enflite/Form-Project-Templates branding/enflite-style-guide.md.

Plain static HTML with relative links, so the folder works from anywhere (e.g. a copy on the
shared drive S:/Engineering/Individual Folders/JSmith/eCMRs/docs/help). The form's Help button opens
index.html there (HELP_BUTTON_URL in tools/apply_form_changes.py); right-click -> Help stays on
Infor's QC CMRs topic, because SyteLine only opens Infor's help site from it.

Run: python3 scripts/build_help.py          (writes docs/help/)
     python3 scripts/build_help.py --check  (fails if docs/help/ is out of date)
"""
import html
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from help_content import FIELDS, FORM, SECTIONS
from procedures_content import NOTICE, PROCEDURES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "help")
ASSETS = {  # published name -> source (the deck's own brand files)
    "enflite-logo.png": os.path.join(ROOT, "plan", "brand", "enflite-logo.png"),
    "icon-form.png": os.path.join(ROOT, "plan", "icons", "i1_white.png"),   # clipboard: the form
    "icon-field.png": os.path.join(ROOT, "plan", "icons", "i3_white.png"),  # tag: a field
    "icon-procedure.png": os.path.join(ROOT, "plan", "icons", "i8_white.png"),  # layers: a procedure
}
ORIGINALS = os.path.join(ROOT, "docs", "reference", "procedures")  # released PDFs, linked from each page
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
/* procedures: document block, numbered steps with a hanging number, changed steps on a thin red rule */
dl.doc{display:grid;grid-template-columns:max-content 1fr;gap:4px 22px;margin:0 0 18px;font-size:14.5px}
dl.doc dt{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--ink);padding-top:2px}
dl.doc dd{margin:0;color:var(--ink)}
.notice{font-size:13.5px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:10px 0;margin:0 0 20px}
.proc h3{margin-top:30px}
.step{display:grid;grid-template-columns:92px 1fr;gap:0 10px;padding:7px 0 7px 14px;border-left:2px solid transparent}
.step .n{font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}
.step.l2{padding-left:34px}.step.l3{padding-left:54px}.step.l4{padding-left:74px}
.step.changed,.step.removed,.step.added{border-left-color:var(--red)}
.step .tag{display:block;font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--red);margin-bottom:2px}
.step .was,.step .why{display:block;font-size:13.5px;margin-top:6px}
.step .was s,.step.removed .was{color:var(--body)}
.step .lbl{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--ink);margin-right:6px}
.legend{font-size:13.5px;margin:0 0 10px}.legend i{display:inline-block;width:14px;height:14px;vertical-align:-2px;border-left:2px solid var(--red);margin-right:6px}
td.l,th.l{text-align:left}
svg.flow{display:block;max-width:560px;margin:10px 0 20px}
svg.flow text{font-family:Calibri,"Segoe UI",Carlito,Arial,sans-serif;font-size:13px;fill:#1A1A1A}
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
    is_open = current == "procedures" or any(p["key"] == current for p in PROCEDURES)
    links = f'<li><a{" class=cur" if current == "procedures" else ""} href="{rel}procedures/index.html">All procedures</a></li>' + \
        "".join(f'<li><a{" class=cur" if p["key"] == current else ""} href="{rel}procedures/{p["key"]}.html">'
                f'{e(p["number"])} {e(p["title"])}</a></li>' for p in PROCEDURES)
    nav.append(f'<details{" open" if is_open else ""}><summary>Procedures</summary><ul>{links}</ul></details>')
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
    b.append("<h2>Procedures</h2><dl class=fields>" + "".join(
        f'<div><dt><a href="procedures/{p["key"]}.html">{e(p["number"])} {e(p["title"])}</a></dt>'
        f'<dd>Rev {e(p["rev_new"])}, updated for the eCMRs form.</dd></div>' for p in PROCEDURES) + "</dl>")
    return page("eCMRs", ("Quality · Change management", "eCMRs",
                          "Change Management Requests: create, track and close a CMR on one form.", "icon-form.png"),
                "\n".join(b), "", "index")


FLOW_SVG = """<svg class="flow" viewBox="0 0 560 330" role="img" aria-label="Flowchart: Problem Identified, then Inventory Transaction? Yes: Create MRR. No: Production Technician Error? Yes: Create TRR. No: Create CMR (eCMRs).">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#1A1A1A"/></marker></defs>
<g fill="none" stroke="#1A1A1A" stroke-width="1">
<rect x="10" y="30" width="120" height="70"/>
<path d="M255,20 L315,65 L255,110 L195,65 Z"/>
<rect x="395" y="45" width="140" height="40" rx="20"/>
<path d="M255,155 L315,200 L255,245 L195,200 Z"/>
<rect x="395" y="180" width="140" height="40" rx="20" stroke="#CF0C2C" stroke-width="1.5"/>
<rect x="185" y="285" width="140" height="40" rx="20"/>
<path d="M130,65 H193" marker-end="url(#ar)"/><path d="M315,65 H393" marker-end="url(#ar)"/>
<path d="M255,110 V153" marker-end="url(#ar)"/><path d="M315,200 H393" marker-end="url(#ar)"/>
<path d="M255,245 V283" marker-end="url(#ar)"/></g>
<text x="70" y="69" text-anchor="middle">Problem Identified</text>
<text x="255" y="61" text-anchor="middle">Inventory</text><text x="255" y="76" text-anchor="middle">Transaction?</text>
<text x="465" y="69" text-anchor="middle">Create MRR</text>
<text x="255" y="189" text-anchor="middle">Production</text><text x="255" y="204" text-anchor="middle">Technician</text><text x="255" y="219" text-anchor="middle">Error?</text>
<text x="465" y="197" text-anchor="middle">Create CMR</text><text x="465" y="212" text-anchor="middle" font-size="11">(eCMRs)</text>
<text x="255" y="309" text-anchor="middle">Create TRR</text>
<text x="352" y="59" text-anchor="middle" font-size="11">YES</text><text x="262" y="137" font-size="11">NO</text>
<text x="352" y="194" text-anchor="middle" font-size="11">NO</text><text x="262" y="270" font-size="11">YES</text>
</svg>"""


def step_html(num, text, kind, was, why):
    level = min(num.rstrip(".").count("."), 4)
    cls = f"step l{level}" + (f" {kind}" if kind else "")
    body = ""
    if kind:
        body += f'<span class="tag">{"Removed" if kind == "removed" else kind.capitalize()}</span>'
    if text:
        body += bold_names(text)
    if was:
        body += f'<span class="was"><span class="lbl">Rev was</span>{"<s>" + e(was) + "</s>" if kind == "removed" else e(was)}</span>'
    if why:
        body += f'<span class="why"><span class="lbl">Why</span>{e(why)}</span>'
    return f'<div class="{cls}"><span class="n">{e(num)}</span><div>{body}</div></div>'


def procedure_page(p):
    changed = [x for x in p["procedure"] if x[0] != "h" and x[2]] + [d for d in p["definitions"] if d[2]]
    b = [f'<p>{e(p["summary"])}</p>',
         f'<dl class="doc"><dt>Document number</dt><dd>{e(p["number"])}</dd>'
         f'<dt>Title</dt><dd>{e(p["title"])}</dd>'
         f'<dt>Current revision</dt><dd>{e(p["rev_old"])}, issued {e(p["issued_old"])} '
         f'(<a href="{e(p["number"])}_Rev_{e(p["rev_old"])}.pdf">released PDF</a>)</dd>'
         f'<dt>This revision</dt><dd>{e(p["rev_new"])} &middot; for review, not released</dd></dl>',
         '<p class="notice">' + " ".join(e(n) for n in NOTICE) +
         (" Company private: see the proprietary notice on the cover page of the released document."
          if p["company_private"] else "") + "</p>",
         '<p class="legend"><i></i>Steps changed for the eCMRs form. <b>Rev was</b> shows the wording in the '
         'current revision.</p>']
    # changes summary
    b.append("<h2>Changes from the current revision</h2><table><tr><th class=l>Step</th><th class=l>Change</th></tr>" +
             "".join(f'<tr><td class=l>{e(x[0])}</td><td class=l>{"Removed. " if x[2] == "removed" else ""}{e(x[4])}</td></tr>'
                     for x in changed) + "</table>")
    if p["review"]:
        b.append("<h3>For the team to review</h3><ul class=sq>" + "".join(f"<li>{bold_names(r)}</li>" for r in p["review"]) + "</ul>")
    # revision log
    b.append("<h2>I. Revision log</h2><table><tr><th>Rev</th><th class=l>Description</th><th>Date</th><th>Prepared</th>"
             "<th>Checked</th><th>Approved</th><th>Regulatory</th></tr>" +
             "".join("<tr>" + "".join(f'<td{" class=l" if i == 1 else ""}>{e(c)}</td>' for i, c in enumerate(r)) + "</tr>"
                     for r in p["revlog"]) + "</table>")
    b.append('<div class="proc">')
    b.append("<h2>1. Scope</h2>" + "".join(f"<p>{e(t)}</p>" for t in p["scope"].split("\n")))
    b.append(f"<h2>2. Purpose</h2><p>{e(p['purpose'])}</p>")
    b.append("<h2>3. Reference</h2><table>" +
             "".join(f"<tr><td class=l>{e(a)}</td><td class=l>{e(t)}</td></tr>" for a, t in p["references"]) + "</table>")
    b.append("<h2>4. Definitions</h2>" +
             "".join(step_html(term, text, kind, was, why) for term, text, kind, was, why in p["definitions"]))
    b.append(f'<h2>{e(p.get("procedure_title", "5. Procedure"))}</h2>')
    for x in p["procedure"]:
        b.append(f"<h3>{e(x[1])}</h3>" if x[0] == "h" else step_html(*x))
    if p["flowchart"]:
        b.append("<h2>6. Flowchart</h2><p>Unchanged, except that <b>Create CMR</b> is marked as the <b>eCMRs</b> form.</p>" + FLOW_SVG)
    b.append("</div>")
    b.append('<h2>Related topics</h2><div class="related"><a href="index.html">All procedures</a>'
             '<a href="../index.html">eCMRs form</a>' +
             "".join(f'<a href="{q["key"]}.html">{e(q["number"])} {e(q["title"])}</a>' for q in PROCEDURES if q is not p) +
             "</div>")
    return page(f'{p["number"]} {p["title"]}', (f'Procedure · {p["number"]} · Rev {p["rev_new"]}', p["title"],
                f'{p["number"]}, updated for the eCMRs form', "icon-procedure.png"), "\n".join(b), "../", p["key"])


def procedures_index():
    b = ["<p>The quality procedures that use CMRs, updated for the <b>eCMRs</b> form. The wording is kept as "
         "released; only the steps the new form changes are changed, and each one shows what it was and why. "
         "These are drafts for the team to review - the released copy in “Released QMS Documents” stays in "
         "effect until the new revision is approved.</p>",
         "<dl class=fields>" + "".join(
             f'<div><dt><a href="{p["key"]}.html">{e(p["number"])} {e(p["title"])}</a></dt>'
             f'<dd>Rev {e(p["rev_old"])} &rarr; {e(p["rev_new"])}. {e(p["summary"])}</dd></div>' for p in PROCEDURES) + "</dl>"]
    return page("Procedures", ("Quality · Procedures", "Procedures", "Updated for the eCMRs form", "icon-procedure.png"),
                "\n".join(b), "../", "procedures")


def build():
    files = {"index.html": index_page(), "help.css": CSS}
    for f in FIELDS:
        files[f"fields/{f['key']}.html"] = field_page(f)
    files["procedures/index.html"] = procedures_index()
    for p in PROCEDURES:
        files[f"procedures/{p['key']}.html"] = procedure_page(p)
        pdf = f"{p['number']}_Rev_{p['rev_old']}.pdf"
        files[f"procedures/{pdf}"] = open(os.path.join(ORIGINALS, pdf), "rb").read()
    files = {k: v.encode("utf-8") if isinstance(v, str) else v for k, v in files.items()}
    for name, src in ASSETS.items():
        files[name] = open(src, "rb").read()
    return files


def main():
    files = build()
    if "--check" in sys.argv:
        stale = [k for k, v in files.items()
                 if not os.path.exists(os.path.join(OUT, k)) or open(os.path.join(OUT, k), "rb").read() != v]
        extra = []
        for d in ("fields", "procedures"):
            if os.path.isdir(os.path.join(OUT, d)):
                extra += [f"{d}/{n}" for n in os.listdir(os.path.join(OUT, d)) if f"{d}/{n}" not in files]
        if stale or extra:
            raise SystemExit(f"docs/help out of date: {', '.join(stale + extra)} - re-run without --check")
        print(f"OK: docs/help is up to date ({len(FIELDS)} field pages, {len(PROCEDURES)} procedures)")
        return
    for d in ("fields", "procedures"):
        if os.path.isdir(os.path.join(OUT, d)):
            shutil.rmtree(os.path.join(OUT, d))
    for k, v in files.items():
        p = os.path.join(OUT, k)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(v)
    print(f"Wrote docs/help/: index.html + {len(FIELDS)} field pages + {len(PROCEDURES)} procedures")


if __name__ == "__main__":
    main()
