"""
`generate_dashboard` subcommand: render a self-contained HTML dashboard of
email response-time performance (ttS, Td, Wd, tttR) from the ds_* date-stamps in
metadata.csv.

Read-only on the workflow: it never ingests 01-input or moves/rewrites anything.
If any autofix mutation is outstanding (or 01-input is non-empty, or an email is
in an unresolvable state), it refuses and tells the user to run
`gtd.py workflow_autofix` first, so all metadata corrections happen there — under
explicit approval — rather than as a side effect of building a report.
"""

import os
import sys

from .. import config as cfg_mod
from .. import dashboard as dash_mod
from .. import emailutil
from .. import fs
from .. import metrics as metrics_mod
from ..metadata import load_metadata, sync_metadata

# The folders whose emails are analysed (01-input is excluded; those files are
# not ingested/tracked yet).
ANALYSED_FOLDERS = [cfg_mod.TRIAGE_DIR, cfg_mod.ACTIONABLE_DIR, cfg_mod.DELEGATED_DIR,
                    cfg_mod.REFERENCE_DIR, cfg_mod.ARCHIVE_DIR]

DEFAULT_BASENAME = "dashboard.html"


def _collect_records(base_dir, metadata):
    """One {"filename", "folder", "row"} per tracked .eml, for plan_autofix."""
    records = []
    for folder in ANALYSED_FOLDERS:
        for name in fs.list_eml_files(base_dir, folder):
            records.append({"filename": name, "folder": folder,
                            "row": metadata.get(name, {})})
    return records


def cmd_generate_dashboard(argv):
    """
    `gtd.py generate_dashboard [output-file]` — build a self-contained HTML
    dashboard reporting ttS, Td, Wd, and tttR across the ongoing, resolved, and
    combined corpora (headline KPIs, box plots, a stacked bar of resolved-email
    time composition, and a Sankey of the flow to resolution).

    Refuses (exit 1, no output) if 01-input is non-empty or if any autofix
    mutation is outstanding, pointing the user at `gtd.py workflow_autofix`.
    Also refuses if `plotly_js_path` is unset/missing, since the dashboard
    inlines that bundle to run offline (no CDN fallback).

    With no output file it writes <working_directory>/dashboard.html; give a
    path to write elsewhere (a ".html" extension is appended if omitted).

    Example:
        cmd_generate_dashboard([])              # -> writes the default dashboard.html
        cmd_generate_dashboard(["out.html"])    # -> writes ./out.html
    """
    if len(argv) > 1:
        print("usage: gtd.py generate_dashboard [output-file]", file=sys.stderr)
        return 2

    cfg = cfg_mod.load_config()
    base_dir = cfg["working_directory"]
    fs.ensure_folders(base_dir)

    # Guard: 01-input must be empty.
    pending_input = fs.list_eml_files(base_dir, cfg_mod.INPUT_DIR)
    if pending_input:
        print(f"error: {len(pending_input)} file(s) are still in "
              f"{cfg_mod.INPUT_DIR}.", file=sys.stderr)
        print(f"       Run `gtd.py list` to ingest them, then "
              f"`gtd.py workflow_autofix`, then try again.", file=sys.stderr)
        return 1

    # Reconcile the CSV, then check whether any autofix is outstanding. If so,
    # refuse and defer all mutations to `workflow_autofix`.
    sync_metadata(base_dir)
    metadata = load_metadata(base_dir)
    records = _collect_records(base_dir, metadata)
    fixes, blockers = metrics_mod.plan_autofix(records)

    if blockers or fixes:
        print("error: metadata.csv has unresolved workflow issues; the "
              "dashboard would be inaccurate.", file=sys.stderr)
        if blockers:
            print(f"       {len(blockers)} email(s) need manual attention; "
                  f"{len(fixes)} stamp(s) need autofixing.", file=sys.stderr)
        else:
            print(f"       {len(fixes)} stamp(s) need autofixing.",
                  file=sys.stderr)
        print("       Run `gtd.py workflow_autofix` to review and apply the "
              "corrections, then try again.", file=sys.stderr)
        return 1

    # Load the Plotly bundle to inline (hard requirement for offline use).
    try:
        plotly_js = dash_mod.read_plotly_bundle(cfg.get("plotly_js_path"))
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    # Resolve the output path.
    if argv:
        out_path = argv[0]
        if not out_path.lower().endswith(".html"):
            out_path += ".html"
    else:
        out_path = os.path.join(base_dir, DEFAULT_BASENAME)

    # Compute metrics for every tracked email, tag each with the configured
    # own-account that received it (read from the .eml headers), and render.
    accounts = cfg.get("my_own_accounts") or []
    computed = []
    for rec in records:
        result = metrics_mod.compute_email_metrics(rec["filename"], rec["row"])
        account_label = None
        if accounts:
            eml_path = os.path.join(base_dir, rec["folder"], rec["filename"])
            try:
                message = emailutil.read_eml_message(eml_path)
                match = emailutil.match_own_account(message, accounts)
                if match:
                    account_label = match["display_name"]
            except (OSError, ValueError):
                account_label = None  # unreadable .eml -> unattributed
        result["account"] = account_label
        computed.append(result)

    account_names = [a["display_name"] for a in accounts]
    html_text = dash_mod.build_dashboard_html(
        computed, plotly_js, base_dir=base_dir, account_names=account_names)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_text)

    counts = dash_mod.build_status_counts(computed)
    print(f"Wrote dashboard ({counts['ongoing']} ongoing, {counts['resolved']} "
          f"resolved, {counts['weird']} weird) -> {out_path}")
    return 0
