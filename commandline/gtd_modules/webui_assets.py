"""
Static assets for the generated website: the stylesheet and the three scripts,
held as plain string constants and written to disk verbatim by `webui.py`.

They live here (rather than as files shipped alongside the code) so the generator
stays a self-contained Python package: nothing to install, nothing to locate at
run time, and no chance of the code and its assets drifting apart in a release.

  * STYLE_CSS  — layout + the Clearlooks/early-2000s theme, light and dark.
  * THEME_JS   — sets the theme before first paint and wires the toolbar toggle.
  * APP_JS     — the mail interface (folder lists, reading pane, command modals).
  * PERF_JS    — the Performance page's Plotly charts.

Conventions these assets must keep:
  * NO external references of any kind — no webfonts, no CDN, no remote images.
    Everything is either a system font, a CSS gradient, or a text glyph.
  * Classic scripts only, never `type="module"`: ES modules are fetched with CORS
    rules that browsers refuse to apply to file:// URLs, so a module would break
    the "just open index.html" requirement.
  * All colours come from the CSS custom properties defined in STYLE_CSS, so
    light/dark mode is one attribute flip on <html> — including for the charts,
    which read the same variables (see PERF_JS `themeColours`).
  * The generated site is a READ-ONLY report: scripts may compute and display
    shell commands for the user to run, but must never claim to have changed the
    workflow itself.
"""

