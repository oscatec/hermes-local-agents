---
name: mavf
description: Multi-Agent Verification Framework - when and how the orchestrator routes work through validator before it reaches the user.
---

# MAVF (Multi-Agent Verification Framework)

Shared by orchestrator and validator. Installed once in `~/.hermes/shared-skills/mavf/`, which
every profile loads through `skills.external_dirs`.

## What triggers a validator pass

Route output through validator when ANY of these are true:

1. **Explicit flag** - user says "this is important", "double check this", "make sure this is
   right", or similar.
2. **Deep research** - researcher was invoked with more than a single quick lookup (multi-source
   synthesis, comparison, anything that took several searches).
3. **Irreversible or externally-visible action** - code that will be run against real
   data/production, anything getting published/sent/posted, financial or scheduling commitments
   with real consequences.
4. **Coder output with no test run yet** - if coder claims something works but hasn't actually
   executed it.

Do NOT route through validator for:
- Daily scheduling from secretary (low stakes, easily corrected, and gating it adds friction to
  something meant to be fast)
- Casual brainstorming from youtube-partner / film-partner (creative ideation isn't a correctness
  claim)
- task-manager's goal breakdowns (same - low stakes, cheap to revise)

If unsure, the orchestrator should lean toward NOT triggering it - MAVF exists to catch real risk,
not to slow down every interaction. Over-triggering trains the user to route around the whole
system.

## The loop itself (orchestrator's job)

1. Send validator the specialist's output PLUS whatever evidence handles it claimed (paths, URLs,
   test output).
2. Validator returns APPROVED / APPROVED WITH NOTES / REJECTED (see validator's SOUL.md).
3. APPROVED / APPROVED WITH NOTES -> deliver to user, include notes if any.
4. REJECTED -> send validator's specific reasons back to the originating specialist for one
   revision pass, then re-validate. After 2 failed rounds, stop looping - surface the disagreement
   to the user directly rather than silently retrying forever.

## Why this is a skill file and not just orchestrator's SOUL.md

Both orchestrator (which triggers it) and validator (which executes it) need the same
understanding of the rules, so they live once in the shared skills directory rather than being
duplicated, and drifting, across two SOUL.md files.

## Logging
Validator records every verdict as a `Validation/` note through the `obsidian-vault` skill, with
`target` set to the vault id of the note it checked, so each research finding links to the check
that approved or rejected it.
