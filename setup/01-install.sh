#!/usr/bin/env bash
# Installs ROCm (if missing), Ollama and Hermes Agent on Ubuntu/Kubuntu. Safe to re-run.
set -euo pipefail

echo "== 1. Prereqs =="
sudo apt update
sudo apt install -y git curl xz-utils

echo "== 2. Check ROCm sees the GPU (RX 7900 XTX = gfx1100) =="
if ! command -v rocminfo >/dev/null 2>&1; then
  echo "ROCm not found. Installing (this is the AMD-official installer path for Ubuntu)."
  echo "NOTE: package name / version may have moved since this script was written —"
  echo "if this 404s, check https://rocm.docs.amd.com/projects/install-on-linux for the current one."
  wget -q https://repo.radeon.com/amdgpu-install/latest/ubuntu/noble/amdgpu-install_6.2.60204-1_all.deb -O /tmp/amdgpu-install.deb || {
    echo "Download failed — fetch the current .deb manually from the ROCm docs link above."; exit 1;
  }
  sudo apt install -y /tmp/amdgpu-install.deb
  sudo amdgpu-install -y --usecase=rocm
  echo "You likely need to add your user to the render/video groups and reboot:"
  echo "  sudo usermod -aG render,video \$USER"
  echo "Then reboot before continuing."
else
  echo "rocminfo already present."
fi
rocminfo | grep -i "gfx" || echo "WARNING: couldn't confirm gfx target — check rocminfo output manually."

echo "== 3. Install Ollama (ROCm-enabled build) =="
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "Ollama already installed."
fi
# Ollama auto-detects ROCm on Linux if the driver is present. Verify after install with:
#   ollama run qwen3.5:4b "say hi"  and watch `rocm-smi` or `radeontop` for GPU usage.

echo "== 4. Install Hermes Agent =="
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

echo "== 5. Make sure ~/.local/bin is on PATH =="
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  echo "Added ~/.local/bin to PATH in ~/.bashrc — restart your shell or 'source ~/.bashrc'."
fi

echo "== Done. Next: setup/02-ollama-models.sh =="