# Written to assets/clearlooks.css.
#
# The look is deliberately pre-flat: every raised surface carries a soft vertical
# gradient plus a 1px light inner highlight above a darker outer border (the
# classic Clearlooks bevel), panels that hold content are inset/sunken instead,
# and corner radii stay at 3px. Both themes are defined as custom-property sets;
# THEME_JS decides which is active.
STYLE_CSS = r"""/* ==========================================================================
   GTD-over-EML — generated report UI
   A Clearlooks / early-2000s desktop theme: soft vertical gradients, explicit
   bevelled borders, sunken content panels, 3px radii. Light + dark.
   ========================================================================== */

:root {
  --font-ui: "Helvetica Neue", Helvetica, Arial, sans-serif;
  --font-mono: "Courier New", Courier, monospace;
  /* Email bodies follow the UI stack by default; the reading pane offers a
     monospace switch for plain-text mail that relies on column alignment
     (ASCII tables, diffs, code). See THEME_JS's bodyFont. */
  --font-body: var(--font-ui);

  /* Window furniture */
  --bg-window: #ded9d2;
  --bg-panel: #ffffff;
  --bg-panel-alt: #f5f3ef;
  --bg-inset: #fbfaf8;
  --chrome-top: #f7f5f2;
  --chrome-bot: #ddd7ce;
  --title-top: #f2efe9;
  --title-bot: #dcd6cc;
  --sidebar-top: #ece8e1;
  --sidebar-bot: #ddd8d0;
  --btn-top: #fdfdfc;
  --btn-bot: #dfd9d0;
  --btn-top-hover: #ffffff;
  --btn-bot-hover: #e9e4dc;

  /* Lines */
  --bd-strong: #9c948a;
  --bd-soft: #c4bdb2;
  --bd-light: #ffffff;
  --shadow: rgba(0, 0, 0, 0.28);

  /* Text */
  --fg: #2b2926;
  --fg-soft: #524e48;
  --fg-muted: #7a746c;
  --fg-on-sel: #ffffff;
  --accent: #2c5d9b;

  /* Selection (Clearlooks blue) */
  --sel-top: #7ba1cf;
  --sel-bot: #43689e;
  --sel-bd: #35547f;

  /* Semantic */
  --age-green: #3f8f3f;
  --age-yellow: #c08a1e;
  --age-red: #b3453c;
  --ok-bg: #e6efdc;
  --warn-bg: #f6eed6;

  /* Charts pick these up so Plotly matches the theme */
  --chart-fg: #4a4640;
  --chart-grid: #cfc9bf;
}

[data-theme="dark"] {
  --bg-window: #322f2c;
  --bg-panel: #262523;
  --bg-panel-alt: #2d2b28;
  --bg-inset: #201f1d;
  --chrome-top: #4a4642;
  --chrome-bot: #35322e;
  --title-top: #46423e;
  --title-bot: #37342f;
  --sidebar-top: #3d3a36;
  --sidebar-bot: #322f2b;
  --btn-top: #4e4a45;
  --btn-bot: #3a3733;
  --btn-top-hover: #5a5550;
  --btn-bot-hover: #43403b;

  --bd-strong: #171615;
  --bd-soft: #4c4842;
  --bd-light: rgba(255, 255, 255, 0.10);
  --shadow: rgba(0, 0, 0, 0.6);

  --fg: #e8e4dd;
  --fg-soft: #cbc6bd;
  --fg-muted: #9b958c;
  --fg-on-sel: #ffffff;
  --accent: #8fb6e6;

  --sel-top: #5d82b4;
  --sel-bot: #35527d;
  --sel-bd: #22364f;

  --age-green: #7ec27e;
  --age-yellow: #e0b054;
  --age-red: #e08078;
  --ok-bg: #33402f;
  --warn-bg: #46402d;

  --chart-fg: #c9c4bb;
  --chart-grid: #4c4842;
}

[data-body-font="mono"] { --font-body: var(--font-mono); }

* { box-sizing: border-box; }

html, body {
  height: 100%;
  margin: 0;
  font-family: var(--font-ui);
  font-size: 13px;
  color: var(--fg);
  background: var(--bg-window);
}

a { color: var(--accent); }
h2, h3 { font-family: var(--font-ui); }
code, kbd { font-family: var(--font-mono); font-size: 12px; }
.grow { flex: 1 1 auto; min-width: 0; }

/* --- Scrollbars: gradient thumb in a sunken trough ----------------------- */
* { scrollbar-width: thin; scrollbar-color: var(--bd-soft) var(--bg-inset); }
::-webkit-scrollbar { width: 14px; height: 14px; }
::-webkit-scrollbar-track {
  background: var(--bg-inset);
  border-left: 1px solid var(--bd-soft);
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(to right, var(--btn-top), var(--btn-bot));
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to right, var(--btn-top-hover), var(--btn-bot-hover));
}
::-webkit-scrollbar-corner { background: var(--bg-inset); }

/* ==========================================================================
   Window layout: toolbar / sidebar / list / reader / status bar
   ========================================================================== */

.app {
  display: grid;
  grid-template-columns: 208px 336px minmax(0, 1fr);
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 4px;
  padding: 4px;
  height: 100vh;
}
.app > .toolbar { grid-column: 1 / -1; }
.app > .statusbar { grid-column: 1 / -1; }
.app > .sidebar { grid-column: 1; grid-row: 2; }
.app > .list-pane { grid-column: 2; grid-row: 2; }
.app > .read-pane { grid-column: 3; grid-row: 2; }
/* Overview and Performance use the full width: the message list steps aside. */
.app.wide > .list-pane { display: none; }
.app.wide > .read-pane { grid-column: 2 / -1; }

/* Raised chrome: gradient + bevel. */
.toolbar, .statusbar, .sidebar, .pane-title {
  background: linear-gradient(to bottom, var(--chrome-top), var(--chrome-bot));
  border: 1px solid var(--bd-strong);
  box-shadow: inset 0 1px 0 var(--bd-light);
  border-radius: 3px;
}

/* --- Toolbar ------------------------------------------------------------- */
.toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 7px;
  flex-wrap: wrap;
}
.brand {
  font-weight: 700;
  letter-spacing: 0.02em;
  padding-right: 8px;
  margin-right: 2px;
  border-right: 1px solid var(--bd-soft);
  box-shadow: 1px 0 0 var(--bd-light);
  text-shadow: 0 1px 0 var(--bd-light);
}
[data-theme="dark"] .brand, [data-theme="dark"] .pane-title { text-shadow: none; }
.brand small { font-weight: 400; color: var(--fg-muted); }
.tb-spacer { flex: 1 1 auto; }
.tb-group { display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }

/* --- Buttons (bevelled, gradient, 3px) ---------------------------------- */
.btn {
  font: inherit;
  color: var(--fg);
  padding: 3px 10px;
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 1px 1px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  white-space: nowrap;
}
.btn:hover:not(:disabled) {
  background: linear-gradient(to bottom, var(--btn-top-hover), var(--btn-bot-hover));
}
.btn:active:not(:disabled) {
  background: linear-gradient(to bottom, var(--btn-bot), var(--btn-top));
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.25);
}
.btn:disabled { opacity: 0.5; cursor: default; }
.btn.primary {
  font-weight: 700;
  border-color: var(--sel-bd);
  color: var(--fg-on-sel);
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}
.btn.primary:hover { filter: brightness(1.07); }
.btn:focus-visible, .field:focus-visible, select:focus-visible {
  outline: 1px dotted var(--fg-soft);
  outline-offset: 1px;
}

/* --- Text fields + selects (sunken) ------------------------------------- */
.field, select, textarea {
  font: inherit;
  color: var(--fg);
  background: var(--bg-inset);
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.16);
  padding: 3px 6px;
}
select {
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.search { position: relative; display: flex; align-items: center; }
.search .field { width: 210px; padding-left: 20px; }
.search::before {
  content: "\2315";
  position: absolute;
  left: 5px;
  color: var(--fg-muted);
  font-size: 12px;
}

/* --- Sidebar ------------------------------------------------------------- */
.sidebar { padding: 4px; overflow-y: auto; }
.sidebar .group-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--fg-muted);
  padding: 6px 6px 3px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  font: inherit;
  text-align: left;
  text-decoration: none;
  color: var(--fg);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 3px;
  padding: 4px 6px;
  cursor: pointer;
}
.nav-item:hover {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.5), rgba(0, 0, 0, 0.04));
  border-color: var(--bd-soft);
}
[data-theme="dark"] .nav-item:hover {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.07), rgba(0, 0, 0, 0.12));
}
.nav-item.active, .nav-item.active:hover {
  color: var(--fg-on-sel);
  border-color: var(--sel-bd);
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.3);
}
.nav-item .label { flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; }
.nav-item .badge {
  font-size: 11px;
  min-width: 20px;
  text-align: center;
  padding: 0 5px;
  border: 1px solid var(--bd-soft);
  border-radius: 8px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--bg-panel), var(--bg-panel-alt));
}
.nav-item.active .badge {
  color: var(--fg-on-sel);
  border-color: rgba(255, 255, 255, 0.55);
  background: rgba(0, 0, 0, 0.18);
}
.sidebar hr {
  border: none;
  border-top: 1px solid var(--bd-soft);
  border-bottom: 1px solid var(--bd-light);
  margin: 6px 4px;
}

/* --- Content panes (sunken) -------------------------------------------- */
.list-pane, .read-pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  background: var(--bg-panel);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.13);
  overflow: hidden;
}
.pane-title {
  border-radius: 0;
  border: none;
  border-bottom: 1px solid var(--bd-strong);
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--fg-soft);
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.pane-title .count { font-weight: 400; text-transform: none; letter-spacing: 0; }
.scroll { overflow: auto; flex: 1 1 auto; }
.read-pane .scroll { padding: 12px 14px 24px; }

/* --- Message list ------------------------------------------------------- */
.row {
  display: block;
  width: 100%;
  text-align: left;
  font: inherit;
  color: var(--fg);
  background: var(--bg-panel);
  border: none;
  border-bottom: 1px solid var(--bd-soft);
  padding: 6px 8px;
  cursor: pointer;
}
.row:nth-child(even) { background: var(--bg-panel-alt); }
.row:hover { background: linear-gradient(to bottom, var(--bg-panel), var(--bg-panel-alt)); }
.row.selected, .row.selected:hover {
  color: var(--fg-on-sel);
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  border-bottom-color: var(--sel-bd);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25);
}
.row .r1 { display: flex; align-items: baseline; gap: 6px; }
.row .subject {
  flex: 1 1 auto;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row .when { font-size: 11px; color: var(--fg-muted); white-space: nowrap; }
.row .r2, .row .r3 {
  display: block;
  font-size: 11.5px;
  color: var(--fg-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row .r3 { color: var(--fg-muted); }
.row.selected .when, .row.selected .r2, .row.selected .r3 {
  color: rgba(255, 255, 255, 0.88);
}
.row .next { font-style: italic; }
.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
  flex: 0 0 auto;
}
.dot.green { background: var(--age-green); }
.dot.yellow { background: var(--age-yellow); }
.dot.red { background: var(--age-red); }
.dot.none { background: var(--bd-soft); }
.pin { color: var(--age-yellow); }
.row.selected .pin { color: #ffe9a8; }
.empty { padding: 18px; color: var(--fg-muted); font-style: italic; }

/* --- Reading pane ------------------------------------------------------- */
.read-subject { margin: 0 0 8px; font-size: 17px; line-height: 1.3; }
.hdr {
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
  padding: 7px 9px;
  margin-bottom: 10px;
}
.hdr dl { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 2px 10px; margin: 0; }
.hdr dt {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
  padding-top: 1px;
}
.hdr dd { margin: 0; overflow-wrap: anywhere; }
.chips { display: flex; flex-wrap: wrap; gap: 5px; margin: 8px 0; }
.chip {
  font-size: 11.5px;
  padding: 1px 7px;
  border: 1px solid var(--bd-soft);
  border-radius: 9px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.chip b { color: var(--fg); }
.chip.flag { border-color: var(--age-yellow); }
.chip.status-resolved { background: linear-gradient(to bottom, var(--ok-bg), var(--btn-bot)); }
.chip.status-weird { background: linear-gradient(to bottom, var(--warn-bg), var(--btn-bot)); }
.section-head {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--fg-muted);
  margin: 16px 0 6px;
  padding-bottom: 3px;
  border-bottom: 1px solid var(--bd-soft);
  box-shadow: 0 1px 0 var(--bd-light);
}
.actions { display: flex; flex-wrap: wrap; gap: 5px; margin: 8px 0 4px; }
.note-line { color: var(--fg-muted); font-size: 12px; margin: 6px 0; }

/* Workflow trail: the ds_* stamps as a chain of steps. */
.trail { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }
.trail .step {
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  padding: 2px 7px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.trail .step b { display: block; font-size: 10.5px; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--fg-muted); }
.trail .arrow { color: var(--fg-muted); }

/* Thread messages: each quoted level is its own bevelled block. */
.msg {
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  background: var(--bg-panel);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.07);
  margin: 8px 0;
  overflow: hidden;
}
.msg > summary, .msg > .msg-head {
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  border-bottom: 1px solid var(--bd-soft);
  padding: 4px 8px;
  font-size: 11.5px;
  color: var(--fg-soft);
  cursor: default;
  display: flex;
  gap: 8px;
  align-items: baseline;
}
.msg > summary { cursor: pointer; }
.msg > summary::-webkit-details-marker { color: var(--fg-muted); }
.msg .who { font-weight: 700; color: var(--fg); }
.msg .msg-body {
  margin: 0;
  padding: 9px 10px;
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.45;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.msg.d1 { margin-left: 12px; }
.msg.d2 { margin-left: 24px; }
.msg.d3 { margin-left: 36px; }
.msg.d4 { margin-left: 48px; }

/* ==========================================================================
   Overview pane
   ========================================================================== */
.cards { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 4px; }
.card {
  flex: 1 1 128px;
  min-width: 128px;
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  padding: 8px 10px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 1px 2px rgba(0, 0, 0, 0.08);
  text-align: left;
  font: inherit;
  color: var(--fg);
}
button.card { cursor: pointer; }
button.card:hover { background: linear-gradient(to bottom, var(--btn-top-hover), var(--btn-bot-hover)); }
.card .big { font-size: 22px; font-weight: 700; line-height: 1.1; }
.card .lbl { font-size: 11.5px; color: var(--fg-soft); }
.card .hint { font-size: 11px; color: var(--fg-muted); margin-top: 3px; }
.card.attn-0 { opacity: 0.72; }
.card.attn-hot { border-color: var(--age-red); }
.card.attn-hot .big { color: var(--age-red); }
.tablewrap {
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
  padding: 2px;
}
table.grid { border-collapse: collapse; width: 100%; font-size: 12.5px; }
table.grid th, table.grid td {
  border: 1px solid var(--bd-soft);
  padding: 3px 7px;
  text-align: left;
}
table.grid thead th {
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-soft);
}
table.grid tbody tr:nth-child(even) { background: var(--bg-panel-alt); }
table.grid tbody tr:nth-child(odd) { background: var(--bg-panel); }
table.grid td.num { text-align: right; font-variant-numeric: tabular-nums; }
.linkish {
  font: inherit;
  color: var(--accent);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
}

/* ==========================================================================
   Status bar
   ========================================================================== */
.statusbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 6px;
  font-size: 11.5px;
  color: var(--fg-soft);
}
.statusbar .cell {
  border: 1px solid var(--bd-soft);
  border-radius: 2px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
  padding: 2px 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.statusbar .cell.grow { flex: 1 1 auto; min-width: 0; }
.statusbar .ro { color: var(--age-red); font-weight: 700; }
.mono { font-family: var(--font-mono); }

/* ==========================================================================
   Modal: a little application window with a gradient title bar
   ========================================================================== */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.42);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 6vh 12px 12px;
  z-index: 50;
}
.overlay[hidden] { display: none; }
.window {
  width: min(720px, 100%);
  max-height: 84vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-window);
  border: 1px solid var(--bd-strong);
  border-radius: 4px;
  box-shadow: 0 8px 26px var(--shadow), inset 0 1px 0 var(--bd-light);
}
.window > .titlebar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  border-bottom: 1px solid var(--bd-strong);
  border-radius: 3px 3px 0 0;
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  color: var(--fg-on-sel);
  font-weight: 700;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
}
.window > .titlebar .grow { flex: 1 1 auto; }
.window .body { padding: 10px 12px; overflow: auto; }
.window .footer {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 8px 12px;
  border-top: 1px solid var(--bd-soft);
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.form-row { display: grid; grid-template-columns: 132px minmax(0, 1fr); gap: 8px;
  align-items: start; margin-bottom: 8px; }
.form-row > label { padding-top: 4px; color: var(--fg-soft); }
.form-row .field, .form-row select, .form-row textarea { width: 100%; }
.form-row textarea { min-height: 54px; resize: vertical; }
.snippet {
  font-family: var(--font-mono);
  font-size: 12.5px;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  margin: 0;
  padding: 8px 9px;
  color: var(--fg);
  background: var(--bg-inset);
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.18);
  user-select: all;
}
.copied { color: var(--age-green); font-weight: 700; }

/* ==========================================================================
   Performance page (charts, KPI tables, notebook tabs)
   ========================================================================== */
.perf { max-width: 1040px; }
.perf section { margin: 0 0 26px; }
.perf h2 {
  font-size: 15px;
  margin: 0 0 4px;
  padding-bottom: 3px;
  border-bottom: 1px solid var(--bd-soft);
  box-shadow: 0 1px 0 var(--bd-light);
}
.perf .prose { margin: 4px 0 10px; color: var(--fg-soft); max-width: 78ch; }
.counts { display: flex; gap: 16px; flex-wrap: wrap; margin: 4px 0 14px; }
.counts span { display: inline-block; }
.acct-filter { display: inline-flex; align-items: center; gap: 6px; padding: 5px 8px;
  margin: 0 0 10px; border: 1px solid var(--bd-soft); border-radius: 3px;
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  box-shadow: inset 0 1px 0 var(--bd-light); }
.acct-block[hidden] { display: none; }
.chart {
  width: 100%;
  height: 460px;
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}
.chart-missing { padding: 16px; color: var(--age-red); }
table.kpi { border-collapse: collapse; width: 100%; font-size: 12.5px; }
table.kpi th, table.kpi td {
  border: 1px solid var(--bd-soft);
  padding: 4px 8px;
  vertical-align: top;
}
table.kpi thead th {
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
  text-align: right;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-soft);
}
table.kpi thead th:first-child { text-align: left; }
table.kpi tbody th { text-align: left; font-weight: 700; white-space: nowrap;
  background: var(--bg-panel-alt); }
table.kpi tbody td { background: var(--bg-panel); }
table.kpi td.num { text-align: right; font-variant-numeric: tabular-nums; }
.kpi-card { text-align: right; font-variant-numeric: tabular-nums; }
.kpi-lbl { color: var(--fg-muted); }
.stat-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0; }
.stat {
  flex: 1 1 8.5rem;
  min-width: 8.5rem;
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  padding: 7px 9px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 1px 2px rgba(0, 0, 0, 0.08);
}
.stat-val { font-size: 21px; font-weight: 700; font-variant-numeric: tabular-nums; }
.stat-lbl { color: var(--fg-soft); font-size: 11.5px; }
.stat .kpi-lbl { font-size: 11px; word-break: break-all; }
.note {
  background: linear-gradient(to bottom, var(--warn-bg), var(--btn-bot));
  border: 1px solid var(--bd-soft);
  border-left: 3px solid var(--age-yellow);
  border-radius: 3px;
  padding: 7px 10px;
  font-size: 12.5px;
  margin: 10px 0 0;
}
/* Notebook tabs: the active tab joins the panel below it. */
.tabs { display: flex; gap: 2px; margin: 0 0 -1px; position: relative; z-index: 1; }
.tabs button {
  font: inherit;
  padding: 4px 12px;
  cursor: pointer;
  color: var(--fg-soft);
  border: 1px solid var(--bd-soft);
  border-bottom: 1px solid var(--bd-soft);
  border-radius: 4px 4px 0 0;
  background: linear-gradient(to bottom, var(--bg-panel-alt), var(--btn-bot));
}
.tabs button[aria-selected="true"] {
  font-weight: 700;
  color: var(--fg);
  border-bottom-color: var(--bg-inset);
  background: linear-gradient(to bottom, var(--btn-top), var(--bg-inset));
}
/* Plotly hard-codes a text-shadow halo on Sankey node labels as an inline
   style; only an !important stylesheet rule can turn it off. */
text.node-label { text-shadow: none !important; }

/* ==========================================================================
   Narrow screens: stack the three panes into one scrolling column
   ========================================================================== */
@media (max-width: 900px) {
  .app, .app.wide {
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: auto auto auto minmax(0, 1fr) auto;
    height: auto;
    min-height: 100vh;
  }
  .app > .sidebar, .app > .list-pane, .app > .read-pane,
  .app.wide > .read-pane { grid-column: 1; grid-row: auto; }
  .app > .list-pane { max-height: 42vh; }
  .app.wide > .list-pane { display: none; }
  .search .field { width: 150px; }
}
"""


