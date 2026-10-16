#!/usr/bin/env bash
# Pulls the two model tiers and builds the long-context variants the profiles use.
set -euo pipefail

echo "== Base models =="
ollama pull qwen3.5:9b     # fast tier: orchestrator, secretary, task-manager
ollama pull qwen3.6:27b    # heavy tier: researcher, coder, validator, youtube-partner, film-partner

# Ollama defaults to a short context window. Agent work (tool schemas, skills, delegated results)
# needs far more, so each tier gets a variant with a larger num_ctx.
echo "== Long-context variants =="
tmp=$(mktemp -d)
printf 'FROM qwen3.5:9b\nPARAMETER num_ctx 65536\n'   > "$tmp/fast"
printf 'FROM qwen3.6:27b\nPARAMETER num_ctx 131072\n' > "$tmp/heavy"
ollama create qwen3.5:9b-64k   -f "$tmp/fast"
ollama create qwen3.6:27b-128k -f "$tmp/heavy"
rm -rf "$tmp"

ollama list
echo
echo "Optional, if heavy-tier reloads get slow (add to the ollama systemd override):"
echo "  OLLAMA_MAX_LOADED_MODELS=2"
echo "  OLLAMA_KEEP_ALIVE=10m"
