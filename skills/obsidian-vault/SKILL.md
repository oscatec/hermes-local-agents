---
name: obsidian-vault
description: When and how to persist information to the shared HermesVault Obsidian vault, using the shared vault_write.py tool. Applies to every specialist agent except orchestrator.
---

# Shared Vault

You have access to a shared Obsidian vault at `~/HermesVault`, split into per-agent folders that
can still link to each other. You do not edit vault markdown files by hand — you call the shared
tool:

```
python3 ~/.hermes/tools/vault_write.py create --folder <YourFolder> --title "..." \
  --field key=value [--field key=value ...] --agent <your-profile-name> --body "..."

python3 ~/.hermes/tools/vault_write.py update --folder <YourFolder> --id <id> \
  --field key=value --agent <your-profile-name>
```

The tool enforces the required fields for your folder and refuses malformed writes — if it errors,
fix the call, don't retry with different arguments guessing at what might work.

## When to write

Write to the vault when you produce something that should outlive this conversation:
- task-manager: every goal step it defines, as a `Goals/` note
- secretary: each day's assignments, as a `Schedule/` note
- researcher: any finding worth keeping (not every passing thought), as a `Research/` note
- coder: real decisions or reusable snippets — not every line of chat, as a `Code/` note
- validator: every verdict it issues, as a `Validation/` note, with `target` pointing at what it
  checked (use the target's vault `id` if it has one, so the link is real, not just a description)
- youtube-partner: pipeline stage changes, as a `Content/` note
- film-partner: per-project edit/color decisions, as an `Editing/` note

## When NOT to write

Don't log routine back-and-forth, clarifying questions, or anything that isn't a durable fact/
decision/step. The vault is a working record, not a chat transcript — if you're not sure something
is worth persisting, it probably isn't.

## Linking across agents

Obsidian links use `[[note-title]]` in the body text. When your note relates to another agent's
note (e.g. secretary logging that today's step was "Learn basic color theory"), link to it by title
so the graph actually connects — don't just restate the goal's text.
