# qdvc-gtd-eml

A **quick-and-dirty vibe-coded ("QDVC")** command-line toolkit for running a [Getting Things Done](https://gettingthingsdone.com/)
workflow over plain `.eml` email files. Export emails you want to act on, drop
them in a folder, and let the tool file and track them.

## How it works

You export emails as `.eml` files into `01-input/`. Running `gtd.py list`:

- **renames** each new file to `yyyy-mm-dd-brief-description.eml` (derived from
  the date and subject), then moves it to `02-triage/` (stamping its `ds_triage`
  date);
- prints a **status report** of what's in each folder, colour-coded by age, with
  correspondents and your next action.

You then file each triaged email into `03-actionable/`, `04-delegated/`,
`05-reference/`, or `06-archive/` — either by hand or with `gtd.py alloc`.
Annotations (notes, project, next action) live in a `metadata.csv` the tool
keeps in sync, which also records the date each email entered a folder
(`ds_triage`, `ds_actionable`, `ds_delegated`, `ds_reference`, `ds_archive`).

```
01-input  →  02-triage  →  03-actionable
                        ↘  04-delegated
                        ↘  05-reference
                        ↘  06-archive
```

## Usage

```bash
python3 gtd.py list                       # ingest new files + print the report
python3 gtd.py list <folder>              # show just one folder (e.g. actionable)
python3 gtd.py export <format> [out]      # export all data to a data format
python3 gtd.py search <text>              # find report entries matching <text>
python3 gtd.py stats                      # count emails in each folder
python3 gtd.py view <file.eml>            # preview one email (headers + body)
python3 gtd.py alloc <file.eml> <dest>    # move an email to another folder
python3 gtd.py close <file.eml> with <other.eml>   # archive + record what closed it
python3 gtd.py pin <file.eml>             # add the "pinned" flag
python3 gtd.py unpin <file.eml>           # remove the "pinned" flag
python3 gtd.py metadata <file.eml> ...    # get/set a metadata.csv field
python3 gtd.py metadata_check             # reconcile metadata.csv + report dangling refs
python3 gtd.py workflow_autofix           # reconcile ds_* stamps with folders + logic
python3 gtd.py generate_dashboard [out]   # build a self-contained HTML KPI dashboard
python3 gtd.py help                       # full command overview
```

`alloc`'s destination is a short name (`actionable`, `delegated`, `reference`,
`archive`, `triage`, `input`) or the full folder name (e.g. `04-delegated`).
On a successful move it stamps the destination's date-stamp field (`ds_triage`,
`ds_actionable`, `ds_delegated`, `ds_reference`, `ds_archive`) with today's
date. If that field is already set, `alloc` refuses and changes nothing, so an
existing arrival date is never overwritten — handle such an email by hand.

`metadata` reads or writes one field for an email:

```bash
python3 gtd.py metadata <file.eml> get next_action
python3 gtd.py metadata <file.eml> set next_action = "Reply by Friday"
```

Editable fields: `general_notes`, `project`, `next_action`, `flags`. Read-only
(readable but never set here): `message_ref` and the date-stamp columns
`ds_triage`, `ds_actionable`, `ds_delegated`, `ds_reference`, `ds_archive`
(written only by `list`, `alloc`, and `close`).

`metadata_check` reconciles `metadata.csv` with the `.eml` files on disk (adding
rows for any not yet tracked, dropping rows for files that have vanished — the
same sync `list` does), then flags stale references: rows whose `eml_filename`
no longer exists, and rows whose `next_action` mentions an `*.eml` filename that
is not present anywhere in the workflow. It is read-only on the emails
themselves and exits non-zero if anything dangling is found.

`workflow_autofix` reconciles the `ds_*` date-stamps with what the folder layout
and the logical GTD progression imply, writing the corrective stamps only after
you approve the whole batch. It fixes two things: **folder/stamp consistency**
(an email you filed by hand into a folder whose arrival stamp was never written
gets that stamp set to today) and **logical date backfills** (a resolved email
must have been triaged and actioned first, so a missing `ds_triage`/`ds_actionable`
is filled from the earliest resolution date or the listed `ds_actionable`; an
ongoing email in triage/actionable without its stamp is stamped today). It
refuses if `01-input/` is non-empty (run `list` first), lists any email it
cannot resolve automatically (an ongoing email hand-filed somewhere with no
dates to infer) and changes nothing in that case, and — before applying —
prints every proposed stamp and asks once for the whole batch. If you track your
EML dataset with git, consider committing first so the changes are reversible:

