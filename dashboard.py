#!/usr/bin/env python3
"""
📊 OmniRoute RAG & Token Shield Live Terminal Dashboard
Shows real-time model execution, stored embedding counts, token savings, and quota efficiency.
"""

import os
import sys
import time
import sqlite3
from telemetry import get_aggregate_stats, DB_PATH

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def render_gauge(pct: float, width: int = 24) -> str:
    filled = int((pct / 100.0) * width)
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    return f"{GREEN}{bar}{RESET} {BOLD}{pct:.1f}%{RESET}"

def render_dashboard():
    stats = get_aggregate_stats()

    print("\033[2J\033[H", end="") # Clear screen
    print(f"{CYAN}{BOLD}")
    print("  ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ ")
    print("  ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗")
    print("  ██║  ██║███████║███████╗███████║██████╔╝██║   ██║███████║██████╔╝██║  ██║")
    print("  ██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║")
    print("  ██████╔╝██║  ██║███████║██║  ██║██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝")
    print("  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ")
    print(f"      ⚡ REAL-TIME AI TOKEN EFFICIENCY & RAG OBSERVABILITY ENGINE{RESET}\n")

    print(f"  ┌─────────────────────────────────┬─────────────────────────────────┐")
    print(f"  │ {BOLD}MODEL & RETRIEVAL VITALS{RESET}        │ {BOLD}QUOTA SAVINGS & EFFICIENCY{RESET}      │")
    print(f"  ├─────────────────────────────────┼─────────────────────────────────┤")
    print(f"  │ • Active Model:  {CYAN}{BOLD}{stats['last_indexer_model']:<14}{RESET}│ • Total Requests: {YELLOW}{stats['total_requests']:<13}{RESET}│")
    print(f"  │ • Embeddings:    {GREEN}{BOLD}{stats['total_embeddings_stored']:<4} chunks{RESET}     │ • Tokens Before:  {MAGENTA}{stats['total_tokens_before']:,}{RESET}")
    print(f"  │ • Indexed Files: {GREEN}{stats['last_indexed_files']} workspace files{RESET} │ • Tokens After:   {GREEN}{BOLD}{stats['total_tokens_after']:,}{RESET}")
    print(f"  │ • Embed Latency: {CYAN}{stats['avg_latency_ms']:.1f} ms (GPU){RESET}      │ • Tokens Saved:   {GREEN}{BOLD}{stats['total_tokens_saved']:,}{RESET}")
    print(f"  │ • Hardware:      {BOLD}NVIDIA RTX 4060{RESET} │ • Quota Saved:    {render_gauge(stats['avg_savings_pct'])}")
    print(f"  └─────────────────────────────────┴─────────────────────────────────┘")

    # Fetch recent requests
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT timestamp, model_name, tokens_before, tokens_after, tokens_saved, savings_pct, latency_ms
                FROM requests ORDER BY id DESC LIMIT 5
            """)
            rows = cur.fetchall()
            conn.close()

            if rows:
                print(f"\n  {BOLD}📜 Recent RAG Compression Requests:{RESET}")
                print(f"  {DIM}Timestamp          Model              Before     After     Saved      Savings   Latency{RESET}")
                print(f"  {DIM}──────────────────────────────────────────────────────────────────────────────────{RESET}")
                for ts, m_name, b, a, s, pct, lat in rows:
                    t_str = time.strftime("%H:%M:%S", time.localtime(ts))
                    print(f"  {t_str}           {CYAN}{m_name:<18}{RESET} {b:<10,} {a:<9,} {GREEN}{s:<10,}{RESET} {GREEN}{pct:5.1f}%{RESET}    {CYAN}{lat:.1f}ms{RESET}")
        except Exception:
            pass

    print(f"\n  {DIM}Press Ctrl+C to exit dashboard • Live updates every 2s{RESET}\n")

def main():
    try:
        while True:
            render_dashboard()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting dashboard.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        render_dashboard()
    else:
        main()
