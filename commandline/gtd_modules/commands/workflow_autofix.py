"""
`workflow_autofix` subcommand: reconcile the ds_* date-stamps in metadata.csv
with what the folder layout and the logical GTD progression imply, writing the
corrective stamps only after the user approves the whole batch.

It is the mutation counterpart to the read-only `generate_dashboard`: that
command refuses to run while any autofix is outstanding and points the user
here, so all metadata writes are intentional and reviewable in one place.
"""

import os
import sys

from .. import config as cfg_mod
from .. import fs
from .. import metrics as metrics_mod
from ..metadata import load_metadata, set_metadata_value, sync_metadata


def _collect_records(base_dir, metadata):
    """
    Build the metrics.plan_autofix record list: one {"filename", "folder", "row"}
    per tracked .eml (folders 02–06; 01-input is handled separately). `metadata`
    is the loaded metadata.csv dict.
    """
    records = []
    for folder in (cfg_mod.TRIAGE_DIR, cfg_mod.ACTIONABLE_DIR, cfg_mod.DELEGATED_DIR,
                   cfg_mod.REFERENCE_DIR, cfg_mod.ARCHIVE_DIR):
        for name in fs.list_eml_files(base_dir, folder):
            records.append({"filename": name, "folder": folder,
                            "row": metadata.get(name, {})})
    return records


def cmd_workflow_autofix(argv):
    """
    `gtd.py workflow_autofix` — propose and (on approval) apply the ds_* stamp
    corrections implied by the folder layout and the GTD logical progression.

    Refuses to run while 01-input holds un-ingested files (run `gtd.py list`
    first). Computes two kinds of fix — folder/stamp consistency (a hand-filed
    email whose arrival stamp was never written gets stamped today) and date
    backfills (a resolved email must have been triaged/actioned first, etc.) —
    plus a list of blockers it will NOT auto-resolve (an ongoing email sitting
    in a resolved folder with no dates to infer from). If there are blockers, it
    lists them and exits without changing anything. Otherwise it prints every
    proposed stamp, warns about committing first if the dataset is under git,
    and asks for a single yes/no covering the whole batch.

    Example:
        cmd_workflow_autofix([])
        # -> lists proposed stamps, prompts, applies on "y"
    """
    if argv:
        print("usage: gtd.py workflow_autofix", file=sys.stderr)
        return 2

    base_dir = cfg_mod.load_config()["working_directory"]
    fs.ensure_folders(base_dir)

    # Guard: 01-input must be empty (those files are not ingested/tracked yet).
    pending_input = fs.list_eml_files(base_dir, cfg_mod.INPUT_DIR)
    if pending_input:
        print(f"error: {len(pending_input)} file(s) are still in "
              f"{cfg_mod.INPUT_DIR}; workflow_autofix cannot run.", file=sys.stderr)
        print(f"       Run `gtd.py list` to ingest them into "
              f"{cfg_mod.TRIAGE_DIR} first, then try again.", file=sys.stderr)
        return 1

    # Reconcile the CSV with on-disk files so every tracked email has a row.
    sync_metadata(base_dir)
    metadata = load_metadata(base_dir)
    records = _collect_records(base_dir, metadata)

    fixes, blockers = metrics_mod.plan_autofix(records)

    if blockers:
        print("=== workflow_autofix: manual attention needed ===")
        print(f"  {len(blockers)} email(s) cannot be fixed automatically and "
              f"must be resolved by hand first:\n")
        for b in blockers:
            print(f"    {b['filename']}  [{b['folder']}]")
            print(f"      {b['reason']}")
        print("\n  Nothing was changed. File each of the above into the folder "
              "that matches its\n  actual state (or correct its metadata), then "
              "run workflow_autofix again.")
        return 1

    if not fixes:
        print("=== workflow_autofix ===")
        print("  metadata.csv is already consistent; no changes needed.")
        return 0

    # Summarise the proposed batch.
    print("=== workflow_autofix: proposed changes ===")
    phase_titles = {"folder-consistency": "Folder/stamp consistency",
                    "date-backfill": "Logical-progression date backfills"}
    for phase in ("folder-consistency", "date-backfill"):
        group = [f for f in fixes if f["phase"] == phase]
        if not group:
            continue
        print(f"\n  {phase_titles[phase]} ({len(group)}):")
        for f in group:
            old = f["old"] or "(unset)"
            print(f"    {f['filename']}  [{f['folder']}]")
            print(f"      {f['field']}: {old} -> {f['new']}")

    print(f"\n  {len(fixes)} stamp(s) will be written to metadata.csv.")
    print("  If you track your EML dataset with git, you may want to cancel now,")
    print("  make a commit, and re-run — so you can reverse these changes")
    print("  immediately if they turn out to be problematic for you.")

    try:
        answer = input("\n  Apply all of these changes? [y/N] ").strip().lower()
    except EOFError:
        answer = ""
    if answer not in ("y", "yes"):
        print("  Aborted; nothing was changed.")
        return 1

    for f in fixes:
        set_metadata_value(base_dir, f["filename"], f["field"], f["new"])

    print(f"\n  Applied {len(fixes)} change(s) to metadata.csv.")
    return 0
