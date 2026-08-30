import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_compressor import ContextCompressor

def test_extreme_context_compression():
    print("Testing 250,000-token context compression...")
    
    # Generate bloated conversation transcript (50 turns with large file dumps)
    messages = [
        {"role": "system", "content": "You are an expert coding assistant with access to tools."}
    ]
    
    for i in range(40):
        messages.append({
            "role": "user",
            "content": f"Turn {i}: Here is the contents of file_{i}.py with 500 lines of code.\n" + ("x = 100\n" * 500)
        })
        messages.append({
            "role": "assistant",
            "content": f"I analyzed file_{i}.py. Output: " + ("result_data = True\n" * 200)
        })

    # Recent turns
    messages.append({"role": "user", "content": "Can you fix the syntax error in main.py?"})
    messages.append({"role": "assistant", "content": "Sure, let me check main.py."})
    messages.append({"role": "user", "content": "go on"})

    compressed, before_tok, after_tok = ContextCompressor.compress_messages(messages, max_target_tokens=4000)
    
    savings_pct = ((before_tok - after_tok) / before_tok) * 100
    
    print(f"  • Before Tokens: {before_tok:,} tokens")
    print(f"  • After Tokens:  {after_tok:,} tokens")
    print(f"  • Quota Saved:   {before_tok - after_tok:,} tokens ({savings_pct:.1f}% reduction!)")
    
    assert after_tok < 5000, "Compressed tokens should be below 5,000"
    assert savings_pct > 80.0, "Should save at least 80% tokens"
    print("\n🎉 Extreme context compression test passed!")

if __name__ == "__main__":
    test_extreme_context_compression()
