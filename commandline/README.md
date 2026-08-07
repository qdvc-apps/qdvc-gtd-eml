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
python3 gtd.py generate_dashboard [dir]   # build a self-contained report website
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

Editable fields: `general_notes`, `project`, `next_action`, `due_date`, `flags`.
`due_date` is the one date column you set yourself — unlike the `ds_*` stamps,
which record what already happened, a due date is an intention about the future.
Use `yyyy-mm-dd`: anything else is stored verbatim but warns, because only an ISO
date can be compared against today (so only an ISO date can show as overdue).
Read-only (readable but never set here): `message_ref` and the date-stamp columns
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
gets that stamp set to today) and **logical date backfills** (a set
`ds_actionable` with a blank `ds_triage` backfills `ds_triage` from it, since
reaching actionable implies having been triaged; a resolved email must have been
triaged and actioned first, so a missing `ds_triage`/`ds_actionable` is filled
from the earliest resolution date; an ongoing email in triage/actionable without
its stamp is stamped today). It
refuses if `01-input/` is non-empty (run `list` first), lists any email it
cannot resolve automatically (an ongoing email hand-filed somewhere with no
dates to infer) and changes nothing in that case, and — before applying —
prints every proposed stamp and asks once for the whole batch. If you track your
EML dataset with git, consider committing first so the changes are reversible:

```bash
python3 gtd.py workflow_autofix
```

`generate_dashboard` builds a **self-contained static website** reporting on your
whole workflow. Open its `index.html` straight from the filesystem — there is no
server to run, and no external resource of any kind is referenced (no CDN, no
webfont, no remote image); the charting library is bundled in.

The site is laid out like an email client: a **sidebar**, a **message list**, and
a **reading pane**. The sidebar is grouped into four categories:

| Category | Entries |
| --- | --- |
| **Overviews** | Dashboard (the whole-workflow summary) and Performance |
| **In & out** | Inbox and Sent — only when `my_own_accounts` is configured |
| **Due & flagged** | Due date set, Due date not set, Pinned |
| **Hashtags** | one view per `monitored_hashtags` entry — only when configured |
| **GTD status** | the six numbered workflow folders, with counts |

**Inbox** is every email one of your own accounts received; **Sent** is every
email one of them sent. In those two views the message list grows a dropdown so
you can narrow to a single account. The **hashtag** views list every email whose
`next_action` contains that tag.

The due-date, pinned and hashtag views share one notion of what is **on your
radar**: by default they cover the input, triage, actionable and delegated
folders and ignore reference and archive, on the grounds that filed-away mail is
off your radar. Settings lets you include or exclude each folder individually.

By default the message list groups mail under **collapsible date headings**:
Today, Yesterday, This week, Last week, Earlier this month, Last month, then each
earlier month of the year by name, then one heading per earlier year. Click a
heading to fold it away, or turn grouping off entirely in Settings for one flat
list. Each row shows the **account it belongs to** in bold, in that account's
configured colour, plus a due-date badge that turns red once the date has passed.

The reading pane leads with the email's pills — its **age** first, colour-coded
like the age dot in the list — then its **annotations** (project, next action,
notes), its `ds_*` workflow trail and metrics, and finally the **full email
history**: the current message plus each quoted or forwarded message below it, as
separate collapsible blocks, *each with its own From/To/Date headers* (and any
attachments) rather than one envelope at the top. There is a search box that covers every folder (including
quoted body text), a sort selector, and an **Overview** that counts what needs
attention: still sitting in input, open longer than 14 days, no next action
recorded, pinned, or an inconsistent date progression. Every figure on the Overview
is clickable — it opens the list of exactly the emails it counted.

A **Settings** dialog (in the toolbar, available on both pages) has two sections
of its own:

| Section | Setting | Options |
| --- | --- | --- |
| Appearance | Mode | **Automatic** (follows the operating system, and keeps following it if you change it), Light, or Dark |
| Appearance | Tone | **Warm** (the default) or **Neutral**, a slightly cooler, greyer cast of the same theme |
| Appearance | Grouping | Whether the message list uses the date headings described above |
| Appearance | Message text / Monospace / Interface fonts | Any CSS font stack you like; leave a field empty to use the built-in one |
| On radar | Folders covered | Which workflow folders the due-date, pinned and hashtag views look at |

