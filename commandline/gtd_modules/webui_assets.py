"""
Static assets for the generated website: the stylesheet and the three scripts,
held as plain string constants and written to disk verbatim by `webui.py`.

They live here (rather than as files shipped alongside the code) so the generator
stays a self-contained Python package: nothing to install, nothing to locate at
run time, and no chance of the code and its assets drifting apart in a release.

  * STYLE_CSS  — layout + the Clearlooks/early-2000s theme, light and dark.
  * SETTINGS_JS — applies every saved preference before first paint, and drives
    the Settings dialog (appearance mode, tone, the three font stacks, reset).
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
    which read the same variables (see PERF_JS `colours`). Preferences live in one
    localStorage blob owned by SETTINGS_JS; nothing else may write it.
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
# Written to assets/theme.css in BOTH builds: the colour/typography custom
# properties and nothing else. Layout lives in clearlooks.css (desktop) and
# mobile.css (mobile), both of which consume these names.
#
# Keeping the tokens in one file is what makes light/dark, Warm/Neutral and the
# font settings work identically on both builds without a second implementation —
# `settings.js` flips `data-theme`/`data-tone` on <html> and sets the font
# properties inline, and every rule in either layout file resolves through here.
THEME_CSS = r"""/* ==========================================================================
   GTD-over-EML — theme tokens (colour + typography), shared by both builds.
   Four sets: Warm light (:root), Warm dark, Neutral light, Neutral dark.
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

/* --------------------------------------------------------------------------
   NEUTRAL tone. Identical in structure to the Warm sets above; every grey is
   the same perceptual lightness with its warm cast removed and a whisper of
   cool added (a nod to MATE's TraditionalOk, whose window grey is #edeceb).
   Chromatic tokens — selection blue, accent, the age colours, the ok/warn
   tints — stay chromatic so nothing loses its meaning; the selection blue
   borrows TraditionalOk's #86abd9.

   Selector order matters: these single-attribute blocks must come AFTER
   [data-theme="dark"], and the combined neutral+dark block after both, so the
   more specific pairing always wins. Each block therefore defines the FULL
   colour token set — a partial block would inherit the wrong tone's greys.
   -------------------------------------------------------------------------- */
[data-tone="neutral"] {
  --bg-window: #dadadc;
  --bg-panel: #ffffff;
  --bg-panel-alt: #f3f3f5;
  --bg-inset: #fafafc;
  --chrome-top: #f5f5f7;
  --chrome-bot: #d8d8da;
  --title-top: #efeff1;
  --title-bot: #d7d7d9;
  --sidebar-top: #e8e8ea;
  --sidebar-bot: #d9d9db;
  --btn-top: #fdfdff;
  --btn-bot: #dadadc;
  --btn-top-hover: #ffffff;
  --btn-bot-hover: #e5e5e7;

  --bd-strong: #959597;
  --bd-soft: #bebec0;
  --bd-light: #ffffff;
  --shadow: rgba(0, 0, 0, 0.28);

  --fg: #29292b;
  --fg-soft: #4f4f51;
  --fg-muted: #757577;
  --fg-on-sel: #ffffff;
  --accent: #2c5d9b;

  --sel-top: #86abd9;
  --sel-bot: #4a72a8;
  --sel-bd: #38577f;

  --age-green: #3d8c46;
  --age-yellow: #bc8a2a;
  --age-red: #b04641;
  --ok-bg: #e3ecdf;
  --warn-bg: #eeeada;

  --chart-fg: #474749;
  --chart-grid: #cacacc;
}

[data-tone="neutral"][data-theme="dark"] {
  --bg-window: #303032;
  --bg-panel: #252527;
  --bg-panel-alt: #2b2b2d;
  --bg-inset: #1f1f21;
  --chrome-top: #474749;
  --chrome-bot: #323234;
  --title-top: #434345;
  --title-bot: #343436;
  --sidebar-top: #3a3a3c;
  --sidebar-bot: #2f2f31;
  --btn-top: #4b4b4d;
  --btn-bot: #373739;
  --btn-top-hover: #565658;
  --btn-bot-hover: #404042;

  --bd-strong: #161618;
  --bd-soft: #49494b;
  --bd-light: rgba(255, 255, 255, 0.10);
  --shadow: rgba(0, 0, 0, 0.6);

  --fg: #e4e4e6;
  --fg-soft: #c6c6c8;
  --fg-muted: #969698;
  --fg-on-sel: #ffffff;
  --accent: #8fb6e6;

  --sel-top: #6389bb;
  --sel-bot: #3a5883;
  --sel-bd: #253850;

  --age-green: #7cc088;
  --age-yellow: #d9ae5f;
  --age-red: #dc827d;
  --ok-bg: #313e33;
  --warn-bg: #403d2f;

  --chart-fg: #c4c4c6;
  --chart-grid: #49494b;
}

[data-body-font="mono"] { --font-body: var(--font-mono); }

/* Account label colours, mirroring my_own_accounts' `colour` values in
   config.yml so an account reads the same in the browser as in the terminal
   report. Deliberately tone-independent: these are identity colours, not part of
   the grey cast. */
:root {
  --acct-green: #2f7a34;
  --acct-yellow: #8a6300;
  --acct-red: #a63a31;
  --acct-blue: #2c5d9b;
  --acct-magenta: #8a3583;
  --acct-cyan: #1f6773;
}
[data-theme="dark"] {
  --acct-green: #83c98c;
  --acct-yellow: #ddb45f;
  --acct-red: #e58d86;
  --acct-blue: #93b9e8;
  --acct-magenta: #d597ce;
  --acct-cyan: #86c2ce;
}
"""


STYLE_CSS = r"""/* ==========================================================================
   GTD-over-EML — desktop layout. Colours and typography come from theme.css,
   which must be loaded first. This file is the Clearlooks / early-2000s window:
   soft vertical gradients, explicit bevelled borders, sunken panels, 3px radii.
   ========================================================================== */

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
/* Must out-specify `.btn:hover:not(:disabled)`, which would otherwise replace
   the blue gradient with the pale grey one and leave white text on near-white. */
.btn.primary:hover:not(:disabled) {
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  filter: brightness(1.08);
}
.btn.primary:active:not(:disabled) {
  background: linear-gradient(to bottom, var(--sel-bot), var(--sel-top));
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
  filter: none;
}
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
/* Account filter strip at the top of the message list, shown for Inbox/Sent. */
.list-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-bottom: 1px solid var(--bd-soft);
  background: linear-gradient(to bottom, var(--chrome-top), var(--chrome-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
  font-size: 11.5px;
  color: var(--fg-soft);
}
.list-filter[hidden] { display: none; }
.list-filter select { flex: 1 1 auto; min-width: 0; }
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
/* Off-radar mail recedes when the reader asks for it: the age dot is already
   rendered grey, so this greys the subject to match. */
.row.off-radar .subject { color: var(--fg-muted); font-weight: 400; }
.row.selected.off-radar .subject { color: inherit; font-weight: 700; }
/* The owning account, bold and in its configured colour so it reads at a glance. */
.acct { font-weight: 700; margin-right: 6px; }
.acct-green { color: var(--acct-green); }
.acct-yellow { color: var(--acct-yellow); }
.acct-red { color: var(--acct-red); }
.acct-blue { color: var(--acct-blue); }
.acct-magenta { color: var(--acct-magenta); }
.acct-cyan { color: var(--acct-cyan); }
/* On a selected row the blue gradient wins, so the identity colour steps aside
   rather than fighting it for contrast. */
.row.selected .acct { color: inherit; }
.row .due {
  flex: 0 0 auto;
  font-size: 10.5px;
  font-weight: 700;
  padding: 0 5px;
  border: 1px solid var(--bd-soft);
  border-radius: 8px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
}
.row .due.overdue {
  color: #fff;
  border-color: rgba(0, 0, 0, 0.35);
  background-color: var(--age-red);
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.28), rgba(0, 0, 0, 0.12));
}
/* On a selected row the badge inverts into a white pill with dark text, so it
   stays legible against the blue gradient instead of inheriting white-on-pale. */
.row.selected .due {
  color: var(--sel-bd);
  border-color: rgba(255, 255, 255, 0.85);
  background: linear-gradient(to bottom, #ffffff, rgba(255, 255, 255, 0.84));
}
/* An overdue badge keeps its red pill — it carries its own background, so it
   reads fine on the selection and stays semantically red. */
.row.selected .due.overdue {
  color: #fff;
  border-color: rgba(0, 0, 0, 0.45);
  background-color: var(--age-red);
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.30), rgba(0, 0, 0, 0.14));
}

/* Collapsible date groups in the message list. The header is sticky so you can
   always see which period you are scrolled into. */
.date-group { border-bottom: 1px solid var(--bd-soft); }
.group-head {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  font: inherit;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--fg-soft);
  text-align: left;
  cursor: pointer;
  padding: 3px 8px;
  border: none;
  border-top: 1px solid var(--bd-light);
  border-bottom: 1px solid var(--bd-soft);
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
}
.group-head:hover { background: linear-gradient(to bottom, var(--btn-top-hover), var(--title-bot)); }
.group-head .twisty { width: 10px; font-size: 10px; color: var(--fg-muted); }
.group-head .group-count {
  font-weight: 400;
  letter-spacing: 0;
  color: var(--fg-muted);
  border: 1px solid var(--bd-soft);
  border-radius: 8px;
  padding: 0 5px;
  background: var(--bg-panel);
}
.group-body[hidden] { display: none; }
/* The age dot and the reading pane's age pill share this glossy bevel so the
   two readings of "how old is this" match exactly. Using a translucent overlay
   gradient over a solid background-color means each age colour needs only ONE
   token, in every tone and theme. */
