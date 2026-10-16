#!/usr/bin/env bash
# Creates the eight profiles, installs shared skills and the vault tool, sets up the
# Obsidian vault, and registers the secretary's morning routine. Run from the repo root.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
HERMES="${HERMES_HOME:-$HOME/.hermes}"
VAULT="${HERMES_VAULT:-$HOME/HermesVault}"

declare -A DESC=(
  [orchestrator]="Front door, delegates to specialists"
  [researcher]="Deep research and fact-finding"
  [coder]="Technical/programming work"
  [validator]="MAVF verification, checks other agents' output"
  [secretary]="Daily schedule, one-step goal actions"
  [task-manager]="Long-term goal decomposition"
  [youtube-partner]="YouTube content workflow collaborator"
  [film-partner]="DaVinci Resolve editing collaborator"
)

echo "== Profiles =="
for p in orchestrator researcher coder validator secretary task-manager youtube-partner film-partner; do
  [ -d "$HERMES/profiles/$p" ] || hermes profile create "$p" --description "${DESC[$p]}"
  cp "$REPO/profiles/$p/config.yaml" "$HERMES/profiles/$p/config.yaml"
  cp "$REPO/profiles/$p/SOUL.md"     "$HERMES/profiles/$p/SOUL.md"
done

echo "== Shared skills and vault tool =="
mkdir -p "$HERMES/shared-skills" "$HERMES/tools"
cp -r "$REPO/skills/mavf" "$REPO/skills/obsidian-vault" "$HERMES/shared-skills/"
cp "$REPO/tools/vault_write.py" "$HERMES/tools/vault_write.py"

echo "== Obsidian vault at $VAULT =="
mkdir -p "$VAULT"/{Goals,Schedule,Research,Code,Validation,Content,Editing,Attachments}
cp "$REPO/vault/bases/"*.base "$VAULT/"

echo "== Secretary morning routine =="
if ! secretary cron list 2>/dev/null | grep -q daily-planning; then
  secretary cron create "0 7 * * *" \
    "Read the Goals/ folder in ~/HermesVault (task-manager's steps) and today's calendar. Assign one small, doable step per active goal for today, and log it as a Schedule/ note via vault_write.py, linking to the goal. Keep it to what actually fits in the day - don't overload it. Deliver as a short morning brief." \
    --name daily-planning --skill obsidian-vault --deliver discord
fi
secretary cron list

echo
echo "Next:"
echo "  1. Put your bot tokens in ~/.hermes/profiles/orchestrator/.env (see .env.example),"
echo "     or run: orchestrator gateway setup"
echo "  2. orchestrator gateway install && orchestrator gateway start"
echo "  3. Open $VAULT in Obsidian and enable the Bases core plugin"
echo "  4. Sanity check: setup/check.sh"
