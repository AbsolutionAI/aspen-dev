# Paperclip company definitions (BEL-197)

aspen-dev is the **canonical source** for Paperclip company definitions and
org charts (ADR-0001: "aspen-dev is the single source of truth for Paperclip
companies and Hermes personas"). This directory is the reviewable record.
Paperclip's database is the running state.

```
paperclip/
├── README.md                      # this file
└── companies/
    ├── bellahtech/                # BTH — holding company
    │   ├── company.json
    │   └── ORG.md
    ├── aspen-os-development/      # ASP — Aspen OS Development Company
    │   ├── company.json
    │   └── ORG.md
    └── absolution-studios/        # ABS — commercial studio (dormant)
        ├── company.json
        └── ORG.md
```

## What a definition contains

`company.json` (schemaVersion 1) is an **allowlist** export:

| Level | Fields |
|---|---|
| Company | `name`, `issuePrefix`, `description`, `requireBoardApprovalForNewAgents` |
| Agent | `name`, `role`, `title`, `adapterType`, `capabilities` (role brief), `reportsTo` (by name) |
| Project | `name` |

These are **never** exported: adapter/runtime config, environment variables,
API keys or tokens, permissions, budgets and spend, ids, heartbeats, metadata,
working directories, and volatile run state (idle/running/paused). Agents
awaiting hire approval (`pending_approval`) and terminated agents are left out.
The exporter also refuses to write any value shaped like a credential.

`ORG.md` is generated from `company.json`. It holds a mermaid chart plus a
roster table.

## Separation policy

- **Aspen OS Development Company (ASP)** is the engineering company for
  AspenOS. It stays independent of commercial companies: no shared agents,
  budgets or issue prefixes.
- **Absolution Studios (ABS)** and future commercial companies are separate
  Paperclip companies with their own rosters. Agents with the same persona
  name (Ergo, Proxy, Trance, Romi, OpenCode, Aider) are **distinct hires**
  per company.
- **BellahTech (BTH)** is the holding company. Former operating companies
  are tracked there as projects; Linear team **BEL** is the work system of
  record.

## Refreshing from a live Paperclip (read-only)

1. On the Paperclip host, dump with read-only `GET`s into a scratch dir
   **outside** any repo. The raw dumps contain adapter config; never commit
   them.
   - `companies.json` ← `GET /api/companies`
   - `agents-<companyId>.json` ← `GET /api/companies/<companyId>/agents`
   - `projects-<companyId>.json` ← `GET /api/companies/<companyId>/projects`
2. Run `python3 scripts/paperclip_export.py --in <dump> --out paperclip/companies`.
3. Delete the raw dump, review the diff, and open a PR.

`--check` exits 1 when the committed files differ from a dump. Use it for a
drift report.

## Runtime cutover (not done yet)

Today Paperclip's database is still authoritative at runtime. This PR makes
the definitions reviewable here and nothing more. Making runtime **seed from**
this directory is a follow-up that needs the owner's sign-off, because it
changes Paperclip agent configuration and is subject to the pending
CHG-0034 containment work. Until then, any agent or company change made in
Paperclip should be followed by a refresh PR here.

Snapshot: exported 2026-10-18 from the live board (read-only).
