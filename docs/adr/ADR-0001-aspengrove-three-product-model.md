# ADR-0001: AspenGrove Three-Product Model

**Status:** Accepted  
**Date:** 2026-08-06  
**Linear:** BEL-193

## Context

The Aspen / Starship work had accumulated many packages and Linear tickets. We needed a coherent product boundary that still supports modular installation.

## Decision

AspenGrove is expressed as three products that can be installed together or separately:

1. **AspenOS** — agentic-first OS / control plane (runtime, fleet, edge, self-healing, RTOS bridge)
2. **Aspen Sentinel** — OSINT + HITL command & control workspace
3. **aspen-dev** — development company backend (this repo is canonical)

Package ownership:
- **Core Runtime** ships with AspenOS
- **Optional Plugins** compose into AspenOS or Sentinel
- **Dev-only** packages are owned by aspen-dev and are not required on production edge nodes

## Consequences

- Clear ownership for agents and humans
- aspen-dev is the single source of truth for Paperclip companies and Hermes personas
- Future extraction and packaging decisions follow this classification

## References

- AspenGrove Master Architecture & Product Specification v4.0
- BEL-193 and child issues A1–A6