# Written to assets/theme.js. Loaded synchronously in <head> so the theme is set
# BEFORE first paint (no flash of the wrong theme), which also means it must not
# touch document.body — it wires the toolbar toggle on DOMContentLoaded instead.
# localStorage is wrapped in try/catch because some browsers refuse it outright
# for file:// pages; the site then simply falls back to the OS preference.
THEME_JS = r"""(function () {
  "use strict";
  var THEME_KEY = "gtd-eml.theme";
  var BODY_FONT_KEY = "gtd-eml.bodyFont";
  var root = document.documentElement;

  function stored(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }
  function remember(key, value) {
    try { window.localStorage.setItem(key, value); } catch (e) { /* not available */ }
  }
  function preferred() {
    return (window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
  }

  function applyBodyFont(font) {
    root.setAttribute("data-body-font", font);
    var button = document.getElementById("body-font-toggle");
    if (button) {
      button.textContent = font === "mono" ? "Proportional body" : "Monospace body";
      button.setAttribute("aria-pressed", font === "mono" ? "true" : "false");
    }
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    var button = document.getElementById("theme-toggle");
    if (button) {
      button.textContent = theme === "dark" ? "Light mode" : "Dark mode";
      button.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }
    try {
      window.dispatchEvent(new CustomEvent("gtd:theme", { detail: theme }));
    } catch (e) { /* very old browser: charts just keep their colours */ }
  }

  var Theme = {
    current: function () { return root.getAttribute("data-theme") || "light"; },
    set: function (theme) { remember(THEME_KEY, theme); apply(theme); },
    toggle: function () { Theme.set(Theme.current() === "dark" ? "light" : "dark"); },
    /* Email-body typeface: "ui" (default, the specified Helvetica stack) or
       "mono". Persisted alongside the theme so it survives page switches. */
    bodyFont: function () { return root.getAttribute("data-body-font") || "ui"; },
    setBodyFont: function (font) { remember(BODY_FONT_KEY, font); applyBodyFont(font); },
    toggleBodyFont: function () {
      Theme.setBodyFont(Theme.bodyFont() === "mono" ? "ui" : "mono");
    },
    /* Read a CSS custom property, so scripts (and Plotly) can use theme colours. */
    colour: function (name, fallback) {
      var value = getComputedStyle(root).getPropertyValue(name);
      return (value || "").trim() || fallback;
    }
  };
  window.GTDTheme = Theme;

  root.setAttribute("data-theme", stored(THEME_KEY) || preferred());
  root.setAttribute("data-body-font", stored(BODY_FONT_KEY) || "ui");
  document.addEventListener("DOMContentLoaded", function () {
    var themeButton = document.getElementById("theme-toggle");
    if (themeButton) {
      themeButton.addEventListener("click", function () { Theme.toggle(); });
    }
    var fontButton = document.getElementById("body-font-toggle");
    if (fontButton) {
      fontButton.addEventListener("click", function () { Theme.toggleBodyFont(); });
    }
    apply(Theme.current());
    applyBodyFont(Theme.bodyFont());
  });
})();
"""


