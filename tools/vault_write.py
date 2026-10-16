#!/usr/bin/env python3
"""
vault_write.py — the shared tool every Hermes agent uses to populate the shared Obsidian vault.
No new agent needed; this is a plain script any profile with terminal access can call.

Usage:
  python3 vault_write.py create --folder Goals --title "Learn basic color theory" \
      --field goal="DaVinci mastery" --field status=not-started --field priority=med \
      --agent task-manager --body "First step toward the color grading goal."

  python3 vault_write.py update --folder Goals --id <id-from-create> \
      --field status=in-progress --agent task-manager

Design choices:
  - No third-party deps (no pyyaml) — hand-rolled minimal YAML frontmatter writer, since only
    strings/lists/bools/numbers are needed for this schema. Keeps it portable across any Python3.
  - "update" matches by --id if given, else by title-slug within the folder, and only rewrites the
    fields you pass — everything else in the note, including list fields, is left alone.
  - Always sets/refreshes `updated`; `created` is only set once, on first creation.
"""
import argparse, os, re, sys, uuid
from datetime import datetime, timezone

VAULT_ROOT = os.path.expanduser(os.environ.get("HERMES_VAULT", "~/HermesVault"))

REQUIRED_FIELDS = {
    "Goals": {"goal", "status", "priority"},
    "Schedule": {"date"},
    "Research": {"topic"},
    "Code": {"project", "status"},
    "Validation": {"verdict", "target"},
    "Content": {"title", "stage"},
    "Editing": {"project", "stage"},
}

def slugify(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return text[:60] or "untitled"

def yaml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        if not v:
            return "[]"
        return "\n" + "\n".join(f"  - {yaml_scalar(x)}" for x in v)
    return yaml_scalar(v)

def yaml_scalar(v):
    s = str(v)
    if re.match(r"^-?\d+(\.\d+)?$", s) or s in ("true", "false"):
        return s
    if any(c in s for c in [":", "#", '"', "'"]) or s.strip() != s:
        return '"' + s.replace('"', '\\"') + '"'
    return s

def write_frontmatter(fields):
    lines = ["---"]
    for k, v in fields.items():
        val = yaml_value(v)
        if val.startswith("\n"):
            lines.append(f"{k}:{val}")
        else:
            lines.append(f"{k}: {val}")
    lines.append("---")
    return "\n".join(lines)

def parse_note(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fields, last_key = {}, None
    for line in fm_text.splitlines():
        if line.startswith("  - ") and last_key is not None:
            # list item belonging to the previous key (e.g. blocked_by, sources)
            if not isinstance(fields[last_key], list):
                fields[last_key] = []
            fields[last_key].append(line[4:].strip().strip('"'))
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            last_key = k.strip()
            v = v.strip()
            fields[last_key] = [] if v == "[]" else v.strip('"').replace('\\"', '"')
    return fields, body

def find_existing(folder_path, note_id, title_slug):
    if not os.path.isdir(folder_path):
        return None
    for fname in os.listdir(folder_path):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(folder_path, fname)
        fields, _ = parse_note(fpath)
        if note_id and fields.get("id") == note_id:
            return fpath
        if not note_id and fname == f"{title_slug}.md":
            return fpath
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["create", "update"])
    ap.add_argument("--folder", required=True, choices=list(REQUIRED_FIELDS.keys()))
    ap.add_argument("--title")
    ap.add_argument("--id")
    ap.add_argument("--agent", required=True)
    ap.add_argument("--field", action="append", default=[], help="key=value, repeatable")
    ap.add_argument("--body", default="")
    args = ap.parse_args()

    folder_path = os.path.join(VAULT_ROOT, args.folder)
    os.makedirs(folder_path, exist_ok=True)

    new_fields = {}
    for f in args.field:
        if "=" not in f:
            sys.exit(f"--field must be key=value, got: {f}")
        k, _, v = f.partition("=")
        if "," in v:
            v = [x.strip() for x in v.split(",")]
        new_fields[k.strip()] = v

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    title_slug = slugify(args.title or new_fields.get("goal") or new_fields.get("topic") or "note")

    existing_path = find_existing(folder_path, args.id, title_slug)

    if args.mode == "create":
        if existing_path:
            sys.exit(f"A note matching this already exists at {existing_path} — use 'update' instead.")
        missing = REQUIRED_FIELDS[args.folder] - set(new_fields.keys())
        if missing:
            sys.exit(f"Missing required fields for {args.folder}: {', '.join(sorted(missing))}")
        fields = {
            "id": str(uuid.uuid4())[:8],
            "created": now,
            "updated": now,
            "agent": args.agent,
            **new_fields,
        }
        if args.title:
            fields["title"] = args.title
        path = os.path.join(folder_path, f"{title_slug}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(write_frontmatter(fields) + "\n\n" + args.body + "\n")
        print(f"Created: {path} (id={fields['id']})")

    else:  # update
        if not existing_path:
            sys.exit("No matching note found to update — pass --id, or a --title that matches an existing note.")
        old_fields, old_body = parse_note(existing_path)
        old_fields.update(new_fields)
        old_fields["updated"] = now
        old_fields["agent"] = args.agent
        body = args.body if args.body else old_body
        with open(existing_path, "w", encoding="utf-8") as fh:
            fh.write(write_frontmatter(old_fields) + "\n\n" + body.strip() + "\n")
        print(f"Updated: {existing_path}")

if __name__ == "__main__":
    main()