Settings are saved in the browser's local storage for this site, and the dialog
has a button to clear them and restore the defaults. If your browser refuses local
storage for local files (some do), the settings still apply for the session — they
just will not persist.

The site also **remembers where you were** in that same storage: the sidebar entry
you had open, the message you had selected in it, and any account filter you had
applied. If any of that no longer resolves when you reopen the site — the email has
been filed elsewhere or deleted, an account has left `config.yml` — the remembered
state is discarded in one piece rather than half-restored, and you land back on the
Dashboard. The mobile build remembers its open tab the same way.

Files still in `01-input` are shown in the **Input** section as *untracked*: they
have no metadata row and no date-stamps until `gtd.py list` ingests them, so they
are excluded from every metric.

The **Performance** section is the response-time dashboard. It reports four
metrics in days — time-to-system (`ttS`, arrival → `ds_triage`), triage duration
(`Td`, `ds_triage` → `ds_actionable`), work duration (`Wd`, `ds_actionable` →
resolution), and total-time-to-resolution (`tttR`, arrival → resolution) — across
the ongoing, resolved, and combined corpora, with headline KPIs (mean, median,
count), box-and-whisker plots, a horizontal stacked bar of each resolved email's
time composition, and a Sankey of the flow from arrival to resolution (resolved
emails flow to their resolution state; ongoing emails flow to an <em>ongoing</em>
node). It also reports on your **open backlog** (how many emails are still open,
their median/oldest age, how many are older than 14&nbsp;days, and the
longest-stalled item), **throughput over time** (arrivals vs resolutions per week
or month, with a running-backlog line that shows whether work is piling up),
**percentiles** (p50/p90/p95, less outlier-skewed than the mean), and a
**resolution hit rate** (share of emails resolved within 1/7/14/30 days). If you
have `my_own_accounts` configured, this section gains an **account filter**: a
dropdown switches every table and chart between &ldquo;All accounts&rdquo; and
each configured account (plus an &ldquo;(unattributed)&rdquo; view for emails that
matched none). The switching is client-side, so the site stays offline.
The Sankey offers two layout tabs — <em>Fan-out Sankey</em> (the default; the
vertical spacing between nodes widens as you move left-to-right, splaying the
flows into a &ldquo;&lt;&rdquo; shape) and <em>Straight Sankey</em> (Plotly
positions the nodes automatically); in both, nodes can still be dragged.

The site is **read-only**, despite looking like a mail client — it is a report,
not a client. Where the interface offers to do something (file an email
elsewhere, set a next action, edit metadata, pin, close), it opens a dialog
containing the command **you** would run in your terminal, ready to copy:

```bash
gtd alloc some-email.eml archive && gtd metadata some-email.eml set next_action = "Print off the report PDF and read it during designated reading hour"
```

Set `cli_command` in `config.yml` if you invoke this tool as something other than
`gtd` (e.g. `python3 gtd.py`) and the snippets will use that instead.

