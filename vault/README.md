# Shared Obsidian vault

One vault, one folder per agent, so notes can link across agents (a Goal note links to the
Schedule entry that acted on it, a Research note links to the Validation note that checked it,
etc). Obsidian's **Bases** feature (core plugin, no separate database, no external API) just reads
YAML frontmatter off these notes and renders filtered table/card views — the ".base" files here
are those saved views, one per folder.

## Structure

```
~/HermesVault/
├── Goals/          (task-manager)   — long-term goal steps
├── Schedule/       (secretary)      — daily logs / what got assigned each day
├── Research/       (researcher)     — findings with sources
├── Code/           (coder)          — technical decisions, snippets, notes worth keeping
├── Validation/     (validator)      — verdict logs (approved/rejected + why)
├── Content/        (youtube-partner)— video pipeline notes
├── Editing/        (film-partner)   — per-project edit/color notes
├── Attachments/    (shared, images/misc)
└── *.base          (one view per folder, at vault root — see bases/)
```

## How notes get created — not by agents editing markdown by hand

Every agent writes notes through one shared script, `tools/vault_write.py` (calling convention in
`skills/obsidian-vault/SKILL.md`), instead of writing YAML frontmatter by hand. The script:

- enforces the frontmatter schema per folder (see below) so nothing malformed lands in the vault
- auto-fills `id`, `created`, `updated`
- updates an existing note in place (matched by `id` or title-slug) instead of creating duplicates
  when an agent revisits something (e.g. task-manager updating a goal's status)

## Frontmatter schema per folder

**Goals/** — `id, created, updated, agent, goal, status[not-started|in-progress|blocked|done], priority[low|med|high], blocked_by[list of ids]`

**Schedule/** — `id, created, updated, agent, date, goal_links[list of ids], completed[bool]`

**Research/** — `id, created, updated, agent, topic, sources[list of urls], confidence[low|med|high], status[draft|verified|rejected]`

**Code/** — `id, created, updated, agent, project, language, status[note|decision|snippet]`

**Validation/** — `id, created, updated, agent, verdict[approved|approved_with_notes|rejected], target[link/id of the note being checked], reasons`

**Content/** — `id, created, updated, agent, title, stage[idea|script|filmed|edited|thumbnail|published]`

**Editing/** — `id, created, updated, agent, project, stage, resolve_page[edit|color|fusion|fairlight]`

All folders also accept a free `tags` list for cross-cutting search.

## Setup

`setup/03-configure.sh` creates the folders, copies the `.base` views to the vault root, and installs
the script and skill. Then open the vault in Obsidian and enable the **Bases** core plugin
(Settings → Core plugins → Bases).
