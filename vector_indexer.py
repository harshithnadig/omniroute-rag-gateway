#!/usr/bin/env python3
"""
🧠 Continuous Local Vector Indexer & Knowledge Vault
Uses local embedding models via Ollama on NVIDIA RTX 4060 to index workspace files incrementally.
"""

import os
import sys
import json
import sqlite3
import hashlib
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any

DB_PATH = os.path.expanduser("~/.local/share/omniroute-rag/knowledge_vault.sqlite")
OLLAMA_URL = "http://127.0.0.1:11434/api/embeddings"
MODEL_NAME = "qwen3-embedding:8b"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_hashes (
            filepath TEXT PRIMARY KEY,
            mtime REAL,
            sha256 TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT,
            chunk_index INTEGER,
            content TEXT,
            embedding TEXT
        )
    """)
    conn.commit()
    return conn

def get_embedding(text: str) -> List[float]:
    req_data = json.dumps({"model": MODEL_NAME, "prompt": text[:2000]}).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("embedding", [])
    except Exception as e:
        return []

def file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def index_directory(directory: str, max_files: int = 50):
    conn = init_db()
    cur = conn.cursor()
    
    indexed_count = 0
    skipped_count = 0

    print(f"\n{CYAN}{BOLD}🧠 Scanning workspace for incremental indexing: {directory}{RESET}")
    
    ignore_dirs = {".git", "node_modules", "target", "dist", "build", "__pycache__", ".venv", ".tmp"}
    valid_exts = {".py", ".sh", ".qml", ".js", ".ts", ".rs", ".md", ".json", ".toml", ".yaml", ".yml"}

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext not in valid_exts:
                continue

            full_path = os.path.join(root, f)
            try:
                stat = os.stat(full_path)
                if stat.st_size > 100000: # Skip files > 100KB
                    continue

                cur.execute("SELECT mtime, sha256 FROM file_hashes WHERE filepath = ?", (full_path,))
                row = cur.fetchone()
                current_sha = file_sha256(full_path)

                if row and row[1] == current_sha:
                    skipped_count += 1
                    continue

                # Read and chunk
                with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handle:
                    text = file_handle.read()

                # Chunking by paragraphs / 50 lines
                lines = text.splitlines()
                chunks = []
                chunk_size = 40
                for i in range(0, len(lines), chunk_size):
                    chunk_text = "\n".join(lines[i:i+chunk_size])
                    if chunk_text.strip():
                        chunks.append(chunk_text)

                # Delete old chunks
                cur.execute("DELETE FROM chunks WHERE filepath = ?", (full_path,))
                
                # Embed chunks
                for idx, ch in enumerate(chunks[:5]):
                    emb = get_embedding(ch)
                    if emb:
                        cur.execute("INSERT INTO chunks (filepath, chunk_index, content, embedding) VALUES (?, ?, ?, ?)",
                                    (full_path, idx, ch, json.dumps(emb)))

                cur.execute("INSERT OR REPLACE INTO file_hashes (filepath, mtime, sha256) VALUES (?, ?, ?)",
                            (full_path, stat.st_mtime, current_sha))
                conn.commit()
                indexed_count += 1
                print(f"  {GREEN}✔ Embedded:{RESET} {os.path.relpath(full_path, directory)}")

                if indexed_count >= max_files:
                    break
            except Exception as e:
                pass

        if indexed_count >= max_files:
            break

    print(f"\n{GREEN}{BOLD}🎉 Indexing complete!{RESET} Embedded: {indexed_count} files | Skipped (Unchanged): {skipped_count} files.\n")
    conn.close()

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Work")
    index_directory(target_dir)
