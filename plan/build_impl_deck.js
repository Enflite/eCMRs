// Implementation plan deck in the Enflite brand style (branding/enflite-style-guide.md in
// Enflite/Form-Project-Templates): white slides, red rounded icon badge + Segoe UI Light title,
// Calibri body, square bullets, red outlined milestone circles, thin red decorative arcs,
// Enflite logo. Same layout as the ServiceOrders and Incidents decks.
//
// All project content lives in deck.config.js. Build: cd plan && npm install && npm run build
// eCMRs (new table + IDO, no UET): trnSteps / prodSteps / a longer launch list come from the config.
const pptxgen = require("pptxgenjs");
const cfg = require("./deck.config.js");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = cfg.title;

const RED = "CF0C2C", INK = "1A1A1A", BODY = "4A4A4A", DIV = "E5E5E5", LIGHTBG = "F7F7F7", WHITE = "FFFFFF";
const DISPLAY = "Segoe UI Light", SANS = "Calibri";
const icon = (n) => `icons/i${n}_white.png`;
// Icon numbers: see icons/README.md
const IC = { brd: 1, scope: 2, fields: 3, design: 6, develop: 7, trn: 8, launch: 9, test: 10, optimize: 11 };

function txt(s, text, o) {
  s.addText(text, Object.assign({ isTextBox: true, fontFace: SANS, margin: 0, valign: "top", color: INK }, o));
}
function arc(s, x, y, d) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { type: "none" }, line: { color: RED, width: 1 } });
}
// Header: red rounded badge with white icon (left or right), light title, gray subtitle
function header(s, title, sub, ic, right = false) {
  s.background = { color: WHITE };
  const bx = right ? 11.33 : 0.5, tx = right ? 0.5 : 2.4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: 0.55, w: 1.5, h: 1.5, rectRadius: 0.12, fill: { color: RED }, line: { color: RED } });
  s.addImage({ path: icon(ic), x: bx + 0.38, y: 0.93, w: 0.75, h: 0.75 });
  txt(s, title, { x: tx, y: 0.55, w: 10.43, h: 0.75, fontFace: DISPLAY, fontSize: 34, valign: "middle" });
  txt(s, sub, { x: tx, y: 1.33, w: 10.43, h: 0.7, fontSize: 16, color: BODY });
}
function label(s, t, x = 0.9, y = 2.75, w = 10) {
  txt(s, t, { x, y, w, h: 0.4, fontSize: 15, bold: true, valign: "middle" });
}
// Square-bullet list: a drawn ■ marker + one text box per item (bold runs stay inline)
function bullets(s, items, x, y, w, h, size = 15, gap = 8) {
  const lineH = size / 72 * 1.22, tw = w - 0.3, perLine = Math.floor(tw * 72 / (size * 0.41));
  let yy = y;
  items.forEach((it) => {
    const runs = Array.isArray(it) ? it : [{ text: it }];
    const len = runs.reduce((n, r) => n + r.text.length, 0);
    const bh = Math.max(1, Math.ceil(len / perLine)) * lineH;
    txt(s, "■", { x, y: yy, w: 0.2, h: lineH, fontSize: size * 0.6, valign: "middle" });
    txt(s, runs.map(r => ({ text: r.text, options: r.options || {} })), { x: x + 0.3, y: yy, w: tw, h: bh, fontSize: size });
    yy += bh + gap / 72;
  });
}
// Plain numbered steps: small bold number, text
function numbered(s, items, x, y, w, rowH, size = 15) {
  items.forEach((t, i) => {
    const yy = y + i * rowH;
    txt(s, String(i + 1), { x, y: yy, w: 0.35, h: 0.45, fontSize: 13, bold: true, valign: "middle" });
    txt(s, t, { x: x + 0.45, y: yy, w, h: 0.45, fontSize: size, valign: "middle" });
  });
}
// Table: muted header text, hairline rules, bold first column
function table(s, x, y, cols, rows, rowH = 0.42, size = 13) {
  let cx = x;
  const xs = cols.map(([, w]) => { const v = cx; cx += w; return v; });
  const W = cx - x;
  cols.forEach(([h, w], j) => txt(s, h, { x: xs[j], y, w: w - 0.15, h: 0.3, fontSize: 12.5, color: BODY, valign: "middle" }));
  s.addShape(pres.shapes.LINE, { x, y: y + 0.33, w: W, h: 0, line: { color: DIV, width: 0.75 } });
  rows.forEach((r, i) => {
    const yy = y + 0.36 + i * rowH;
    r.forEach((c, j) => txt(s, c, { x: xs[j], y: yy, w: cols[j][1] - 0.15, h: rowH, fontSize: size, bold: j === 0, valign: "middle" }));
    s.addShape(pres.shapes.LINE, { x, y: yy + rowH, w: W, h: 0, line: { color: DIV, width: 0.75 } });
  });
}
function note(s, t, y = 6.55) {
  txt(s, t, { x: 0.9, y, w: 11.5, h: 0.45, fontSize: 13, italic: true, color: BODY, valign: "middle" });
}

