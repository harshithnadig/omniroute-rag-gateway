#!/usr/bin/env bash
# 🚀 1-Click Launch Script for OmniRoute + RAG Context Compressor
set -euo pipefail

CYAN="\033[96m"
GREEN="\033[92m"
YELLOW="\033[93m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "\n${CYAN}${BOLD}⚡ Starting OmniRoute Multi-Provider Gateway & RAG Token Compressor...${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Start OmniRoute Gateway (Port 20128)
if [[ -x "./node_modules/.bin/omniroute" ]]; then
  ./node_modules/.bin/omniroute start &
  OMNI_PID=$!
elif command -v omniroute &>/dev/null; then
  omniroute start &
  OMNI_PID=$!
else
  echo -e "${YELLOW}▲ OmniRoute binary not found, running RAG compressor in direct proxy mode.${RESET}"
  OMNI_PID=""
fi

# 2. Start RAG Compressor (Port 8080)
python3 rag_compressor.py &
RAG_PID=$!

cleanup() {
  echo -e "\n${YELLOW}Stopping gateway services...${RESET}"
  kill "$RAG_PID" 2>/dev/null || true
  if [[ -n "${OMNI_PID:-}" ]]; then
    kill "$OMNI_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo -e "\n${GREEN}${BOLD}🎉 Gateway Stack Active & Ready!${RESET}"
echo -e "  • ${CYAN}🔀 OmniRoute Provider Gateway:${RESET} http://127.0.0.1:20128"
echo -e "  • ${GREEN}⚡ RAG Token Compressor Proxy:${RESET} http://127.0.0.1:8080"
echo -e "\n${YELLOW}👉 Point Codex / Cursor / Claude Code to:${RESET} ${BOLD}http://127.0.0.1:8080/v1${RESET}\n"

wait "$RAG_PID"
