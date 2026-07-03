"""
Dashboard rendering for `gtd.py generate_dashboard`: turn the per-email metrics
(from metrics.compute_email_metrics) into a single self-contained HTML file.

Self-contained means the file embeds the Plotly.js bundle verbatim inside a
<script> tag (read from the local path configured as `plotly_js_path`), so the
dashboard opens and renders with no network access and no CDN — the same idea as
Quarto's `embed-resources: true`. The only external input at build time is that
local .js file; the output has no external references at all.

Charts drawn (all via the embedded Plotly):
  * Headline KPI table — mean & median of ttS, Td, Wd, tttR across the ongoing,
    resolved, and combined ("both") corpora.
  * Box-and-whisker plots — one per metric, split by corpus.
  * Horizontal stacked bar — one bar per resolved email, segments ttS / Td / Wd
    (some may be zero-width where a stage was backfilled to a same-day stamp).
  * Sankey — flow from "took place" through triage / actionable to the
    resolution states, with same-date steps collapsed into "hops".

Everything is plain data assembled in Python and handed to Plotly.newPlot in a
small inline script; no build step or framework.
"""

import html
import json
import os
from datetime import date

from . import metrics as metrics_mod

# The metrics we report on, in display order, with their full names.
METRIC_ORDER = ["ttS", "Td", "Wd", "tttR"]
METRIC_FULLNAME = {
    "ttS": "Time-to-system (ttS)",
    "Td": "Triage duration (Td)",
    "Wd": "Work duration (Wd)",
    "tttR": "Total-time-to-resolution (tttR)",
}
# Corpora (subsets of emails) each metric is summarised over.
CORPORA = ["ongoing", "resolved", "both"]
CORPUS_LABEL = {"ongoing": "Ongoing", "resolved": "Resolved",
                "both": "Both (ongoing + resolved)"}

# Sankey canvas heights (px). The fixed layout is taller so the pinned nodes
# (archive at the top, triage raised) have room to fan out; the pinned y values
# in build_sankey's COLUMN_Y are chosen against this height.
SANKEY_AUTO_HEIGHT_PX = 460
SANKEY_FIXED_HEIGHT_PX = 640


def _mean(values):
    """Arithmetic mean of a list of numbers, or None if empty."""
    return sum(values) / len(values) if values else None


def _median(values):
    """
    Median of a list of numbers, or None if empty. For an even count, the mean
    of the two middle values.

    Example:
        _median([1, 2, 3, 4])  # -> 2.5
    """
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2


def _fmt(value):
    """Format a metric summary value: one decimal place, or an en-dash if None."""
    if value is None:
        return "\u2013"
    return f"{value:.1f}"


def collect_metric_values(computed):
    """
    Bucket the metric values by (metric, corpus). `computed` is the list of
    per-email dicts from metrics.compute_email_metrics. Weird emails carry no
    metrics, so they contribute nothing. The "both" corpus is ongoing ∪
    resolved (i.e. every non-weird email that has the metric).

    Returns {metric: {corpus: [values...]}}.

    Example:
        collect_metric_values([...])["ttS"]["resolved"]  # -> [2, 4, 0, ...]
    """
    buckets = {m: {c: [] for c in CORPORA} for m in METRIC_ORDER}
    for email in computed:
        status = email["status"]
        if status == "weird":
            continue
        for metric, value in email["metrics"].items():
            if metric not in buckets:
                continue
            if status in ("ongoing", "resolved"):
                buckets[metric][status].append(value)
            buckets[metric]["both"].append(value)
    return buckets


def build_kpi_rows(buckets):
    """
    Build the headline KPI table rows: for each metric and corpus, the mean,
    median, and count. Returns a list of dicts ready to render as table rows.

    Example:
        build_kpi_rows(buckets)[0]
        # -> {"metric": "ttS", "corpus": "ongoing", "n": 3,
        #     "mean": 1.7, "median": 2.0}
    """
    rows = []
    for metric in METRIC_ORDER:
        for corpus in CORPORA:
            values = buckets[metric][corpus]
            rows.append({
                "metric": metric,
                "corpus": corpus,
                "n": len(values),
                "mean": _mean(values),
                "median": _median(values),
            })
    return rows


