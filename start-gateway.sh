#!/usr/bin/env bash
# 🚀 1-Click Launch Script for OmniRoute + Local Vector RAG Compressor
set -euo pipefail

CYAN="\033[96m"
GREEN="\033[92m"
YELLOW="\033[93m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "\n${CYAN}${BOLD}⚡ Starting Local Vector RAG Compressor & OmniRoute Gateway...${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Run incremental local vector indexer
python3 vector_indexer.py "$HOME/Work" >/dev/null 2>&1 &

# 2. Start OmniRoute Gateway (Port 20128)
if [[ -x "./node_modules/.bin/omniroute" ]]; then
  ./node_modules/.bin/omniroute start >/dev/null 2>&1 &
  OMNI_PID=$!
elif command -v omniroute &>/dev/null; then
  omniroute start >/dev/null 2>&1 &
  OMNI_PID=$!
else
  OMNI_PID=""
fi

# 3. Start RAG Vector Compressor (Port 8080)
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

echo -e "\n${GREEN}${BOLD}🎉 Local RAG Vector Engine Active!${RESET}"
echo -e "  • ${GREEN}⚡ Vector RAG Compressor:${RESET} http://127.0.0.1:8080"
echo -e "  • ${CYAN}🧠 Local Embedding Engine:${RESET} GPU Accelerated (Ollama on RTX 4060)"
echo -e "  • ${YELLOW}👉 Point Codex / Cursor / Claude to:${RESET} ${BOLD}http://127.0.0.1:8080/v1${RESET}\n"

wait "$RAG_PID"
