"""BEL-197: sanitized Paperclip company export (stdlib unittest)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import paperclip_export as pe  # noqa: E402

FAKE_SECRET = "ghp_" + "A" * 36  # credential-shaped, never real

COMPANY = {
    "id": "c1", "name": "Example Dev Company", "issuePrefix": "EXD",
    "description": "Builds things.", "requireBoardApprovalForNewAgents": True,
    "budgetMonthlyCents": 5000, "spentMonthlyCents": 1234,
    "defaultResponsibleUserId": "u-1",
}
AGENTS = [
    {"id": "a1", "name": "Lead", "role": "ceo", "title": "Lead", "status": "idle",
     "adapterType": "hermes_local", "reportsTo": None, "capabilities": "Leads.",
     "adapterConfig": {"env": {"GITHUB_TOKEN": FAKE_SECRET}, "cwd": "/home/x"},
     "runtimeConfig": {"heartbeat": {"maxConcurrentRuns": 2}},
     "permissions": {"canCreateAgents": True}, "budgetMonthlyCents": 1000,
     "metadata": {"note": "internal"}},
    {"id": "a2", "name": "Coder", "role": "engineer", "title": "Coder",
     "status": "paused", "adapterType": "opencode_local", "reportsTo": "a1",
     "capabilities": None, "adapterConfig": {"apiKey": FAKE_SECRET}},
    {"id": "a3", "name": "Candidate", "role": "general", "title": "Pending hire",
     "status": "pending_approval", "adapterType": "claude_local", "reportsTo": "a1"},
    {"id": "a4", "name": "Gone", "role": "general", "title": "Old",
     "status": "terminated", "adapterType": "hermes_local", "reportsTo": "a1"},
]
PROJECTS = [{"id": "p1", "name": "Widget", "status": "in_progress",
             "description": "local path /home/x/widget", "workspaces": []}]


def _dump(tmp: Path, agents=AGENTS) -> Path:
    d = tmp / "dump"
    d.mkdir()
    (d / "companies.json").write_text(json.dumps([COMPANY]))
    (d / "agents-c1.json").write_text(json.dumps(agents))
    (d / "projects-c1.json").write_text(json.dumps(PROJECTS))
    return d


class ExportTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_allowlist_only(self):
        files = pe.export(_dump(self.tmp))
        self.assertEqual(list(files), ["example-dev"])
        text = files["example-dev"]["company.json"]
        defn = json.loads(text)
        self.assertEqual(set(defn), {"schemaVersion", *pe.COMPANY_FIELDS, "agents", "projects"})
        for agent in defn["agents"]:
            self.assertEqual(set(agent), {*pe.AGENT_FIELDS, "reportsTo"})
        self.assertEqual(defn["projects"], [{"name": "Widget"}])
        for forbidden in (FAKE_SECRET, "adapterConfig", "runtimeConfig", "permissions",
                          "budgetMonthlyCents", "spentMonthlyCents", "/home/x", "metadata",
                          '"id"', "u-1"):
            self.assertNotIn(forbidden, text)
            self.assertNotIn(forbidden, files["example-dev"]["ORG.md"])

    def test_pending_and_terminated_excluded_and_reports_to_by_name(self):
        defn = json.loads(pe.export(_dump(self.tmp))["example-dev"]["company.json"])
        names = [a["name"] for a in defn["agents"]]
        self.assertEqual(names, ["Lead", "Coder"])
        self.assertEqual(defn["agents"][1]["reportsTo"], "Lead")
        self.assertIsNone(defn["agents"][0]["reportsTo"])

    def test_refuses_credential_shaped_free_text(self):
        bad = [dict(AGENTS[0], capabilities=f"use {FAKE_SECRET}")]
        with self.assertRaises(pe.SecretShapeError):
            pe.export(_dump(self.tmp, agents=bad))

    def test_org_md_has_mermaid_edges(self):
        org = pe.export(_dump(self.tmp))["example-dev"]["ORG.md"]
        self.assertIn("```mermaid", org)
        self.assertIn("n_Lead --> n_Coder", org)

    def test_cli_write_then_check(self):
        dump = _dump(self.tmp)
        out = self.tmp / "out"
        cli = [sys.executable, str(ROOT / "scripts" / "paperclip_export.py"),
               "--in", str(dump), "--out", str(out)]
        self.assertEqual(subprocess.run(cli, capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run(cli + ["--check"], capture_output=True).returncode, 0)
        (out / "example-dev" / "ORG.md").write_text("edited\n")
        self.assertEqual(subprocess.run(cli + ["--check"], capture_output=True).returncode, 1)


class CommittedDefinitionsTests(unittest.TestCase):
    """The committed snapshot obeys the same allowlist and is regenerable."""

    def test_committed_companies_are_allowlisted_and_clean(self):
        companies = sorted((ROOT / "paperclip" / "companies").glob("*/company.json"))
        self.assertTrue(companies, "expected committed company definitions")
        for path in companies:
            defn = json.loads(path.read_text())
            self.assertEqual(defn["schemaVersion"], pe.SCHEMA_VERSION)
            self.assertEqual(set(defn), {"schemaVersion", *pe.COMPANY_FIELDS, "agents", "projects"})
            for a in defn["agents"]:
                self.assertEqual(set(a), {*pe.AGENT_FIELDS, "reportsTo"})
            pe._assert_clean(defn, str(path))
            # ORG.md is exactly what the renderer produces from company.json.
            self.assertEqual((path.parent / "ORG.md").read_text(), pe.render_org(defn))
            names = {a["name"] for a in defn["agents"]}
            for a in defn["agents"]:
                self.assertTrue(a["reportsTo"] is None or a["reportsTo"] in names)


if __name__ == "__main__":
    unittest.main()