def build_box_traces(buckets):
    """
    Build Plotly box-plot traces: one trace per corpus, with a box for each
    metric on the x-axis (grouped). Returns a list of trace dicts.

    Example:
        build_box_traces(buckets)  # -> [{"type": "box", "name": "Ongoing", ...}]
    """
    traces = []
    for corpus in CORPORA:
        xs, ys = [], []
        for metric in METRIC_ORDER:
            for value in buckets[metric][corpus]:
                xs.append(METRIC_FULLNAME[metric])
                ys.append(value)
        traces.append({
            "type": "box", "name": CORPUS_LABEL[corpus],
            "x": xs, "y": ys, "boxmean": True,
        })
    return traces


def build_stacked_bar(computed):
    """
    Build the horizontal stacked-bar traces for the resolved corpus: one
    horizontal bar per resolved email, stacked from ttS + Td + Wd. Emails are
    ordered by tttR (largest at the top). Returns a list of three traces (one
    per component). Zero-width segments (from same-day backfills) are kept; they
    simply render invisibly.

    Example:
        build_stacked_bar(computed)  # -> [ttS trace, Td trace, Wd trace]
    """
    resolved = [e for e in computed if e["status"] == "resolved"]
    resolved.sort(key=lambda e: e["metrics"].get("tttR", 0))
    labels = [e["filename"] for e in resolved]
    components = [("ttS", "Time-to-system"), ("Td", "Triage duration"),
                  ("Wd", "Work duration")]
    traces = []
    for key, name in components:
        traces.append({
            "type": "bar", "orientation": "h", "name": name,
            "y": labels,
            "x": [e["metrics"].get(key, 0) for e in resolved],
        })
    return traces


def build_sankey(computed):
    """
    Build Plotly Sankey traces for the resolved corpus. Each resolved email
    contributes one path through its distinct-date stages (consecutive stages
    sharing a date are "hops" and are skipped, so the path links the stages that
    actually advanced the date). A resolution reached on a date shared by more
    than one resolution stamp terminates at a single "tied resolution" node.

    Returns (auto_trace, fixed_trace, has_tie):
      * auto_trace  — Plotly's own automatic node layout (no pinned positions);
      * fixed_trace — the same flows with nodes pinned to chosen columns/rows
        for readability (reference aligned to the actionable column; archive and
        triage nudged upward);
      * has_tie     — whether any email used the tied-resolution node (so the
        caller can show the explanatory blurb).

    The dashboard offers these as two tabs ("auto layout" / "fixed layout").

    Example:
        auto, fixed, tie = build_sankey(computed)
    """
    node_labels = []
    node_index = {}

    def node(label):
        if label not in node_index:
            node_index[label] = len(node_labels)
            node_labels.append(label)
        return node_index[label]

    link_counts = {}  # (src_idx, dst_idx) -> count
    has_tie = False

    for email in computed:
        if email["status"] != "resolved":
            continue
        if email.get("resolution_tied"):
            has_tie = True
        # Collapse hops: keep a stage only when its date differs from the last
        # kept stage's date. The first stage ("took place") always starts it.
        stages = email["stages"]
        kept = []
        last_date = None
        for label, when in stages:
            if last_date is None or when != last_date:
                kept.append(label)
                last_date = when
            else:
                # same date as previous kept stage -> hop; but if this is the
                # terminal resolution stage and everything hopped, we still want
                # a resolution node, so replace the last kept label with it.
                kept[-1] = label
        for src, dst in zip(kept, kept[1:]):
            si, di = node(src), node(dst)
            link_counts[(si, di)] = link_counts.get((si, di), 0) + 1

    sources = [s for (s, _) in link_counts]
    targets = [t for (_, t) in link_counts]
    values = [link_counts[k] for k in link_counts]

    # Leave node colours to Plotly (it assigns a distinct colour per node, which
    # keeps the stages visually separable). Only the LINKS need help: Plotly's
    # default link fill is a near-transparent light grey that disappears over a
    # transparent background, so give links an explicit translucent grey that
    # stays visible in both light and dark themes without clashing with the
    # multi-coloured nodes.
    link_colour = "rgba(128, 128, 128, 0.4)"

    common_node = {"label": node_labels, "pad": 18, "thickness": 18}
    common_link = {"source": sources, "target": targets, "value": values,
                   "color": [link_colour] * len(sources)}

    # --- auto layout: let Plotly place the nodes (no pinned x/y). -------------
    auto_trace = {
        "type": "sankey",
        "textfont": {"color": "#888", "size": 12},
        "node": dict(common_node),
        "link": dict(common_link),
    }

    # --- fixed layout: pin each node by label. --------------------------------
    # Plotly honours node x/y under the default "snap" arrangement while keeping
    # nodes draggable, but only if EVERY node has coordinates (unset ones snap to
    # 0), so we assign all of them by label. x is the logical column; y is the
    # vertical slot within a column. Both must be strictly inside (0, 1).
    #
    # Columns left->right: took place, triage, actionable, resolution. Readability
    # tweaks: "reference" sits in the SAME column as triage/actionable rather than
    # out at the resolution column; "archive" is pushed to the very top and
    # "triage" is raised, so the resolution branches fan out clearly. The y values
    # correspond to the requested upward pixel nudges on the taller fixed-layout
    # canvas (see SANKEY_FIXED_HEIGHT_PX): from the mid-line, archive up ~400px
    # and triage up ~100px.
    COLUMN_X = {
        "took place": 0.02,
        "triage": 0.34,
        "actionable": 0.66,
        # resolution nodes default to the far-right column ...
        "delegated": 0.98,
        "tied resolution": 0.98,
        "archive": 0.98,
        # ... except "reference", pulled back to the actionable column.
        "reference": 0.66,
    }
    COLUMN_Y = {
        "took place": 0.5,
        "triage": 0.02,       # pinned to the very top, above every other node
        "actionable": 0.5,
        "delegated": 0.5,
        "tied resolution": 0.5,
        "archive": 0.08,      # near the top, just below triage
        "reference": 0.80,    # sits lower so it doesn't collide with actionable
    }
    node_x = [COLUMN_X.get(lbl, 0.98) for lbl in node_labels]
    node_y = [COLUMN_Y.get(lbl, 0.5) for lbl in node_labels]

    fixed_node = dict(common_node)
    fixed_node["x"] = node_x
    fixed_node["y"] = node_y
    fixed_trace = {
        "type": "sankey",
        "arrangement": "snap",
        "textfont": {"color": "#888", "size": 12},
        "node": fixed_node,
        "link": dict(common_link),
    }

    return auto_trace, fixed_trace, has_tie