// Title
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  s.addImage({ path: "brand/enflite-logo-original.jpg", x: 0.5, y: 0.5, w: 3.0, h: 0.63 });
  arc(s, 9.6, -1.2, 5.2);
  txt(s, "PROJECT PLAN", { x: 0.5, y: 4.55, w: 8, h: 0.4, fontSize: 14, bold: true, color: RED, charSpacing: 2, valign: "middle" });
  txt(s, cfg.title, { x: 0.5, y: 4.95, w: 11, h: 1.6, fontFace: DISPLAY, fontSize: 60, color: RED, valign: "middle" });
  txt(s, cfg.subtitle, { x: 0.5, y: 6.55, w: 10.5, h: 0.5, fontSize: 17, color: BODY });
}

// Seven milestones
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  txt(s, "Seven milestones to production", { x: 0.9, y: 0.85, w: 11.5, h: 0.9, fontFace: DISPLAY, fontSize: 38, valign: "middle" });
  txt(s, "The plan at a glance — each phase in order.", { x: 0.9, y: 1.72, w: 11.5, h: 0.5, fontSize: 17, color: BODY });
  s.addShape(pres.shapes.LINE, { x: 1.16, y: 2.56, w: 0, h: 4.0, line: { color: DIV, width: 2 } });
  cfg.phases.forEach(([h, d], i) => {
    const y = 2.35 + i * 0.66;
    s.addShape(pres.shapes.OVAL, { x: 0.95, y, w: 0.42, h: 0.42, fill: { color: WHITE }, line: { color: RED, width: 1 } });
    txt(s, String(i + 1), { x: 0.95, y, w: 0.42, h: 0.42, fontSize: 14, bold: true, align: "center", valign: "middle" });
    txt(s, [{ text: h, options: { bold: true, fontSize: 17, breakLine: true } }, { text: d, options: { fontSize: 13, color: BODY } }],
      { x: 1.67, y: y - 0.08, w: 10.5, h: 0.62 });
  });
}

// Scope
{
  const s = pres.addSlide(); header(s, "Scope", cfg.scope.sub, IC.scope);
  arc(s, 11.48, 5.91, 3.5);
  label(s, "The actual phase flow");
  const flow = cfg.scope.flow, step = 10.75 / flow.length;
  flow.forEach(([h, d], i) => {
    const x = 0.9 + i * step;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.2, w: step - 0.35, h: 2.0, rectRadius: 0.08, fill: { color: LIGHTBG }, line: { color: DIV, width: 0.75 } });
    txt(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: d }], { x: x + 0.18, y: 3.38, w: step - 0.71, h: 1.7, fontSize: 14 });
    if (i < flow.length - 1) txt(s, "→", { x: x + step - 0.35, y: 3.2, w: 0.35, h: 2.0, fontSize: 18, color: RED, align: "center", valign: "middle" });
  });
}

// BRD
{
  const s = pres.addSlide(); header(s, "BRD", "Business requirements for the change.", IC.brd);
  label(s, "Business requirements");
  bullets(s, cfg.brd, 0.9, 3.2, 11.53, 3.9, 15, 5);
}

// Mockup (optional)
if (cfg.mockup && cfg.mockup.image) {
  const m = cfg.mockup;
  const s = pres.addSlide(); header(s, m.title, m.sub, IC.fields);
  label(s, "What changes", 0.5, 2.3, 5);
  bullets(s, m.bullets || [], 0.5, 2.8, 5.9, 3.8, 15, 8);
  s.addImage({ path: m.image, x: 6.7, y: 2.3, w: 6.1, h: 3.22, sizing: { type: "contain", w: 6.1, h: 3.22 } });
  txt(s, m.caption || "", { x: 6.7, y: 5.6, w: 6.1, h: 0.35, fontSize: 12, italic: true, color: BODY });
}

