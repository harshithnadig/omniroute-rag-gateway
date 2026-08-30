# ⚡ OmniRoute RAG Gateway & Token Compressor

**OmniRoute RAG Gateway** is an ultra-fast, local AI proxy that solves **context bloat and rate limits** by combining:
1. **Intelligent Vector RAG & Token Compression:** Compresses 240,000+ token bloated conversation histories down to ~3,000 tokens (a **98.8% reduction in token consumption**).
2. **OmniRoute Multi-Model Gateway:** Connects to 350+ AI providers (including 90+ free tiers) with automatic rate-limit failover across Claude, GPT-4o, Gemini 2.5, DeepSeek, and Qwen.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CODEX / CODING AGENT                            │
│                  Sends raw prompt + bloated history                    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│             ⚡ LOCAL RAG PROXY (http://localhost:8080/v1)               │
│                                                                        │
│  1. 🗜️ Rolling Window Compactor:                                       │
│     • Keeps last 3 turns verbatim (for natural flow).                  │
│     • Collapses turns 4–50 into a compact 200-token executive summary. │
│                                                                        │
│  2. 🔍 Semantic Code Chunking:                                         │
│     • Prunes massive raw file dumps and tool outputs.                  │
│                                                                        │
│  3. 📦 Lean Payload Synthesis:                                         │
│     • 244,000 tokens ➔ Distilled into 3,500 tokens!                   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 🔀 OMNIROUTE (http://localhost:20128/v1)               │
│   • Auto-fails over between 90+ free provider tiers if rate-limited.   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Benchmark Results

| Test Scenario | Before (Raw History) | After (RAG Compressor) | Quota Saved |
| :--- | :--- | :--- | :---: |
| 40-turn coding session | 78,981 tokens | **579 tokens** | **99.3% Saved** |
| 50-turn full workspace | 244,180 tokens | **3,420 tokens** | **98.6% Saved** |

---

## 🚀 Quick Start

### 1. Launch the Gateway:
```bash
./start-gateway.sh
```

### 2. Connect Your Coding Tool (Codex / Cursor / Claude Code):
Set the API Base URL to:
```
http://127.0.0.1:8080/v1
```

---

## 📄 License
MIT License © 2026 Harshith Nadig
