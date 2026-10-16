#!/usr/bin/env bash
# Quick health check across the whole system.
for p in orchestrator researcher coder validator secretary task-manager youtube-partner film-partner; do
  echo "== $p"; $p doctor 2>&1 | grep -E "✗|Profiles|gateway" || true
done
echo "== models";   ollama list
echo "== skills";   ls "${HERMES_HOME:-$HOME/.hermes}/shared-skills"
echo "== cron";     secretary cron list
echo "== gateway";  orchestrator gateway status
echo "== gpu";      rocminfo 2>/dev/null | grep -m1 -o "gfx[0-9]*"
