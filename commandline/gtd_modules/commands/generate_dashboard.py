"""
`generate_dashboard` subcommand: render a self-contained static WEBSITE reporting
on the whole workflow — an email-client-style interface over every tracked email
(plus whatever is still sitting in 01-input), with the response-time performance
dashboard (ttS, Td, Wd, tttR) as one of its sections.

Read-only on the workflow: it never ingests 01-input or moves/rewrites anything.
If any autofix mutation is outstanding (or an email is in an unresolvable state),
it refuses and tells the user to run `gtd.py workflow_autofix` first, so all
metadata corrections happen there — under explicit approval — rather than as a
side effect of building a report.

Files in 01-input are NOT a hard error here (they are for `workflow_autofix`):
the site has an Input section that exists precisely to show them, so the command
notes them, includes them as untracked, and carries on. They are excluded from
every metric, exactly as they are from the tracked set `gtd.py list` reports on.
"""

import os
import sys
from datetime import date, datetime

from .. import config as cfg_mod
from .. import dashboard as dash_mod
from .. import emailutil
from .. import fs
from .. import metrics as metrics_mod
from .. import site as site_mod
from .. import webui
from ..metadata import load_metadata, sync_metadata

# The folders whose emails are analysed for metrics (01-input is excluded; those
# files are not ingested/tracked yet, so they have no date-stamps to measure).
ANALYSED_FOLDERS = [cfg_mod.TRIAGE_DIR, cfg_mod.ACTIONABLE_DIR, cfg_mod.DELEGATED_DIR,
                    cfg_mod.REFERENCE_DIR, cfg_mod.ARCHIVE_DIR]

# Output directory name used when none is given.
DEFAULT_DIRNAME = "dashboard"


def _collect_records(base_dir, metadata):
    """One {"filename", "folder", "row"} per tracked .eml, for plan_autofix."""
    records = []
    for folder in ANALYSED_FOLDERS:
        for name in fs.list_eml_files(base_dir, folder):
            records.append({"filename": name, "folder": folder,
                            "row": metadata.get(name, {})})
    return records


def _resolve_out_dir(argv, base_dir):
    """
    Work out where to write the site, returning (path, was_html_path). With no
    argument it is <working_directory>/dashboard/. A given path is used as the
    output DIRECTORY; because earlier versions of this command wrote a single
    dashboard.html, a path ending in ".html" has that extension dropped (and the
    caller reports the substitution) rather than being taken as a filename.

    Example:
        _resolve_out_dir(["~/gtd-dashboard.html"], "/g")
        # -> ("~/gtd-dashboard", True)
    """
    if not argv:
        return os.path.join(base_dir, DEFAULT_DIRNAME), False
    out_dir = argv[0].rstrip(os.sep)
    if out_dir.lower().endswith(".html"):
        return os.path.splitext(out_dir)[0], True
    return out_dir, False


def cmd_generate_dashboard(argv):
    """
    `gtd.py generate_dashboard [output-directory]` — build a static website
    reporting on the workflow: an Overview, one section per workflow folder with a
    message list and a full reading pane (including the quoted email history), and
    a Performance section with the response-time metrics, charts and Sankey. The
    site is read-only; its buttons compose the `gtd` commands you would run to
    actually change something.

    Refuses (exit 1, nothing written) if any autofix mutation is outstanding,
    pointing the user at `gtd.py workflow_autofix`. Also refuses if
    `plotly_js_path` is unset/missing, since the site bundles that file to run
    offline (no CDN fallback).

    Writes TWO builds: `desktop/` (sidebar, message list, reading pane, charts)
    and `mobile/gtd-eml.html` — a single self-contained file with bottom tabs and
    tap-through pages, sized for a phone — plus a small chooser page at the root. With no argument the output directory is
    <working_directory>/dashboard/; give a path to write elsewhere. Open the
    resulting index.html in a browser — no server needed.

    Example:
        cmd_generate_dashboard([])            # -> writes <wd>/dashboard/index.html
        cmd_generate_dashboard(["~/report"])  # -> writes ~/report/index.html
    """
    if len(argv) > 1:
        print("usage: gtd.py generate_dashboard [output-directory]", file=sys.stderr)
        return 2

    cfg = cfg_mod.load_config()
    base_dir = cfg["working_directory"]
    fs.ensure_folders(base_dir)

    # Files still in 01-input are reported as untracked rather than blocking the
    # build: the site's Input section exists to show them.
    pending_input = fs.list_eml_files(base_dir, cfg_mod.INPUT_DIR)
    if pending_input:
        print(f"note: {len(pending_input)} file(s) are still in {cfg_mod.INPUT_DIR}; "
              f"they are shown as untracked and excluded from every metric.")
        print("      Run `gtd.py list` to ingest them for the full picture.")

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

    # Load the Plotly bundle to copy into the site (a hard requirement for
    # offline use — never a CDN fallback).
    try:
        plotly_js = dash_mod.read_plotly_bundle(cfg.get("plotly_js_path"))
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out_dir, was_html_path = _resolve_out_dir(argv, base_dir)
    if was_html_path:
        print("note: the dashboard is now a folder of files rather than one HTML "
              f"file; writing the site to {out_dir}{os.sep} instead.")

    # Compute metrics for every tracked email and tag each with the configured
    # own-account that received it (read from the .eml headers).
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
    performance_body, performance_data = dash_mod.build_performance_page(
        computed, today=date.today(), account_names=account_names)
    # The mobile build shows the metric tables rather than the charts, so it needs
    # the pre-rendered HTML blocks for the all-accounts view.
    view_keys, _payloads, blocks = dash_mod.build_views(
        computed, today=date.today(), account_names=account_names)
    performance_blocks = blocks[view_keys[0]]

    # The mail interface: every email (including 01-input) with its metadata,
    # thread history, and the metrics already computed above.
    site_data = site_mod.build_site_data(
        base_dir, cfg, metadata=metadata,
        computed_by_file={e["filename"]: e for e in computed},
        generated_at=datetime.now())

    try:
        index_path = webui.write_site(out_dir, site_data, performance_body,
                                      performance_data, performance_blocks,
                                      plotly_js)
    except OSError as e:
        print(f"error: could not write the site to {out_dir}: {e}", file=sys.stderr)
        return 1

    counts = dash_mod.build_status_counts(computed)
    total = site_data["overview"]["counts"]["total"]
    print(f"Wrote site ({total} email(s): {counts['ongoing']} ongoing, "
          f"{counts['resolved']} resolved, {counts['weird']} weird, "
          f"{len(pending_input)} awaiting ingestion) -> {index_path}")
    print(f"      desktop build: {os.path.join(out_dir, webui.DESKTOP_DIR, 'index.html')}")
    print(f"      mobile build:  "
          f"{os.path.join(out_dir, webui.MOBILE_DIR, webui.MOBILE_FILE)}")
    return 0
