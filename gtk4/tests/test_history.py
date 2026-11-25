"""History chains, Set Next Action and drop rules (ported from the macOS
edition's CoreTests.testCloseHistory and testSetNextActionIfBlank), plus the
monorepo checks that keep this app in step with commandline/ and mac/."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from qdvc import folders as F
from qdvc import views
from qdvc.history import CloseHistory, Node, closed_by_note, closing_reference
from qdvc.workspace import GTDError, Workspace

ROOT = Path(__file__).resolve().parents[1]
MONOREPO = ROOT.parent


def node(name, action="", epoch=0, folder="06-archive"):
    return Node(f"{folder}/{name}", name, action, epoch)


class History(unittest.TestCase):
    def test_closing_reference(self):
        self.assertEqual(closing_reference("Closed with b.eml"), "b.eml")
        self.assertEqual(closing_reference("  closed with B.EML, see notes"), "B.EML")
        self.assertEqual(closing_reference("Closed with 2026-09-20-re-contract.eml."),
                         "2026-09-20-re-contract.eml")
        self.assertIsNone(closing_reference("Closed with b.emlx"))
        self.assertIsNone(closing_reference("Closed with Bob on the phone"))
        self.assertIsNone(closing_reference("Check whether it was closed with b.eml"))

    def test_chain_order_and_branches(self):
        # a -> c, b -> c, c -> d (open), plus an unrelated email.
        h = CloseHistory([
            node("b.eml", "Closed with c.eml", 20),
            node("a.eml", "Closed with c.eml", 10),
            node("c.eml", "Closed with D.eml", 30),
            node("d.eml", "Reply to Jane #urgent", 40, "03-actionable"),
            node("e.eml", "", 5, "02-triage"),
        ])
        chain = h.chain("03-actionable/d.eml")
        self.assertEqual([e.filename for e in chain], ["a.eml", "b.eml", "c.eml", "d.eml"])
        self.assertEqual([e.closed_by for e in chain], ["06-archive/c.eml", "06-archive/c.eml",
                                                        "03-actionable/d.eml", None])
        self.assertEqual(h.chain("06-archive/a.eml"), chain)
        self.assertFalse(h.is_in_chain("02-triage/e.eml"))
        self.assertEqual(h.chain("02-triage/e.eml"), [])
        # a was closed with c, which is not the next row: say so.
        self.assertEqual(closed_by_note(chain, chain[0], lambda i: i.split("/")[1]),
                         "Closed with “c.eml”")
        self.assertIsNone(closed_by_note(chain, chain[1], str))
        self.assertIsNone(closed_by_note(chain, chain[3], str))

    def test_missing_self_and_loops(self):
        h = CloseHistory([
            node("x.eml", "Closed with gone.eml"),
            node("y.eml", "Closed with y.eml"),
            node("p.eml", "Closed with q.eml", 2),
            node("q.eml", "Closed with p.eml", 1),
        ])
        missing = h.chain("06-archive/x.eml")
        self.assertEqual([e.filename for e in missing], ["x.eml", "gone.eml"])
        self.assertEqual([e.is_missing for e in missing], [False, True])
        self.assertIsNone(missing[-1].record_id)
        self.assertFalse(h.is_in_chain("06-archive/y.eml"))
        self.assertEqual([e.filename for e in h.chain("06-archive/p.eml")], ["q.eml", "p.eml"])


class NextAction(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ws = Workspace(self.tmp, today=lambda: date(2026, 9, 30))
        self.ws.ensure_folders()
        for subject in ("One", "Two"):
            Path(self.ws.path(F.INPUT, f"{subject}.eml")).write_text(
                f"From: x@example.com\nSubject: {subject}\n"
                "Date: Wed, 30 Sep 2026 09:00:00 +0000\n\nHi\n")
        self.ws.ingest(60)
        self.ws.set_fields("2026-09-30-one.eml", {"next_action": "  "})
        self.ws.set_fields("2026-09-30-two.eml", {"next_action": "Call Bob"})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_set_next_action_if_blank(self):
        self.assertIsNone(self.ws.next_action_refusal("2026-09-30-one.eml"))
        self.ws.set_next_action_if_blank("2026-09-30-one.eml", "#urgent")
        self.assertEqual(self.ws.load_metadata()["2026-09-30-one.eml"]["next_action"], "#urgent")
        with self.assertRaises(GTDError) as cm:
            self.ws.set_next_action_if_blank("2026-09-30-two.eml", "#urgent")
        self.assertIn("already has a next action (Call Bob)", cm.exception.message)
        self.assertEqual(self.ws.load_metadata()["2026-09-30-two.eml"]["next_action"],
                         "Call Bob")
        with self.assertRaises(GTDError):
            self.ws.set_next_action_if_blank("nope.eml", "#urgent")

    def test_drop_and_menu_rules(self):
        class R:
            def __init__(self, folder, action, filename="f.eml"):
                self.folder, self.next_action, self.filename = folder, action, filename
        blank, busy, waiting = R(F.TRIAGE, " "), R(F.TRIAGE, "Call Bob"), R(F.INPUT, "")
        tag = ("tag", "#urgent")
        self.assertIsNone(views.drop_refusal([blank, busy], tag, None, {}))
        self.assertIn("already has a next action: “Call Bob”",
                      views.drop_refusal([busy], tag, None, {}))
        self.assertIn("every one of these emails",
                      views.drop_refusal([busy, busy], tag, None, {}))
        self.assertIn("or is still in Input", views.drop_refusal([busy, waiting], tag, None, {}))
        self.assertEqual(views.drop_refusal([], tag, None, {}), "")
        self.assertEqual(views.drop_refusal([blank], ("folder", "triage"), None, {}), "")
        self.assertIn("Cannot move to Triage: Ingest it first",
                      views.drop_refusal([waiting], ("folder", "triage"), None, {}))
        self.assertEqual(views.tag_menu_title([busy]), "Set Next Action — Already has one")
        self.assertEqual(views.tag_menu_title([waiting]), "Set Next Action — Ingest it first")
        self.assertEqual(views.tag_menu_title([blank, busy]), "Set Next Action")


@unittest.skipUnless((MONOREPO / "commandline" / "gtd_modules").is_dir(),
                     "not inside the qdvc-gtd-eml monorepo")
class Monorepo(unittest.TestCase):
    def test_vendored_core_matches_commandline(self):
        res = subprocess.run([sys.executable, str(ROOT / "tools" / "vendor_core.py"), "--drift"],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)

    @unittest.skipUnless((MONOREPO / "mac").is_dir(), "no mac/ edition here")
    def test_parity_fixture_matches_the_mac_edition(self):
        ours = ROOT / "tests" / "fixtures" / "parity.json"
        theirs = MONOREPO / "mac" / "Tests" / "GTDCoreTests" / "Fixtures" / "parity.json"
        self.assertEqual(ours.read_bytes(), theirs.read_bytes(),
                         "copy mac/Tests/GTDCoreTests/Fixtures/parity.json here")

    def test_one_sample_workspace(self):
        self.assertTrue((MONOREPO / "sample-workspace" / "metadata.csv").is_file())


if __name__ == "__main__":
    unittest.main()
