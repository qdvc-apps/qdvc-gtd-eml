#!/usr/bin/env python3
"""Copy the CLI's pure modules into qdvc/gtd_modules/, unmodified.

The app's core *is* the command-line tool's code, so the two can never
disagree about filenames, metadata.csv bytes or refusals. This script copies
the modules the app uses from a qdvc-gtd-eml checkout and records where they
came from (commit and SHA-256 of each file) in qdvc/gtd_modules/VENDORED.json.
The CLI lives beside this app in the qdvc-gtd-eml monorepo (`../commandline`).

    python3 tools/vendor_core.py               # refresh from ../commandline
    python3 tools/vendor_core.py --check       # verify against the manifest
    python3 tools/vendor_core.py --drift       # ...and against ../commandline

`--check` (also run by the tests) fails if a vendored file was edited by
hand: fixes belong in the CLI, then come here with a refresh. `--drift`
(also run by the tests, when ../commandline is there) fails when the CLI has
changed since the last refresh. After a
refresh, run the tests (scripts/build-app.sh does); a parity failure is
either a CLI change the app must follow, or a bug.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "qdvc" / "gtd_modules"
MANIFEST = DEST / "VENDORED.json"
DEFAULT_CLI = ROOT.parent / "commandline"
SOURCE = "https://github.com/qdvc-apps/qdvc-gtd-eml (commandline/)"

# The pure modules the app imports, plus their own intra-package imports.
# Not copied: commands/ (CLI front-end), webui*/export/preview (the static
# site and other outputs the app does not produce).
MODULES = ["__init__.py", "config.py", "dashboard.py", "emailutil.py", "fs.py",
           "ingest.py", "metadata.py", "metrics.py", "naming.py", "report.py",
           "site.py", "thread.py"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh(cli_repo):
    src = Path(cli_repo).resolve() / "gtd_modules"
    if not src.is_dir():
        sys.exit(f"{src} not found: pass the CLI's folder (commandline/ in the monorepo)")
    try:
        commit = subprocess.run(["git", "-C", str(src.parent), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(src.parent), "status", "--porcelain",
                                "--", "gtd_modules"], capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = "unknown", ""
    DEST.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in MODULES:
        shutil.copyfile(src / name, DEST / name)
        files[name] = sha256(DEST / name)
    MANIFEST.write_text(json.dumps({
        "source": SOURCE,
        "commit": commit + ("+local-changes" if dirty else ""),
        "files": files,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Vendored {len(files)} modules from {commit[:12]}{' (dirty)' if dirty else ''}.")


def check():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bad = [name for name, digest in manifest["files"].items()
           if not (DEST / name).is_file() or sha256(DEST / name) != digest]
    if bad:
        print("Edited or missing vendored files: " + ", ".join(bad), file=sys.stderr)
        return 1
    print(f"gtd_modules matches CLI commit {manifest['commit'][:12]}.")
    return 0


def drift(cli_repo=DEFAULT_CLI):
    """Vendored files that differ from the CLI's current ones."""
    src = Path(cli_repo) / "gtd_modules"
    return [name for name in MODULES
            if not (src / name).is_file() or sha256(src / name) != sha256(DEST / name)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cli-repo", default=str(DEFAULT_CLI),
                    help="the CLI's folder (default: ../commandline)")
    ap.add_argument("--check", action="store_true", help="verify the vendored files")
    ap.add_argument("--drift", action="store_true",
                    help="also compare them with the CLI's current files")
    args = ap.parse_args()
    if args.check or args.drift:
        status = check()
        if args.drift:
            changed = drift(args.cli_repo)
            if changed:
                print("Changed in the CLI since the last refresh: " + ", ".join(changed)
                      + " (run tools/vendor_core.py)", file=sys.stderr)
                status = 1
        return status
    refresh(args.cli_repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
