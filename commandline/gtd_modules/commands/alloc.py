"""
`alloc` subcommand: move an email from wherever it is filed to another folder.
"""

import os
import sys

from .. import config as cfg_mod
from .. import fs
from .. import metadata as meta_mod


def cmd_alloc(argv):
    """
    `gtd.py alloc <file.eml> <destination>` — find where an email is currently
    filed and move it to the destination folder. Destination accepts a short
    alias (actionable, delegated, reference, archive, triage, input) or the full
    folder name (e.g. 04-delegated).

    On a successful move, the destination folder's date-stamp field (ds_triage,
    ds_actionable, ds_delegated, ds_reference, ds_archive) is set to today's
    date. If that field already holds a value, the command refuses (exit 1) and
    changes nothing, so an existing arrival date is never overwritten.

    Example:
        cmd_alloc(["2026-06-03-x.eml", "delegated"])
        # -> moves the file to 04-delegated, stamps ds_delegated, returns 0
    """
    if len(argv) != 2:
        print("usage: gtd.py alloc <file.eml> <destination>", file=sys.stderr)
        print("       destinations: " + ", ".join(cfg_mod.FOLDERS_BY_ALIAS),
              file=sys.stderr)
        return 2

    filename, destination = argv
    dest_folder = fs.resolve_folder(destination)
    if dest_folder is None:
        print(f"error: unknown destination '{destination}'", file=sys.stderr)
        print("       choose one of: " + ", ".join(cfg_mod.FOLDERS_BY_ALIAS),
              file=sys.stderr)
        return 2

    base_dir = cfg_mod.load_config()["working_directory"]
    src_path = fs.find_eml(base_dir, filename)
    if src_path is None:
        print(f"error: '{filename}' not found in any GTD folder under {base_dir}",
              file=sys.stderr)
        return 1

    src_folder = os.path.basename(os.path.dirname(src_path))
    if src_folder == dest_folder:
        print(f"'{os.path.basename(src_path)}' is already in {dest_folder}; nothing to do.")
        return 0

    canonical = os.path.basename(src_path)

    # Refuse to overwrite an existing date-stamp for the destination folder. The
    # ds_* field records when the email FIRST entered that folder; re-filing it
    # there would clobber that history, so stop and let the user sort it out by
    # hand. Checked before the move so a refusal changes nothing.
    stamp_field = meta_mod.date_stamp_field(dest_folder)
    if stamp_field is not None:
        existing = meta_mod.get_metadata_value(base_dir, canonical, stamp_field)
        if existing:
            print(f"error: '{canonical}' already has {stamp_field} = {existing}; "
                  f"refusing to move it to {dest_folder} and overwrite that date.",
                  file=sys.stderr)
            print(f"       Please handle this email manually.", file=sys.stderr)
            return 1

    try:
        fs.move_eml(src_path, base_dir, dest_folder)
    except FileExistsError:
        print(f"error: a file named '{canonical}' already exists "
              f"in {dest_folder}", file=sys.stderr)
        return 1

    # Stamp the destination's date-stamp field with today's date (a no-op for
    # folders without one, i.e. 01-input).
    if stamp_field is not None:
        meta_mod.stamp_date_field(base_dir, canonical, dest_folder, meta_mod.today_stamp())

    print(f"Moved {canonical}: {src_folder} -> {dest_folder}")
    return 0