# Written to assets/app.js — the mail interface. Reads window.GTD_MAIL (emitted as
# data/mail.js) and renders the folder lists, the reading pane, the overview, and
# the command-snippet modals.
#
# Two rules matter here. (1) Every figure it displays was computed in Python:
# this script filters, sorts and formats, but never derives a statistic. (2) It
# NEVER pretends to mutate the workflow — an "action" only composes the shell
# command the user may choose to run, because the site is a report.
APP_JS = r"""(function () {
  "use strict";

  var DATA = window.GTD_MAIL || {};
  var EMAILS = DATA.emails || [];
  var SECTIONS = DATA.sections || [];
  var OVERVIEW = DATA.overview || {};
  var DESTINATIONS = DATA.destinations || [];
  var CLI = DATA.cli || "gtd";

  var BY_FILE = {};
  var SECTION_LABEL = { overview: "Overview" };
  var i;
  for (i = 0; i < EMAILS.length; i++) { BY_FILE[EMAILS[i].file] = EMAILS[i]; }
  for (i = 0; i < SECTIONS.length; i++) { SECTION_LABEL[SECTIONS[i].key] = SECTIONS[i].label; }

  /* section: which sidebar entry is active; subset: a temporary list built from
     an overview figure; query: the search box (searches every folder). */
  var state = { section: "overview", file: null, query: "", sort: "date-desc", subset: null };

  /* ---------------------------------------------------------------- helpers */
  function $(id) { return document.getElementById(id); }

  function esc(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }
  function oneLine(value) { return String(value || "").replace(/\s+/g, " ").trim(); }

  /* Shell quoting for the generated snippets: bare when safe, double-quoted
     (with $, `, \ and " escaped) otherwise. */
  function dq(value) {
    return '"' + String(value).replace(/([\\"$`])/g, "\\$1") + '"';
  }
  function shellArg(value) {
    value = String(value === undefined || value === null ? "" : value);
    return /^[A-Za-z0-9._\/@:+=-]+$/.test(value) && value !== "" ? value : dq(value);
  }
  function gtd() {
    var parts = [CLI];
    for (var n = 0; n < arguments.length; n++) { parts.push(arguments[n]); }
    return parts.join(" ");
  }
  function chain(commands) {
    var kept = commands.filter(function (c) { return !!c; });
    return kept.length ? kept.join(" && ") : "";
  }

  function haystack(email) {
    if (email._hay === undefined) {
      var parts = [email.subject, email.file, email.from, email.to, email.cc,
                   email.project, email.nextAction, email.notes, email.ref,
                   email.account, (email.correspondents || []).join(" "),
                   (email.flags || []).join(" ")];
      (email.thread || []).forEach(function (message) {
        parts.push(message.text, message.from, message.subject);
      });
      email._hay = parts.join(" \n ").toLowerCase();
    }
    return email._hay;
  }

  var SORTERS = {
    "date-desc": function (a, b) { return cmp(b.date, a.date) || cmp(a.subject, b.subject); },
    "date-asc": function (a, b) { return cmp(a.date, b.date) || cmp(a.subject, b.subject); },
    "subject": function (a, b) { return cmp(low(a.subject), low(b.subject)); },
    "from": function (a, b) { return cmp(low(a.from), low(b.from)); },
    "folder": function (a, b) { return cmp(a.folderDir, b.folderDir) || cmp(b.date, a.date); }
  };
  function low(value) { return String(value || "").toLowerCase(); }
  function cmp(a, b) { return a < b ? -1 : (a > b ? 1 : 0); }

  function listEmails() {
    var pool;
    if (state.subset) {
      pool = state.subset.files.map(function (f) { return BY_FILE[f]; })
                              .filter(function (e) { return !!e; });
    } else if (state.query) {
      var needle = state.query.toLowerCase();
      pool = EMAILS.filter(function (e) { return haystack(e).indexOf(needle) >= 0; });
    } else {
      pool = EMAILS.filter(function (e) { return e.folder === state.section; });
    }
    return pool.slice().sort(SORTERS[state.sort] || SORTERS["date-desc"]);
  }

  function isWide() {
    return state.section === "overview" && !state.query && !state.subset;
  }

  /* ------------------------------------------------------------ list pane */
  function rowHtml(email, selected) {
    var when = email.date ? esc(email.date) : "(no date)";
    if (email.ageDays !== null && email.ageDays !== undefined) {
      when += " \u00b7 " + email.ageDays + "d";
    }
    var who = (email.correspondents || []).join(", ") || email.from || "(no correspondents)";
    var third;
    if (!email.tracked) {
      third = "not yet ingested \u2014 run `" + CLI + " list`";
    } else if (email.nextAction) {
      third = "next: " + email.nextAction;
    } else if (email.project) {
      third = "project: " + email.project;
    } else {
      third = email.preview || "";
    }
    var pin = (email.flags || []).indexOf("pinned") >= 0
      ? '<span class="pin" title="pinned">\u2605</span>' : "";
    return '<button class="row' + (selected ? " selected" : "") + '" type="button" ' +
      'data-file="' + esc(email.file) + '">' +
      '<span class="r1">' +
        '<span class="dot ' + (email.ageClass || "none") + '"></span>' + pin +
        '<span class="subject">' + esc(email.subject) + "</span>" +
        '<span class="when">' + when + "</span>" +
      "</span>" +
      '<span class="r2">' + esc(who) + "</span>" +
      '<span class="r3' + (email.nextAction ? " next" : "") + '">' + esc(third) + "</span>" +
      "</button>";
  }

  function renderList(emails) {
    var title = state.subset ? state.subset.label
      : (state.query ? 'Search: "' + state.query + '"' : SECTION_LABEL[state.section] || "Messages");
    $("list-title").innerHTML = esc(title) +
      ' <span class="count">' + plural(emails.length, "message") + "</span>";
    if (!emails.length) {
      $("list").innerHTML = '<p class="empty">No messages here.</p>';
      return;
    }
    var html = [];
    for (var n = 0; n < emails.length; n++) {
      html.push(rowHtml(emails[n], emails[n].file === state.file));
    }
    $("list").innerHTML = html.join("");
    var selected = $("list").querySelector(".row.selected");
    if (selected && selected.scrollIntoView) { selected.scrollIntoView({ block: "nearest" }); }
  }

  /* --------------------------------------------------------- reading pane */
  function chip(label, value, extra) {
    if (!value) { return ""; }
    return '<span class="chip ' + (extra || "") + '">' +
      (label ? esc(label) + " " : "") + "<b>" + esc(value) + "</b></span>";
  }

  function headerRow(label, value) {
    return value ? "<dt>" + esc(label) + "</dt><dd>" + esc(value) + "</dd>" : "";
  }

  function threadHtml(email) {
    var messages = email.thread || [];
    if (!messages.length) {
      return '<p class="note-line">This email has no text body (it may be '
        + "attachment-only).</p>";
    }
    var html = [];
    for (var n = 0; n < messages.length; n++) {
      var message = messages[n];
      var who = message.from || (n === 0 ? email.from : "") || "Quoted message";
      var when = message.date || (n === 0 ? email.dateDisplay : "");
      var head = '<span class="who">' + esc(who) + "</span>" +
        (when ? "<span>" + esc(when) + "</span>" : "") +
        (message.subject ? '<span class="grow">' + esc(message.subject) + "</span>" : "");
      var body = '<pre class="msg-body">' + esc(message.text) + "</pre>";
      var cls = "msg d" + (message.indent || 0);
      if (n === 0) {
        html.push('<div class="' + cls + '"><div class="msg-head">' + head +
                  "</div>" + body + "</div>");
      } else {
        html.push('<details class="' + cls + '"><summary>' + head + "</summary>" +
                  body + "</details>");
      }
    }
    return html.join("");
  }

  function trailHtml(email) {
    if (!email.tracked) {
      return '<p class="note-line">Not tracked yet: files in <code>01-input</code> have '
        + "no metadata row and no date-stamps until <code>" + esc(CLI)
        + " list</code> ingests them.</p>";
    }
    var steps = (email.stamps || []).map(function (stamp) {
      return '<span class="step"><b>' + esc(stamp.label) + "</b>" + esc(stamp.date) + "</span>";
    });
    if (!steps.length) { return '<p class="note-line">No date-stamps recorded.</p>'; }
    return '<div class="trail">' + steps.join('<span class="arrow">\u2192</span>') + "</div>";
  }

  function metricsChips(email) {
    var names = { ttS: "time-to-system", Td: "triage duration", Wd: "work duration",
                  tttR: "total time to resolution" };
    var out = [], key;
    for (key in names) {
      if (email.metrics && email.metrics[key] !== undefined) {
        out.push(chip(names[key], email.metrics[key] + "d"));
      }
    }
    return out.join("");
  }

  function renderReader(email) {
    var target = $("reader");
    if (!email) {
      $("read-title").innerHTML = "Message";
      target.innerHTML = '<p class="empty">Select a message on the left to read it.</p>';
      return;
    }
    $("read-title").innerHTML = esc(email.folderLabel) +
      ' <span class="count">' + esc(email.file) + "</span>";

    var chips = [
      chip("", email.status || "untracked", "status-" + (email.status || "untracked")),
      chip("", email.folderLabel),
      email.ageDays === null || email.ageDays === undefined ? "" : chip("age", email.ageDays + " days"),
      chip("to", email.account),
      chip("ref", email.ref)
    ];
    (email.flags || []).forEach(function (flag) { chips.push(chip("", flag, "flag")); });

    var annotations = [
      headerRow("Project", email.project),
      headerRow("Next action", email.nextAction),
      headerRow("Notes", email.notes)
    ].join("");

    var html = [
      "<h2 class=\"read-subject\">" + esc(email.subject) + "</h2>",
      '<div class="chips">' + chips.join("") + "</div>",
      '<div class="hdr"><dl>',
      headerRow("From", email.from),
      headerRow("To", email.to),
      headerRow("Cc", email.cc),
      headerRow("Bcc", email.bcc),
      headerRow("Date", email.dateDisplay),
      headerRow("File", email.file),
      (email.attachments || []).length
        ? headerRow("Attached", email.attachments.join(", ")) : "",
      email.error ? headerRow("Error", email.error) : "",
      "</dl></div>",
      '<div class="section-head">Workflow</div>',
      trailHtml(email),
      metricsChips(email) ? '<div class="chips">' + metricsChips(email) + "</div>" : "",
      '<div class="section-head">Annotations</div>',
      annotations ? '<div class="hdr"><dl>' + annotations + "</dl></div>"
                  : '<p class="note-line">Nothing recorded yet.</p>',
      '<div class="section-head">Do something about it</div>',
      '<div class="actions" id="reader-actions"></div>',
      '<p class="note-line">This site is a read-only report. These buttons build the '
        + "command to run in your terminal &mdash; nothing here changes your workflow.</p>",
      '<div class="section-head">Message history <span class="count">'
        + plural((email.thread || []).length, "message") + "</span></div>",
      (email.thread || []).length > 1
        ? '<div class="actions"><button class="btn" type="button" id="expand-all">'
          + "Expand quoted history</button></div>" : "",
      threadHtml(email)
    ];
    target.innerHTML = html.join("\n");
    target.scrollTop = 0;
    renderActions($("reader-actions"), email);

    var expand = $("expand-all");
    if (expand) {
      expand.addEventListener("click", function () {
        var open = expand.getAttribute("data-open") !== "yes";
        var all = target.querySelectorAll("details.msg");
        for (var n = 0; n < all.length; n++) { all[n].open = open; }
        expand.setAttribute("data-open", open ? "yes" : "no");
        expand.textContent = open ? "Collapse quoted history" : "Expand quoted history";
      });
    }
  }

  /* -------------------------------------------------------- overview pane */
  function renderOverview() {
    var counts = OVERVIEW.counts || {};
    var statuses = OVERVIEW.statuses || {};
    var cards = SECTIONS.map(function (section) {
      return '<button class="card" type="button" data-section="' + esc(section.key) + '">' +
        '<div class="big">' + (counts[section.key] || 0) + "</div>" +
        '<div class="lbl">' + esc(section.label) + "</div></button>";
    }).join("");

    var attention = (OVERVIEW.attention || []).map(function (item) {
      var cls = "card" + (item.count ? (item.key === "input" || item.key === "stale"
        || item.key === "weird" ? " attn-hot" : "") : " attn-0");
      return '<button class="' + cls + '" type="button" data-attn="' + esc(item.key) + '">' +
        '<div class="big">' + item.count + "</div>" +
        '<div class="lbl">' + esc(item.label) + "</div>" +
        '<div class="hint">' + esc(item.hint) + "</div></button>";
    }).join("");

    var statusRows = ["ongoing", "resolved", "weird", "untracked"].map(function (key) {
      return "<tr><th>" + esc(key) + '</th><td class="num">' + (statuses[key] || 0) +
        "</td></tr>";
    }).join("");

    var projects = (OVERVIEW.projects || []);
    var projectRows = projects.length ? projects.map(function (project) {
      return "<tr><td>" + esc(project.name) + '</td><td class="num">' + project.count +
        '</td><td><button class="linkish" type="button" data-project="' +
        esc(project.name) + '">show</button></td></tr>';
    }).join("") : '<tr><td colspan="3">No projects recorded.</td></tr>';

    $("read-title").innerHTML = 'Overview <span class="count">' +
      plural(counts.total || 0, "email") + " across the workflow</span>";
    $("reader").innerHTML = [
      '<div class="perf">',
      "<h2>Where everything is</h2>",
      '<p class="prose">Counts per workflow folder, as of ' + esc(DATA.generatedAt) +
        ". Click a folder to open it.</p>",
      '<div class="cards">' + cards + "</div>",
      "<h2>Needs attention</h2>",
      '<p class="prose">Each figure is a list &mdash; click to see exactly which '
        + "emails it counted.</p>",
      '<div class="cards">' + attention + "</div>",
      "<h2>Workflow status</h2>",
      '<p class="prose">How the tracked emails classify for the performance '
        + "metrics. <em>Weird</em> means an inconsistent date progression; "
        + "<em>untracked</em> means still sitting in <code>01-input</code>.</p>",
      '<div class="tablewrap"><table class="grid"><thead><tr><th>Status</th>'
        + "<th>Emails</th></tr></thead><tbody>" + statusRows + "</tbody></table></div>",
      "<h2>Projects</h2>",
      '<div class="tablewrap"><table class="grid"><thead><tr><th>Project</th>'
        + "<th>Emails</th><th></th></tr></thead><tbody>" + projectRows +
        "</tbody></table></div>",
      "</div>"
    ].join("\n");
    $("reader").scrollTop = 0;
  }

  /* -------------------------------------------------------------- actions */
  var ACTIONS = [
    {
      id: "alloc", label: "File elsewhere\u2026", scope: "tracked",
      open: function (email) {
        openModal({
          title: "File " + email.file + " elsewhere",
          intro: "`" + CLI + " alloc` moves the email and stamps the destination's "
            + "arrival date. Add a next action and both commands are chained for you.",
          fields: [
            { name: "dest", label: "Destination", type: "select",
              value: suggestDestination(email),
              options: DESTINATIONS.map(function (d) { return { value: d, label: d }; }) },
            { name: "next", label: "Next action", type: "textarea",
              value: email.nextAction,
              hint: "Optional. Leave unchanged to move the email only." }
          ],
          build: function (values) {
            var commands = [gtd("alloc", shellArg(email.file), shellArg(values.dest))];
            var next = oneLine(values.next);
            if (next && next !== oneLine(email.nextAction)) {
              commands.push(gtd("metadata", shellArg(email.file), "set next_action =",
                                dq(next)));
            }
            return chain(commands);
          }
        });
      }
    },
    {
      id: "next", label: "Set next action\u2026", scope: "tracked",
      open: function (email) {
        openModal({
          title: "Next action for " + email.file,
          intro: "The one thing that moves this email forward.",
          fields: [{ name: "next", label: "Next action", type: "textarea",
                     value: email.nextAction }],
          build: function (values) {
            var next = oneLine(values.next);
            if (!next) { return "# type a next action above to build the command"; }
            return gtd("metadata", shellArg(email.file), "set next_action =", dq(next));
          }
        });
      }
    },
    {
      id: "meta", label: "Edit metadata\u2026", scope: "tracked",
      open: function (email) {
        openModal({
          title: "Metadata for " + email.file,
          intro: "Only the fields you actually change are turned into commands.",
          fields: [
            { name: "project", label: "Project", type: "text", value: email.project },
            { name: "next_action", label: "Next action", type: "text", value: email.nextAction },
            { name: "general_notes", label: "Notes", type: "textarea", value: email.notes },
            { name: "flags", label: "Flags", type: "text",
              value: (email.flags || []).join(" "),
              hint: "Space-separated tokens, e.g. `pinned urgent`." }
          ],
          build: function (values) {
            var current = { project: email.project, next_action: email.nextAction,
                            general_notes: email.notes,
                            flags: (email.flags || []).join(" ") };
            var commands = [];
            Object.keys(current).forEach(function (field) {
              var value = oneLine(values[field]);
              if (value !== oneLine(current[field])) {
                commands.push(gtd("metadata", shellArg(email.file), "set", field, "=",
                                  dq(value)));
              }
            });
            return chain(commands) || "# edit a field above to build a command";
          }
        });
      }
    },
    {
      id: "pin", scope: "tracked",
      label: function (email) {
        return (email.flags || []).indexOf("pinned") >= 0 ? "Unpin" : "Pin";
      },
      open: function (email) {
        var pinned = (email.flags || []).indexOf("pinned") >= 0;
        openModal({
          title: (pinned ? "Unpin " : "Pin ") + email.file,
          intro: "Adds or removes the `pinned` token in the email's flags field.",
          fields: [],
          build: function () {
            return gtd(pinned ? "unpin" : "pin", shellArg(email.file));
          }
        });
      }
    },
    {
      id: "close", label: "Close with\u2026", scope: "tracked",
      open: function (email) {
        var others = EMAILS.filter(function (candidate) {
          return candidate.tracked && candidate.file !== email.file;
        });
        openModal({
          title: "Close " + email.file,
          intro: "`" + CLI + " close` archives this email and records which email "
            + "closed it. The other email must already exist in the workflow.",
          fields: [{ name: "other", label: "Closed by", type: "select",
                     value: others.length ? others[0].file : "",
                     options: others.map(function (candidate) {
                       return { value: candidate.file,
                                label: candidate.file + "  \u2014  " + candidate.subject };
                     }) }],
          build: function (values) {
            if (!values.other) { return "# no other email available to close this one"; }
            return gtd("close", shellArg(email.file), "with", shellArg(values.other));
          }
        });
      }
    },
    {
      id: "view", label: "Read in terminal\u2026", scope: "any",
      open: function (email) {
        openModal({
          title: "Read " + email.file + " in the terminal",
          intro: "Prints the full email, markdown-friendly, so it also pipes into "
            + "`glow -`.",
          fields: [],
          build: function () { return gtd("view", shellArg(email.file)); }
        });
      }
    },
    {
      id: "ingest", label: "Ingest this file\u2026", scope: "untracked",
      open: function () {
        openModal({
          title: "Ingest the files in 01-input",
          intro: "`" + CLI + " list` renames each new file to the "
            + "yyyy-mm-dd-brief-description convention, moves it into "
            + "<code>02-triage</code>, and stamps its triage date. It ingests the "
            + "whole folder, not one file.",
          fields: [],
          build: function () { return gtd("list"); }
        });
      }
    }
  ];

  function suggestDestination(email) {
    var order = ["triage", "actionable", "delegated", "reference", "archive"];
    var at = order.indexOf(email.folder);
    return at >= 0 && at + 1 < order.length ? order[at + 1] : "archive";
  }

  function actionsFor(email) {
    return ACTIONS.filter(function (action) {
      if (action.scope === "any") { return true; }
      if (action.scope === "tracked") { return !!(email && email.tracked); }
      return !!(email && !email.tracked);
    });
  }

  function renderActions(container, email) {
    if (!container) { return; }
    /* With nothing selected the buttons still render (disabled) so the toolbar
       does not jump around; show the tracked set, which is the common case. */
    var actions = email ? actionsFor(email)
      : ACTIONS.filter(function (action) { return action.scope !== "untracked"; });
    container.innerHTML = actions.map(function (action) {
      var label = typeof action.label === "function" ? action.label(email || {})
                                                     : action.label;
      return '<button class="btn" type="button" data-action="' + esc(action.id) + '"' +
        (email ? "" : " disabled") + ">" + esc(label) + "</button>";
    }).join("");
  }

  function runAction(id) {
    var email = BY_FILE[state.file];
    if (!email) { return; }
    for (var n = 0; n < ACTIONS.length; n++) {
      if (ACTIONS[n].id === id) { ACTIONS[n].open(email); return; }
    }
  }

  /* ---------------------------------------------------------------- modal */
  var modalSpec = null;

  function fieldHtml(field) {
    var id = "f-" + field.name;
    var input;
    if (field.type === "select") {
      input = '<select id="' + id + '" data-name="' + esc(field.name) + '">' +
        (field.options || []).map(function (option) {
          return '<option value="' + esc(option.value) + '"' +
            (option.value === field.value ? " selected" : "") + ">" +
            esc(option.label) + "</option>";
        }).join("") + "</select>";
    } else if (field.type === "textarea") {
      input = '<textarea id="' + id + '" class="field" data-name="' + esc(field.name) +
        '">' + esc(field.value) + "</textarea>";
    } else {
      input = '<input id="' + id + '" class="field" type="text" data-name="' +
        esc(field.name) + '" value="' + esc(field.value) + '">';
    }
    return '<div class="form-row"><label for="' + id + '">' + esc(field.label) +
      "</label><div>" + input +
      (field.hint ? '<div class="note-line">' + field.hint + "</div>" : "") +
      "</div></div>";
  }

  function modalValues() {
    var values = {};
    var inputs = $("modal-body").querySelectorAll("[data-name]");
    for (var n = 0; n < inputs.length; n++) {
      values[inputs[n].getAttribute("data-name")] = inputs[n].value;
    }
    return values;
  }

  function refreshSnippet() {
    if (!modalSpec) { return; }
    $("snippet").textContent = modalSpec.build(modalValues());
    $("copy-state").textContent = "";
  }

  function openModal(spec) {
    modalSpec = spec;
    $("modal-title").textContent = spec.title;
    $("modal-body").innerHTML =
      (spec.intro ? '<p class="note-line">' + spec.intro + "</p>" : "") +
      (spec.fields || []).map(fieldHtml).join("") +
      '<div class="section-head">Run this in your terminal</div>' +
      '<pre class="snippet" id="snippet"></pre>';
    var inputs = $("modal-body").querySelectorAll("[data-name]");
    for (var n = 0; n < inputs.length; n++) {
      inputs[n].addEventListener("input", refreshSnippet);
      inputs[n].addEventListener("change", refreshSnippet);
    }
    $("modal").hidden = false;
    refreshSnippet();
    if (inputs.length) { inputs[0].focus(); } else { $("copy-snippet").focus(); }
  }

  function closeModal() {
    $("modal").hidden = true;
    modalSpec = null;
  }

  function selectSnippet() {
    var node = $("snippet");
    if (!node || !window.getSelection) { return null; }
    var range = document.createRange();
    range.selectNodeContents(node);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    return selection;
  }

  /* Clipboard access is unavailable on file:// in some browsers (it is not a
     secure context), so fall back to selecting the text and asking execCommand,
     and failing that just leave it selected for the user to copy by hand. */
  function copySnippet() {
    var text = $("snippet").textContent;
    var done = function () { $("copy-state").textContent = "Copied"; };
    var manual = function () {
      selectSnippet();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      $("copy-state").textContent = ok ? "Copied"
        : "Selected \u2014 press " + (isMac() ? "\u2318" : "Ctrl") + "+C";
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, manual);
    } else {
      manual();
    }
  }
  function isMac() { return /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent); }

  /* --------------------------------------------------------------- render */
  function renderStatus(emails) {
    var email = BY_FILE[state.file];
    $("sb-where").textContent = (state.subset ? state.subset.label
      : (state.query ? "Search results" : SECTION_LABEL[state.section] || "")) +
      " \u00b7 " + plural(emails.length, "message");
    $("sb-file").textContent = email
      ? email.file + "  (" + email.folderDir + ")"
      : "No message selected";
  }

  function syncNav() {
    var items = document.querySelectorAll(".nav-item[data-section]");
    for (var n = 0; n < items.length; n++) {
      var active = items[n].getAttribute("data-section") === state.section;
      items[n].classList.toggle("active", active);
      if (active) { items[n].setAttribute("aria-current", "true"); }
      else { items[n].removeAttribute("aria-current"); }
    }
  }

  function render() {
    var wide = isWide();
    $("app").classList.toggle("wide", wide);
    syncNav();
    var emails = wide ? [] : listEmails();
    if (wide) {
      renderOverview();
    } else {
      if (!state.file || !emails.some(function (e) { return e.file === state.file; })) {
        state.file = emails.length ? emails[0].file : null;
      }
      renderList(emails);
      renderReader(BY_FILE[state.file]);
    }
    renderActions($("tb-actions"), BY_FILE[state.file]);
    renderStatus(wide ? EMAILS : emails);
  }

  function setSection(key, options) {
    state.section = key;
    state.subset = null;
    if (!(options && options.keepQuery)) {
      state.query = "";
      if ($("search")) { $("search").value = ""; }
    }
    state.file = null;
    if (window.location.hash.slice(1) !== key) {
      window.location.hash = key;  /* triggers hashchange, which re-renders */
    } else {
      render();
    }
  }

  function showSubset(label, files) {
    state.subset = { label: label, files: files };
    state.query = "";
    if ($("search")) { $("search").value = ""; }
    state.file = null;
    render();
  }

  function openFile(file) {
    var email = BY_FILE[file];
    if (!email) { return; }
    state.subset = null;
    state.query = "";
    if ($("search")) { $("search").value = ""; }
    state.section = email.folder;
    state.file = file;
    if (window.location.hash.slice(1) !== email.folder) {
      window.location.hash = email.folder;
    } else {
      render();
    }
  }

  /* ----------------------------------------------------------------- wire */
  function wire() {
    document.querySelectorAll(".nav-item[data-section]").forEach(function (item) {
      item.addEventListener("click", function () {
        setSection(item.getAttribute("data-section"));
      });
    });

    $("list").addEventListener("click", function (event) {
      var row = event.target.closest ? event.target.closest(".row") : null;
      if (!row) { return; }
      state.file = row.getAttribute("data-file");
      render();
    });

    $("reader").addEventListener("click", function (event) {
      var target = event.target.closest ? event.target.closest("[data-action],"
        + "[data-section],[data-attn],[data-project]") : null;
      if (!target) { return; }
      if (target.hasAttribute("data-action")) {
        runAction(target.getAttribute("data-action"));
      } else if (target.hasAttribute("data-section")) {
        setSection(target.getAttribute("data-section"));
      } else if (target.hasAttribute("data-attn")) {
        var key = target.getAttribute("data-attn");
        var item = (OVERVIEW.attention || []).filter(function (entry) {
          return entry.key === key;
        })[0];
        if (item) { showSubset(item.count + " \u00b7 " + item.label, item.files); }
      } else if (target.hasAttribute("data-project")) {
        var name = target.getAttribute("data-project");
        var project = (OVERVIEW.projects || []).filter(function (entry) {
          return entry.name === name;
        })[0];
        if (project) { showSubset("Project: " + name, project.files); }
      }
    });

    $("tb-actions").addEventListener("click", function (event) {
      var button = event.target.closest ? event.target.closest("[data-action]") : null;
      if (button && !button.disabled) { runAction(button.getAttribute("data-action")); }
    });

    $("search").addEventListener("input", function () {
      state.query = $("search").value.trim();
      state.subset = null;
      state.file = null;
      render();
    });

    $("sort").addEventListener("change", function () {
      state.sort = $("sort").value;
      render();
    });

    $("copy-snippet").addEventListener("click", copySnippet);
    $("select-snippet").addEventListener("click", function () { selectSnippet(); });
    $("close-modal").addEventListener("click", closeModal);
    $("close-modal-x").addEventListener("click", closeModal);
    $("modal").addEventListener("click", function (event) {
      if (event.target === $("modal")) { closeModal(); }
    });

    window.addEventListener("hashchange", applyHash);

    document.addEventListener("keydown", function (event) {
      if (!$("modal").hidden) {
        if (event.key === "Escape") { closeModal(); }
        return;
      }
      var tag = (event.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") {
        if (event.key === "Escape" && event.target === $("search")) {
          $("search").value = "";
          state.query = "";
          render();
          $("search").blur();
        }
        return;
      }
      if (event.key === "/") { event.preventDefault(); $("search").focus(); }
      else if (event.key === "j" || event.key === "ArrowDown") { move(1, event); }
      else if (event.key === "k" || event.key === "ArrowUp") { move(-1, event); }
    });
  }

  function move(delta, event) {
    if (isWide()) { return; }
    var emails = listEmails();
    if (!emails.length) { return; }
    var at = 0;
    for (var n = 0; n < emails.length; n++) {
      if (emails[n].file === state.file) { at = n; break; }
    }
    var next = Math.min(emails.length - 1, Math.max(0, at + delta));
    if (emails[next].file !== state.file) {
      state.file = emails[next].file;
      render();
    }
    if (event) { event.preventDefault(); }
  }

  function applyHash() {
    var hash = decodeURIComponent(window.location.hash.slice(1) || "");
    var known = hash === "overview" || SECTION_LABEL[hash] !== undefined;
    state.section = known && hash ? hash : "overview";
    state.subset = null;
    state.file = null;
    render();
  }

  window.GTDMail = { openFile: openFile, setSection: setSection };

  document.addEventListener("DOMContentLoaded", function () {
    wire();
    applyHash();
  });
})();
"""