```bash
python3 gtd.py workflow_autofix
```

`generate_dashboard` builds a **self-contained HTML dashboard** of your email
response-time performance from the `ds_*` stamps. It reports four metrics in
days — time-to-system (`ttS`, arrival → `ds_triage`), triage duration (`Td`,
`ds_triage` → `ds_actionable`), work duration (`Wd`, `ds_actionable` →
resolution), and total-time-to-resolution (`tttR`, arrival → resolution) —
across the ongoing, resolved, and combined corpora, with headline KPIs (mean,
median, count), box-and-whisker plots, a horizontal stacked bar of each resolved
email's time composition, and a Sankey of the flow from arrival to resolution
(resolved emails flow to their resolution state; ongoing emails flow to an
<em>ongoing</em> node).
The Sankey offers two layout tabs — <em>Fan-out Sankey</em> (the default; the
terminus states spread out vertically so the flows fan out left-to-right into a
&ldquo;&lt;&rdquo; shape) and <em>Straight Sankey</em> (Plotly positions the
nodes automatically); in both, nodes can still be dragged.
It is read-only on the workflow, but refuses (changing nothing) if `01-input/`
is non-empty or if any `workflow_autofix` correction is still outstanding —
pointing you at `workflow_autofix` first, so metadata edits are always
intentional. The charting library is inlined into the output (see
[Dashboard assets](#dashboard-assets)) so the file opens and renders fully
offline. With no output file it writes `<working_directory>/dashboard.html`;
pass a path to write elsewhere:

```bash
python3 gtd.py generate_dashboard
python3 gtd.py generate_dashboard ~/gtd-dashboard.html
```

Emails whose date progression is inconsistent (e.g. triaged before the email's
own date, including from timezone skew) are classified **weird** and excluded
from every metric and chart.

`export` writes every tracked email (the same set `gtd.py list` reports on:
triage, actionable, delegated, reference, archive) to another data format. The
only format so far is `masterdetail_yaml`, a single YAML (`.yml`) document
conforming to the
[master-detail viewer SPEC](https://github.com/blairwang-online/qdvc-masterdetail-viewer/blob/main/SPEC.md)
— a top-level sequence of items, one per email, each a mapping with a `title`
heading (the subject) plus its folder, date, correspondents, and any metadata
(project, next action, notes, flags). With no output file it writes
`<working_directory>/export-masterdetail.yml`; pass a path to write elsewhere:

```bash
python3 gtd.py export masterdetail_yaml
python3 gtd.py export masterdetail_yaml ~/gtd-export.yml
```

Like `search`, it is read-only on the workflow: it reconciles `metadata.csv`
but does not ingest `01-input/` or move any email.

`search` looks through the full report (everything `gtd.py list` prints) for a
string and shows the matching entries, with the matched text highlighted. The
words after `search` are joined into a single query, so it matches the literal
string — spaces, `#`, and `@` included — and the match is case-insensitive:

```bash
python3 gtd.py search project pudding
python3 gtd.py search "#quick"
python3 gtd.py search jane@example.com
```

The highlight is drawn with terminal colour, so it shows on a terminal (or via
`FORCE_COLOR=1 python3 gtd.py search … | less -R`); piping to a plain file
yields clean, un-highlighted text like the rest of the tool.

`close` archives an email and records what closed it. It refuses if the email
is already in `06-archive/`, or if its `ds_archive` date is already set;
otherwise it moves the email there, sets its `next_action` to
`Closed with <other.eml>`, and stamps `ds_archive` with today's date. The
`<other.eml>` you close with must itself exist in the workflow — if it doesn't,
the command errors and nothing is moved or changed:

```bash
python3 gtd.py close 2026-06-03-project-pudding.eml with 2026-06-10-reply.eml
```

`pin` / `unpin` add or remove the `pinned` token in an email's `flags` field:

```bash
python3 gtd.py pin <file.eml>
python3 gtd.py unpin <file.eml>
```

Page through a long report with colours and scrolling:

```bash
FORCE_COLOR=1 python3 gtd.py list | less -R
```

`view` output is markdown-friendly, so it also pipes nicely into
[`glow`](https://github.com/charmbracelet/glow):

```bash
python3 gtd.py view <file.eml> | glow -
```

## Shell completion

If you use **zsh with [oh-my-zsh](https://ohmyz.sh/)**, there's a Tab-completion
script for the `gtd` command (subcommands, `.eml` filenames, metadata fields,
and `alloc` destinations). See
[`misc/shell_completion.md`](misc/shell_completion.md) for setup.

## Configuration

Settings live in `config.yml` next to the scripts:

```yaml
working_directory: "/home/james/gtd-eml-data"   # where the folders + metadata.csv live
archive_report_n: 10            # how many recent archive items to show
green_max_days: 2               # report colour thresholds (age in days)
yellow_max_days: 14
plotly_js_path: "/home/james/gtd-assets/plotly.min.js"   # inlined by generate_dashboard
my_own_accounts:                # your addresses: excluded from "correspondents",
  - email_address: james.smith@example.com   # and labelled when they receive mail
    display_name: "Work account"
    colour: yellow
```

Every key is optional and has a sensible default. The full set:

| Key | Refers to | Default |
| --- | --- | --- |
| `working_directory` | Root holding the six workflow folders + `metadata.csv`. | `./gtd-eml` next to the code |
| `max_filename_chars` | Cap on a generated filename, including `.eml`. | `60` |
| `archive_report_n` | How many most-recent archive items `list` shows. | `10` |
| `green_max_days` / `yellow_max_days` | Age thresholds for the report's green/yellow/red colouring. | `2` / `14` |
| `max_subject_chars` | Subjects longer than this are truncated in the report. | `72` |
| `force_colour` | Always emit ANSI colour (as if piping through `less -R`). | `false` |
| `plotly_js_path` | Local path to the minified Plotly.js bundle that `generate_dashboard` inlines into its HTML output (see [Dashboard assets](#dashboard-assets)). | *(unset)* |
| `my_own_accounts` | Your own addresses: excluded from "correspondents" and labelled when they receive mail. | *(empty)* |

## Dashboard assets

`generate_dashboard` renders its charts with **[Plotly.js](https://plotly.com/javascript/)**,
and inlines the whole bundle into the generated HTML (like Quarto's
`embed-resources: true`) so the file opens and renders with no network access
and no CDN reference. You supply the bundle locally and point `config.yml` at
it; nothing is downloaded at run time.

- **Asset:** the minified Plotly.js distribution bundle — a single JavaScript
  file, `plotly.min.js`. Plotly.js needs no separate CSS file (its styling is
  applied from JavaScript), so this one file is all you need.
- **Upstream:** download it from the official CDN, e.g.
  `https://cdn.plot.ly/plotly-3.7.0.min.js`, or from the
  [`plotly.js-dist-min`](https://www.npmjs.com/package/plotly.js-dist-min) npm
  package. **Always use the minified build.**
- **Version tested against:** **3.7.0**. A nearby 3.x release should work too,
  but 3.7.0 is the version this feature was tested with.
- **Config key:** set `plotly_js_path` to the local path of that file, e.g.
  `plotly_js_path: "/home/james/gtd-assets/plotly.min.js"`.

If `plotly_js_path` is unset or points at a missing file, `generate_dashboard`
errors and does not fall back to a CDN (that would break the offline
guarantee).

## Requirements

- Python 3.8+
- [PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`) — only if you
  use a `config.yml`
- A local Plotly.js bundle — only for `generate_dashboard` (see
  [Dashboard assets](#dashboard-assets)); no runtime download, no other
  third-party Python packages

## Maintainers

See [MAINTENANCE.md](MAINTENANCE.md) for the module layout, dependency graph, and
the conventions to preserve when editing.

## Acknowledgements

This codebase was vibe-coded with assistance from Claude Opus 4.8 High. The full
conversation behind it is preserved in
[`vibe-coding/2026-06-23-conversation-with-claude.md`](vibe-coding/2026-06-23-conversation-with-claude.md).