// TRN first, then production
{
  const s = pres.addSlide(); header(s, "TRN first, then production", "Everything is built and proven on TRN, then pushed to production later.", IC.trn, true);
  label(s, "On TRN", 0.9, 2.75, 5);
  numbered(s, cfg.trnSteps || ["Build the UET setup", "Import the form through FormSync", "Test with the team", "Export each UET form to Excel as the production checklist"], 0.9, 3.25, 5.0, 0.6);
  txt(s, "→", { x: 6.2, y: 3.2, w: 0.6, h: 2.4, fontSize: 28, color: RED, align: "center", valign: "middle" });
  label(s, "In production", 7.1, 2.75, 5);
  numbered(s, cfg.prodSteps || ["Same UET entries, same order, from the TRN exports", "Run UET Impact Schema in a scheduled window", "Import the same form XML through FormSync", "Smoke test, then hand over to the team"], 7.1, 3.25, 5.2, 0.6);
}

// Design, one slide per UET form (badge alternates sides)
cfg.design.forEach((d, i) => {
  const s = pres.addSlide(); header(s, "Design", d.sub, IC.design, i % 2 === 1);
  label(s, d.label);
  const rowH = d.rows.length > 5 ? 0.36 : 0.5, size = d.rows.length > 5 ? 13 : 14;
  table(s, 0.9, 3.2, d.cols, d.rows, rowH, size);
  if (d.note) note(s, d.note);
});

// Develop
{
  const s = pres.addSlide(); header(s, "Develop", "Build on TRN first — never directly in production.", IC.develop);
  label(s, "Actual build steps");
  bullets(s, cfg.develop, 0.9, 3.2, 11.53, 3.3, 15, 6);
}

// Develop · FormSync
{
  const s = pres.addSlide(); header(s, "Develop", "The form is built as XML and imported through FormSync.", IC.launch, true);
  label(s, "Building the form with FormSync");
  numbered(s, cfg.formsync, 0.9, 3.25, 11.1, 0.72);
}

// Staging
{
  const s = pres.addSlide(); header(s, "Staging", "Freeze the TRN build and run final validation before production.", IC.trn, true);
  label(s, "Actual staging approach");
  numbered(s, cfg.staging, 0.9, 3.2, 11.1, 0.72);
}

// Launch + rollback
{
  const s = pres.addSlide(); header(s, "Launch", "Deploy to production.", IC.launch);
  label(s, "Production steps");
  // Up to 3 steps at the template's spacing; longer lists (eCMRs: 6) are packed tighter.
  const lh = cfg.launch.length > 3 ? Math.min(0.72, 2.6 / cfg.launch.length) : 0.72;
  numbered(s, cfg.launch, 0.9, 3.2, 11.1, lh);
  const ry = Math.max(5.45, 3.2 + cfg.launch.length * lh + 0.15);
  label(s, "Rollback", 0.9, ry);
  bullets(s, [cfg.rollback], 0.9, ry + 0.45, 11.53, 0.6, 15);
}

// Test
{
  const s = pres.addSlide(); header(s, "Test", "Run tests to make sure everything looks good.", IC.test, true);
  label(s, "Actual test list");
  bullets(s, cfg.test, 0.9, 3.2, 11.53, 3.4, 15, 10);
}

// Optimize (centered)
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  arc(s, -3.4, 4.9, 6.0); arc(s, 10.5, -1.5, 5.0);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.92, y: 0.55, w: 1.5, h: 1.5, rectRadius: 0.12, fill: { color: RED }, line: { color: RED } });
  s.addImage({ path: icon(IC.optimize), x: 6.29, y: 0.93, w: 0.75, h: 0.75 });
  txt(s, "Optimize", { x: 0, y: 2.2, w: 13.33, h: 1.0, fontFace: DISPLAY, fontSize: 48, color: RED, align: "center", valign: "middle" });
  txt(s, "Two weeks of optimization, working closely with the team.", { x: 1.5, y: 3.15, w: 10.33, h: 0.6, fontSize: 17, color: BODY, align: "center", valign: "middle" });
  label(s, "Actual optimization backlog", 3.6, 4.42, 6);
  bullets(s, cfg.optimize, 3.6, 4.85, 7.0, 1.9, 15, 4);
}

pres.writeFile({ fileName: cfg.fileName }).then(f => console.log("wrote", f));