def build_status_counts(computed):
    """
    Count emails by status. Returns {"ongoing": n, "resolved": n, "weird": n}.

    Example:
        build_status_counts(computed)  # -> {"ongoing": 4, "resolved": 9, "weird": 1}
    """
    counts = {"ongoing": 0, "resolved": 0, "weird": 0}
    for email in computed:
        counts[email["status"]] = counts.get(email["status"], 0) + 1
    return counts


def read_plotly_bundle(plotly_js_path):
    """
    Read the local minified Plotly.js bundle to inline into the dashboard.
    Raises FileNotFoundError with a clear message if the path is unset or the
    file is missing — the caller turns that into a friendly CLI error, since
    running offline is a hard requirement (no CDN fallback).

    Example:
        read_plotly_bundle("/home/me/assets/plotly.min.js")  # -> "<the JS>"
    """
    if not (plotly_js_path or "").strip():
        raise FileNotFoundError(
            "no plotly_js_path is set in config.yml. Download the minified "
            "Plotly.js bundle (see README.md) and point plotly_js_path at it.")
    if not os.path.isfile(plotly_js_path):
        raise FileNotFoundError(
            f"plotly_js_path points at '{plotly_js_path}', which does not exist. "
            f"Download the minified Plotly.js bundle (see README.md) and set "
            f"plotly_js_path to its location.")
    with open(plotly_js_path, encoding="utf-8") as f:
        return f.read()


