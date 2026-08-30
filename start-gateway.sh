#!/usr/bin/env bash
# 🚀 1-Click Launch Script for OmniRoute + RAG Context Compressor
set -euo pipefail

CYAN="\033[96m"
GREEN="\033[92m"
YELLOW="\033[93m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "\n${CYAN}${BOLD}⚡ Starting OmniRoute + RAG Token Optimizer Gateway...${RESET}"

# Start RAG Compressor on port 8080
python3 rag_compressor.py &
RAG_PID=$!

trap 'kill "$RAG_PID" 2>/dev/null || true' EXIT

echo -e "${GREEN}✔ RAG Token Compressor active on http://127.0.0.1:8080${RESET}"
echo -e "${YELLOW}👉 Point Codex / Cursor / Claude Code to: ${BOLD}http://127.0.0.1:8080/v1${RESET}\n"

wait "$RAG_PID"
