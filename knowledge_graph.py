#!/usr/bin/env python3
"""
🕸️ Local Entity-Relation Knowledge Graph Memory
Stores subject-predicate-object semantic triples in SQLite.
Enables instant fact retrieval with 0 token waste.
"""

import os
import sqlite3
import time
from typing import List, Tuple, Dict

DB_PATH = os.path.expanduser("~/.local/share/omniroute-rag/knowledge_graph.sqlite")

def init_graph_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS triples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            predicate TEXT,
            object TEXT,
            timestamp REAL,
            UNIQUE(subject, predicate)
        )
    """)
    conn.commit()
    conn.close()

def add_fact(subject: str, predicate: str, obj: str):
    init_graph_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO triples (subject, predicate, object, timestamp)
        VALUES (?, ?, ?, ?)
    """, (subject.strip(), predicate.strip(), obj.strip(), time.time()))
    conn.commit()
    conn.close()

def get_relevant_facts(query: str, limit: int = 5) -> List[Tuple[str, str, str]]:
    init_graph_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    words = [w.lower() for w in query.split() if len(w) > 2]
    if not words:
        cur.execute("SELECT subject, predicate, object FROM triples ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows

    # Search matches in subject, predicate, or object
    placeholders = " OR ".join(["LOWER(subject) LIKE ? OR LOWER(predicate) LIKE ? OR LOWER(object) LIKE ?"] * len(words))
    params = []
    for w in words:
        params.extend([f"%{w}%", f"%{w}%", f"%{w}%"])

    sql = f"SELECT subject, predicate, object FROM triples WHERE {placeholders} LIMIT {limit}"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def format_facts_for_prompt(facts: List[Tuple[str, str, str]]) -> str:
    if not facts:
        return ""
    lines = ["### PERSISTENT KNOWLEDGE GRAPH MEMORY (Verified Facts):"]
    for s, p, o in facts:
        lines.append(f"• {s} -> {p}: {o}")
    return "\n".join(lines)

if __name__ == "__main__":
    init_graph_db()
    # Populate default system & project knowledge triples
    add_fact("Harshith", "environment", "Omarchy Linux with Hyprland Wayland Compositor")
    add_fact("Hardware", "gpu", "NVIDIA GeForce RTX 4060 Laptop GPU")
    add_fact("RAGGateway", "port", "http://127.0.0.1:8080/v1 (Local Token Compressor)")
    add_fact("OmniRoute", "port", "http://127.0.0.1:20128/v1 (Multi-Provider Gateway)")
    add_fact("EmbeddingEngine", "model", "qwen3-embedding:8b on Ollama (Local GPU accelerated)")
    add_fact("CodexCLI", "compact_limit", "12,000 tokens (Auto-compact tuned)")
    
    print("Knowledge Graph initialized with verified system facts:")
    for f in get_relevant_facts(""):
        print(" ", f)
