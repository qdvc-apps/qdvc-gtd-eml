"""The history chains made by `close … with …` (a port of the macOS
edition's GTDCore/History.swift, which has the same tests).

An email whose next action is "Closed with <file>.eml" was closed by that
file, which may itself have been closed by another, and so on. Several emails
can be closed with the same one, so a chain can branch; each email is closed
by at most one.

Every email in a chain gets the whole chain, ordered so that each email comes
before the one that closed it (emails closed by the same one in date order),
ending with the latest email. A reference to a file that is not in the
workspace stays in the chain as a missing entry. Pure: no GTK.
"""

import re
from dataclasses import dataclass

MISSING_PREFIX = "missing/"
_CLOSED_WITH = re.compile(r"^\s*closed with\s+(\S+?\.eml)(?=$|[\s,;:.)\]])", re.IGNORECASE)


def closing_reference(next_action):
    """The file named by a "Closed with <file>.eml" next action (as `close`
    writes it, any case, with any text after the name), or None."""
    m = _CLOSED_WITH.match(next_action or "")
    return m.group(1) if m else None


@dataclass(frozen=True)
class Node:
    """What chains are built from: one email."""
    id: str
    filename: str
    next_action: str
    epoch: float        # sorts emails closed by the same one (the Date header)


@dataclass(frozen=True)
class Entry:
    """One email of a chain."""
    id: str             # the record id, or "missing/<file>" for a file not in the workspace
    filename: str
    closed_by: object   # the id of the entry that closed this one (None for the latest)

    @property
    def is_missing(self):
        return self.id.startswith(MISSING_PREFIX)

    @property
    def record_id(self):
        return None if self.is_missing else self.id


class CloseHistory:
    def __init__(self, nodes=()):
        """`nodes` in workflow-folder order: when a name appears in two
        folders, a reference goes to the first, as `find` does."""
        by_name, by_lower = {}, {}
        for n in nodes:
            by_name.setdefault(n.filename, n)
            by_lower.setdefault(n.filename.lower(), n)

        # Each email's closer: an exact name first, then a case-insensitive one.
        closer, filenames, epochs = {}, {}, {}
        for n in nodes:
            filenames[n.id] = n.filename
            epochs[n.id] = n.epoch
            ref = closing_reference(n.next_action)
            if ref is None:
                continue
            target = by_name.get(ref) or by_lower.get(ref.lower())
            if target is not None:
                if target.id != n.id:
                    closer[n.id] = target.id
            else:
                key = MISSING_PREFIX + ref
                closer[n.id] = key
                filenames.setdefault(key, ref)

        # Connected components (union-find over the closing links).
        parent = {}

        def root(k):
            while parent.get(k, k) != k:
                parent[k] = parent.get(parent[k], parent[k])
                k = parent[k]
            return k
        for frm, to in closer.items():
            parent.setdefault(frm, frm)
            parent.setdefault(to, to)
            a, b = root(frm), root(to)
            if a != b:
                parent[a] = b
        components = {}
        for k in parent:
            components.setdefault(root(k), []).append(k)
        closed_with = {}
        for frm, to in closer.items():
            closed_with.setdefault(to, []).append(frm)

        def order_key(k):
            return (epochs.get(k, float("inf")), k)

        self._chains = {}
        for members in components.values():
            if len(members) < 2:
                continue
            order, seen = [], set()

            def visit(k):
                # Iterative depth-first: earlier emails, then the one that closed them.
                stack = [(k, False)]
                while stack:
                    node, done = stack.pop()
                    if done:
                        order.append(node)
                        continue
                    if node in seen:
                        continue
                    seen.add(node)
                    stack.append((node, True))
                    for earlier in sorted(closed_with.get(node, []), key=order_key, reverse=True):
                        stack.append((earlier, False))
            for head in sorted((m for m in members if m not in closer), key=order_key):
                visit(head)
            # A chain has one latest email unless the links go round in a loop.
            order += sorted((m for m in members if m not in seen), key=order_key)
            entries = [Entry(k, filenames.get(k, k), closer.get(k)) for k in order]
            for k in order:
                if not k.startswith(MISSING_PREFIX):
                    self._chains[k] = entries

    @classmethod
    def from_records(cls, records):
        return cls([Node(r.id, r.filename, r.next_action, r.date.timestamp()) for r in records])

    def chain(self, rid):
        """The chain the email belongs to (empty when it is in none)."""
        return self._chains.get(rid, [])

    def is_in_chain(self, rid):
        return rid in self._chains


def closed_by_note(chain, entry, title_of):
    """Where a chain branches, which email closed this one (it is not simply
    the next in the list): "Closed with “…”". `title_of(id)` names an entry."""
    if entry.closed_by is None:
        return None
    i = chain.index(entry)
    if i + 1 < len(chain) and chain[i + 1].id == entry.closed_by:
        return None
    return f"Closed with “{title_of(entry.closed_by)}”"
