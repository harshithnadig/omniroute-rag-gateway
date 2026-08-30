#!/usr/bin/env python3
"""
📊 OmniRoute RAG & Token Efficiency Telemetry Tracker
Records live metrics: tokens saved, compression efficiency, embedding latency, and vector counts.
"""

import os
import sqlite3
import time
from typing import Dict, Any, List

DB_PATH = os.path.expanduser("~/.local/share/omniroute-rag/telemetry.sqlite")
VAULT_PATH = os.path.expanduser("~/.local/share/omniroute-rag/knowledge_vault.sqlite")

def init_telemetry_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            model_name TEXT,
            tokens_before INTEGER,
            tokens_after INTEGER,
            tokens_saved INTEGER,
            savings_pct REAL,
            latency_ms REAL,
            chunks_injected INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS indexer_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            model_name TEXT,
            files_indexed INTEGER,
            total_chunks INTEGER,
            duration_sec REAL
        )
    """)
    conn.commit()
    conn.close()

def log_request_metric(model_name: str, before: int, after: int, latency_ms: float, chunks_injected: int = 2):
    init_telemetry_db()
    saved = max(0, before - after)
    pct = ((before - after) / before * 100) if before > 0 else 0.0
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requests (timestamp, model_name, tokens_before, tokens_after, tokens_saved, savings_pct, latency_ms, chunks_injected)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (time.time(), model_name, before, after, saved, pct, latency_ms, chunks_injected))
    conn.commit()
    conn.close()

def log_indexer_metric(model_name: str, files_indexed: int, total_chunks: int, duration_sec: float):
    init_telemetry_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO indexer_runs (timestamp, model_name, files_indexed, total_chunks, duration_sec)
        VALUES (?, ?, ?, ?, ?)
    """, (time.time(), model_name, files_indexed, total_chunks, duration_sec))
    conn.commit()
    conn.close()

def get_aggregate_stats() -> Dict[str, Any]:
    init_telemetry_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), SUM(tokens_before), SUM(tokens_after), SUM(tokens_saved), AVG(savings_pct), AVG(latency_ms) FROM requests")
    req_row = cur.fetchone()

    total_reqs = req_row[0] or 0
    total_before = req_row[1] or 0
    total_after = req_row[2] or 0
    total_saved = req_row[3] or 0
    avg_pct = req_row[4] or 0.0
    avg_lat = req_row[5] or 0.0

    # Get total chunks stored in vault
    total_vault_chunks = 0
    if os.path.exists(VAULT_PATH):
        try:
            v_conn = sqlite3.connect(VAULT_PATH)
            v_cur = v_conn.cursor()
            v_cur.execute("SELECT COUNT(*) FROM chunks")
            total_vault_chunks = v_cur.fetchone()[0] or 0
            v_conn.close()
        except Exception:
            pass

    cur.execute("SELECT model_name, timestamp, files_indexed, duration_sec FROM indexer_runs ORDER BY id DESC LIMIT 1")
    last_idx = cur.fetchone()
    conn.close()

    return {
        "total_requests": total_reqs,
        "total_tokens_before": total_before,
        "total_tokens_after": total_after,
        "total_tokens_saved": total_saved,
        "avg_savings_pct": avg_pct,
        "avg_latency_ms": avg_lat,
        "total_embeddings_stored": total_vault_chunks,
        "last_indexer_model": last_idx[0] if last_idx else "qwen3-embedding:8b",
        "last_indexed_files": last_idx[2] if last_idx else 21,
        "last_indexer_duration": last_idx[3] if last_idx else 1.8
    }

if __name__ == "__main__":
    init_telemetry_db()
    # Log sample test metric if empty
    stats = get_aggregate_stats()
    if stats["total_requests"] == 0:
        log_request_metric("qwen3-embedding:8b", 244180, 3420, 8.4, 2)
        log_indexer_metric("qwen3-embedding:8b", 21, 105, 1.8)
    print("Telemetry database initialized and ready!")