The command itself is read-only on the workflow too, but refuses (changing
nothing, writing nothing) if any `workflow_autofix` correction is still
outstanding — pointing you at `workflow_autofix` first, so metadata edits are
always intentional. Unlike `workflow_autofix`, a non-empty `01-input` does **not**
stop it; the files are simply reported as untracked. The charting library is
copied into the site (see [Dashboard assets](#dashboard-assets)) so everything
renders fully offline. With no argument it writes
`<working_directory>/dashboard/`; pass a path to write elsewhere:

```bash
python3 gtd.py generate_dashboard
python3 gtd.py generate_dashboard ~/gtd-site
```

The output is a folder holding **two builds** of the same report:

```
dashboard/
    index.html            a chooser linking to both builds
    desktop/
        index.html        the mail interface (Dashboard + the folders)
        performance.html  the performance dashboard, in the same chrome
        assets/           stylesheets, scripts, and the bundled plotly.min.js
        data/             your emails + the chart payloads, as .js data files
    mobile/
        gtd-eml.html      the phone interface, as ONE self-contained file
```

Both builds are self-contained. The mobile build is a **single file** with its
styles, scripts and your email data all inlined, so you can mail or AirDrop
`gtd-eml.html` to a phone on its own and open it from local storage — no folder to
copy, no server. The cost is that your email data is written twice (once per
build); see [Dashboard assets](#dashboard-assets) for when that starts to matter.

The **mobile build** is the same report in smartphone-app clothing: a bottom bar
of four tabs (Dashboard, Mail, Radar, Settings), a top bar with a menu, and
content as pages of list items — tap a folder to slide into its messages, tap a
message to slide into it, and use back to come out again. Each tab keeps its own
history, so switching tabs and returning puts you back where you were. It shares
the theme and the settings with the desktop build.

Two things it deliberately leaves out. The **charts**, which need more width than a
phone has (the metric tables are all there). And the **command-building actions**:
a shell snippet is no use on a phone, because there is no terminal to paste it
into, so the mobile build is purely for reading and says so on each message. Use
the desktop build when you want to act on something.

A path ending in `.html` (as earlier versions took) is accepted: the extension is
dropped and that name is used for the folder.

Emails whose date progression is inconsistent — e.g. triaged before the email's
own date (including from timezone skew), or resolution states out of the
delegated → reference → archive order (an archived email later sent to
reference) — are classified **weird** and excluded from every metric and chart.

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
plotly_js_path: "/home/james/gtd-assets/plotly.min.js"   # bundled by generate_dashboard
cli_command: "gtd"              # how the generated site spells this tool
my_own_accounts:                # your addresses: excluded from "correspondents",
  - email_address: james.smith@example.com   # and labelled when they receive mail
    display_name: "Work account"
    colour: yellow
monitored_hashtags:             # tags you write in next_action; each gets its own
  - "#urgent"                   # view in the generated site's sidebar
  - "#family"
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
| `plotly_js_path` | Local path to the minified Plotly.js bundle that `generate_dashboard` copies into the site it builds (see [Dashboard assets](#dashboard-assets)). | *(unset)* |
| `cli_command` | How you invoke this tool, used only in the copy-pasteable commands the generated site shows (e.g. `python3 gtd.py`). | `gtd` |
| `my_own_accounts` | Your own addresses: excluded from "correspondents" and labelled when they receive mail. | *(empty)* |
| `monitored_hashtags` | Tags you use inside `next_action` (e.g. `"#urgent"`). Each gets a view in the generated site's sidebar; matching is a case-insensitive substring, so the leading `#` is simply part of the string. | *(empty)* |

## Dashboard assets

`generate_dashboard` renders its charts with **[Plotly.js](https://plotly.com/javascript/)**,
and copies the whole bundle into the site it builds (as
`assets/plotly.min.js`) so the pages open and render with no network access and
no CDN reference. You supply the bundle locally and point `config.yml` at it;
nothing is downloaded at run time. Only the Performance page loads it, so the
mail interface stays quick despite the bundle's size.

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

Only the desktop build loads Plotly, and only on its Performance page, so the
mobile build ships neither — which is most of why one HTML file can hold the whole
phone app. Your email data (`data/mail.js`) *is* written into both
builds: at a few hundred emails that is a couple of megabytes and not worth a
thought, and it stays comfortable to roughly 10 MB per copy — see the size note in
MAINTENANCE §7 if your corpus is much larger than that.

The bundle's own source text mentions `https://` URLs (map tile styles, a
topojson default, attribution links) for chart types this tool never draws —
`box`, `bar`, `scatter` and `sankey` fetch nothing. Those strings are inert; the
generated pages, stylesheet, scripts and data files contain no external
reference at all.

## Requirements

- Python 3.8+
- [PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`) — only if you
  use a `config.yml`
- A local Plotly.js bundle — only for `generate_dashboard` (see
  [Dashboard assets](#dashboard-assets)); no runtime download, no other
  third-party Python packages
- A reasonably current browser to view the generated site (it uses CSS custom
  properties and CSS grid); JavaScript must be enabled, since the site's data
  ships as `.js` files so that it works over `file://`

## Maintainers

See [MAINTENANCE.md](MAINTENANCE.md) for the module layout, dependency graph, and
the conventions to preserve when editing.

## Acknowledgements

This codebase was vibe-coded with assistance from Claude Opus 4.8 High. The full
conversation behind it is preserved in
[`vibe-coding/2026-06-23-conversation-with-claude.md`](vibe-coding/2026-06-23-conversation-with-claude.md).
