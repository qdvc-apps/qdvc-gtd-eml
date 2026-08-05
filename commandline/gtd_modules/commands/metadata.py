"""
`metadata` subcommand: get or set a field in metadata.csv for one email.

Note: this module is `gtd_modules.commands.metadata`; the metadata *store*
module is `gtd_modules.metadata`, imported below as `meta_mod`.
"""

import os
import re
import sys

from .. import config as cfg_mod
from .. import fs
from .. import metadata as meta_mod

# due_date is stored verbatim like every other free-text field, but a value that
# is not yyyy-mm-dd cannot be sorted or compared against today, so warn (without
# refusing — the user may deliberately be jotting "end of Q3").
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def cmd_metadata(argv):
    """
    `gtd.py metadata <file.eml> get <field>` — print a stored metadata value.
    `gtd.py metadata <file.eml> set <field> [=] <value>` — write a value.

    Editable fields: general_notes, project, next_action, due_date, flags.
    Readable also includes message_ref and the ds_* stamps. Setting a due_date
    that is not yyyy-mm-dd is allowed but warns, since only an ISO date can be
    compared against today. The ".eml" extension is optional. The "=" between
    field and value is optional, and the value may be quoted or span multiple
    shell words (they are rejoined with spaces).

    Examples:
        cmd_metadata(["x.eml", "get", "next_action"])
        cmd_metadata(["x.eml", "set", "next_action", "=", "Do something"])
    """
    if len(argv) < 3:
        print('usage: gtd.py metadata <file.eml> get <field>', file=sys.stderr)
        print('       gtd.py metadata <file.eml> set <field> [=] <value>', file=sys.stderr)
        return 2

    filename, action = argv[0], argv[1]
    field = argv[2]
    rest = argv[3:]

    base_dir = cfg_mod.load_config()["working_directory"]

    # Resolve to the canonical on-disk filename so the metadata key matches and
    # the extension is optional.
    path = fs.find_eml(base_dir, filename)
    if path is None:
        print(f"error: '{filename}' not found in any GTD folder under {base_dir}",
              file=sys.stderr)
        return 1
    canonical = os.path.basename(path)

    if action == "get":
        if rest:
            print("usage: gtd.py metadata <file.eml> get <field>", file=sys.stderr)
            return 2
        try:
            value = meta_mod.get_metadata_value(base_dir, canonical, field)
        except KeyError:
            print(f"error: unknown field '{field}'", file=sys.stderr)
            print("       readable fields: " + ", ".join(meta_mod.READABLE_FIELDS),
                  file=sys.stderr)
            return 2
        if value is None:
            # No row yet (e.g. metadata.csv not built). Treat as empty.
            value = ""
        print(value)
        return 0

    if action == "set":
        # Only user-editable fields may be written through this command. The
        # ds_* date-stamp columns are writable by the store (for the workflow
        # commands) but must not be settable by hand, so gate here explicitly
        # rather than relying on set_metadata_value's broader WRITABLE_FIELDS.
        if field not in meta_mod.EDITABLE_FIELDS:
            print(f"error: field '{field}' is not editable", file=sys.stderr)
            print("       editable fields: " + ", ".join(meta_mod.EDITABLE_FIELDS),
                  file=sys.stderr)
            return 2
        # Allow an optional leading "=" token, and rejoin the remaining words
        # into the value (the shell has already removed any quotes).
        if rest and rest[0] == "=":
            rest = rest[1:]
        value = " ".join(rest)
        try:
            meta_mod.set_metadata_value(base_dir, canonical, field, value)
        except KeyError:
            print(f"error: field '{field}' is not editable", file=sys.stderr)
            print("       editable fields: " + ", ".join(meta_mod.EDITABLE_FIELDS),
                  file=sys.stderr)
            return 2
        except FileNotFoundError:
            print(f"error: '{canonical}' is not in the workflow", file=sys.stderr)
            return 1
        if field == "due_date" and value.strip() and not _ISO_DATE_RE.match(value.strip()):
            print(f"warning: due_date {value.strip()!r} is not in yyyy-mm-dd form, "
                  f"so it cannot be compared against today's date.", file=sys.stderr)
        print(f"{canonical}: {field} = {value!r}")
        return 0

    print(f"error: unknown action '{action}' (expected 'get' or 'set')", file=sys.stderr)
    return 2