# Written to assets/perf.js — the Performance page's charts. Reads
# window.GTD_PERF (emitted as data/performance.js) and draws the precomputed
# payloads with the bundled Plotly.
#
# selectAccount / selectFlow / selectSankey are exposed as globals on purpose:
# the account dropdown and the notebook tabs are rendered in Python (see
# dashboard.build_performance_page) with inline onchange/onclick handlers.
#
# Chart colours are read from the same CSS custom properties as the rest of the
# UI, and every chart is redrawn on the "gtd:theme" event, so dark mode is not a
# second implementation.
PERF_JS = r"""(function () {
  "use strict";

  var DATA = window.GTD_PERF || { views: {}, keys: [] };
  var activeAccount = (DATA.keys || [])[0];
  var flowMode = "monthly";
  var sankeyMode = "fanout";
  var cfg = { responsive: true, displayModeBar: false };
  var sankeyCfg = { responsive: false, displayModeBar: false };
  var PALETTE = { arrivals: "#4c78a8", resolutions: "#59a14f", backlog: "#c1524a",
                  age: "#c1524a" };

  function el(id) { return document.getElementById(id); }
  function view() { return (DATA.views || {})[activeAccount] || {}; }

  function colours() {
    var theme = window.GTDTheme;
    return {
      fg: theme ? theme.colour("--chart-fg", "#666") : "#666",
      grid: theme ? theme.colour("--chart-grid", "#ccc") : "#ccc"
    };
  }

  /* Merge a chart's own layout over the themed base, one level deep so an axis
     title does not wipe out the themed axis colours. */
  function layout(extra) {
    var c = colours();
    var base = {
      margin: { t: 20, r: 20, b: 60, l: 60 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: '"Helvetica Neue", Helvetica, Arial, sans-serif',
              color: c.fg, size: 12 },
      xaxis: { gridcolor: c.grid, zerolinecolor: c.grid, linecolor: c.grid },
      yaxis: { gridcolor: c.grid, zerolinecolor: c.grid, linecolor: c.grid },
      legend: { font: { color: c.fg } }
    };
    Object.keys(extra || {}).forEach(function (key) {
      var value = extra[key];
      if (base[key] && typeof base[key] === "object" && typeof value === "object"
          && !Array.isArray(value)) {
        base[key] = Object.assign({}, base[key], value);
      } else {
        base[key] = value;
      }
    });
    return base;
  }

  function drawStatic() {
    var v = view();
    Plotly.react("box", v.box || [],
      layout({ boxmode: "group", yaxis: { title: "days" } }), cfg);
    Plotly.react("bar", v.bar || [],
      layout({ barmode: "stack", xaxis: { title: "days" },
               yaxis: { showticklabels: false, title: "resolved emails" } }), cfg);
    Plotly.react("ageHist", [{
      type: "bar", x: v.ageLabels || [], y: v.ageCounts || [],
      marker: { color: PALETTE.age }
    }], layout({ xaxis: { title: "open age (days)" },
                 yaxis: { title: "ongoing emails" } }), cfg);
  }

  function drawFlow() {
    var v = view();
    var d = (flowMode === "weekly" ? v.flowWeekly : v.flowMonthly) || {};
    Plotly.react("flowBars", [
      { type: "bar", name: "Arrivals", x: d.periods || [], y: d.arrivals || [],
        marker: { color: PALETTE.arrivals } },
      { type: "bar", name: "Resolutions", x: d.periods || [], y: d.resolutions || [],
        marker: { color: PALETTE.resolutions } }
    ], layout({ barmode: "group", yaxis: { title: "emails" } }), cfg);
    Plotly.react("flow", [
      { type: "scatter", mode: "lines+markers", name: "Backlog (open)",
        x: d.periods || [], y: d.backlog || [], line: { color: PALETTE.backlog } }
    ], layout({ yaxis: { title: "open backlog" } }), cfg);
  }

  function sankeyTraces() {
    var v = view();
    var traces = (sankeyMode === "straight" ? v.sankeyStraight : v.sankeyFanout) || [];
    var c = colours();
    traces.forEach(function (trace) { trace.textfont = { color: c.fg, size: 12 }; });
    return traces;
  }

  function drawSankey() {
    var node = el("sankey");
    if (!node) { return; }
    var v = view();
    var height = (sankeyMode === "straight" ? v.sankeyStraightHeight
                                            : v.sankeyFanoutHeight) || 460;
    node.style.height = height + "px";
    /* Plotly.react replaces the plot in place, so nodes stay draggable and the
       instances never stack up. */
    Plotly.react(node, sankeyTraces(), {
      margin: { t: 10, r: 10, b: 10, l: 10 },
      font: { family: '"Helvetica Neue", Helvetica, Arial, sans-serif',
              color: colours().fg },
      width: node.clientWidth, height: height,
      paper_bgcolor: "rgba(0,0,0,0)"
    }, sankeyCfg);
  }

  function drawAll() {
    drawStatic();
    drawFlow();
    drawSankey();
  }

  function selectFlow(mode) {
    flowMode = mode;
    el("flow-monthly").setAttribute("aria-selected", String(mode === "monthly"));
    el("flow-weekly").setAttribute("aria-selected", String(mode === "weekly"));
    drawFlow();
  }

  function selectSankey(mode) {
    sankeyMode = mode;
    el("tab-fanout").setAttribute("aria-selected", String(mode === "fanout"));
    el("tab-straight").setAttribute("aria-selected", String(mode === "straight"));
    el("sankey-caption").textContent = (mode === "straight")
      ? "Plotly places the nodes automatically."
      : "Node spacing widens left to right, so the flows fan out.";
    drawSankey();
  }

  /* Switching account flips which pre-rendered HTML blocks are visible, then
     redraws every chart from that view's precomputed payload. */
  function selectAccount(name) {
    activeAccount = name;
    var blocks = document.getElementsByClassName("acct-block");
    for (var n = 0; n < blocks.length; n++) {
      blocks[n].hidden = (blocks[n].getAttribute("data-account") !== name);
    }
    drawAll();
  }

  window.selectFlow = selectFlow;
  window.selectSankey = selectSankey;
  window.selectAccount = selectAccount;

  function noPlotly() {
    var charts = document.getElementsByClassName("chart");
    for (var n = 0; n < charts.length; n++) {
      charts[n].innerHTML = '<p class="chart-missing">Charts unavailable: '
        + "assets/plotly.min.js did not load. Re-run "
        + "<code>generate_dashboard</code> to rebuild the site.</p>";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!window.Plotly) { noPlotly(); return; }
    drawAll();
    window.addEventListener("gtd:theme", drawAll);

    /* Redraw the Sankey when the window width actually changes (it is drawn at a
       fixed pixel width, unlike the responsive charts). */
    var node = el("sankey");
    var width = node ? node.clientWidth : 0;
    var timer;
    window.addEventListener("resize", function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        if (node && node.clientWidth !== width) {
          width = node.clientWidth;
          drawSankey();
        }
      }, 200);
    });
  });
})();
"""