def _kpi_table_html(kpi_rows):
    """Render the KPI rows as an HTML table (escaped)."""
    out = ['<table class="kpi">',
           "<thead><tr><th>Metric</th><th>Corpus</th><th>n</th>"
           "<th>Mean (days)</th><th>Median (days)</th></tr></thead>", "<tbody>"]
    for row in kpi_rows:
        out.append(
            "<tr>"
            f"<td>{html.escape(METRIC_FULLNAME[row['metric']])}</td>"
            f"<td>{html.escape(CORPUS_LABEL[row['corpus']])}</td>"
            f"<td>{row['n']}</td>"
            f"<td>{_fmt(row['mean'])}</td>"
            f"<td>{_fmt(row['median'])}</td>"
            "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def build_dashboard_html(computed, plotly_js, generated_on=None, base_dir=""):
    """
    Assemble the full self-contained dashboard HTML string. `computed` is the
    list of per-email metric dicts; `plotly_js` is the raw text of the Plotly
    bundle to inline. Returns the HTML as a string.

    Example:
        build_dashboard_html(computed, plotly_js)  # -> "<!DOCTYPE html> ... "
    """
    generated_on = generated_on or date.today().isoformat()
    buckets = collect_metric_values(computed)
    kpi_rows = build_kpi_rows(buckets)
    box_traces = build_box_traces(buckets)
    bar_traces = build_stacked_bar(computed)
    sankey_auto, sankey_fixed, has_tie = build_sankey(computed)
    counts = build_status_counts(computed)

    tie_blurb = ("" if not has_tie else
                 '<p class="note"><strong>Tied resolution:</strong> some emails '
                 "reached their latest resolution date on more than one "
                 "resolution stamp (e.g. reference and archive on the same day). "
                 "Because no single resolution state is the unambiguous final "
                 "one, those flows terminate at a shared <em>tied resolution</em> "
                 "node.</p>")

    weird_note = ("" if not counts["weird"] else
                  f'<p class="note"><strong>{counts["weird"]}</strong> email(s) '
                  "were classified <em>weird</em> (their date progression is "
                  "inconsistent, e.g. triaged before the email date) and are "
                  "excluded from every metric and chart above.</p>")

    payload = {
        "box": box_traces,
        "bar": bar_traces,
        "sankeyAuto": [sankey_auto],
        "sankeyFixed": [sankey_fixed],
        "sankeyAutoHeight": SANKEY_AUTO_HEIGHT_PX,
        "sankeyFixedHeight": SANKEY_FIXED_HEIGHT_PX,
    }
    data_json = json.dumps(payload)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GTD-over-EML dashboard</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         margin: 0 auto; max-width: 1000px; padding: 1.5rem; line-height: 1.5; }}
  h1 {{ margin-bottom: 0.2rem; }}
  .sub {{ color: #666; margin-top: 0; }}
  section {{ margin: 2.2rem 0; }}
  table.kpi {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
  table.kpi th, table.kpi td {{ border: 1px solid #ccc; padding: 0.35rem 0.6rem;
         text-align: right; }}
  table.kpi th:first-child, table.kpi td:first-child,
  table.kpi th:nth-child(2), table.kpi td:nth-child(2) {{ text-align: left; }}
  table.kpi thead th {{ background: rgba(127,127,127,0.15); }}
  .note {{ background: rgba(127,127,127,0.10); border-left: 3px solid #999;
         padding: 0.5rem 0.8rem; font-size: 0.9rem; }}
  .counts span {{ display: inline-block; margin-right: 1.2rem; }}
  .chart {{ width: 100%; height: 460px; }}
  /* Plotly applies a dark 4-way text-shadow halo to Sankey node labels as an
     INLINE style on each <text class="node-label"> element (there is no
     trace/layout option to disable it). An inline style only yields to a
     stylesheet rule marked !important, and the class is .node-label in this
     build — so target that specifically. */
  text.node-label {{ text-shadow: none !important; }}
  /* Tabs for the Sankey layout switch. */
  .tabs {{ display: flex; gap: 0.25rem; margin-bottom: 0.5rem; }}
  .tabs button {{ font: inherit; padding: 0.3rem 0.9rem; cursor: pointer;
         border: 1px solid #bbb; border-bottom: none;
         border-radius: 6px 6px 0 0; background: rgba(127,127,127,0.10);
         color: inherit; }}
  .tabs button[aria-selected="true"] {{ background: rgba(127,127,127,0.28);
         font-weight: 600; }}
  .tabpanel[hidden] {{ display: none; }}
</style>
<script>{plotly_js}</script>
</head>
<body>
<h1>GTD-over-EML dashboard</h1>
<p class="sub">Email response-time performance &middot; generated {html.escape(generated_on)}</p>

<p class="counts">
  <span><strong>{counts['ongoing']}</strong> ongoing</span>
  <span><strong>{counts['resolved']}</strong> resolved</span>
  <span><strong>{counts['weird']}</strong> weird</span>
</p>

<section>
  <h2>Headline KPIs</h2>
  <p>Mean and median (in days) of each metric across the ongoing, resolved, and
     combined corpora. Weird emails are excluded.</p>
  {_kpi_table_html(kpi_rows)}
  {weird_note}
</section>

<section>
  <h2>Distributions (box &amp; whisker)</h2>
  <p>Each box spans the interquartile range; the line is the median and the
     dashed marker the mean. Metrics are grouped by corpus.</p>
  <div id="box" class="chart"></div>
</section>

<section>
  <h2>Resolved emails: time composition</h2>
  <p>One horizontal bar per resolved email, stacked as time-to-system + triage
     duration + work duration (which sum to total-time-to-resolution). Ordered
     by total-time-to-resolution. Some segments may be zero-width where a stage
     was recorded on the same day as the previous one.</p>
  <div id="bar" class="chart" style="height: 620px;"></div>
</section>

<section>
  <h2>Flow from arrival to resolution (Sankey)</h2>
  <p>How resolved emails flowed from taking place, through triage and
     actionable, to their resolution state. Steps sharing a date are collapsed
     (&ldquo;hops&rdquo;), so an email that was triaged and actioned on the same
     day links straight through.</p>
  <div class="tabs" role="tablist" aria-label="Sankey layout">
    <button id="tab-auto" role="tab" aria-controls="sankey" aria-selected="true"
            onclick="selectSankey('auto')">Auto layout</button>
    <button id="tab-fixed" role="tab" aria-controls="sankey" aria-selected="false"
            onclick="selectSankey('fixed')">Fixed layout</button>
  </div>
  <p class="sub" id="sankey-caption">Plotly places the nodes automatically.</p>
  <div id="sankey" class="chart"></div>
  {tie_blurb}
</section>

<script>
  var DATA = {data_json};
  var layoutBase = {{ margin: {{ t: 20, r: 20, b: 60, l: 60 }},
                      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)" }};
  var cfg = {{ responsive: true, displayModeBar: false }};
  // Sankey: NOT responsive. Plotly re-renders responsive Sankeys on every
  // resize but does not clear the prior SVG text, so labels accumulate into a
  // ghosted blur. A one-shot (non-responsive) render avoids that; we size it to
  // the container width once at load and re-render only on an explicit resize.
  var sankeyCfg = {{ responsive: false, displayModeBar: false }};
  Plotly.newPlot("box", DATA.box,
    Object.assign({{ boxmode: "group", yaxis: {{ title: "days" }} }}, layoutBase), cfg);
  Plotly.newPlot("bar", DATA.bar,
    Object.assign({{ barmode: "stack",
                     xaxis: {{ title: "days" }},
                     yaxis: {{ showticklabels: false, title: "resolved emails" }} }},
                  layoutBase), cfg);
  var sankeyEl = document.getElementById("sankey");
  var sankeyMode = "auto";  // "auto" | "fixed"
  function currentSankey() {{
    return sankeyMode === "fixed" ? DATA.sankeyFixed : DATA.sankeyAuto;
  }}
  function currentSankeyHeight() {{
    return sankeyMode === "fixed" ? DATA.sankeyFixedHeight : DATA.sankeyAutoHeight;
  }}
  function drawSankey() {{
    // Plotly.react replaces the plot in place (nodes stay draggable). The
    // "ghosted" label look was Plotly's dark text-shadow halo on each node
    // label, switched off via CSS (text.node-label above), not by disabling drag.
    // The fixed layout uses a taller canvas so the pinned nodes fan out.
    var h = currentSankeyHeight();
    sankeyEl.style.height = h + "px";
    Plotly.react(sankeyEl, currentSankey(), {{ margin: {{ t: 10, r: 10, b: 10, l: 10 }},
                     font: {{ color: "#888" }}, width: sankeyEl.clientWidth, height: h,
                     paper_bgcolor: "rgba(0,0,0,0)" }}, sankeyCfg);
  }}
  function selectSankey(mode) {{
    sankeyMode = mode;
    var autoTab = document.getElementById("tab-auto");
    var fixedTab = document.getElementById("tab-fixed");
    autoTab.setAttribute("aria-selected", mode === "auto");
    fixedTab.setAttribute("aria-selected", mode === "fixed");
    document.getElementById("sankey-caption").textContent = (mode === "fixed")
      ? "Nodes are pinned: reference shares the actionable column; archive and triage are raised."
      : "Plotly places the nodes automatically.";
    drawSankey();
  }}
  drawSankey();
  // Debounced redraw on window resize (react replaces rather than stacks), and
  // only when the width actually changed.
  var sankeyW = sankeyEl.clientWidth, sankeyTimer;
  window.addEventListener("resize", function () {{
    clearTimeout(sankeyTimer);
    sankeyTimer = setTimeout(function () {{
      if (sankeyEl.clientWidth !== sankeyW) {{ sankeyW = sankeyEl.clientWidth; drawSankey(); }}
    }}, 200);
  }});
</script>
</body>
</html>
"""