.dot, .chip.age {
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.30), rgba(0, 0, 0, 0.12));
  border: 1px solid rgba(0, 0, 0, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
}
.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex: 0 0 auto;
}
.dot.green, .chip.age.green { background-color: var(--age-green); }
.dot.yellow, .chip.age.yellow { background-color: var(--age-yellow); }
.dot.red, .chip.age.red { background-color: var(--age-red); }
.dot.none, .chip.age.none { background-color: var(--bd-soft); }
.chip.age {
  color: #fff;
  font-weight: 700;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
}
.chip.age b { color: #fff; }
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
.chip.due-chip { border-color: var(--bd-strong); }
.chip.due-chip.overdue {
  color: #fff;
  border-color: rgba(0, 0, 0, 0.35);
  background-color: var(--age-red);
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.28), rgba(0, 0, 0, 0.12));
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
}
.chip.due-chip.overdue b { color: #fff; }
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
/* Each message carries its own From/To/Date block, so the reading pane reads as
   a thread rather than one envelope followed by undifferentiated text. */
.msg .msg-meta {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1px 8px;
  margin: 0;
  padding: 7px 10px 0;
  font-size: 12px;
}
.msg .msg-meta dt {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
  padding-top: 1px;
}
.msg .msg-meta dd { margin: 0; overflow-wrap: anywhere; color: var(--fg-soft); }
.msg .msg-attach {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
  padding: 6px 10px 0;
}
.msg .attach-label {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
}
.msg .attach {
  font-size: 11.5px;
  padding: 1px 7px;
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.msg .msg-empty { margin: 0; padding: 9px 10px; font-style: italic; }
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

/* Settings dialog: grouped rows, with the destructive reset set apart. */
/* The Settings dialog gets its own sidebar, mirroring the app's chrome. */
.wide-window { width: min(860px, 100%); }
.settings-layout {
  display: grid;
  grid-template-columns: 168px minmax(0, 1fr);
  gap: 0;
  overflow: hidden;
}
.settings-nav {
  padding: 8px 6px;
  border-right: 1px solid var(--bd-strong);
  background: linear-gradient(to bottom, var(--sidebar-top), var(--sidebar-bot));
  box-shadow: inset -1px 0 0 var(--bd-light);
  overflow-y: auto;
}
.settings-layout > .body { overflow: auto; }
.settings-pane[hidden] { display: none; }
.check-column { flex-direction: column; align-items: stretch; }
.check-column label { justify-content: flex-start; }

.settings-group {
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  background: var(--bg-panel-alt);
  box-shadow: inset 0 1px 0 var(--bd-light);
  padding: 9px 11px 4px;
  margin-bottom: 10px;
}
.settings-group > legend, .settings-group > .legend {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--fg-muted);
  padding: 0 4px;
}
.radio-row { display: flex; flex-wrap: wrap; gap: 4px; }
/* Segmented control: radios drawn as a row of joined buttons. */
.radio-row label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  cursor: pointer;
  border: 1px solid var(--bd-strong);
  border-radius: 3px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.radio-row label:hover {
  background: linear-gradient(to bottom, var(--btn-top-hover), var(--btn-bot-hover));
}
.radio-row label.checked {
  color: var(--fg-on-sel);
  border-color: var(--sel-bd);
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.3);
}
.settings-group .form-row { grid-template-columns: 148px minmax(0, 1fr); }
.settings-group .form-row .field { font-family: var(--font-mono); font-size: 12px; }
.danger-zone {
  border: 1px solid var(--age-red);
  border-radius: 3px;
  padding: 9px 11px;
  background: linear-gradient(to bottom, var(--warn-bg), var(--btn-bot));
}
.danger-zone .btn { border-color: var(--age-red); }
.sample {
  margin: 6px 0 2px;
  padding: 6px 8px;
  border: 1px solid var(--bd-soft);
  border-radius: 3px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.12);
  font-size: 12.5px;
}
.sample .s-ui { font-family: var(--font-ui); }
.sample .s-body { font-family: var(--font-body); }
.sample .s-mono { font-family: var(--font-mono); }

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
  .settings-layout { grid-template-columns: minmax(0, 1fr); }
  .settings-nav {
    display: flex;
    gap: 4px;
    border-right: none;
    border-bottom: 1px solid var(--bd-strong);
    box-shadow: inset 0 -1px 0 var(--bd-light);
  }
}
"""


# Written to assets/settings.js. Loaded synchronously in <head> so the theme and
# fonts are applied BEFORE first paint (no flash of the wrong appearance), which
# also means it must not touch document.body — it wires the toolbar button and the
# dialog on DOMContentLoaded instead.
#
# It owns every user preference, stored as ONE JSON blob under a single
# localStorage key so that "reset" is a single removeItem and so a future setting
# needs no new key. localStorage is wrapped in try/catch throughout because
# browsers routinely refuse it for file:// pages; with storage unavailable the
# settings still apply for the session and simply do not persist.
SETTINGS_JS = r"""(function () {
  "use strict";

  var KEY = "gtd-eml.settings";
  var root = document.documentElement;

  /* Defaults. `mode: "auto"` follows the OS; `tone` picks the grey cast. The
     three font stacks are empty when default, meaning "whatever the stylesheet
     says" — so an empty field is not a broken font, it is the built-in one. */
  var DEFAULTS = {
    mode: "auto",
    tone: "warm",
    fontUi: "",
    fontBody: "",
    fontMono: "",
    groupByDate: true,
    /* Time & dates. `timeZone` is an IANA name, or "" for the browser's own zone.
       `dateFormat` is long/medium/iso. `naiveDates` says how to read a quoted
       header that named no timezone: "local" (as written) or "utc" (convert). */
    timeZone: "",
    dateFormat: "long",
    naiveDates: "local",
    /* Grey out mail in folders that are not on the reader's radar. */
    dimOffRadar: false
  };
  /* Which workflow folders count as "on your radar". Shared by the due-date,
     pinned and hashtag views. Open folders are in by default; reference and
     archive are out, because filed-away mail is off the radar and counting it
     would bury the mail that is still on it. */
  var RADAR_SCOPE_DEFAULTS = {
    input: true, triage: true, actionable: true, delegated: true,
    reference: false, archive: false
  };
  /* Remembered interface state (NOT a preference): which sidebar entry was open,
     which message was selected in it, and any pane-2 filter. Restored on load
     and dropped wholesale if any part of it no longer resolves. */
  var UI_DEFAULTS = { section: "", file: "", account: "", sort: "",
                      /* mobile only: which bottom tab was open. The desktop build
                         never sets it, and ignores it on restore. */
                      tab: "" };
  /* Shown as the placeholder in each font field, and what an empty value yields.
     Kept in step with STYLE_CSS's :root declarations. */
  var STOCK_FONTS = {
    fontUi: '"Helvetica Neue", Helvetica, Arial, sans-serif',
    fontBody: '"Helvetica Neue", Helvetica, Arial, sans-serif',
    fontMono: '"Courier New", Courier, monospace'
  };
  var FONT_VAR = { fontUi: "--font-ui", fontBody: "--font-body", fontMono: "--font-mono" };

  function read() {
    var stored = null;
    try { stored = window.localStorage.getItem(KEY); } catch (e) { stored = null; }
    var parsed = {};
    if (stored) {
      try { parsed = JSON.parse(stored) || {}; } catch (e) { parsed = {}; }
    }
    var out = {};
    Object.keys(DEFAULTS).forEach(function (k) {
      if (typeof DEFAULTS[k] === "boolean") {
        out[k] = (typeof parsed[k] === "boolean") ? parsed[k] : DEFAULTS[k];
      } else {
        out[k] = (typeof parsed[k] === "string" && parsed[k] !== "") ? parsed[k] : DEFAULTS[k];
      }
    });
    /* An empty string is meaningful for some settings — a font field means "use
       the stock stack", and an empty timeZone means "use the browser's zone" — so
       restore those verbatim rather than through the truthiness check above. */
    Object.keys(FONT_VAR).concat(["timeZone"]).forEach(function (k) {
      if (typeof parsed[k] === "string") { out[k] = parsed[k]; }
    });
    out.radarScope = {};
    Object.keys(RADAR_SCOPE_DEFAULTS).forEach(function (k) {
      var stored = parsed.radarScope && parsed.radarScope[k];
      out.radarScope[k] = (typeof stored === "boolean") ? stored : RADAR_SCOPE_DEFAULTS[k];
    });
    out.ui = {};
    Object.keys(UI_DEFAULTS).forEach(function (k) {
      out.ui[k] = (typeof (parsed.ui || {})[k] === "string") ? parsed.ui[k] : UI_DEFAULTS[k];
    });
    return out;
  }

  var current = read();

  function persist() {
    try { window.localStorage.setItem(KEY, JSON.stringify(current)); }
    catch (e) { /* storage unavailable: session-only, which is fine */ }
  }

  function systemDark() {
    return !!(window.matchMedia &&
              window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function resolvedTheme() {
    if (current.mode === "dark") { return "dark"; }
    if (current.mode === "light") { return "light"; }
    return systemDark() ? "dark" : "light";
  }

  function apply() {
    root.setAttribute("data-theme", resolvedTheme());
    root.setAttribute("data-tone", current.tone === "neutral" ? "neutral" : "warm");
    Object.keys(FONT_VAR).forEach(function (k) {
      if (current[k]) { root.style.setProperty(FONT_VAR[k], current[k]); }
      else { root.style.removeProperty(FONT_VAR[k]); }
    });
    try {
      window.dispatchEvent(new CustomEvent("gtd:theme", { detail: resolvedTheme() }));
    } catch (e) { /* very old browser: charts just keep their colours */ }
  }

  /* Fired when a setting that affects CONTENT (not just colour) changes, so
     app.js can re-render the message list. Colour/font changes need no re-render
     because they are pure CSS. */
  function announce() {
    try {
      window.dispatchEvent(new CustomEvent("gtd:settings", { detail: Settings.all() }));
    } catch (e) { /* very old browser */ }
  }

  var Settings = {
    all: function () { var copy = {}; Object.keys(current).forEach(function (k) {
      copy[k] = current[k]; }); return copy; },
    get: function (name) { return current[name]; },
    /* Dotted names address the nested groups, e.g. "radarScope.archive". */
    set: function (name, value) {
      var parts = name.split(".");
      if (parts.length === 2) { current[parts[0]][parts[1]] = value; }
      else { current[name] = value; }
      persist();
      apply();
      syncForm();
      announce();
    },
    radarScope: function () { return current.radarScope; },
    /* Interface state is saved without re-applying the theme or redrawing. */
    ui: function () {
      var copy = {};
      Object.keys(UI_DEFAULTS).forEach(function (k) { copy[k] = current.ui[k]; });
      return copy;
    },
    setUi: function (state) {
      Object.keys(UI_DEFAULTS).forEach(function (k) {
        current.ui[k] = (state && typeof state[k] === "string") ? state[k] : "";
      });
      persist();
    },
    clearUi: function () {
      Object.keys(UI_DEFAULTS).forEach(function (k) { current.ui[k] = ""; });
      persist();
    },
    reset: function () {
      try { window.localStorage.removeItem(KEY); } catch (e) { /* nothing to clear */ }
      current = read();   /* back to defaults, UI state included */
      apply();
      syncForm();
      announce();
    },
    theme: function () { return resolvedTheme(); },
    /* Read a CSS custom property so scripts (and Plotly) can use theme colours. */
    colour: function (name, fallback) {
      var value = getComputedStyle(root).getPropertyValue(name);
      return (value || "").trim() || fallback;
    }
  };
  window.GTDSettings = Settings;

  /* ------------------------------------------------------------------ dialog */
  function syncForm() {
    var dialog = document.getElementById("settings-modal");
    if (!dialog) { return; }
    dialog.querySelectorAll("input[type=radio]").forEach(function (input) {
      var on = current[input.name] === input.value;
      input.checked = on;
      if (input.parentNode && input.parentNode.classList) {
        input.parentNode.classList.toggle("checked", on);
      }
    });
    dialog.querySelectorAll("input[type=checkbox][data-setting]").forEach(function (box) {
      var name = box.getAttribute("data-setting");
      var parts = name.split(".");
      var on = (parts.length === 2) ? !!current[parts[0]][parts[1]] : !!current[name];
      box.checked = on;
      if (box.parentNode && box.parentNode.classList) {
        box.parentNode.classList.toggle("checked", on);
      }
    });
    Object.keys(FONT_VAR).forEach(function (k) {
      var field = document.getElementById("set-" + k);
      if (field && field.value !== current[k]) { field.value = current[k]; }
      if (field) { field.placeholder = STOCK_FONTS[k]; }
    });
    fillZones();
    dialog.querySelectorAll("select[data-setting]").forEach(function (select) {
      var name = select.getAttribute("data-setting");
      var parts = name.split(".");
      var value = (parts.length === 2) ? current[parts[0]][parts[1]] : current[name];
      if (select.value !== value) { select.value = value; }
    });
    var note = document.getElementById("settings-storage-note");
    if (note) {
      var available = true;
      try { window.localStorage.setItem(KEY + ".probe", "1");
            window.localStorage.removeItem(KEY + ".probe"); }
      catch (e) { available = false; }
      note.textContent = available
        ? "Settings are saved in this browser's local storage for this site."
        : "This browser blocks local storage for local files, so these settings "
          + "apply to this session only.";
    }
  }

  /* The timezone list is long and comes from Intl, so build it once and keep the
     "System default" entry first — an empty value, meaning "whatever the browser
     reports", which is what most people want. */
  function fillZones() {
    var select = document.getElementById("set-timeZone");
    if (!select || select.options.length > 1) { return; }
    var zones = (window.GTDDates && window.GTDDates.zoneOptions()) || [];
    var detected = "";
    try { detected = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; }
    catch (e) { detected = ""; }
    var html = ['<option value="">System default'
                + (detected ? " (" + detected + ")" : "") + "</option>"];
    zones.forEach(function (name) {
      html.push('<option value="' + name + '">' + name + "</option>");
    });
    select.innerHTML = html.join("");
    select.value = current.timeZone || "";
  }

  function openDialog() {
    var dialog = document.getElementById("settings-modal");
    if (!dialog) { return; }
    syncForm();
    dialog.hidden = false;
    var first = dialog.querySelector("input[type=radio]:checked, input[type=radio]");
    if (first) { first.focus(); }
  }
  function closeDialog() {
    var dialog = document.getElementById("settings-modal");
    if (dialog) { dialog.hidden = true; }
  }
  Settings.open = openDialog;
  Settings.close = closeDialog;

  function wire() {
    var button = document.getElementById("settings-button");
    if (button) { button.addEventListener("click", openDialog); }

    var dialog = document.getElementById("settings-modal");
    if (!dialog) { return; }

    dialog.addEventListener("change", function (event) {
      var target = event.target;
      if (target.type === "radio") { Settings.set(target.name, target.value); }
      else if (target.type === "checkbox" && target.getAttribute("data-setting")) {
        Settings.set(target.getAttribute("data-setting"), target.checked);
      } else if (target.tagName === "SELECT" && target.getAttribute("data-setting")) {
        Settings.set(target.getAttribute("data-setting"), target.value);
      }
    });
    /* Font fields update live as you type, so you can see the effect. */
    dialog.addEventListener("input", function (event) {
      var target = event.target;
      if (target.tagName === "INPUT" && target.type === "text"
          && target.getAttribute("data-setting")) {
        current[target.getAttribute("data-setting")] = target.value;
        persist();
        apply();
      }
    });

    /* The dialog's own sidebar: show one pane at a time. */
    dialog.querySelectorAll(".settings-nav .nav-item").forEach(function (item) {
      item.addEventListener("click", function () {
        var wanted = item.getAttribute("data-pane");
        dialog.querySelectorAll(".settings-nav .nav-item").forEach(function (other) {
          other.classList.toggle("active", other === item);
        });
        dialog.querySelectorAll(".settings-pane").forEach(function (pane) {
          pane.hidden = pane.getAttribute("data-pane") !== wanted;
        });
      });
    });

    var closers = ["settings-close", "settings-close-x"];
    closers.forEach(function (id) {
      var node = document.getElementById(id);
      if (node) { node.addEventListener("click", closeDialog); }
    });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) { closeDialog(); }
    });

    var reset = document.getElementById("settings-reset");
    if (reset) {
      reset.addEventListener("click", function () {
        if (window.confirm("Clear this site's saved settings and restore the "
                           + "defaults?")) {
          Settings.reset();
        }
      });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !dialog.hidden) { closeDialog(); }
    });
  }

  /* Follow the OS while in automatic mode. */
  if (window.matchMedia) {
    var query = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function () { if (current.mode === "auto") { apply(); } };
    if (query.addEventListener) { query.addEventListener("change", onChange); }
    else if (query.addListener) { query.addListener(onChange); }
  }

  apply();
  document.addEventListener("DOMContentLoaded", function () {
    wire();
    syncForm();
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
  var VIEWS = DATA.views || [];            /* Inbox / Sent (empty if no accounts) */
  var ACCOUNTS = DATA.accounts || [];      /* my_own_accounts display names */
  var HASHTAGS = DATA.hashtags || [];      /* monitored_hashtags, if configured */
  var CLI = DATA.cli || "gtd";

  var BY_FILE = {};
  var SECTION_LABEL = { overview: "Overview" };
  var i;
  for (i = 0; i < EMAILS.length; i++) { BY_FILE[EMAILS[i].file] = EMAILS[i]; }
  for (i = 0; i < SECTIONS.length; i++) { SECTION_LABEL[SECTIONS[i].key] = SECTIONS[i].label; }
  for (i = 0; i < VIEWS.length; i++) { SECTION_LABEL[VIEWS[i].key] = VIEWS[i].label; }

  /* Inbox and Sent are account-role views, not folders: an email belongs to them
     if one of my own accounts received (inbox) or sent (sent) it. Both carry a
     per-account filter in the message list. */
  function isAccountView(key) { return key === "inbox" || key === "sent"; }

  /* Views driven by a marker on the email rather than by its folder: due dates,
     the pinned flag, and each monitored hashtag. All of them are narrowed to the
     folders the reader counts as "on radar" (a Settings value), so membership and
     the sidebar badges are computed here rather than in Python. */
  var MARKER_VIEWS = {
    "due-set": function (e) { return onRadar(e) && !!e.dueDate; },
    "due-unset": function (e) { return onRadar(e) && !e.dueDate; },
    "pinned": function (e) { return onRadar(e) && (e.flags || []).indexOf("pinned") >= 0; }
  };
  SECTION_LABEL["due-set"] = "Due date set";
  SECTION_LABEL["due-unset"] = "Due date not set";
  SECTION_LABEL["pinned"] = "Pinned";

  /* One view per configured hashtag: a case-insensitive substring match on
     next_action, which is where these tags are written. */
  HASHTAGS.forEach(function (entry) {
    var needle = String(entry.tag || "").toLowerCase();
    SECTION_LABEL[entry.key] = entry.label;
    MARKER_VIEWS[entry.key] = function (email) {
      return onRadar(email) && !!needle &&
        String(email.nextAction || "").toLowerCase().indexOf(needle) >= 0;
    };
  });

  function isMarkerView(key) { return Object.prototype.hasOwnProperty.call(MARKER_VIEWS, key); }

  function radarScope() {
    var settings = window.GTDSettings;
    return (settings && settings.radarScope && settings.radarScope()) || {};
  }
  function onRadar(email) { return radarScope()[email.folder] === true; }

  function settingOn(name, fallback) {
    var settings = window.GTDSettings;
    if (!settings) { return fallback; }
    var value = settings.get(name);
    return (typeof value === "boolean") ? value : fallback;
  }

  /* section: which sidebar entry is active; subset: a temporary list built from
     an overview figure; query: the search box (searches every folder). */
  var state = { section: "overview", file: null, query: "", sort: "date-desc",
                subset: null, account: "" };  /* account: "" = all accounts */
  /* Which date groups the reader has collapsed. Session-only: it is a transient
     view preference, not something worth restoring days later. */
  var collapsed = {};

  /* ---------------------------------------------------------------- helpers */
  function $(id) { return document.getElementById(id); }

  function esc(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }

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

  /* Ordering uses `epoch` (the instant the Date header names), not the day-precision
     `date` string — two emails on the same day must still order by time. Emails
     with no usable date sort last in both directions. */
  function stamp(email) {
    return (email.epoch === null || email.epoch === undefined) ? null : email.epoch;
  }
  function byInstant(a, b, direction) {
    var ea = stamp(a), eb = stamp(b);
    if (ea === null && eb === null) { return cmp(a.subject, b.subject); }
    if (ea === null) { return 1; }
    if (eb === null) { return -1; }
    return direction * (ea - eb) || cmp(a.subject, b.subject);
  }

  var SORTERS = {
    "date-desc": function (a, b) { return byInstant(a, b, -1); },
    "date-asc": function (a, b) { return byInstant(a, b, 1); },
    "subject": function (a, b) { return cmp(low(a.subject), low(b.subject)); },
    "from": function (a, b) { return cmp(low(a.from), low(b.from)); },
    "folder": function (a, b) { return cmp(a.folderDir, b.folderDir) || byInstant(a, b, -1); },
    "due-asc": function (a, b) { return dueCmp(a, b, 1); },
    "due-desc": function (a, b) { return dueCmp(a, b, -1); }
  };

  /* Sorting by due date has three tiers, because the column is free text: real
     ISO dates first (in date order), then unparseable values (alphabetically, so
     they at least group), then emails with no due date at all. Reversing the
     direction reorders within the tiers but always leaves "no due date" last —
     flipping the sort should not fill the screen with blanks. */
  function dueTier(email) {
    if (!email.dueDate) { return 2; }
    return /^\d{4}-\d{2}-\d{2}$/.test(email.dueDate) ? 0 : 1;
  }
  function dueCmp(a, b, direction) {
    var ta = dueTier(a), tb = dueTier(b);
    if (ta !== tb) { return ta - tb; }
    if (ta === 2) { return byInstant(a, b, -1); }
    return direction * cmp(a.dueDate, b.dueDate) || byInstant(a, b, -1);
  }
  /* A due date is overdue when it is a parseable ISO date strictly before the
     reader's today. Free-text due dates (allowed by `gtd metadata`) simply never
     count as overdue rather than being guessed at. */
  function todayIso() {
    return window.GTDCommands.helpers.todayIso();
  }

  function isOverdue(email) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(email.dueDate || "")) { return false; }
    /* Compared against today IN THE READER'S ZONE, so "overdue" flips at their
       midnight rather than the browser's. */
    return email.dueDate < window.GTDDates.today();
  }

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
    } else if (isMarkerView(state.section)) {
      pool = EMAILS.filter(MARKER_VIEWS[state.section]);
    } else if (isAccountView(state.section)) {
      var role = state.section;  /* "inbox" | "sent" — the record's own key */
      pool = EMAILS.filter(function (e) {
        var names = e[role] || [];
        if (!names.length) { return false; }
        return !state.account || names.indexOf(state.account) >= 0;
      });
    } else {
      pool = EMAILS.filter(function (e) { return e.folder === state.section; });
    }
    return pool.slice().sort(SORTERS[state.sort] || SORTERS["date-desc"]);
  }

  function isWide() {
    return state.section === "overview" && !state.query && !state.subset;
  }

  /* -------------------------------------------------------- date grouping */
  /* The buckets a mail client shows: Today, Yesterday, This week, Last week,
     Earlier this month, Last month, then each earlier month of the current year
     by name, then one bucket per earlier year.
     
     These are computed HERE rather than in Python, against the reader's own
     "today". A generated site may be opened days after it was built, and a
     heading saying "Today" over week-old mail would be simply wrong. Bucket
     boundaries are contiguous and evaluated newest-first, so every date lands in
     exactly one bucket and none can fall through a gap (which is why "Earlier
     this month" exists even though a mail client rarely shows it). */
  var MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
                     "August", "September", "October", "November", "December"];

  function iso(date) {
    var m = date.getMonth() + 1, d = date.getDate();
    return date.getFullYear() + "-" + (m < 10 ? "0" : "") + m + "-" + (d < 10 ? "0" : "") + d;
  }
  function addDays(date, n) {
    var out = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    out.setDate(out.getDate() + n);
    return out;
  }
  function mondayOf(date) {
    /* getDay(): 0 = Sunday. Weeks start Monday, matching the weekly buckets the
       performance report already uses. */
    var shift = (date.getDay() + 6) % 7;
    return addDays(date, -shift);
  }

  function dateBuckets(oldestIso) {
    /* "Today" is the reader's today in the reader's chosen zone. */
    var bits = window.GTDDates.today().split("-");
    var today = new Date(+bits[0], +bits[1] - 1, +bits[2]);
    var buckets = [];
    /* `cursor` is the newest date not yet claimed by a bucket. Every bucket runs
       from its own start date up to the cursor, which then steps back to the day
       before that start. Buckets are therefore contiguous and non-overlapping BY
       CONSTRUCTION — important because ranges that merely look right can still
       collide at the edges (a Sunday belongs to "Yesterday" on a Monday, not to
       "Last week", even though the Monday-week contains it). A range whose start
       is newer than the cursor has nothing left in it and is skipped, which is
       how the empty "This week" on a Monday disappears. */
    var cursor = today;
    function claim(key, label, startDate) {
      if (startDate > cursor) { return; }
      buckets.push({ key: key, label: label, start: iso(startDate), end: iso(cursor) });
      cursor = addDays(startDate, -1);
    }

    claim("today", "Today", today);
    claim("yesterday", "Yesterday", addDays(today, -1));
    var thisMonday = mondayOf(today);
    claim("this-week", "This week", thisMonday);
    claim("last-week", "Last week", addDays(thisMonday, -7));
    claim("earlier-this-month", "Earlier this month",
          new Date(today.getFullYear(), today.getMonth(), 1));

    var oldest = oldestIso || iso(cursor);
    var firstEarlierMonth = true;
    var guard = 0;
    while (iso(cursor) >= oldest && guard++ < 600) {
      var year = cursor.getFullYear(), month = cursor.getMonth();
      if (year === today.getFullYear() || firstEarlierMonth) {
        /* Months of the current year get their own bucket, named. The month
           immediately before is "Last month" — including when that falls in the
           previous year (December, viewed from January), which is why it is
           claimed before the year buckets take over. */
        var monthStart = new Date(year, month, 1);
        claim("m-" + year + "-" + month,
              firstEarlierMonth ? "Last month" : MONTH_NAMES[month], monthStart);
        firstEarlierMonth = false;
      } else {
        /* Earlier years collapse into one bucket each. */
        claim("y-" + year, String(year), new Date(year, 0, 1));
      }
    }
    return buckets;
  }

  /* Group emails into the buckets above, keeping the caller's ordering within
     each. Emails with no parseable date collect at the end. */
  function groupByDate(emails) {
    /* Bucket on the day the email falls on in the READER'S zone, not the day the
       sender's offset put it on, or a chosen zone could file an email under the
       wrong heading. */
    var dayOf = function (email) {
      return email._day || (email._day = window.GTDDates.dayFromEpoch(email.epoch));
    };
    var dated = emails.filter(function (e) { return !!dayOf(e); });
    var oldest = dated.reduce(function (acc, e) {
      var day = dayOf(e);
      return (!acc || day < acc) ? day : acc;
    }, "");
    var buckets = dateBuckets(oldest);
    var groups = buckets.map(function (b) { return { label: b.label, key: b.key,
                                                     bucket: b, emails: [] }; });
    var undated = { label: "No date", key: "no-date", bucket: null, emails: [] };
    emails.forEach(function (email) {
      var day = dayOf(email);
      if (!day) { undated.emails.push(email); return; }
      for (var n = 0; n < groups.length; n++) {
        var b = groups[n].bucket;
        if (day >= b.start && day <= b.end) { groups[n].emails.push(email); return; }
      }
      /* Older than every bucket (should not happen: buckets extend to the oldest
         email) — keep it visible rather than dropping it. */
      undated.emails.push(email);
    });
    groups = groups.filter(function (g) { return g.emails.length > 0; });
    if (undated.emails.length) { groups.push(undated); }
    return groups;
  }

  /* ------------------------------------------------------------ list pane */
  function rowHtml(email, selected) {
    /* The compact form: a full "Tuesday, 3 August 2026" would crowd the subject
       out of a list row. */
    var when = email.epoch !== null && email.epoch !== undefined
      ? esc(window.GTDDates.compactFromEpoch(email.epoch)) : "(no date)";
    if (email.ageDays !== null && email.ageDays !== undefined) {
      when += " \u00b7 " + email.ageDays + "d";
    }
    /* Off-radar mail can be made to recede: grey dot, grey subject. */
    var dim = settingOn("dimOffRadar", false) && !onRadar(email);
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
    /* Which of my accounts this mail belongs to, in that account's configured
       colour and bold, so it reads at a glance. */
    var account = email.account
      ? '<span class="acct acct-' + esc(email.accountColour || "cyan") + '">' +
        esc(email.account) + "</span>"
      : "";
    var due = email.dueDate
      ? '<span class="due' + (isOverdue(email) ? " overdue" : "") + '">due ' +
        esc(window.GTDDates.fromIsoDay(email.dueDate)) + "</span>"
      : "";
    return '<button class="row' + (selected ? " selected" : "") +
      (dim ? " off-radar" : "") + '" type="button" ' +
      'data-file="' + esc(email.file) + '">' +
      '<span class="r1">' +
        '<span class="dot ' + (dim ? "none" : (email.ageClass || "none")) +
        '"></span>' + pin +
        '<span class="subject">' + esc(email.subject) + "</span>" +
        due +
        '<span class="when">' + when + "</span>" +
      "</span>" +
      '<span class="r2">' + account + esc(who) + "</span>" +
      '<span class="r3' + (email.nextAction ? " next" : "") + '">' + esc(third) + "</span>" +
      "</button>";
  }

  /* The filter strip only makes sense for the account views; everywhere else it
     is hidden and the filter is cleared so it cannot silently narrow a folder. */
  function renderAccountFilter() {
    var strip = $("account-filter");
    if (!strip) { return; }
    if (!isAccountView(state.section) || ACCOUNTS.length === 0) {
      strip.hidden = true;
      return;
    }
    var select = $("account-select");
    var options = ['<option value="">All accounts</option>'];
    ACCOUNTS.forEach(function (name) {
      options.push('<option value="' + esc(name) + '">' + esc(name) + "</option>");
    });
    var wanted = options.join("");
    if (select.innerHTML !== wanted) { select.innerHTML = wanted; }
    select.value = state.account;
    strip.hidden = false;
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
    if (settingOn("groupByDate", true)) {
      groupByDate(emails).forEach(function (group) {
        var open = collapsed[group.key] !== true;
        html.push('<div class="date-group">' +
          '<button class="group-head" type="button" data-group="' + esc(group.key) +
          '" aria-expanded="' + (open ? "true" : "false") + '">' +
          '<span class="twisty">' + (open ? "\u25be" : "\u25b8") + "</span>" +
          '<span class="grow">' + esc(group.label) + "</span>" +
          '<span class="group-count">' + group.emails.length + "</span></button>" +
          '<div class="group-body"' + (open ? "" : " hidden") + ">" +
          group.emails.map(function (email) {
            return rowHtml(email, email.file === state.file);
          }).join("") + "</div></div>");
      });
    } else {
      for (var n = 0; n < emails.length; n++) {
        html.push(rowHtml(emails[n], emails[n].file === state.file));
      }
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

  /* One header block per message. The newest message takes them from the .eml's
     own envelope; quoted messages use whatever thread.py managed to parse out of
     their attribution line, and simply omit what is not known. */
  function messageMeta(message, email, isNewest) {
    var rows = [];
    if (isNewest) {
      rows.push(headerRow("From", message.from || email.from));
      rows.push(headerRow("To", email.to));
      rows.push(headerRow("Cc", email.cc));
      rows.push(headerRow("Bcc", email.bcc));
      /* The .eml's own Date header: an absolute instant, shown in the reader's
         chosen zone. */
      rows.push(headerRow("Date", window.GTDDates.fromEpoch(email.epoch)));
      rows.push(headerRow("Subject", email.subject));
      rows.push(headerRow("Attached", (email.attachments || []).join(", ")));
    } else {
      rows.push(headerRow("From", message.from));
      rows.push(headerRow("To", message.to));
      rows.push(headerRow("Cc", message.cc));
      /* A quoted header: usually bare wall-clock numbers, so it goes through
         fromParts, which applies the reader's "treat as" choice. */
      rows.push(headerRow("Date",
        window.GTDDates.fromParts(message.dateParts, message.date)));
      rows.push(headerRow("Subject", message.subject));
    }
    var inner = rows.join("");
    return inner ? '<dl class="msg-meta">' + inner + "</dl>" : "";
  }

  function attachmentStrip(email) {
    var names = email.attachments || [];
    if (!names.length) { return ""; }
    return '<div class="msg-attach"><span class="attach-label">Attached</span>' +
      names.map(function (name) {
        return '<span class="attach">\u2398 ' + esc(name) + "</span>";
      }).join("") + "</div>";
  }

  function threadHtml(email) {
    var messages = email.thread || [];
    if (!messages.length) {
      /* No text body at all — but the email still has headers and possibly
         attachments, and those are the whole point of an attachment-only mail.
         Render the envelope as a message block with an empty body rather than a
         bare note, or the attachments would have nowhere to appear. */
      messages = [{ depth: 0, indent: 0, text: "", empty: true }];
    }
    var html = [];
    for (var n = 0; n < messages.length; n++) {
      var message = messages[n];
      var isNewest = n === 0;
      var who = message.from || (isNewest ? email.from : "") || "Quoted message";
      var when = isNewest
        ? window.GTDDates.fromEpoch(email.epoch)
        : window.GTDDates.fromParts(message.dateParts, message.date);
      var summary = '<span class="who">' + esc(who) + "</span>" +
        (when ? "<span>" + esc(when) + "</span>" : "");
      /* Attachments belong to the .eml itself, so they are shown with the newest
         message — the one the file actually is — rather than in a separate block
         detached from the thread. */
      var inner = messageMeta(message, email, isNewest) +
        (isNewest ? attachmentStrip(email) : "") +
        (message.empty
          ? '<p class="note-line msg-empty">No text body (this email may be '
            + "attachment-only).</p>"
          : '<pre class="msg-body">' + esc(message.text) + "</pre>");
      var cls = "msg d" + (message.indent || 0);
      if (isNewest) {
        html.push('<div class="' + cls + '"><div class="msg-head">' + summary +
                  "</div>" + inner + "</div>");
      } else {
        html.push('<details class="' + cls + '"><summary>' + summary + "</summary>" +
                  inner + "</details>");
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
    var steps = (email.stamps || []).map(function (entry) {
      return '<span class="step"><b>' + esc(entry.label) + "</b>" +
        esc(window.GTDDates.fromIsoDay(entry.date)) + "</span>";
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

    /* Age leads and is colour-coded exactly like the list's age dot, so the
       urgency reading is the same in both panes. */
    var age = (email.ageDays === null || email.ageDays === undefined)
      ? "" : ('<span class="chip age ' + (email.ageClass || "none") + '">' +
              esc(email.ageDays + (email.ageDays === 1 ? " day old" : " days old")) +
              "</span>");
    var due = email.dueDate
      ? '<span class="chip due-chip' + (isOverdue(email) ? " overdue" : "") + '">due <b>' +
        esc(window.GTDDates.fromIsoDay(email.dueDate)) + "</b>" +
        (isOverdue(email) ? " (overdue)" : "") + "</span>"
      : "";
    var chips = [
      age,
      due,
      chip("", email.status || "untracked", "status-" + (email.status || "untracked")),
      chip("", email.folderLabel),
      chip("to", email.account),
      chip("ref", email.ref)
    ];
    (email.flags || []).forEach(function (flag) { chips.push(chip("", flag, "flag")); });

    /* Annotations come first: they are the point of the system. */
    var annotations = [
      headerRow("Project", email.project),
      headerRow("Next action", email.nextAction),
      headerRow("Due date", window.GTDDates.fromIsoDay(email.dueDate)),
      headerRow("Notes", email.notes)
    ].join("");

    var html = [
      "<h2 class=\"read-subject\">" + esc(email.subject) + "</h2>",
      '<div class="chips">' + chips.join("") + "</div>",
      '<div class="section-head">Annotations</div>',
      annotations ? '<div class="hdr"><dl>' + annotations + "</dl></div>"
                  : '<p class="note-line">Nothing recorded yet. Use the toolbar '
                    + "buttons above to build the command that adds some.</p>",
      '<div class="section-head">Workflow</div>',
      trailHtml(email),
      metricsChips(email) ? '<div class="chips">' + metricsChips(email) + "</div>" : "",
      email.error ? '<div class="hdr"><dl>' + headerRow("Error", email.error)
                    + "</dl></div>" : "",
      '<div class="section-head">Message history <span class="count">'
        + plural(Math.max((email.thread || []).length, 1), "message") + "</span></div>",
      (email.thread || []).length > 1
        ? '<div class="actions"><button class="btn" type="button" id="expand-all">'
          + "Expand quoted history</button></div>" : "",
      threadHtml(email)
    ];
    target.innerHTML = html.join("\n");
    target.scrollTop = 0;

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

    $("read-title").innerHTML = 'Dashboard <span class="count">' +
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
  /* The command definitions live in commands.js (window.GTDCommands) so the
     desktop and mobile front ends cannot drift apart on what `gtd` invocation an
     action produces. This file only decides how to present them. */
  function actionsFor(email) {
    return window.GTDCommands ? window.GTDCommands.forEmail(email) : [];
  }

  function renderActions(container, email) {
    if (!container) { return; }
    /* With nothing selected the buttons still render (disabled) so the toolbar
       does not jump around; show the tracked set, which is the common case. */
    var all = window.GTDCommands ? window.GTDCommands.forEmail({ tracked: true }) : [];
    var actions = email ? actionsFor(email) : all;
    container.innerHTML = actions.map(function (action) {
      var label = window.GTDCommands.labelFor(action, email);
      return '<button class="btn" type="button" data-action="' + esc(action.id) + '"' +
        (email ? "" : " disabled") + ">" + esc(label) + "</button>";
    }).join("");
  }

  function runAction(id) {
    var email = BY_FILE[state.file];
    var action = email && window.GTDCommands ? window.GTDCommands.byId(id) : null;
    if (action) { openModal(action.spec(email)); }
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
    var generated = document.getElementById("sb-generated");
    if (generated && DATA.generatedEpoch) {
      generated.textContent = "Generated " +
        window.GTDDates.fromEpoch(DATA.generatedEpoch);
    }
    var where = state.subset ? state.subset.label
      : (state.query ? "Search results" : SECTION_LABEL[state.section] || "");
    if (isAccountView(state.section) && state.account) {
      where += " \u2014 " + state.account;
    }
    $("sb-where").textContent = where + " \u00b7 " + plural(emails.length, "message");
    $("sb-file").textContent = email
      ? email.file + "  (" + email.folderDir + ")"
      : "No message selected";
  }

  /* The Due/Pinned badges depend on the due-date scope setting, so they are
     filled in here and refreshed whenever that setting changes. */
  function syncMarkerBadges() {
    Object.keys(MARKER_VIEWS).forEach(function (key) {
      var badge = document.querySelector('[data-count-for="' + key + '"]');
      if (badge) { badge.textContent = EMAILS.filter(MARKER_VIEWS[key]).length; }
    });
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
    if (!isAccountView(state.section)) { state.account = ""; }
    syncNav();
    syncMarkerBadges();
    var emails = wide ? [] : listEmails();
    if (wide) {
      renderOverview();
    } else {
      if (!state.file || !emails.some(function (e) { return e.file === state.file; })) {
        var order = settingOn("groupByDate", true) ? visibleOrder() : emails;
        state.file = order.length ? order[0].file : null;
      }
      renderAccountFilter();
      renderList(emails);
      renderReader(BY_FILE[state.file]);
    }
    renderActions($("tb-actions"), BY_FILE[state.file]);
    renderStatus(wide ? EMAILS : emails);
  }

  function setSection(key, options) {
    state.section = key;
    state.subset = null;
    if (!isAccountView(key)) { state.account = ""; }
    if (!(options && options.keepQuery)) {
      state.query = "";
      if ($("search")) { $("search").value = ""; }
    }
    state.file = null;
    if (window.location.hash.slice(1) !== key) {
      window.location.hash = key;  /* triggers hashchange, which re-renders */
    } else {
      render();
      rememberUi();
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
      var head = event.target.closest ? event.target.closest(".group-head") : null;
      if (head) {
        var key = head.getAttribute("data-group");
        collapsed[key] = collapsed[key] !== true;
        render();
        return;
      }
      var row = event.target.closest ? event.target.closest(".row") : null;
      if (!row) { return; }
      state.file = row.getAttribute("data-file");
      rememberUi();
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

    var accountSelect = $("account-select");
    if (accountSelect) {
      accountSelect.addEventListener("change", function () {
        state.account = accountSelect.value;
        state.file = null;
        render();
        rememberUi();
      });
    }

    $("sort").addEventListener("change", function () {
      state.sort = $("sort").value;
      render();
      rememberUi();
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

  /* The order the rows actually appear in: flattened date groups when grouping is
     on, otherwise the plain sorted list. Used by j/k so the keyboard follows the
     screen even when a non-date sort is grouped by date. */
  function visibleOrder() {
    var emails = listEmails();
    if (!settingOn("groupByDate", true)) { return emails; }
    var out = [];
    groupByDate(emails).forEach(function (group) {
      group.emails.forEach(function (email) { out.push(email); });
    });
    return out;
  }

  /* Expand whichever date group holds this file, so a selection that moves into a
     collapsed group is never hidden. */
  function expandGroupFor(file) {
    if (!settingOn("groupByDate", true)) { return; }
    groupByDate(listEmails()).forEach(function (group) {
      if (group.emails.some(function (e) { return e.file === file; })) {
        delete collapsed[group.key];
      }
    });
  }

  function move(delta, event) {
    if (isWide()) { return; }
    var emails = visibleOrder();
    if (!emails.length) { return; }
    var at = 0;
    for (var n = 0; n < emails.length; n++) {
      if (emails[n].file === state.file) { at = n; break; }
    }
    var next = Math.min(emails.length - 1, Math.max(0, at + delta));
    if (emails[next].file !== state.file) {
      state.file = emails[next].file;
      expandGroupFor(state.file);
      render();
      rememberUi();
    }
    if (event) { event.preventDefault(); }
  }

  /* ------------------------------------------------------- remembered state */
  /* Saved after every navigation so a reload lands you back where you were.
     Deliberately NOT saved for the Dashboard (there is nothing to restore) or for
     a search, which is a transient action rather than a place. */
  function rememberUi() {
    var settings = window.GTDSettings;
    if (!settings || !settings.setUi) { return; }
    settings.setUi({
      section: state.subset || state.query ? "" : state.section,
      file: state.file || "",
      account: state.account || "",
      sort: state.sort || ""
    });
  }

  /* Restore in one piece, or not at all: per the requirement, if ANY remembered
     part no longer resolves — the section is gone, the email has been filed
     elsewhere or deleted, the account has been removed from config.yml — the
     whole remembered state is discarded rather than half-applied. */
  function restoreUi() {
    var settings = window.GTDSettings;
    if (!settings || !settings.ui) { return false; }
    var saved = settings.ui();
    if (!saved.section) { return false; }

    var sectionKnown = saved.section === "overview" ||
      SECTION_LABEL[saved.section] !== undefined;
    var accountOk = !saved.account ||
      (isAccountView(saved.section) && ACCOUNTS.indexOf(saved.account) >= 0);
    var sortOk = !saved.sort || Object.prototype.hasOwnProperty.call(SORTERS, saved.sort);
    if (!sectionKnown || !accountOk || !sortOk) { settings.clearUi(); return false; }

    var previous = { section: state.section, account: state.account, sort: state.sort };
    state.section = saved.section;
    state.account = saved.account;
    state.sort = saved.sort || state.sort;
    state.subset = null;
    state.query = "";

    /* The remembered email must still be present AND still belong to this view. */
    if (saved.file) {
      var visible = listEmails().some(function (e) { return e.file === saved.file; });
      if (!visible) {
        state.section = previous.section;
        state.account = previous.account;
        state.sort = previous.sort;
        settings.clearUi();
        return false;
      }
      state.file = saved.file;
    }
    if ($("sort")) { $("sort").value = state.sort; }
    return true;
  }

  function applyHash() {
    var hash = decodeURIComponent(window.location.hash.slice(1) || "");
    var known = hash === "overview" || SECTION_LABEL[hash] !== undefined;
    state.account = "";
    state.section = known && hash ? hash : "overview";
    state.subset = null;
    state.file = null;
    render();
    rememberUi();
  }

  /* First load. Navigating writes the section into the URL hash, so after any use
     of the app a reload arrives WITH a hash — which must not by itself defeat the
     remembered state. The rule: the hash decides the section, and when it names
     the same section we remembered, the remembered selection and filter are
     restored on top of it. A hash naming a DIFFERENT section is a deliberate
     navigation (a bookmark, or a link in from the Performance page) and wins
     outright. */
  function initialView() {
    var hash = decodeURIComponent(window.location.hash.slice(1) || "");
    var settings = window.GTDSettings;
    var saved = (settings && settings.ui) ? settings.ui() : {};

    if (hash) {
      if (saved.section && saved.section === hash && restoreUi()) {
        render();
        return;
      }
      applyHash();
      return;
    }
    if (restoreUi()) {
      render();
      /* Reflect the restored section in the URL without firing hashchange (which
         would reset the selection we just restored). Harmless if the browser
         refuses the History API for file:// pages. */
      try {
        window.history.replaceState(null, "", "#" + encodeURIComponent(state.section));
      } catch (e) { /* leave the URL alone */ }
      return;
    }
    render();
  }

  window.GTDMail = { openFile: openFile, setSection: setSection };

  document.addEventListener("DOMContentLoaded", function () {
    wire();
    initialView();
    /* Changing a setting can change what the list shows (grouping, due-date
       scope), so re-render rather than waiting for the next navigation. */
    window.addEventListener("gtd:settings", function () {
      /* A timezone change moves which day an email belongs to, so drop the cache. */
      EMAILS.forEach(function (email) { delete email._day; });
      render();
    });
  });
})();
"""


# Written to assets/commands.js — the single definition of every terminal command
# the site can build, shared verbatim by the desktop and mobile front ends.
#
# Why it is its own file: both UIs offer the same actions (file elsewhere, set a
# next action, set a due date, pin, close, read in terminal, ingest), and if each
# built its own command strings they would drift — one would quietly emit a stale
# flag or forget to shell-quote. Here each action is UI-AGNOSTIC data: an id, a
# scope, a label, and a `spec(email)` returning the dialog's title, its blurb, its
# fields, and a `build(values)` that returns the command line. The desktop renders
# that as a modal; mobile renders it as a bottom sheet. Neither knows how to spell
# `gtd alloc`.
COMMANDS_JS = r"""(function () {
  "use strict";

  var DATA = window.GTD_MAIL || {};
  var EMAILS = DATA.emails || [];
  var DESTINATIONS = DATA.destinations || [];
  var CLI = DATA.cli || "gtd";

  function oneLine(value) { return String(value || "").replace(/\s+/g, " ").trim(); }

  /* Shell quoting for the generated snippets: bare when safe, double-quoted (with
     $, `, \ and " escaped) otherwise. */
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
  function todayIso() {
    var now = new Date();
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    return now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate());
  }

  function suggestDestination(email) {
    var order = ["triage", "actionable", "delegated", "reference", "archive"];
    var at = order.indexOf(email.folder);
    return at >= 0 && at + 1 < order.length ? order[at + 1] : "archive";
  }

  var ACTIONS = [
    {
      id: "alloc", label: "File elsewhere\u2026", scope: "tracked",
      spec: function (email) {
        return {
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
        };
      }
    },
    {
      id: "next", label: "Set next action\u2026", scope: "tracked",
      spec: function (email) {
        return {
          title: "Next action for " + email.file,
          intro: "The one thing that moves this email forward.",
          fields: [{ name: "next", label: "Next action", type: "textarea",
                     value: email.nextAction }],
          build: function (values) {
            var next = oneLine(values.next);
            if (!next) { return "# type a next action above to build the command"; }
            return gtd("metadata", shellArg(email.file), "set next_action =", dq(next));
          }
        };
      }
    },
    {
      id: "due", label: "Set due date\u2026", scope: "tracked",
      spec: function (email) {
        return {
          title: "Due date for " + email.file,
          intro: "Stored in metadata.csv's <code>due_date</code> column. Use "
            + "yyyy-mm-dd so it can be compared against today; clear the field to "
            + "remove the due date.",
          fields: [{ name: "due", label: "Due date", type: "text",
                     value: email.dueDate,
                     hint: "e.g. " + todayIso() + ". Anything else is stored "
                       + "verbatim but never counts as overdue." }],
          build: function (values) {
            var due = oneLine(values.due);
            if (due === oneLine(email.dueDate)) {
              return "# change the date above to build the command";
            }
            return gtd("metadata", shellArg(email.file), "set due_date =", dq(due));
          }
        };
      }
    },
    {
      id: "meta", label: "Edit metadata\u2026", scope: "tracked",
      spec: function (email) {
        return {
          title: "Metadata for " + email.file,
          intro: "Only the fields you actually change are turned into commands.",
          fields: [
            { name: "project", label: "Project", type: "text", value: email.project },
            { name: "next_action", label: "Next action", type: "text", value: email.nextAction },
            { name: "due_date", label: "Due date", type: "text", value: email.dueDate },
            { name: "general_notes", label: "Notes", type: "textarea", value: email.notes },
            { name: "flags", label: "Flags", type: "text",
              value: (email.flags || []).join(" "),
              hint: "Space-separated tokens, e.g. `pinned urgent`." }
          ],
          build: function (values) {
            var current = { project: email.project, next_action: email.nextAction,
                            due_date: email.dueDate, general_notes: email.notes,
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
        };
      }
    },
    {
      id: "pin", scope: "tracked",
      label: function (email) {
        return (email.flags || []).indexOf("pinned") >= 0 ? "Unpin" : "Pin";
      },
      spec: function (email) {
        var pinned = (email.flags || []).indexOf("pinned") >= 0;
        return {
          title: (pinned ? "Unpin " : "Pin ") + email.file,
          intro: "Adds or removes the `pinned` token in the email's flags field.",
          fields: [],
          build: function () {
            return gtd(pinned ? "unpin" : "pin", shellArg(email.file));
          }
        };
      }
    },
    {
      id: "close", label: "Close with\u2026", scope: "tracked",
      spec: function (email) {
        var others = EMAILS.filter(function (candidate) {
          return candidate.tracked && candidate.file !== email.file;
        });
        return {
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
        };
      }
    },
    {
      id: "view", label: "Read in terminal\u2026", scope: "any",
      spec: function (email) {
        return {
          title: "Read " + email.file + " in the terminal",
          intro: "Prints the full email, markdown-friendly, so it also pipes into "
            + "`glow -`.",
          fields: [],
          build: function () { return gtd("view", shellArg(email.file)); }
        };
      }
    },
    {
      id: "ingest", label: "Ingest this file\u2026", scope: "untracked",
      spec: function () {
        return {
          title: "Ingest the files in 01-input",
          intro: "`" + CLI + " list` renames each new file to the "
            + "yyyy-mm-dd-brief-description convention, moves it into "
            + "<code>02-triage</code>, and stamps its triage date. It ingests the "
            + "whole folder, not one file.",
          fields: [],
          build: function () { return gtd("list"); }
        };
      }
    }
  ];

  function suggestDestination(email) {
    var order = ["triage", "actionable", "delegated", "reference", "archive"];
    var at = order.indexOf(email.folder);
    return at >= 0 && at + 1 < order.length ? order[at + 1] : "archive";
  }

  window.GTDCommands = {
    cli: CLI,
    /* The actions applicable to one email. `scope` is what keeps `alloc` off a
       file still sitting in 01-input, and `list` (ingest) on it. */
    forEmail: function (email) {
      return ACTIONS.filter(function (action) {
        if (action.scope === "any") { return true; }
        if (action.scope === "tracked") { return !!(email && email.tracked); }
        return !!(email && !email.tracked);
      });
    },
    byId: function (id) {
      for (var n = 0; n < ACTIONS.length; n++) {
        if (ACTIONS[n].id === id) { return ACTIONS[n]; }
      }
      return null;
    },
    labelFor: function (action, email) {
      return typeof action.label === "function" ? action.label(email || {}) : action.label;
    },
    helpers: { dq: dq, shellArg: shellArg, oneLine: oneLine, gtd: gtd, chain: chain,
               todayIso: todayIso }
  };
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
    var settings = window.GTDSettings;
    return {
      fg: settings ? settings.colour("--chart-fg", "#666") : "#666",
      grid: settings ? settings.colour("--chart-grid", "#ccc") : "#ccc"
    };
  }

  /* Charts should follow the UI font setting too, so read it back off the root
     rather than hard-coding the stack in two places. */
  function fontFamily() {
    var settings = window.GTDSettings;
    return (settings && settings.colour("--font-ui", "")) ||
      '"Helvetica Neue", Helvetica, Arial, sans-serif';
  }

  /* Merge a chart's own layout over the themed base, one level deep so an axis
     title does not wipe out the themed axis colours. */
  function layout(extra) {
    var c = colours();
    var base = {
      margin: { t: 20, r: 20, b: 60, l: 60 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { family: fontFamily(), color: c.fg, size: 12 },
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
      font: { family: fontFamily(), color: colours().fg },
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


# Written to mobile/assets/mobile.css.
#
# The mobile build follows smartphone-app conventions rather than the desktop's
# window metaphor: a fixed top app bar, a fixed bottom tab bar, and content as a
# stack of full-screen "pages" that slide in from the right when you tap a row.
#
# It reuses the DESKTOP THEME TOKENS verbatim (same custom properties, same
# names), so light/dark, Warm/Neutral and the font settings all work here with no
# second implementation — this file only restates the layout. The gradients and
# explicit borders stay, so the two builds are recognisably the same product; what
# changes is touch sizing (44px minimum targets), the navigation model, and the
# safe-area insets a phone needs.
MOBILE_CSS = r"""/* ==========================================================================
   GTD-over-EML — mobile build. Layout only; every colour comes from the shared
   theme tokens in the desktop stylesheet's :root (duplicated here so this build
   stays self-contained).
   ========================================================================== */

html, body {
  height: 100%;
  margin: 0;
  font-family: var(--font-ui);
  font-size: 15px;
  color: var(--fg);
  background: var(--bg-panel);
  -webkit-text-size-adjust: 100%;
}
* { box-sizing: border-box; }
a { color: var(--accent); }
code, kbd { font-family: var(--font-mono); font-size: 13px; }

/* --- app shell ---------------------------------------------------------- */
.app {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Top app bar: back (or spacer), title, menu. */
.appbar {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 48px;
  padding: 0 4px;
  padding-top: env(safe-area-inset-top, 0);
  border-bottom: 1px solid var(--bd-strong);
  background: linear-gradient(to bottom, var(--chrome-top), var(--chrome-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 1px 3px rgba(0, 0, 0, 0.12);
  z-index: 3;
}
.appbar .title {
  flex: 1 1 auto;
  min-width: 0;
  font-size: 17px;
  font-weight: 700;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.appbar .subtitle {
  display: block;
  font-size: 11px;
  font-weight: 400;
  color: var(--fg-muted);
  overflow: hidden;
  text-overflow: ellipsis;
}
/* Icon buttons: 44px touch target, bevelled like the desktop's buttons. */
.iconbtn {
  flex: 0 0 auto;
  width: 44px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font: inherit;
  color: var(--fg);
  cursor: pointer;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
}
.iconbtn:active {
  border-color: var(--bd-soft);
  background: linear-gradient(to bottom, var(--btn-bot), var(--btn-top));
}
.iconbtn[hidden] { display: none; }
.iconbtn svg { width: 22px; height: 22px; fill: none; stroke: currentColor;
  stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

/* --- the page stack ---------------------------------------------------- */
.stack {
  position: relative;
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}
.page {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  overflow: hidden;
  /* Pages slide in from the right, the standard "drill into detail" gesture. */
  transition: transform 220ms ease, opacity 220ms ease;
  transform: translateX(0);
}
.page.entering { transform: translateX(100%); }
.page.leaving { transform: translateX(100%); }
/* The page underneath drifts slightly left, so the stack reads as depth. */
.page.beneath { transform: translateX(-22%); opacity: 0.6; }
.page > .scroll {
  flex: 1 1 auto;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 12px;
}
@media (prefers-reduced-motion: reduce) {
  .page { transition: none; }
}

/* --- list rows --------------------------------------------------------- */
.list { list-style: none; margin: 0; padding: 0; }
.list-head {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--fg-soft);
  border-top: 1px solid var(--bd-light);
  border-bottom: 1px solid var(--bd-soft);
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  display: flex;
  align-items: center;
  gap: 8px;
}
.list-head .grow { flex: 1 1 auto; }
.list-head .count { font-weight: 400; letter-spacing: 0; color: var(--fg-muted); }
.list-head.tappable { cursor: pointer; width: 100%; text-align: left; font: inherit;
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.07em; border-left: none; border-right: none; }
.twisty { width: 12px; color: var(--fg-muted); font-size: 11px; }

.item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-height: 56px;
  padding: 8px 10px 8px 12px;
  font: inherit;
  color: var(--fg);
  text-align: left;
  cursor: pointer;
  background: var(--bg-panel);
  border: none;
  border-bottom: 1px solid var(--bd-soft);
}
.item:active { background: linear-gradient(to bottom, var(--bg-panel-alt), var(--btn-bot)); }
.item.selected {
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  color: var(--fg-on-sel);
}
.item .body { flex: 1 1 auto; min-width: 0; }
.item .line1 { display: flex; align-items: baseline; gap: 6px; }
.item .primary {
  flex: 1 1 auto;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.item .meta { flex: 0 0 auto; font-size: 12px; color: var(--fg-muted); }
.item .line2, .item .line3 {
  display: block;
  font-size: 13px;
  color: var(--fg-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.item .line3 { color: var(--fg-muted); font-size: 12.5px; }
.item .chev { flex: 0 0 auto; color: var(--fg-muted); font-size: 18px; }
.item .badge {
  flex: 0 0 auto;
  min-width: 26px;
  text-align: center;
  font-size: 12px;
  padding: 1px 7px;
  border: 1px solid var(--bd-soft);
  border-radius: 10px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--bg-panel), var(--bg-panel-alt));
}
.item.off-radar .primary { color: var(--fg-muted); font-weight: 400; }
.item.selected.off-radar .primary { color: inherit; font-weight: 700; }
.item .acct { font-weight: 700; margin-right: 6px; }
.acct-green { color: var(--acct-green); }
.acct-yellow { color: var(--acct-yellow); }
.acct-red { color: var(--acct-red); }
.acct-blue { color: var(--acct-blue); }
.acct-magenta { color: var(--acct-magenta); }
.acct-cyan { color: var(--acct-cyan); }
.dot {
  flex: 0 0 auto;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.30), rgba(0, 0, 0, 0.12));
}
.dot.green { background-color: var(--age-green); }
.dot.yellow { background-color: var(--age-yellow); }
.dot.red { background-color: var(--age-red); }
.dot.none { background-color: var(--bd-soft); }
.pin { color: var(--age-yellow); }
.due {
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border: 1px solid var(--bd-soft);
  border-radius: 9px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
}
.due.overdue {
  color: #fff;
  border-color: rgba(0, 0, 0, 0.35);
  background-color: var(--age-red);
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.28), rgba(0, 0, 0, 0.12));
}
.empty { padding: 24px 16px; color: var(--fg-muted); font-style: italic; }

/* --- search field ------------------------------------------------------ */
.searchbar {
  flex: 0 0 auto;
  padding: 8px 10px;
  border-bottom: 1px solid var(--bd-soft);
  background: linear-gradient(to bottom, var(--chrome-top), var(--chrome-bot));
}
.searchbar input {
  width: 100%;
  min-height: 38px;
  font: inherit;
  color: var(--fg);
  padding: 6px 10px;
  border: 1px solid var(--bd-strong);
  border-radius: 6px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.16);
}
.filterbar {
  flex: 0 0 auto;
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 7px 10px;
  font-size: 12.5px;
  color: var(--fg-soft);
  border-bottom: 1px solid var(--bd-soft);
  background: linear-gradient(to bottom, var(--chrome-top), var(--chrome-bot));
}
.filterbar select {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 34px;
  font: inherit;
  color: var(--fg);
  padding: 4px 6px;
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}

/* --- message page ------------------------------------------------------ */
.msgview { padding: 12px; }
.msgview h1 { font-size: 19px; line-height: 1.3; margin: 0 0 8px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.chip {
  font-size: 12.5px;
  padding: 2px 8px;
  border: 1px solid var(--bd-soft);
  border-radius: 10px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.chip b { color: var(--fg); }
.chip.age, .chip.due-chip.overdue {
  color: #fff;
  font-weight: 700;
  border-color: rgba(0, 0, 0, 0.35);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
  background-image: linear-gradient(to bottom,
      rgba(255, 255, 255, 0.30), rgba(0, 0, 0, 0.12));
}
.chip.age.green { background-color: var(--age-green); }
.chip.age.yellow { background-color: var(--age-yellow); }
.chip.age.red { background-color: var(--age-red); }
.chip.age.none { background-color: var(--bd-soft); }
.chip.due-chip.overdue { background-color: var(--age-red); }
.chip.due-chip.overdue b, .chip.age b { color: #fff; }
.section-head {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--fg-muted);
  margin: 18px 0 6px;
  padding-bottom: 3px;
  border-bottom: 1px solid var(--bd-soft);
}
.kv {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 3px 10px;
  margin: 0;
  padding: 9px 10px;
  border: 1px solid var(--bd-soft);
  border-radius: 5px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}
.kv dt {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
  padding-top: 2px;
}
.kv dd { margin: 0; overflow-wrap: anywhere; }
.note-line { color: var(--fg-muted); font-size: 13px; margin: 8px 0; }
.trail { display: flex; flex-wrap: wrap; gap: 5px; }
.trail .step {
  border: 1px solid var(--bd-soft);
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 12.5px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.trail .step b { display: block; font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--fg-muted); }

.msg {
  border: 1px solid var(--bd-soft);
  border-radius: 5px;
  margin: 10px 0;
  overflow: hidden;
  background: var(--bg-panel);
}
.msg > summary, .msg > .msg-head {
  padding: 8px 10px;
  font-size: 13px;
  color: var(--fg-soft);
  border-bottom: 1px solid var(--bd-soft);
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
}
.msg > summary { cursor: pointer; }
.msg .who { display: block; font-weight: 700; color: var(--fg); }
.msg .msg-meta {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 2px 8px;
  margin: 0;
  padding: 8px 10px 0;
  font-size: 12.5px;
}
.msg .msg-meta dt {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
  padding-top: 1px;
}
.msg .msg-meta dd { margin: 0; color: var(--fg-soft); overflow-wrap: anywhere; }
.msg .msg-attach { display: flex; flex-wrap: wrap; gap: 5px; align-items: center;
  padding: 7px 10px 0; }
.msg .attach-label { font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--fg-muted); }
.msg .attach {
  font-size: 12px;
  padding: 2px 7px;
  border: 1px solid var(--bd-soft);
  border-radius: 4px;
  color: var(--fg-soft);
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
}
.msg .msg-empty { margin: 0; padding: 10px; font-style: italic; }
.msg .msg-body {
  margin: 0;
  padding: 10px;
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.msg.d1 { margin-left: 8px; }
.msg.d2 { margin-left: 16px; }
.msg.d3 { margin-left: 22px; }
.msg.d4 { margin-left: 28px; }

/* --- buttons ----------------------------------------------------------- */
.btn {
  min-height: 42px;
  font: inherit;
  color: var(--fg);
  padding: 8px 14px;
  cursor: pointer;
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 1px 2px rgba(0, 0, 0, 0.1);
}
.btn:active { background: linear-gradient(to bottom, var(--btn-bot), var(--btn-top)); }
.btn.primary {
  font-weight: 700;
  color: var(--fg-on-sel);
  border-color: var(--sel-bd);
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}
.btn.full { width: 100%; }
.btnrow { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }

/* --- bottom tab bar ---------------------------------------------------- */
.tabbar {
  flex: 0 0 auto;
  display: flex;
  border-top: 1px solid var(--bd-strong);
  background: linear-gradient(to bottom, var(--chrome-top), var(--chrome-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 -1px 3px rgba(0, 0, 0, 0.12);
  padding-bottom: env(safe-area-inset-bottom, 0);
  z-index: 3;
}
.tab {
  flex: 1 1 0;
  min-height: 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font: inherit;
  font-size: 11px;
  color: var(--fg-muted);
  cursor: pointer;
  border: none;
  background: transparent;
}
.tab svg { width: 24px; height: 24px; fill: none; stroke: currentColor;
  stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.tab.active { color: var(--accent); font-weight: 700; }
.tab.active svg { stroke-width: 2.1; }
.tab .tabbadge {
  position: absolute;
  transform: translate(14px, -12px);
  min-width: 16px;
  padding: 0 4px;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  border-radius: 8px;
  background: var(--age-red);
}

/* --- bottom sheet (commands, menu) ------------------------------------ */
.sheet-overlay {
  position: fixed;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: flex-end;
  background: rgba(0, 0, 0, 0.45);
}
.sheet-overlay[hidden] { display: none; }
.sheet {
  width: 100%;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--bd-strong);
  border-radius: 12px 12px 0 0;
  background: var(--bg-window);
  box-shadow: 0 -6px 24px var(--shadow);
  padding-bottom: env(safe-area-inset-bottom, 0);
  animation: sheet-up 200ms ease;
}
@keyframes sheet-up { from { transform: translateY(100%); } to { transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .sheet { animation: none; } }
.sheet > .grabber {
  flex: 0 0 auto;
  width: 42px;
  height: 4px;
  margin: 8px auto 4px;
  border-radius: 2px;
  background: var(--bd-soft);
}
.sheet > .sheet-title {
  flex: 0 0 auto;
  padding: 4px 14px 8px;
  font-size: 16px;
  font-weight: 700;
  overflow-wrap: anywhere;
}
.sheet > .sheet-body { flex: 1 1 auto; overflow-y: auto; padding: 0 14px 12px; }
.sheet > .sheet-foot {
  flex: 0 0 auto;
  display: flex;
  gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid var(--bd-soft);
}
.sheet .field, .sheet select, .sheet textarea {
  width: 100%;
  min-height: 40px;
  font: inherit;
  color: var(--fg);
  padding: 8px 10px;
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.15);
}
.sheet select { background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light); }
.sheet textarea { min-height: 76px; resize: vertical; }
.sheet label.fieldlabel {
  display: block;
  margin: 10px 0 4px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
}
.snippet {
  font-family: var(--font-mono);
  font-size: 13px;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  margin: 10px 0 0;
  padding: 10px;
  color: var(--fg);
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.18);
  user-select: all;
}
.copied { color: var(--age-green); font-weight: 700; font-size: 13px; }

/* --- settings + dashboard blocks -------------------------------------- */
.group {
  margin: 12px 10px;
  border: 1px solid var(--bd-soft);
  border-radius: 6px;
  background: var(--bg-panel-alt);
  box-shadow: inset 0 1px 0 var(--bd-light);
  padding: 10px 12px;
}
.group > .legend {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--fg-muted);
  margin-bottom: 6px;
}
.segmented { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 4px; }
.segmented label {
  flex: 1 1 auto;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.segmented label.checked {
  color: var(--fg-on-sel);
  border-color: var(--sel-bd);
  background: linear-gradient(to bottom, var(--sel-top), var(--sel-bot));
}
.segmented input { position: absolute; opacity: 0; pointer-events: none; }
.checkrow {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  border-bottom: 1px solid var(--bd-soft);
}
.checkrow:last-child { border-bottom: none; }
.checkrow input { width: 20px; height: 20px; }
.fontfield { margin-bottom: 10px; }
.group select {
  width: 100%;
  min-height: 40px;
  font: inherit;
  color: var(--fg);
  margin-bottom: 6px;
  padding: 8px 10px;
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.fontfield input {
  width: 100%;
  min-height: 40px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--fg);
  padding: 8px 10px;
  border: 1px solid var(--bd-strong);
  border-radius: 5px;
  background: var(--bg-inset);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.15);
}
.cards { display: flex; flex-wrap: wrap; gap: 8px; padding: 10px; }
.card {
  flex: 1 1 44%;
  min-width: 128px;
  padding: 10px 12px;
  text-align: left;
  font: inherit;
  color: var(--fg);
  cursor: pointer;
  border: 1px solid var(--bd-strong);
  border-radius: 6px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light), 0 1px 2px rgba(0, 0, 0, 0.08);
}
.card .big { font-size: 24px; font-weight: 700; line-height: 1.1; }
.card .lbl { font-size: 12.5px; color: var(--fg-soft); }
.card.hot { border-color: var(--age-red); }
.card.hot .big { color: var(--age-red); }
.card.zero { opacity: 0.7; }

/* Performance tables reuse the desktop's markup, so restate its table rules. */
.perf { padding: 10px; }
.perf h2 { font-size: 16px; margin: 16px 0 4px; }
.perf .prose { color: var(--fg-soft); font-size: 13.5px; }
.perf .counts { display: flex; flex-wrap: wrap; gap: 12px; margin: 6px 0 12px; }
table.kpi { border-collapse: collapse; width: 100%; font-size: 12.5px; }
table.kpi th, table.kpi td { border: 1px solid var(--bd-soft); padding: 5px 7px; }
table.kpi thead th {
  background: linear-gradient(to bottom, var(--title-top), var(--title-bot));
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--fg-soft);
  text-align: right;
}
table.kpi thead th:first-child { text-align: left; }
table.kpi tbody th { text-align: left; background: var(--bg-panel-alt); white-space: nowrap; }
table.kpi tbody td { background: var(--bg-panel); text-align: right;
  font-variant-numeric: tabular-nums; }
.tablewrap { overflow-x: auto; }
.stat-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
.stat {
  flex: 1 1 44%;
  min-width: 130px;
  padding: 8px 10px;
  border: 1px solid var(--bd-strong);
  border-radius: 6px;
  background: linear-gradient(to bottom, var(--btn-top), var(--btn-bot));
  box-shadow: inset 0 1px 0 var(--bd-light);
}
.stat-val { font-size: 20px; font-weight: 700; font-variant-numeric: tabular-nums; }
.stat-lbl { font-size: 12px; color: var(--fg-soft); }
.kpi-lbl { color: var(--fg-muted); font-size: 11.5px; }
.kpi-card { text-align: right; }
.note {
  margin: 10px 0;
  padding: 8px 10px;
  font-size: 12.5px;
  border: 1px solid var(--bd-soft);
  border-left: 3px solid var(--age-yellow);
  border-radius: 4px;
  background: linear-gradient(to bottom, var(--warn-bg), var(--btn-bot));
}
.statusline {
  padding: 10px 12px 20px;
  font-size: 12px;
  color: var(--fg-muted);
}
.mono { font-family: var(--font-mono); }
"""


# Written to mobile/assets/mobile.js — the mobile build's behaviour.
#
# Navigation is a PAGE STACK, the smartphone idiom: four bottom tabs, each with
# its own stack of pages, and tapping a list row pushes a page that slides in from
# the right. The back button (and the hardware/browser back gesture, via
# history.pushState where the browser allows it on file://) pops it.
#
# It shares what matters with the desktop build: `window.GTD_MAIL` for data and
# `window.GTDSettings` for preferences and remembered state. What is local to this
# file is presentation: pages, sheets, and touch-sized lists.
#
# It deliberately does NOT offer the desktop's command-building actions. A shell
# snippet is useless on a phone — there is no terminal to paste it into — so the
# mobile build is purely for reading, and says so on each message rather than
# offering an action that goes nowhere.
MOBILE_JS = r"""(function () {
  "use strict";

  var DATA = window.GTD_MAIL || {};
  var EMAILS = DATA.emails || [];
  var SECTIONS = DATA.sections || [];
  var VIEWS = DATA.views || [];
  var HASHTAGS = DATA.hashtags || [];
  var ACCOUNTS = DATA.accounts || [];
  var OVERVIEW = DATA.overview || {};
  var PERF = window.GTD_PERF_BLOCKS || null;
  var CLI = DATA.cli || "gtd";

  var BY_FILE = {};
  EMAILS.forEach(function (email) { BY_FILE[email.file] = email; });

  var LABEL = { overview: "Dashboard", "due-set": "Due date set",
                "due-unset": "Due date not set", pinned: "Pinned" };
  SECTIONS.forEach(function (s) { LABEL[s.key] = s.label; });
  VIEWS.forEach(function (v) { LABEL[v.key] = v.label; });
  HASHTAGS.forEach(function (h) { LABEL[h.key] = h.label; });

  /* ---------------------------------------------------------------- helpers */
  function el(id) { return document.getElementById(id); }
  function esc(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }
  function settingOn(name, fallback) {
    var s = window.GTDSettings;
    if (!s) { return fallback; }
    var v = s.get(name);
    return (typeof v === "boolean") ? v : fallback;
  }
  function radarScope() {
    var s = window.GTDSettings;
    return (s && s.radarScope && s.radarScope()) || {};
  }
  function onRadar(email) { return radarScope()[email.folder] === true; }
  function isOverdue(email) {
    return /^\d{4}-\d{2}-\d{2}$/.test(email.dueDate || "") &&
      email.dueDate < window.GTDDates.today();
  }

  /* Membership predicates for the marker views, matching the desktop build. */
  var MARKERS = {
    "due-set": function (e) { return onRadar(e) && !!e.dueDate; },
    "due-unset": function (e) { return onRadar(e) && !e.dueDate; },
    "pinned": function (e) { return onRadar(e) && (e.flags || []).indexOf("pinned") >= 0; }
  };
  HASHTAGS.forEach(function (entry) {
    var needle = String(entry.tag || "").toLowerCase();
    MARKERS[entry.key] = function (email) {
      return onRadar(email) && !!needle &&
        String(email.nextAction || "").toLowerCase().indexOf(needle) >= 0;
    };
  });

  function emailsFor(sectionKey) {
    if (MARKERS[sectionKey]) { return EMAILS.filter(MARKERS[sectionKey]); }
    if (sectionKey === "inbox" || sectionKey === "sent") {
      return EMAILS.filter(function (e) { return (e[sectionKey] || []).length > 0; });
    }
    return EMAILS.filter(function (e) { return e.folder === sectionKey; });
  }

  /* Order by the instant the Date header names, so same-day mail sorts by time. */
  function byInstant(a, b, direction) {
    var ea = (a.epoch === null || a.epoch === undefined) ? null : a.epoch;
    var eb = (b.epoch === null || b.epoch === undefined) ? null : b.epoch;
    if (ea === null && eb === null) { return cmp(a.subject, b.subject); }
    if (ea === null) { return 1; }
    if (eb === null) { return -1; }
    return direction * (ea - eb) || cmp(a.subject, b.subject);
  }

  var SORTERS = {
    "date-desc": function (a, b) { return byInstant(a, b, -1); },
    "date-asc": function (a, b) { return byInstant(a, b, 1); },
    "due-asc": function (a, b) { return dueCmp(a, b, 1); },
    "due-desc": function (a, b) { return dueCmp(a, b, -1); },
    "subject": function (a, b) { return cmp(low(a.subject), low(b.subject)); }
  };
  function cmp(a, b) { return a < b ? -1 : (a > b ? 1 : 0); }
  function low(v) { return String(v || "").toLowerCase(); }
  function dueTier(e) {
    if (!e.dueDate) { return 2; }
    return /^\d{4}-\d{2}-\d{2}$/.test(e.dueDate) ? 0 : 1;
  }
  function dueCmp(a, b, direction) {
    var ta = dueTier(a), tb = dueTier(b);
    if (ta !== tb) { return ta - tb; }
    if (ta === 2) { return byInstant(a, b, -1); }
    return direction * cmp(a.dueDate, b.dueDate) || byInstant(a, b, -1);
  }

  function matches(email, needle) {
    if (email._hay === undefined) {
      var parts = [email.subject, email.file, email.from, email.to, email.project,
                   email.nextAction, email.notes, email.account,
                   (email.correspondents || []).join(" ")];
      (email.thread || []).forEach(function (m) { parts.push(m.text, m.from); });
      email._hay = parts.join(" \n ").toLowerCase();
    }
    return email._hay.indexOf(needle) >= 0;
  }

  /* ------------------------------------------------------------ page stack */
  /* Each tab keeps its own stack, so switching tabs and coming back returns you
     to where you were — what a phone app does. A page is {title, subtitle,
     render(host)} plus whatever state it needs. */
  var TABS = ["dashboard", "mail", "radar", "settings"];
  var stacks = { dashboard: [], mail: [], radar: [], settings: [] };
  var activeTab = "mail";
  var animating = false;

  function stack() { return stacks[activeTab]; }
  function top() { return stack()[stack().length - 1]; }

  function pageElement(page) {
    var host = document.createElement("div");
    host.className = "page";
    page.render(host);
    return host;
  }

  function renderTop(direction) {
    var container = el("stack");
    var page = top();
    if (!page) { return; }
    var incoming = pageElement(page);
    var existing = container.querySelector(".page:not(.leaving)");

    el("appbar-title").innerHTML = esc(page.title) +
      (page.subtitle ? '<span class="subtitle">' + esc(page.subtitle) + "</span>" : "");
    el("back").hidden = stack().length <= 1;

    if (!existing || direction === "none") {
      container.innerHTML = "";
      container.appendChild(incoming);
      return;
    }
    animating = true;
    if (direction === "push") {
      incoming.classList.add("entering");
      container.appendChild(incoming);
      /* Force a reflow so the transition runs from the off-screen position. */
      void incoming.offsetWidth;
      incoming.classList.remove("entering");
      existing.classList.add("beneath");
    } else {
      container.insertBefore(incoming, existing);
      existing.classList.add("leaving");
    }
    window.setTimeout(function () {
      Array.prototype.slice.call(container.querySelectorAll(".page"))
        .forEach(function (node) { if (node !== incoming) { container.removeChild(node); } });
      incoming.classList.remove("beneath");
      animating = false;
    }, 240);
  }

  function push(page, silent) {
    if (animating) { return; }
    stack().push(page);
    renderTop("push");
    remember();
    if (!silent) {
      try { window.history.pushState({ depth: stack().length }, ""); }
      catch (e) { /* file:// may refuse the History API; the back button still works */ }
    }
  }

  function pop() {
    if (stack().length <= 1 || animating) { return false; }
    stack().pop();
    renderTop("pop");
    remember();
    return true;
  }

  function setTab(name, silent) {
    activeTab = name;
    TABS.forEach(function (tab) {
      var button = el("tab-" + tab);
      if (button) { button.classList.toggle("active", tab === name); }
    });
    if (!stack().length) { stack().push(rootPage(name)); }
    renderTop("none");
    if (!silent) { remember(); }
  }

  /* ------------------------------------------------------------ list pages */
  function rowFor(email, onTap) {
    var when = (email.epoch === null || email.epoch === undefined)
      ? "(no date)" : window.GTDDates.compactFromEpoch(email.epoch);
    var dim = settingOn("dimOffRadar", false) && !onRadar(email);
    var account = email.account
      ? '<span class="acct acct-' + esc(email.accountColour || "cyan") + '">' +
        esc(email.account) + "</span>" : "";
    var due = email.dueDate
      ? '<span class="due' + (isOverdue(email) ? " overdue" : "") + '">' +
        esc(window.GTDDates.fromIsoDay(email.dueDate)) + "</span>" : "";
    var pin = (email.flags || []).indexOf("pinned") >= 0
      ? '<span class="pin">\u2605</span>' : "";
    var third = email.nextAction ? "next: " + email.nextAction
      : (email.tracked ? (email.preview || "") : "not yet ingested");
    var button = document.createElement("button");
    button.className = "item" + (dim ? " off-radar" : "");
    button.type = "button";
    button.setAttribute("data-file", email.file);
    button.innerHTML =
      '<span class="dot ' + (dim ? "none" : (email.ageClass || "none")) + '"></span>' +
      '<span class="body">' +
        '<span class="line1">' + pin +
          '<span class="primary">' + esc(email.subject) + "</span>" + due +
          '<span class="meta">' + esc(when) + "</span>" +
        "</span>" +
        '<span class="line2">' + account +
          esc((email.correspondents || []).join(", ") || email.from) + "</span>" +
        '<span class="line3">' + esc(third) + "</span>" +
      "</span>" +
      '<span class="chev">\u203a</span>';
    button.addEventListener("click", function () { onTap(email); });
    return button;
  }

  /* A message list, with search, sort, and (for Inbox/Sent) an account filter. */
  function listPage(sectionKey) {
    var page = {
      title: LABEL[sectionKey] || "Messages",
      kind: "list",
      section: sectionKey,
      query: "",
      account: "",
      sort: (sectionKey === "due-set" || sectionKey === "due-unset")
        ? "due-asc" : "date-desc",
      render: function (host) {
        var self = this;
        var search = document.createElement("div");
        search.className = "searchbar";
        search.innerHTML = '<input type="search" placeholder="Search these messages"' +
          ' value="' + esc(self.query) + '" aria-label="Search these messages">';
        host.appendChild(search);

        var bar = document.createElement("div");
        bar.className = "filterbar";
        var sortOptions = [["date-desc", "Newest first"], ["date-asc", "Oldest first"],
                           ["due-asc", "Due date (soonest)"],
                           ["due-desc", "Due date (latest)"], ["subject", "Subject"]];
        bar.innerHTML = "<span>Sort</span><select data-role=\"sort\">" +
          sortOptions.map(function (o) {
            return '<option value="' + o[0] + '"' +
              (self.sort === o[0] ? " selected" : "") + ">" + esc(o[1]) + "</option>";
          }).join("") + "</select>" +
          ((sectionKey === "inbox" || sectionKey === "sent") && ACCOUNTS.length
            ? "<select data-role=\"account\"><option value=\"\">All accounts</option>" +
              ACCOUNTS.map(function (name) {
                return '<option value="' + esc(name) + '"' +
                  (self.account === name ? " selected" : "") + ">" + esc(name) + "</option>";
              }).join("") + "</select>"
            : "");
        host.appendChild(bar);

        var scroll = document.createElement("div");
        scroll.className = "scroll";
        host.appendChild(scroll);

        function draw() {
          var list = emailsFor(self.section);
          if (self.account) {
            list = list.filter(function (e) {
              return (e[self.section] || []).indexOf(self.account) >= 0;
            });
          }
          if (self.query) {
            var needle = self.query.toLowerCase();
            list = list.filter(function (e) { return matches(e, needle); });
          }
          list = list.slice().sort(SORTERS[self.sort] || SORTERS["date-desc"]);
          scroll.innerHTML = "";
          if (!list.length) {
            scroll.innerHTML = '<p class="empty">No messages here.</p>';
            return;
          }
          var head = document.createElement("div");
          head.className = "list-head";
          head.innerHTML = '<span class="grow">' + esc(LABEL[self.section] || "") +
            '</span><span class="count">' + plural(list.length, "message") + "</span>";
          scroll.appendChild(head);
          var holder = document.createElement("div");
          holder.className = "list";
          list.forEach(function (email) {
            holder.appendChild(rowFor(email, function (chosen) {
              push(messagePage(chosen));
            }));
          });
          scroll.appendChild(holder);
        }

        search.querySelector("input").addEventListener("input", function (event) {
          self.query = event.target.value.trim();
          draw();
        });
        bar.addEventListener("change", function (event) {
          var role = event.target.getAttribute("data-role");
          if (role === "sort") { self.sort = event.target.value; }
          if (role === "account") { self.account = event.target.value; }
          draw();
          remember();
        });
        draw();
      }
    };
    return page;
  }

  /* ---------------------------------------------------------- message page */
  function messageMetaHtml(message, email, isNewest) {
    function row(label, value) {
      return value ? "<dt>" + esc(label) + "</dt><dd>" + esc(value) + "</dd>" : "";
    }
    var rows = isNewest
      ? [row("From", message.from || email.from), row("To", email.to),
         row("Cc", email.cc), row("Date", window.GTDDates.fromEpoch(email.epoch)),
         row("Attached", (email.attachments || []).join(", "))].join("")
      : [row("From", message.from), row("To", message.to),
         row("Date", window.GTDDates.fromParts(message.dateParts, message.date)),
         row("Subject", message.subject)].join("");
    return rows ? '<dl class="msg-meta">' + rows + "</dl>" : "";
  }

  function attachHtml(email) {
    var names = email.attachments || [];
    if (!names.length) { return ""; }
    return '<div class="msg-attach"><span class="attach-label">Attached</span>' +
      names.map(function (n) { return '<span class="attach">\u2398 ' + esc(n) + "</span>"; })
        .join("") + "</div>";
  }

  function messagePage(email) {
    return {
      title: email.subject || "(no subject)",
      subtitle: email.folderLabel,
      kind: "message",
      file: email.file,
      render: function (host) {
        var scroll = document.createElement("div");
        scroll.className = "scroll";
        var chips = [];
        if (email.ageDays !== null && email.ageDays !== undefined) {
          chips.push('<span class="chip age ' + (email.ageClass || "none") + '">' +
            esc(email.ageDays + (email.ageDays === 1 ? " day old" : " days old")) + "</span>");
        }
        if (email.dueDate) {
          chips.push('<span class="chip due-chip' + (isOverdue(email) ? " overdue" : "") +
            '">due <b>' + esc(window.GTDDates.fromIsoDay(email.dueDate)) +
            "</b></span>");
        }
        chips.push('<span class="chip">' + esc(email.status || "untracked") + "</span>");
        if (email.account) { chips.push('<span class="chip">to <b>' + esc(email.account) + "</b></span>"); }
        (email.flags || []).forEach(function (f) {
          chips.push('<span class="chip">' + esc(f) + "</span>");
        });

        function kv(label, value) {
          return value ? "<dt>" + esc(label) + "</dt><dd>" + esc(value) + "</dd>" : "";
        }
        var annotations = kv("Project", email.project) + kv("Next action", email.nextAction) +
          kv("Due date", window.GTDDates.fromIsoDay(email.dueDate)) +
          kv("Notes", email.notes);
        var trail = (email.stamps || []).map(function (entry) {
          return '<span class="step"><b>' + esc(entry.label) + "</b>" +
            esc(window.GTDDates.fromIsoDay(entry.date)) + "</span>";
        }).join("");

        var messages = (email.thread || []);
        if (!messages.length) {
          /* See the desktop build: keep a block so headers and attachments show. */
          messages = [{ depth: 0, indent: 0, text: "", empty: true }];
        }
        var thread = messages.map(function (message, index) {
          var isNewest = index === 0;
          var who = message.from || (isNewest ? email.from : "") || "Quoted message";
          var when = isNewest
            ? window.GTDDates.fromEpoch(email.epoch)
            : window.GTDDates.fromParts(message.dateParts, message.date);
          var head = '<span class="who">' + esc(who) + "</span>" + esc(when);
          var inner = messageMetaHtml(message, email, isNewest) +
            (isNewest ? attachHtml(email) : "") +
            (message.empty
              ? '<p class="note-line msg-empty">No text body (this email may be '
                + "attachment-only).</p>"
              : '<pre class="msg-body">' + esc(message.text) + "</pre>");
          var cls = "msg d" + (message.indent || 0);
          return isNewest
            ? '<div class="' + cls + '"><div class="msg-head">' + head + "</div>" + inner + "</div>"
            : '<details class="' + cls + '"><summary>' + head + "</summary>" + inner + "</details>";
        }).join("");

        scroll.innerHTML =
          '<div class="msgview">' +
          "<h1>" + esc(email.subject) + "</h1>" +
          '<div class="chips">' + chips.join("") + "</div>" +
          '<div class="section-head">Annotations</div>' +
          (annotations ? '<dl class="kv">' + annotations + "</dl>"
                       : '<p class="note-line">Nothing recorded yet.</p>') +
          '<p class="note-line">Read-only report \u2014 nothing here changes your ' +
            "workflow. Use the desktop build (or your terminal) to act on this.</p>" +
          '<div class="section-head">Workflow</div>' +
          (trail ? '<div class="trail">' + trail + "</div>"
                 : '<p class="note-line">No date-stamps recorded.</p>') +
          '<div class="section-head">Message history <span class="count">' +
            plural(messages.length, "message") + "</span></div>" +
          thread +
          "</div>";
        host.appendChild(scroll);
      }
    };
  }

  /* ------------------------------------------------------------- dashboard */
  function dashboardPage() {
    return {
      title: "Dashboard",
      subtitle: DATA.workingDirectory,
      kind: "dashboard",
      render: function (host) {
        var scroll = document.createElement("div");
        scroll.className = "scroll";
        var counts = OVERVIEW.counts || {};
        var cards = SECTIONS.map(function (section) {
          return '<button class="card" type="button" data-section="' + esc(section.key) +
            '"><span class="big">' + (counts[section.key] || 0) + '</span>' +
            '<span class="lbl">' + esc(section.label) + "</span></button>";
        }).join("");
        var attention = (OVERVIEW.attention || []).map(function (item) {
          var cls = "card" + (item.count
            ? (["input", "stale", "weird"].indexOf(item.key) >= 0 ? " hot" : "")
            : " zero");
          return '<button class="' + cls + '" type="button" data-attn="' + esc(item.key) +
            '"><span class="big">' + item.count + '</span><span class="lbl">' +
            esc(item.label) + "</span></button>";
        }).join("");

        scroll.innerHTML =
          '<div class="list-head">Where everything is</div>' +
          '<div class="cards">' + cards + "</div>" +
          '<div class="list-head">Needs attention</div>' +
          '<div class="cards">' + attention + "</div>" +
          '<div class="list-head">Reports</div>' +
          '<div class="list"><button class="item" type="button" data-role="perf">' +
            '<span class="body"><span class="line1"><span class="primary">Performance' +
            '</span></span><span class="line2">Response-time metrics and KPIs</span>' +
            '</span><span class="chev">\u203a</span></button></div>' +
          '<p class="statusline">Generated ' +
            esc(window.GTDDates.fromEpoch(DATA.generatedEpoch) || DATA.generatedAt) +
            ' \u00b7 read-only report \u00b7 <span class="mono">' +
            esc(DATA.workingDirectory) + "</span></p>";

        scroll.addEventListener("click", function (event) {
          var target = event.target.closest("[data-section],[data-attn],[data-role]");
          if (!target) { return; }
          if (target.hasAttribute("data-section")) {
            push(listPage(target.getAttribute("data-section")));
          } else if (target.hasAttribute("data-attn")) {
            var key = target.getAttribute("data-attn");
            var item = (OVERVIEW.attention || []).filter(function (a) {
              return a.key === key;
            })[0];
            if (item) { push(subsetPage(item.label, item.files)); }
          } else if (target.getAttribute("data-role") === "perf") {
            push(performancePage());
          }
        });
        host.appendChild(scroll);
      }
    };
  }

  /* A fixed list of files (an attention figure drilled into). */
  function subsetPage(label, files) {
    return {
      title: label.charAt(0).toUpperCase() + label.slice(1),
      kind: "subset",
      render: function (host) {
        var scroll = document.createElement("div");
        scroll.className = "scroll";
        var list = files.map(function (f) { return BY_FILE[f]; })
                        .filter(function (e) { return !!e; });
        if (!list.length) {
          scroll.innerHTML = '<p class="empty">Nothing here \u2014 good.</p>';
        } else {
          var holder = document.createElement("div");
          holder.className = "list";
          list.forEach(function (email) {
            holder.appendChild(rowFor(email, function (chosen) { push(messagePage(chosen)); }));
          });
          scroll.appendChild(holder);
        }
        host.appendChild(scroll);
      }
    };
  }

  function performancePage() {
    return {
      title: "Performance",
      kind: "performance",
      render: function (host) {
        var scroll = document.createElement("div");
        scroll.className = "scroll";
        if (!PERF) {
          scroll.innerHTML = '<p class="empty">No performance data was generated.</p>';
        } else {
          /* The mobile build deliberately ships the metric TABLES but not the
             charts: Plotly is several megabytes and unreadable at this width. The
             desktop build has the charts. */
          scroll.innerHTML = '<div class="perf">' +
            '<div class="counts">' + PERF.counts + "</div>" +
            "<h2>Open backlog</h2>" + PERF.backlog +
            "<h2>Headline KPIs</h2>" +
            '<div class="tablewrap">' + PERF.kpi + "</div>" +
            "<h2>Percentiles</h2>" +
            '<div class="tablewrap">' + PERF.percentile + "</div>" +
            "<h2>Resolution hit rate</h2>" + PERF.hit_rate +
            '<p class="note-line">Charts are in the desktop build \u2014 they need more ' +
            "width than a phone has.</p></div>";
        }
        host.appendChild(scroll);
      }
    };
  }

  /* ------------------------------------------------------------- tab roots */
  function menuListPage(title, groups) {
    return {
      title: title,
      kind: "menu",
      render: function (host) {
        var scroll = document.createElement("div");
        scroll.className = "scroll";
        groups.forEach(function (group) {
          if (!group.items.length) { return; }
          var head = document.createElement("div");
          head.className = "list-head";
          head.textContent = group.label;
          scroll.appendChild(head);
          var holder = document.createElement("div");
          holder.className = "list";
          group.items.forEach(function (item) {
            var button = document.createElement("button");
            button.className = "item";
            button.type = "button";
            button.innerHTML = '<span class="body"><span class="line1">' +
              '<span class="primary">' + esc(item.label) + "</span></span>" +
              (item.hint ? '<span class="line2">' + esc(item.hint) + "</span>" : "") +
              '</span><span class="badge">' + item.count + "</span>" +
              '<span class="chev">\u203a</span>';
            button.addEventListener("click", function () { push(listPage(item.key)); });
            holder.appendChild(button);
          });
          scroll.appendChild(holder);
        });
        host.appendChild(scroll);
      }
    };
  }

  function mailRoot() {
    var groups = [];
    if (VIEWS.length) {
      groups.push({ label: "In & out", items: VIEWS.map(function (v) {
        return { key: v.key, label: v.label, count: v.count }; }) });
    }
    groups.push({ label: "GTD status", items: SECTIONS.map(function (s) {
      return { key: s.key, label: s.label, count: s.count }; }) });
    return menuListPage("Mail", groups);
  }

  function radarRoot() {
    var markers = [
      { key: "due-set", label: "Due date set" },
      { key: "due-unset", label: "Due date not set" },
      { key: "pinned", label: "Pinned" }
    ].map(function (item) {
      return { key: item.key, label: item.label, count: emailsFor(item.key).length };
    });
    var groups = [{ label: "Due & flagged", items: markers }];
    if (HASHTAGS.length) {
      groups.push({ label: "Hashtags", items: HASHTAGS.map(function (h) {
        return { key: h.key, label: h.label, count: emailsFor(h.key).length }; }) });
    }
    return menuListPage("On radar", groups);
  }

  function rootPage(tab) {
    if (tab === "dashboard") { return dashboardPage(); }
    if (tab === "radar") { return radarRoot(); }
    if (tab === "settings") { return settingsPage(); }
    return mailRoot();
  }

  /* -------------------------------------------------------------- settings */
  function settingsPage() {
    return {
      title: "Settings",
      kind: "settings",
      render: function (host) {
        var scroll = document.createElement("div");
        scroll.className = "scroll";
        scroll.setAttribute("data-settings-form", "");
        var settings = window.GTDSettings;
        var all = settings ? settings.all() : {};

        function segmented(name, options) {
          return '<div class="segmented">' + options.map(function (o) {
            return "<label" + (all[name] === o[0] ? ' class="checked"' : "") + ">" +
              '<input type="radio" name="' + name + '" value="' + o[0] + '"' +
              (all[name] === o[0] ? " checked" : "") + ">" + esc(o[1]) + "</label>";
          }).join("") + "</div>";
        }
        function checkrow(setting, label, on) {
          return '<label class="checkrow"><input type="checkbox" data-setting="' +
            esc(setting) + '"' + (on ? " checked" : "") + "><span>" + esc(label) +
            "</span></label>";
        }
        function fontfield(setting, label) {
          return '<div class="fontfield"><label class="legend" for="m-' + setting + '">' +
            esc(label) + '</label><input type="text" id="m-' + setting +
            '" data-setting="' + setting + '" spellcheck="false" ' +
            'autocapitalize="off" autocomplete="off" value="' +
            esc(all[setting] || "") + '"></div>';
        }

        var scopeRows = SECTIONS.map(function (section) {
          return checkrow("radarScope." + section.key, section.label,
                          (all.radarScope || {})[section.key]);
        }).join("");

        var zones = (window.GTDDates && window.GTDDates.zoneOptions()) || [];
        var detected = "";
        try { detected = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; }
        catch (e) { detected = ""; }
        var zoneSelect = '<select data-setting="timeZone">' +
          '<option value=""' + (all.timeZone ? "" : " selected") +
          '>System default' + (detected ? " (" + esc(detected) + ")" : "") + "</option>" +
          zones.map(function (name) {
            return '<option value="' + esc(name) + '"' +
              (all.timeZone === name ? " selected" : "") + ">" + esc(name) + "</option>";
          }).join("") + "</select>";

        scroll.innerHTML =
          '<div class="group"><div class="legend">Appearance</div>' +
            segmented("mode", [["auto", "Automatic"], ["light", "Light"], ["dark", "Dark"]]) +
            segmented("tone", [["warm", "Warm"], ["neutral", "Neutral"]]) +
          "</div>" +
          '<div class="group"><div class="legend">Time &amp; dates</div>' +
            '<label class="legend" for="m-timeZone">Show times in</label>' +
            zoneSelect +
            '<p class="note-line">Each .eml names an exact moment; this is the zone ' +
            "it is shown in.</p>" +
            '<label class="legend">Date format</label>' +
            segmented("dateFormat", [["long", "Tuesday, 3 August 2026"],
                                     ["medium", "3 Aug 2026"],
                                     ["iso", "2026-08-03"]]) +
            '<label class="legend">Quoted headers with no timezone</label>' +
            segmented("naiveDates", [["local", "As written"], ["utc", "Treat as UTC"]]) +
          "</div>" +
          '<div class="group"><div class="legend">Message list</div>' +
            checkrow("groupByDate", "Group messages under date headings",
                     all.groupByDate !== false) +
          "</div>" +
          '<div class="group"><div class="legend">Fonts</div>' +
            fontfield("fontBody", "Message text") +
            fontfield("fontMono", "Monospace text") +
            fontfield("fontUi", "Interface") +
          "</div>" +
          '<div class="group"><div class="legend">On radar</div>' +
            '<p class="note-line">Which folders the due-date, pinned and hashtag ' +
            "views look at.</p>" + scopeRows +
            checkrow("dimOffRadar", "Grey out mail that is off your radar",
                     all.dimOffRadar) +
          "</div>" +
          '<div class="group"><div class="legend">Stored data</div>' +
            '<p class="note-line" id="storage-note"></p>' +
            '<button class="btn full" type="button" data-role="reset">' +
            "Reset saved settings</button></div>" +
          '<div class="group"><div class="legend">Other</div>' +
            '<p class="note-line">The desktop build has the charts and a wider ' +
            'layout.</p><a class="btn full" style="display:block;text-align:center;' +
            'text-decoration:none" href="../desktop/index.html">Open desktop version</a>' +
          "</div>" +
          '<p class="statusline">Generated ' +
            esc(window.GTDDates.fromEpoch(DATA.generatedEpoch) || DATA.generatedAt) +
            " \u00b7 " + esc(CLI) + " generate_dashboard</p>";

        scroll.addEventListener("change", function (event) {
          var target = event.target;
          if (!settings) { return; }
          if (target.type === "radio") { settings.set(target.name, target.value); }
          else if (target.type === "checkbox" && target.getAttribute("data-setting")) {
            settings.set(target.getAttribute("data-setting"), target.checked);
          } else if (target.tagName === "SELECT" && target.getAttribute("data-setting")) {
            settings.set(target.getAttribute("data-setting"), target.value);
          }
          markSegments(scroll);
        });
        scroll.addEventListener("input", function (event) {
          var target = event.target;
          if (settings && target.type === "text" && target.getAttribute("data-setting")) {
            settings.set(target.getAttribute("data-setting"), target.value);
          }
        });
        scroll.querySelector('[data-role="reset"]').addEventListener("click", function () {
          if (window.confirm("Clear this site's saved settings and restore the defaults?")) {
            settings.reset();
            renderTop("none");
          }
        });
        host.appendChild(scroll);
        var note = scroll.querySelector("#storage-note");
        if (note) {
          var ok = true;
          try { window.localStorage.setItem("gtd-eml.probe", "1");
                window.localStorage.removeItem("gtd-eml.probe"); }
          catch (e) { ok = false; }
          note.textContent = ok
            ? "Settings are saved in this browser for this site."
            : "This browser blocks local storage for local files, so settings apply "
              + "to this session only.";
        }
      }
    };
  }

  function markSegments(root) {
    Array.prototype.slice.call(root.querySelectorAll(".segmented label"))
      .forEach(function (label) {
        var input = label.querySelector("input");
        label.classList.toggle("checked", !!(input && input.checked));
      });
  }

  /* ---------------------------------------------------------------- sheets */
  function openSheet(title, bodyHtml, footHtml) {
    el("sheet-title").textContent = title;
    el("sheet-body").innerHTML = bodyHtml;
    el("sheet-foot").innerHTML = footHtml || "";
    el("sheet-overlay").hidden = false;
    return el("sheet-body");
  }
  function closeSheet() { el("sheet-overlay").hidden = true; }

  /* The top-bar menu: app-level items rather than per-message ones. */
  function openMenu() {
    var items = [
      { role: "settings", label: "Settings", hint: "Appearance, fonts, on-radar folders" },
      { role: "desktop", label: "Open desktop version", hint: "Charts and a wider layout" },
      { role: "top", label: "Back to the top of this tab", hint: "Close any open pages" }
    ];
    var body = openSheet("Menu", '<div class="list">' + items.map(function (item) {
      return '<button class="item" type="button" data-role="' + item.role + '">' +
        '<span class="body"><span class="line1"><span class="primary">' +
        esc(item.label) + '</span></span><span class="line2">' + esc(item.hint) +
        "</span></span></button>";
    }).join("") + "</div>",
      '<button class="btn full" type="button" data-role="close">Cancel</button>');
    body.addEventListener("click", function (event) {
      var button = event.target.closest("[data-role]");
      if (!button) { return; }
      var role = button.getAttribute("data-role");
      closeSheet();
      if (role === "settings") { setTab("settings"); }
      else if (role === "desktop") { window.location.href = "../desktop/index.html"; }
      else if (role === "top") {
        stacks[activeTab] = [rootPage(activeTab)];
        renderTop("pop");
        remember();
      }
    });
    el("sheet-foot").querySelector('[data-role="close"]')
      .addEventListener("click", closeSheet);
  }

  /* --------------------------------------------------- remembered UI state */
  /* Stored through the same GTDSettings blob the desktop uses, so the two builds
     do not fight over storage. Only the tab, the current section and the open
     message are remembered — enough to land back where you were. */
  function remember() {
    var settings = window.GTDSettings;
    if (!settings || !settings.setUi) { return; }
    var page = top() || {};
    var section = "";
    var file = "";
    stack().forEach(function (entry) {
      if (entry.kind === "list") { section = entry.section; }
      if (entry.kind === "message") { file = entry.file; }
    });
    settings.setUi({ section: section, file: file,
                     account: (page.account || ""), sort: (page.sort || ""),
                     tab: activeTab });
  }

  function restore() {
    var settings = window.GTDSettings;
    var saved = (settings && settings.ui) ? settings.ui() : {};
    var tab = (TABS.indexOf(saved.tab) >= 0) ? saved.tab : "mail";

    /* All-or-nothing, exactly as on the desktop: if the remembered section or
       message no longer resolves, drop the lot and start at the tab root. */
    if (saved.section || saved.file) {
      var sectionOk = !saved.section && !saved.file;
      var pages = [rootPage(tab)];
      if (saved.section && LABEL[saved.section] !== undefined) {
        var list = listPage(saved.section);
        if (saved.sort && SORTERS[saved.sort]) { list.sort = saved.sort; }
        if (saved.account && ACCOUNTS.indexOf(saved.account) >= 0) {
          list.account = saved.account;
        }
        pages.push(list);
        sectionOk = true;
      }
      if (saved.file) {
        var email = BY_FILE[saved.file];
        var inSection = email && (!saved.section ||
          emailsFor(saved.section).some(function (e) { return e.file === saved.file; }));
        if (!email || !inSection || !sectionOk) {
          settings.clearUi();
          activeTab = tab;
          stacks[tab] = [rootPage(tab)];
          setTab(tab, true);
          return;
        }
        pages.push(messagePage(email));
      }
      if (!sectionOk) { settings.clearUi(); }
      else { stacks[tab] = pages; }
    }
    activeTab = tab;
    setTab(tab, true);
  }

  /* ------------------------------------------------------------------ wire */
  document.addEventListener("DOMContentLoaded", function () {
    TABS.forEach(function (tab) {
      var button = el("tab-" + tab);
      if (button) { button.addEventListener("click", function () { setTab(tab); }); }
    });
    el("back").addEventListener("click", function () { pop(); });
    el("menu").addEventListener("click", openMenu);
    el("sheet-overlay").addEventListener("click", function (event) {
      if (event.target === el("sheet-overlay")) { closeSheet(); }
    });
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") { return; }
      if (!el("sheet-overlay").hidden) { closeSheet(); } else { pop(); }
    });
    window.addEventListener("popstate", function () {
      if (!el("sheet-overlay").hidden) { closeSheet(); return; }
      pop();
    });
    /* A settings change can alter what a list contains (grouping, radar scope), so
       redraw the visible page. */
    window.addEventListener("gtd:settings", function () {
      if (top() && top().kind !== "settings") { renderTop("none"); }
    });
    restore();
  });
})();
"""


# Written to assets/dates.js (desktop) and inlined into the mobile file: the single
# place that turns a timestamp into text.
#
# Three reader settings feed it, all held by settings.js:
#   * timeZone   — an IANA name, or "" for whatever the browser reports.
#   * dateFormat — "long" (Tuesday, 3 August 2026 12:34), "medium" (3 Aug 2026
#                  12:34) or "iso" (2026-08-03 12:34).
#   * naiveDates — how to read a quoted header that names no timezone: "local"
#                  (show the wall-clock numbers as written) or "utc" (treat them as
#                  UTC and convert).
#
# Two kinds of value arrive here and they must not be confused:
#   * An .eml Date header is an ABSOLUTE INSTANT (it carries an offset), passed as
#     `epoch` seconds. Converting it to the reader's timezone is meaningful.
#   * A quoted in-text header ("Sent: Tuesday, 3 August 2026 12:34") is usually
#     just wall-clock NUMBERS with no zone, passed as the `dateParts` that
#     thread.parse_date_text recovered. Converting those is only meaningful once
#     the reader says what zone they were written in — hence `naiveDates`. When the
#     quoted header did state an offset, that offset wins and the setting is
#     ignored.
#   * A ds_* stamp or a due_date is a plain calendar DAY from metadata.csv with no
#     time and no zone. It is only ever reformatted, never shifted.
DATES_JS = r"""(function () {
  "use strict";

  /* Month and weekday names are built once from Intl in en-GB, which fixes the
     day-before-month order the rest of this project uses. Formatting is assembled
     by hand from the parts rather than handed to toLocaleString, so the output does
     not change shape with the browser's locale. */
  var MONTHS = [];
  var MONTHS_SHORT = [];
  var WEEKDAYS = [];
  (function () {
    for (var m = 0; m < 12; m++) {
      var day = new Date(Date.UTC(2021, m, 1));
      MONTHS.push(fmt({ month: "long", timeZone: "UTC" }).format(day));
      MONTHS_SHORT.push(fmt({ month: "short", timeZone: "UTC" }).format(day));
    }
    /* 2021-11-01 was a Monday. */
    for (var d = 0; d < 7; d++) {
      WEEKDAYS.push(fmt({ weekday: "long", timeZone: "UTC" })
        .format(new Date(Date.UTC(2021, 10, 1 + d))));
    }
  })();

  function fmt(options) {
    try { return new Intl.DateTimeFormat("en-GB", options); }
    catch (e) { return new Intl.DateTimeFormat("en-GB"); }
  }

  function setting(name, fallback) {
    var s = window.GTDSettings;
    if (!s) { return fallback; }
    var value = s.get(name);
    return (typeof value === "string" && value !== "") ? value : fallback;
  }

  function zone() {
    var chosen = setting("timeZone", "");
    return chosen || undefined;   /* undefined = the browser's own zone */
  }

  /* Break an instant into calendar fields in the chosen zone. Intl is the only
     thing that knows about DST, so the fields come from formatToParts rather than
     from Date's own getters (which are stuck on the browser's zone). */
  function fieldsInZone(date, tz) {
    var parts;
    try {
      parts = new Intl.DateTimeFormat("en-GB", {
        timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
        weekday: "short"
      }).formatToParts(date);
    } catch (e) {
      /* An unknown timezone name: fall back to the browser's own. */
      parts = new Intl.DateTimeFormat("en-GB", {
        year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit",
        minute: "2-digit", second: "2-digit", hour12: false, weekday: "short"
      }).formatToParts(date);
    }
    var out = {};
    parts.forEach(function (part) { out[part.type] = part.value; });
    var hour = parseInt(out.hour, 10);
    return { y: parseInt(out.year, 10), mo: parseInt(out.month, 10),
             d: parseInt(out.day, 10), h: (hour === 24 ? 0 : hour),
             mi: parseInt(out.minute, 10) };
  }

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  function weekdayName(y, mo, d) {
    return WEEKDAYS[(new Date(Date.UTC(y, mo - 1, d)).getUTCDay() + 6) % 7];
  }

  /* Render calendar fields in the chosen format. `withTime` is false for values
     that have no time of day (a due date, a ds_* stamp, an attribution that named
     only a day). */
  function renderFields(f, withTime, format) {
    var time = withTime ? pad(f.h) + ":" + pad(f.mi) : "";
    if (format === "iso") {
      return f.y + "-" + pad(f.mo) + "-" + pad(f.d) + (time ? " " + time : "");
    }
    if (format === "medium") {
      return f.d + " " + MONTHS_SHORT[f.mo - 1] + " " + f.y + (time ? " " + time : "");
    }
    return weekdayName(f.y, f.mo, f.d) + ", " + f.d + " " + MONTHS[f.mo - 1] +
      " " + f.y + (time ? " " + time : "");
  }

  var Dates = {
    /* The chosen zone, resolved to a name for display in Settings. */
    zoneName: function () {
      var chosen = setting("timeZone", "");
      if (chosen) { return chosen; }
      try { return Intl.DateTimeFormat().resolvedOptions().timeZone || "system"; }
      catch (e) { return "system"; }
    },

    /* An .eml Date header: an absolute instant, shown in the reader's zone. */
    fromEpoch: function (epoch, options) {
      if (epoch === null || epoch === undefined) { return ""; }
      options = options || {};
      var format = options.format || setting("dateFormat", "long");
      var fields = fieldsInZone(new Date(epoch * 1000), zone());
      return renderFields(fields, options.time !== false, format);
    },

    /* The compact form used in list rows, where a full weekday would crowd out the
       subject. Follows the chosen format family: ISO stays ISO. */
    compactFromEpoch: function (epoch) {
      if (epoch === null || epoch === undefined) { return ""; }
      var format = setting("dateFormat", "long");
      return Dates.fromEpoch(epoch, { format: format === "iso" ? "iso" : "medium" });
    },

    /* The calendar day an instant falls on IN THE READER'S ZONE, as yyyy-mm-dd.
       Date grouping and "today" comparisons must use this, or an email would sit
       under the wrong heading whenever the chosen zone shifts it across midnight. */
    dayFromEpoch: function (epoch) {
      if (epoch === null || epoch === undefined) { return ""; }
      var f = fieldsInZone(new Date(epoch * 1000), zone());
      return f.y + "-" + pad(f.mo) + "-" + pad(f.d);
    },

    /* Today in the reader's zone, as yyyy-mm-dd. */
    today: function () { return Dates.dayFromEpoch(Math.floor(Date.now() / 1000)); },

    /* A plain calendar day from metadata.csv (a due date, a ds_* stamp): reformat,
       never shift. Anything that is not yyyy-mm-dd is free text and passes through
       untouched, because `gtd metadata` allows it. */
    fromIsoDay: function (value) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) { return value || ""; }
      var bits = value.split("-");
      return renderFields({ y: +bits[0], mo: +bits[1], d: +bits[2] }, false,
                          setting("dateFormat", "long"));
    },

    /* A quoted in-text header. `parts` is what thread.parse_date_text recovered;
       `raw` is the original text, returned unchanged when nothing was parsed. */
    fromParts: function (parts, raw) {
      if (!parts) { return raw || ""; }
      var format = setting("dateFormat", "long");
      var withTime = parts.h !== undefined && parts.h !== null;
      var offset = parts.offset;
      var naive = setting("naiveDates", "local");

      if (offset === undefined || offset === null) {
        if (naive !== "utc" || !withTime) {
          /* Treat the numbers as already being local: show them as written. (A
             date with no time cannot be shifted meaningfully either way.) */
          return renderFields(parts, withTime, format);
        }
        offset = 0;   /* "treat as UTC", then convert below */
      }
      var instant = Date.UTC(parts.y, parts.mo - 1, parts.d,
                             parts.h || 0, parts.mi || 0, parts.s || 0)
        - offset * 60000;
      return renderFields(fieldsInZone(new Date(instant), zone()), withTime, format);
    },

    /* The IANA zones offered in Settings. Intl can enumerate them on modern
       browsers; the fallback list covers the common ones so the setting is never
       unusable. */
    zoneOptions: function () {
      try {
        if (typeof Intl.supportedValuesOf === "function") {
          var all = Intl.supportedValuesOf("timeZone");
          if (all && all.length) { return all; }
        }
      } catch (e) { /* fall through */ }
      return ["UTC", "Europe/London", "Europe/Dublin", "Europe/Paris",
              "Europe/Berlin", "Europe/Madrid", "Europe/Rome", "Europe/Athens",
              "Europe/Moscow", "America/New_York", "America/Chicago",
              "America/Denver", "America/Los_Angeles", "America/Toronto",
              "America/Vancouver", "America/Mexico_City", "America/Sao_Paulo",
              "Africa/Cairo", "Africa/Johannesburg", "Africa/Lagos",
              "Africa/Nairobi", "Asia/Jerusalem", "Asia/Dubai", "Asia/Karachi",
              "Asia/Kolkata", "Asia/Dhaka", "Asia/Bangkok", "Asia/Shanghai",
              "Asia/Hong_Kong", "Asia/Singapore", "Asia/Tokyo", "Asia/Seoul",
              "Australia/Perth", "Australia/Adelaide", "Australia/Brisbane",
              "Australia/Sydney", "Australia/Hobart", "Pacific/Auckland"];
    }
  };

  window.GTDDates = Dates;
})();
"""
